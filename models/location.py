from marshmallow.validate import Length
from config import *
from marshmallow import Schema, fields, validates_schema
from marshmallow import ValidationError



class Location(db.Model):
    __tablename__ = "location"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city = db.Column(db.String(256))
    part_of_city = db.Column(db.String(256))

    def __init__(self, city, part_of_city):
        self.city = city
        self.part_of_city = part_of_city

    def __json__(self):
        return {
            'city': self.city,
            'part_of_city': self.part_of_city
        }


class LocationSchema(Schema):
    city = fields.Str(required=True, validate=Length(min=2), allow_none=False)
    part_of_city = fields.Str(default=None, validate=Length(min=2), allow_none=True)

    @validates_schema
    def validate(self, data, **kwargs):
        existing_location = Location.query.filter(
            Location.city == data['city'],
            Location.part_of_city == (data['part_of_city'] if 'part_of_city' in data else None)
        ).first()
        print(existing_location)
        if existing_location:
            raise ValidationError("Already exists")
