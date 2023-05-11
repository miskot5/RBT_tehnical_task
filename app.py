from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/nekretnine'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
migrate = Migrate(app, db)
db.init_app(app)


class Location(db.Model):
    __tablename__ = "location"
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(30))
    part_of_city = db.Column(db.String(30))

class TypeOfRealEstate(db.Model):
    __tablename__ = "type_of_real_estate"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    category = db.Column(db.String(256))
class RealEstate(db.Model):
    __tablename__ = 'real_estate'
    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('type_of_real_estate.id'))
    type = db.relationship('TypeOfRealEstate', backref = db.backref('real_estate', lazy=False))
    offer = db.Column(db.String(20))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    location = db.relationship('Location', backref = db.backref('real_estate', lazy=True))
    square_meter = db.Column(db.Integer)
    year = db.Column(db.Integer)
    area = db.Column(db.Integer)
    storey = db.Column(db.String(20))
    num_of_floors = db.Column(db.Integer)
    registration = db.Column(db.String(5))
    heating_type = db.Column(db.Text)
    num_of_rooms = db.Column(db.Integer)
    num_of_toilets = db.Column(db.Integer)
    parking = db.Column(db.String(10))
    elevator = db.Column(db.String(10))
    other = db.Column(db.String(200))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
