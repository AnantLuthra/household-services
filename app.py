from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import date


#------------ Initialisations ---------------#
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3"
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()


#------------ Database classes ---------------#

class professional(db.Model):

    __tablename__ = "professional"
    professional_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    date_created = db.Column(db.Date, nullable=False)
    description = db.Column(db.String, nullable=False)
    # service_type = 