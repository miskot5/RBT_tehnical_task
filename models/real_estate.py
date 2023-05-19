from config import *
from marshmallow import Schema, fields, validates_schema, validate
from models.type_of_real_estate import TypeOfRealEstate
from models.location import Location
from werkzeug.exceptions import NotFound


class RealEstate(db.Model):
    __tablename__ = 'real_estate'
    external_id = db.Column(db.String(256))
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_id = db.Column(db.Integer, db.ForeignKey('type_of_real_estate.id'))
    type = db.relationship('TypeOfRealEstate', backref=db.backref('real_estate', lazy='joined'))
    offer = db.Column(db.String(256))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    location = db.relationship('Location', backref=db.backref('real_estate', lazy='joined'))
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

    def __init__(self, external_id, type_id, location_id, offer, square_meter, year, area, storey, num_of_floors,
                 registration, heating_type, num_of_rooms, num_of_toilets, parking, elevator, other):
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
            "external_id": self.external_id,
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


class RealEstateSchema(Schema):
    type_id = fields.Int(required=True)
    location_id = fields.Int(required=True)
    square_meter = fields.Int(required=True)
    year = fields.Int(required=False, default=None, allow_none=True)
    offer = fields.Str(required=True, validate=validate.OneOf(["Prodaja", "Izdavanje"]))
    area = fields.Int(required=False, default=None, allow_none=True)
    storey = fields.Str(required=False, default=None, allow_none=True)
    num_of_floors = fields.Int(default=None, allow_none=True)
    registration = fields.Boolean(default=False)
    heating_type = fields.Str(default=None, allow_none=True)
    num_of_rooms = fields.Int(default=None, allow_none=True)
    num_of_toilets = fields.Int(default=None, allow_none=True)
    parking = fields.Boolean(default=False)
    elevator = fields.Boolean(default=False)
    other = fields.Boolean(default=False)

    @validates_schema
    def validate(self, data, **kwargs):
        existing_type = TypeOfRealEstate.query.filter(TypeOfRealEstate.id == data['type_id']).first()
        print(data['type_id'])
        print(existing_type)
        if not existing_type:
            raise NotFound("Type with this id not exist")

        existing_location = Location.query.filter(Location.id == data['location_id']).first()
        if not existing_location:
            raise NotFound("Location with this id not exist")


class UpdateRealEstateSchema(Schema):
    registration = fields.Bool(required=False)
    heating_type = fields.Str(required=False)

