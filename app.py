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

    def __init__(self, type_id, location_id, offer, square_meter, year, area, storey, num_of_floors, registration, heating_type, num_of_rooms, num_of_toilets, parking, elevator, other):
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

    if not url:
        return "Nije pronađen URL u POST zahtevu."

    if url == "https://www.nekretnine.rs" or (url == "http://www.nekretnine.rs") or url == "www.nekretnine.rs":
        url = "http://www.nekretnine.rs/"

    if not url.__contains__("nekretnine.rs"):
        return "URL nije validan"

    realEstateUrls = crawler.processing_all_real_estate(url)
    count_real_estate = 0
    count_types_of_real_estate = 0
    count_location = 0
    for realEstateUrl in realEstateUrls:
        realEstate = crawler.real_estate_processing(realEstateUrl)
        print(realEstate.registration)
        print(realEstate.elevator)
        print(realEstate.other)
        print(realEstate.parking)
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

        #provera da li u tipu postoje informacije i o kategoriji i o potkategoriji(pr. Stan, Petosoban stan)
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

        existing_real_estate = RealEstate.query.filter(
            RealEstate.type_id == real_estate.type_id,
            RealEstate.location_id == real_estate.location_id,
            RealEstate.offer == real_estate.offer,
            RealEstate.square_meter == real_estate.square_meter,
            RealEstate.year == real_estate.year,
            RealEstate.area == real_estate.area,
            RealEstate.registration == real_estate.registration,
            RealEstate.storey == real_estate.storey,
            RealEstate.num_of_floors == real_estate.num_of_floors,
            RealEstate.heating_type == real_estate.heating_type,
            RealEstate.num_of_rooms == real_estate.num_of_rooms,
            RealEstate.num_of_toilets == real_estate.num_of_toilets,
            RealEstate.parking == real_estate.parking,
            RealEstate.elevator == real_estate.elevator,
            RealEstate.other == real_estate.other
        ).all()

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
    real_estate = db.session.query(RealEstate).filter_by(id == id).first()

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
        'location': real_estate.location.city + ", " + real_estate.location.part_of_city,
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



@app.route('/new_real_estate', methods=['POST'])
def create_real_estate():
    data = request.json
    print(data)
    type_id = data['type_id']
    if type(type_id) is not int:
        return jsonify(error='Invalid type of parameter type_id'), 400

    location_id = data['location_id']
    if type(location_id) is not int:
        return jsonify(error='Invalid type of parameter location_id'), 400

    type_of_real_estate = TypeOfRealEstate.query.get(type_id)
    location = Location.query.get(location_id)

    if not type_of_real_estate or not location:
        return jsonify(error='Invalid type_id or location_id'), 400

    if type(data['offer']) is not str:
        return jsonify(error='Invalid type of parameter offer'), 400
    if type(data['square_meter']) is not int:
        return jsonify(error='Invalid type of parameter square_meter'), 400
    if type(data['year']) is not int:
        return jsonify(error='Invalid type of parameter year'), 400
    if type(data['area']) is not int:
        return jsonify(error='Invalid type of parameter area'), 400
    if type(data['storey']) is not str:
        return jsonify(error='Invalid type of parameter storey'), 400
    if type(data['num_of_floors']) is not int:
        return jsonify(error='Invalid type of parameter num_of_floors'), 400
    if type(data['registration']) is not str:
        return jsonify(error='Invalid type of parameter registration'), 400
    if type(data['heating_type']) is not str:
        return jsonify(error='Invalid type of parameter heating_type'), 400
    if type(data['num_of_rooms']) is not int:
        return jsonify(error='Invalid type of parameter num_of_rooms'), 400
    if type(data['num_of_toilets']) is not int:
        return jsonify(error='Invalid type of parameter num_of_toilets'), 400
    if type(data['parking']) is not bool:
        return jsonify(error='Invalid type of parameter parking'), 400
    if type(data['elevator']) is not bool:
        return jsonify(error='Invalid type of parameter elevator'), 400
    if type(data['other']) is not bool:
        return jsonify(error='Invalid type of parameter other'), 400

    real_estate = RealEstate(
        type_id=type_id,
        location_id=location_id,
        offer=data['offer'],
        square_meter=data['square_meter'],
        year=data['year'],
        area=data['area'],
        storey=data['storey'],
        num_of_floors=data['num_of_floors'],
        registration=data['registration'],
        heating_type=data['heating_type'],
        num_of_rooms=data['num_of_rooms'],
        num_of_toilets=data['num_of_toilets'],
        parking=data['parking'],
        elevator=data['elevator'],
        other=data['other']
    )
    db.session.add(real_estate)
    db.session.commit()

    return "Uspesno dodata nekretnina", 201

@app.route('/update_real_estate', methods = ['POST'])
def update_real_estate():
    data = request.json
    id = data['id']
    if type(id) is not int:
        return jsonify(error='Invalid type of parameter id'), 400
    real_estate = db.session.query(RealEstate).filter_by(id=id).first()
    print(real_estate)
    if not real_estate:
        return jsonify(error='Invalid real_estate_id'), 400

    if 'registration' in data and isinstance(data['registration'],str):
        real_estate.registration = data['registration']

    if 'heating_type' in data and isinstance(data['heating_type'],str):
        real_estate.heating_type = data['heating_type']

    db.session.commit();

    return "Successful update", 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
