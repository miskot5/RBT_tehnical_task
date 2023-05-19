from flask import Flask
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/nekretnine'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
