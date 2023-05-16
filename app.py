from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify
from sqlalchemy import and_
import crawler

db = SQLAlchemy()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/nekretnine'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
migrate = Migrate(app, db)
db.init_app(app)


class Location(db.Model):
    __tablename__ = "location"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city = db.Column(db.String(256))
    part_of_city = db.Column(db.String(256))

    def __init__(self, city, part_of_city):
        self.city = city
        self.part_of_city = part_of_city


class TypeOfRealEstate(db.Model):
    __tablename__ = "type_of_real_estate"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256))
    category = db.Column(db.String(256))

    def __init__(self, name, category):
        self.name = name
        self.category = category


class RealEstate(db.Model):
    __tablename__ = 'real_estate'
    external_id = db.Column(db.String(256))
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_id = db.Column(db.Integer, db.ForeignKey('type_of_real_estate.id'))
    type = db.relationship('TypeOfRealEstate', backref = db.backref('real_estate', lazy='joined'))
    offer = db.Column(db.String(256))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    location = db.relationship('Location', backref = db.backref('real_estate', lazy='joined'))
    square_meter = db.Column(db.Integer)
    year = db.Column(db.Integer)
    area = db.Column(db.Integer)
    storey = db.Column(db.String(256))
    num_of_floors = db.Column(db.Integer)
    registration = db.Column(db.Boolean)
    heating_type = db.Column(db.String(256))
    num_of_rooms = db.Column(db.Integer)
    num_of_toilets = db.Column(db.Integer)
    parking = db.Column(db.Boolean)
    elevator = db.Column(db.Boolean)
    other = db.Column(db.Boolean)

    def __init__(self, external_id,type_id, location_id, offer, square_meter, year, area, storey, num_of_floors, registration, heating_type, num_of_rooms, num_of_toilets, parking, elevator, other):
        self.external_id = external_id
        self.type_id = type_id
        self.location_id = location_id
        self.offer = offer
        self.square_meter = square_meter
        self.year = year
        self.area = area
        self.storey = storey
        self.num_of_floors = num_of_floors
        self.registration = registration
        self.heating_type = heating_type
        self.num_of_rooms = num_of_rooms
        self.num_of_toilets = num_of_toilets
        self.parking = parking
        self.elevator = elevator
        self.other = other

    def __json__(self):
        return {
            "external_id" : self.external_id,
            "type_id": self.type_id,
            "location_id": self.location_id,
            "type_name": self.type.name,
            "location": self.location.city + ',' + self.location.part_of_city,
            "spm": self.square_meter,
            "year": self.year,
            "area": self.area,
            "storey": self.storey,
            "num_of_floors": self.num_of_floors,
            "registration": self.registration,
            "heating_type": self.heating_type,
            "num_of_rooms": self.num_of_rooms,
            "num_of_toilets": self.num_of_toilets,
            "parking": self.parking,
            "elevator": self.elevator,
            "other": self.other
        }


@app.route('/crawl', methods=['POST'])
def crawl():
    data = request.get_json()
    url = data.get('url', None)
    limit = data.get('limit')
    try:
        limit = int(limit)
    except Exception as e:
        return jsonify("Parameter is not int"), 400
    if not url:
        return "Nije pronađen URL u POST zahtevu."

    if url == "https://www.nekretnine.rs" or url == "http://www.nekretnine.rs" or url == "www.nekretnine.rs":
        url = "http://www.nekretnine.rs/"

    if not url.__contains__("nekretnine.rs"):
        return "URL nije validan"

    realEstateUrls = crawler.processing_all_real_estate(url, limit)
    count_real_estate = 0
    count_types_of_real_estate = 0
    count_location = 0
    for realEstateUrl in realEstateUrls:
        realEstate = crawler.real_estate_processing(realEstateUrl)

        #uzimamo grad i deo grada iz lokacije
        city = realEstate.location.city
        part_of_city = realEstate.location.part_of_city
        location = Location(city, part_of_city)

        existing_location = Location.query.filter(
            Location.city == location.city,
            Location.part_of_city == location.part_of_city
        ).first()

        if existing_location:
            location = existing_location
        else:
            count_location+=1
            db.session.add(location)
            db.session.commit()

        #provera da li u tipu postoje informacije i o kategoriji i o potkategoriji(npr. Stan, Petosoban stan)
        if ',' in realEstate.type:
            type = realEstate.type.split(',')[0]
            category = realEstate.type.split(',')[1]
        else:
            type = realEstate.type
            category = 'nepoznato'

        type_of_real_estate = TypeOfRealEstate(type, category)
        existing_type = TypeOfRealEstate.query.filter(
            TypeOfRealEstate.name == type_of_real_estate.name,
            TypeOfRealEstate.category == type_of_real_estate.category
        ).first()

        if existing_type:
            type_of_real_estate = existing_type
        else:
            count_types_of_real_estate+=1
            db.session.add(type_of_real_estate)
            db.session.commit()

        real_estate = RealEstate(
            external_id=realEstate.external_id,
            type_id=type_of_real_estate.id,
            location_id=location.id,
            offer = realEstate.offer,
            square_meter = realEstate.spm,
            year = realEstate.year,
            registration = realEstate.registration,
            area = realEstate.area,
            storey = realEstate.storey,
            num_of_floors = realEstate.num_of_floors,
            heating_type = realEstate.heating_type,
            num_of_rooms = realEstate.num_of_rooms,
            num_of_toilets = realEstate.num_of_toilets,
            parking = realEstate.parking,
            elevator = realEstate.elevator,
            other = realEstate.other)

        #proveru da li nekretnina postoji cemo vrsiti po jedinstvenom uuid koji dobijamo direktno iz linka nekretnine sa sajta
        #da bismo ubrzali proveru i da se ne bi vrsila po svakom atributu objekta real_estate
        existing_real_estate = RealEstate.query.filter(RealEstate.external_id==real_estate.external_id).all()

        if existing_real_estate:
            real_estate = existing_real_estate
        else:
            count_real_estate+=1
            db.session.add(real_estate)
            db.session.commit()

    return {"Broj dodatih lokacija" : count_location,
            "Broj dodatih tipova nekretnina" : count_types_of_real_estate,
            "Broj dodatih nekretnina" : count_real_estate}


@app.route('/real_estate/<int:id>', methods = ['GET'])
def get_real_estate_by_id(id):
    real_estate = db.session.query(RealEstate).filter(id == id).first()

    if not real_estate:
        return jsonify({'error': 'Real estate not found'}), 404
    return jsonify(real_estate.__json__())


@app.route('/search', methods = ['GET'])
def search():
    query = RealEstate.query
    if 'type' in request.args:
        query = query.filter(RealEstate.type.has(name = request.args.get('type')))
    if 'min_spm' in request.args:
        query = query.filter(and_(RealEstate.square_meter > request.args.get('min_spm')))
    if 'max_spm' in request.args:
        query = query.filter(and_(RealEstate.square_meter < request.args.get('max_spm')))
    if 'parking' in request.args:
        query = query.filter(and_(RealEstate.parking == request.args.get('parking')))

    page = request.args.get('page', 1, type = int)
    real_estates = query.paginate(page = page, per_page = 5)
    result = [{
        'type_id':real_estate.type_id,
        'type': real_estate.type.name + ", " + real_estate.type.category,
        'location_id': real_estate.location_id,
        'location': real_estate.location.city + ", " + real_estate.location.part_of_city if real_estate.location.part_of_city is not None else real_estate.location.city + ", "  'nepoznato',
        'offer' : real_estate.offer,
        'year' : real_estate.year,
        'area' : real_estate.area,
        'spm' : real_estate.square_meter,
        'num_of_rooms' : real_estate.num_of_rooms,
        'registration' : real_estate.registration,
        'storey' : real_estate.storey,
        'num_of_floors' : real_estate.num_of_floors,
        'num_of_toilets' : real_estate.num_of_toilets,
        'parking' : real_estate.parking,
        'elevator' : real_estate.elevator,
        'other' : real_estate.other
    } for real_estate in real_estates]

    return jsonify({
        'success': True,
        'results' : result,
        'count' : len(result)
    })

@app.route('/new_location', methods = ['POST'])
def create_location():
    data = request.json
    print(data)
    try:
        city = data['city']
        if type(city) is not str:
           return jsonify("Invalid parameter city")
    except KeyError:
        return jsonify("City missing"), 400

    try:
        part_of_city = data['part_of_city']
        print(part_of_city)
        if type(part_of_city) is not str:
            return jsonify("Invalid parameter part_of_city")
    except KeyError:
        return jsonify("Part_of_city missing"), 400

    existing_location = Location.query.filter(
        Location.city == city,
        Location.part_of_city == part_of_city
    ).first()

    if existing_location:
        return jsonify("Location already exist"), 400
    else:
        location = Location(city, part_of_city)
        db.session.add(location)
        db.session.commit()
        return jsonify("Location created"), 200


@app.route('/new_type_of_real_estate', methods=['POST'])
def create_type_of_real_estate():
    data = request.json

    try:
        name = data['name']
        if type(name) is not str:
            return jsonify("Invalid parameter name")
    except KeyError:
        return jsonify("Name missing"), 400

    try:
        category = data['category']
        if type(category) is not str:
            return jsonify("Invalid parameter category")
    except KeyError:
        return jsonify("category missing"), 400

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


@app.route('/new_real_estate', methods=['POST'])
def create_real_estate():
    data = request.json

    # Podaci iz zahteva
    try:
        location_id = int(data['location_id'])
    except KeyError:
        return jsonify("Location_id missing")
    except Exception as e:
        return jsonify("Invalid parameter location_id")

    location = Location.query.filter(Location.id == location_id).first()
    if not location:
        return jsonify("Location not exist"), 404

    try:
        type_id = int(data['type_id'])
    except KeyError:
        return jsonify("Location_id missing")
    except Exception as e:
        return jsonify("Invalid parameter location_id")

    type_of_real_estate = TypeOfRealEstate.query.filter(TypeOfRealEstate.id == type_id).first()
    if not type_of_real_estate:
        return jsonify("Type of real estate not exist"), 404

    offer = data.get('offer', None)
    if type(offer) is not str:
        return jsonify("Invalid parameter offer"), 400

    registration = data.get('registration', False)
    if type(registration) is not bool:
        return jsonify("Invalid parameter registration"), 400


    storey = data.get('storey')
    if type(storey) is not str:
        return jsonify("Invalid parameter storey"), 400

    try:
        num_of_floors = int(data.get('num_of_floors'))
    except Exception as e:
        return jsonify("Paramerer num_of_floors is not int")

    try:
        num_of_rooms = int(data.get('num_of_rooms'))
    except Exception as e:
        return jsonify("Paramerer num_of_rooms is not int")

    try:
        square_meter = int(data.get('square_meter'))
    except Exception as e:
        return jsonify("Paramerer square_meter is not int")

    try:
        num_of_toilets = int(data.get('num_of_toilets'))
    except Exception as e:
        return jsonify("Paramerer num_of_toilets is not int")

    elevator = data.get('elevator', False)
    if type(elevator) is not bool:
        return jsonify("Invalid parameter elevator"), 400


    parking = data.get('parking', False)
    if type(parking) is not bool:
        return jsonify("Invalid parameter parking"), 400

    other = data.get('other', False)
    if type(other) is not bool:
        return jsonify("Invalid parameter other"), 400

    try:
        area = int(data.get('area'))
    except Exception as e:
        return jsonify("Paramerer area is not int")

    try:
        year = int(data.get('year'))
    except KeyError:
        year = None
    except Exception as e:
        return jsonify("Paramerer year is not int")

    heating_type = data.get('heating_type', None)
    if type(heating_type) is not str:
        return jsonify("Invalid parameter heating_type"), 400

    if type_of_real_estate.name == 'Kuca':
        real_estate = RealEstate(
            external_id = None,
            type_id=type_id,
            location_id=location_id,
            offer=offer,
            square_meter=square_meter,
            year=year,
            area=area,
            storey = None,
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

@app.route('/update_real_estate', methods = ['POST'])
def update_real_estate():
    data = request.json
    try:
        id = data['id']
    except KeyError:
        return jsonify(error = 'Parameter id missing'), 400

    if len(data) > 3:
        return jsonify(error = 'Too many parameters'), 400

    if type(id) is not int:
        return jsonify(error='Invalid type of parameter id'), 400
    real_estate = db.session.query(RealEstate).filter_by(id=id).first()
    print(real_estate)
    if not real_estate:
        return jsonify(error='Invalid real_estate_id'), 400

    for key in data:
        if key != 'registration' and key != 'heating_type' and key != 'id':
            return jsonify("Invalid parameters")
        if key == 'registration' and isinstance(data[key], bool):
            real_estate.registration = data[key]
        if key == 'heating_type' and isinstance(data[key], str):
            real_estate.heating_type = data[key]

    db.session.commit();

    return "Successful update", 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
