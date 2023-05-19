from config import *
from flask_migrate import Migrate
from flask import request, jsonify
from sqlalchemy import and_
import crawler
from models.location import Location
from models.real_estate import RealEstate
from models.type_of_real_estate import TypeOfRealEstate

migrate = Migrate(app, db)
db.init_app(app)


@app.route('/crawl', methods=['POST'])
def crawl():
    data = request.get_json()
    url = data.get('url', None)
    limit = data.get('limit')
    try:
        limit = int(limit)
    except ValueError:
        return jsonify("Parameter is not int"), 400
    if not url:
        return "No url in request"

    if url == "https://www.nekretnine.rs" or url == "https://www.nekretnine.rs" or url == "www.nekretnine.rs":
        url = "https://www.nekretnine.rs/"

    if not url.__contains__("nekretnine.rs"):
        return "URL is not valid"

    real_estate_urls = crawler.processing_all_real_estate(url, limit)
    count_real_estate = 0
    count_types_of_real_estate = 0
    count_location = 0
    for realEstateUrl in real_estate_urls:
        real_e = crawler.real_estate_processing(realEstateUrl)

        city = real_e.location.city
        part_of_city = real_e.location.part_of_city

        existing_location = Location.query.filter(
            Location.city == city,
            Location.part_of_city == part_of_city
        ).first()

        if existing_location:
            location = existing_location
        else:
            location = Location(city, part_of_city)
            count_location += 1
            db.session.add(location)
            db.session.commit()

        if ',' in real_e.type:
            name = real_e.type.split(',')[0]
            category = real_e.type.split(',')[1]
        else:
            name = real_e.type
            category = 'nepoznato'

        existing_type = TypeOfRealEstate.query.filter(
            TypeOfRealEstate.name == name,
            TypeOfRealEstate.category == category
        ).first()

        if existing_type:
            type_of_real_estate = existing_type
        else:
            type_of_real_estate = TypeOfRealEstate(name, category)
            count_types_of_real_estate += 1
            db.session.add(type_of_real_estate)
            db.session.commit()

        real_estate = RealEstate(
            external_id=real_e.external_id,
            type_id=type_of_real_estate.id,
            location_id=location.id,
            offer=real_e.offer,
            square_meter=real_e.spm,
            year=real_e.year,
            registration=real_e.registration,
            area=real_e.area,
            storey=real_e.storey,
            num_of_floors=real_e.num_of_floors,
            heating_type=real_e.heating_type,
            num_of_rooms=real_e.num_of_rooms,
            num_of_toilets=real_e.num_of_toilets,
            parking=real_e.parking,
            elevator=real_e.elevator,
            other=real_e.other)

        existing_real_estate = RealEstate.query.filter(RealEstate.external_id == real_estate.external_id).first()

        if existing_real_estate is None:
            count_real_estate += 1
            db.session.add(real_estate)
            db.session.commit()

    return {"Broj dodatih lokacija": count_location,
            "Broj dodatih tipova nekretnina": count_types_of_real_estate,
            "Broj dodatih nekretnina": count_real_estate}


@app.route('/real_estate/<int:id>', methods=['GET'])
def get_real_estate_by_id(estate_id):
    real_estate = db.session.query(RealEstate).filter(id == estate_id).first()

    if not real_estate:
        return jsonify({'error': 'Real estate not found'}), 404
    return jsonify(real_estate.__json__())


@app.route('/search', methods=['GET'])
def search():
    query = RealEstate.query
    if 'type' in request.args:
        query = query.filter(RealEstate.type.has(name=request.args.get('type')))
    if 'min_spm' in request.args:
        query = query.filter(and_(RealEstate.square_meter > request.args.get('min_spm')))
    if 'max_spm' in request.args:
        query = query.filter(and_(RealEstate.square_meter < request.args.get('max_spm')))
    if 'parking' in request.args:
        query = query.filter(and_(RealEstate.parking == request.args.get('parking')))

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    num_of_real_estates = len(RealEstate.query.filter().all())
    real_estates = query.paginate(page=page, per_page=per_page)
    result = [{
        'type_id': real_estate.type_id,
        'type': real_estate.type.name + ", " + real_estate.type.category,
        'location_id': real_estate.location_id,
        'location': real_estate.location.city + ", " + real_estate.location.part_of_city
        if real_estate.location.part_of_city is not None else real_estate.location.city + ", "  'nepoznato',
        'offer': real_estate.offer,
        'year': real_estate.year,
        'area': real_estate.area,
        'spm': real_estate.square_meter,
        'num_of_rooms': real_estate.num_of_rooms,
        'registration': real_estate.registration,
        'storey': real_estate.storey,
        'num_of_floors': real_estate.num_of_floors,
        'num_of_toilets': real_estate.num_of_toilets,
        'parking': real_estate.parking,
        'elevator': real_estate.elevator,
        'other': real_estate.other
    } for real_estate in real_estates]

    return jsonify({
        'results': result,
        'pagnation': {
            'count': len(result),
            'number of real estates': num_of_real_estates,
            'current page': page
        },
        'success': True
    }, 200)

    @app.route('/location', methods=['POST'])
    def create_location():
        data = request.json
        print(data)
        try:
            city = data['city']
            if type(city) is not str:
                return jsonify("Invalid parameter city"), 404
        except KeyError:
            return jsonify("City missing"), 404

        try:
            part_of_city = data['part_of_city']
            print(part_of_city)
            if type(part_of_city) is not str:
                return jsonify("Invalid parameter part_of_city"), 404
        except KeyError:
            return jsonify("Part_of_city missing"), 400

        existing_location = Location.query.filter(
            Location.city == city,
            Location.part_of_city == part_of_city
        ).first()

        if existing_location:
            return jsonify("Location already exist"), 404
        else:
            location = Location(city, part_of_city)
            db.session.add(location)
            db.session.commit()
            return jsonify("Location created"), 200

    @app.route('/type_of_real_estate', methods=['POST'])
    def create_type_of_real_estate():
        data = request.json

        try:
            name = data['name']
            if type(name) is not str:
                return jsonify("Invalid parameter name"), 404
        except KeyError:
            return jsonify("Name missing"), 404

        try:
            category = data['category']
            if type(category) is not str:
                return jsonify("Invalid parameter category"), 404
        except KeyError:
            return jsonify("category missing"), 404

        existing_type = TypeOfRealEstate.query.filter(
            TypeOfRealEstate.name == name,
            TypeOfRealEstate.category == category
        ).first()

        if existing_type:
            return jsonify("Location already exist"), 400
        else:
            type_of_real_estate = TypeOfRealEstate(name, category)
            db.session.add(type_of_real_estate)
            db.session.commit()
            return jsonify("Type of real estate created"), 200

    @app.route('/real_estate', methods=['POST'])
    def create_real_estate():
        data = request.json

        # Podaci iz zahteva
        try:
            location_id = int(data['location_id'])
        except KeyError:
            return jsonify("Location_id missing"), 404
        except ValueError:
            return jsonify("Invalid parameter location_id"), 404

        location = Location.query.filter(Location.id == location_id).first()
        if not location:
            return jsonify("Location not exist"), 404

        try:
            type_id = int(data['type_id'])
        except KeyError:
            return jsonify("Location_id missing"), 404
        except ValueError:
            return jsonify("Invalid parameter location_id"), 404

        type_of_real_estate = TypeOfRealEstate.query.filter(TypeOfRealEstate.id == type_id).first()
        if not type_of_real_estate:
            return jsonify("Type of real estate not exist"), 404

        offer = data.get('offer', None)
        if type(offer) is not str:
            return jsonify("Invalid parameter offer"), 404

        registration = data.get('registration', False)
        if type(registration) is not bool:
            return jsonify("Invalid parameter registration"), 404

        storey = data.get('storey')
        if type(storey) is not str:
            return jsonify("Invalid parameter storey"), 404

        try:
            num_of_floors = int(data.get('num_of_floors'))
        except ValueError:
            return jsonify("Paramerer num_of_floors is not int"), 404

        try:
            num_of_rooms = int(data.get('num_of_rooms'))
        except ValueError:
            return jsonify("Paramerer num_of_rooms is not int"), 404

        try:
            square_meter = int(data.get('square_meter'))
        except ValueError:
            return jsonify("Paramerer square_meter is not int"), 404

        try:
            num_of_toilets = int(data.get('num_of_toilets'))
        except ValueError:
            return jsonify("Paramerer num_of_toilets is not int"), 404

        elevator = data.get('elevator', False)
        if type(elevator) is not bool:
            return jsonify("Invalid parameter elevator"), 404

        parking = data.get('parking', False)
        if type(parking) is not bool:
            return jsonify("Invalid parameter parking"), 404

        other = data.get('other', False)
        if type(other) is not bool:
            return jsonify("Invalid parameter other"), 404

        try:
            area = int(data.get('area'))
        except ValueError:
            return jsonify("Paramerer area is not int"), 404

        try:
            year = int(data.get('year'))
        except KeyError:
            year = None
        except ValueError:
            return jsonify("Paramerer year is not int"), 404

        heating_type = data.get('heating_type', None)
        if type(heating_type) is not str:
            return jsonify("Invalid parameter heating_type"), 404

        if type_of_real_estate.name == 'Kuca':
            real_estate = RealEstate(
                external_id=None,
                type_id=type_id,
                location_id=location_id,
                offer=offer,
                square_meter=square_meter,
                year=year,
                area=area,
                storey=None,
                num_of_floors=num_of_floors,
                registration=registration,
                heating_type=heating_type,
                num_of_rooms=num_of_rooms,
                num_of_toilets=num_of_toilets,
                parking=parking,
                elevator=elevator,
                other=other
            )
        else:
            real_estate = RealEstate(
                external_id=None,
                type_id=type_id,
                location_id=location_id,
                offer=offer,
                square_meter=square_meter,
                year=year,
                area=0,
                storey=storey,
                num_of_floors=num_of_floors,
                registration=registration,
                heating_type=heating_type,
                num_of_rooms=num_of_rooms,
                num_of_toilets=num_of_toilets,
                parking=parking,
                elevator=elevator,
                other=other
            )
        db.session.add(real_estate)
        db.session.commit()

        return "Creating successful", 201

    @app.route('/update_real_estate/<int:estate_id>', methods=['PUT'])
    def update_real_estate(estate_id):
        data = request.json

        try:
            estate_id = data['id']
        except KeyError:
            return jsonify(error='Parameter id missing'), 404

        if len(data) > 3:
            return jsonify(error='Too many parameters'), 404

        if type(id) is not int:
            return jsonify(error='Invalid type of parameter id'), 404
        real_estate = db.session.query(RealEstate).filter_by(id=estate_id).first()
        print(real_estate)
        if not real_estate:
            return jsonify(error='Invalid real_estate_id'), 404

        for key in data:
            if key != 'registration' and key != 'heating_type' and key != 'id':
                return jsonify("Invalid parameters")
            if key == 'registration' and isinstance(data[key], bool):
                real_estate.registration = data[key]
            if key == 'heating_type' and isinstance(data[key], str):
                real_estate.heating_type = data[key]

        db.session.commit()

        return "Successful update", 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
