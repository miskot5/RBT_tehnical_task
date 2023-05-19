from config import *


class Location(db.Model):
    __tablename__ = "location"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city = db.Column(db.String(256))
    part_of_city = db.Column(db.String(256))

    def __init__(self, city, part_of_city):
        self.city = city
        self.part_of_city = part_of_city
