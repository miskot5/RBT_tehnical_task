from marshmallow.validate import Length
from config import *
from marshmallow import Schema, fields, validates_schema
from marshmallow import ValidationError


class TypeOfRealEstate(db.Model):
    __tablename__ = "type_of_real_estate"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256))
    category = db.Column(db.String(256))

    def __init__(self, name, category):
        self.name = name
        self.category = category

    def __json__(self):
        return {
            "name": self.name,
            "category": self.category
        }


class TypeOfRealEstateSchema(Schema):
    name = fields.Str(required=True, validate=Length(min=4), allow_none=False)
    category = fields.Str(default=None, validate=Length(min=4), allow_none=True)

    @validates_schema
    def validate(self, data, **kwargs):
        existing_type = TypeOfRealEstate.query.filter(
            TypeOfRealEstate.name == data['name'],
            TypeOfRealEstate.category == (data['category'] if 'category' in data else None)
        ).first()

        if existing_type:
            raise ValidationError("Type of real estate already exists")
