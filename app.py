import math

import config
from config import *
from flask_migrate import Migrate
from flask import request, jsonify
from sqlalchemy import and_
import crawler
from models.location import Location, LocationSchema
from models.real_estate import RealEstate, RealEstateSchema, UpdateRealEstateSchema
from models.type_of_real_estate import TypeOfRealEstate, TypeOfRealEstateSchema

migrate = Migrate(config.app, db)
db.init_app(config.app)


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
            'per_page': len(result),
            'number of pages': math.ceil(num_of_real_estates / per_page),
            'number of real estates': num_of_real_estates,
            'current page': page
        },
        'success': True
    }, 200)


@app.route('/location', methods=['POST'])
def create_location():
    data = request.json

    location_schema = LocationSchema()
    new_location = location_schema.load(data)

    location = Location(new_location.get('city'), new_location.get('part_of_city'))
    db.session.add(location)
    db.session.commit()

    return location.__json__(), 200


@app.route('/type_of_real_estate', methods=['POST'])
def create_type_of_real_estate():
    data = request.json

    type_schema = TypeOfRealEstateSchema()
    new_type = type_schema.load(data)

    type_of_real_estate = TypeOfRealEstate(new_type.get('name'), new_type.get('category'))
    db.session.add(type_of_real_estate)
    db.session.commit()

    return type_of_real_estate.__json__(), 200


@app.route('/real_estate', methods=['POST'])
def create_real_estate():
    data_json = request.json

    real_estate_schema = RealEstateSchema()
    data = real_estate_schema.load(data_json)
    new_real_estate = RealEstate(external_id=None, type_id=data.get('type_id'), location_id=data.get('location_id'),
                                 offer=data.get('offer'), year=data.get('year'), area=data.get('area'),
                                 num_of_floors=data.get('num_of_floors'), registration=data.get('registration'),
                                 num_of_rooms=data.get('num_of_rooms'), num_of_toilets=data.get('num_of_toilets'),
                                 elevator=data.get('elevator'), parking=data.get('parking'), other=data.get('other'),
                                 heating_type=data.get('heating_type'), square_meter=data.get('square_meter'),
                                 storey=data.get('storey'))

    db.session.add(new_real_estate)
    db.session.commit()

    return new_real_estate.__json__(), 200


@app.route('/real_estate/<int:estate_id>', methods=['PUT'])
def update_real_estate(estate_id):
    data_json = request.json
    update_real_estate_schema = UpdateRealEstateSchema()
    data = update_real_estate_schema.load(data_json)

    print(data_json)
    print(estate_id)
    real_estate = RealEstate.query.filter(RealEstate.id == estate_id).first()
    if not real_estate:
        return jsonify("Real estate with this id not exist"), 404
    else:
        if 'heating_type' in data:
            real_estate.heating_type = data['heating_type']
        if 'registration' in data:
            real_estate.registration = data['registration']

    return real_estate.__json__(), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
