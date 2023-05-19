from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from error import error_bp
db = SQLAlchemy()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/nekretnine'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.register_blueprint(error_bp)
