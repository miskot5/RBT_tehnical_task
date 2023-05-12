import re

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify

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
    type = db.relationship('TypeOfRealEstate', backref = db.backref('real_estate', lazy=False))
    offer = db.Column(db.String(256))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    location = db.relationship('Location', backref = db.backref('real_estate', lazy=True))
    square_meter = db.Column(db.Integer)
    year = db.Column(db.Integer)
    area = db.Column(db.Integer)
    storey = db.Column(db.String(256))
    num_of_floors = db.Column(db.Integer)
    registration = db.Column(db.String(256))
    heating_type = db.Column(db.String(256))
    num_of_rooms = db.Column(db.Integer)
    num_of_toilets = db.Column(db.Integer)
    parking = db.Column(db.String(256))
    elevator = db.Column(db.String(256))
    other = db.Column(db.String(256))

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

    realEstateUrls = crawler.processing_home_page(url)
    count_real_estate = 0
    count_types_of_real_estate = 0
    count_location = 0
    for realEstateUrl in realEstateUrls:
        realEstate = crawler.real_estate_processing(realEstateUrl)

        #uzimamo grad i deo grada iz lokacije
        city = realEstate.location.split(',')[0]
        part_of_city = realEstate.location.split(',')[1]
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


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
