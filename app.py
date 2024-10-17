from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required


#------------ Initialisations ---------------#
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3"
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

#------------ Global Variables --------------#
ADMIN_PASS = "good123"

#------------ Database classes ---------------#

class professional(db.Model):

    __tablename__ = "professional"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    date_created = db.Column(db.Date, nullable=False)
    description = db.Column(db.String, nullable=False)
    service_type = db.Column()
    experience = db.Column(db.Integer, nullable=False)
    request = db.Column(db.Boolean, default=None)

    service = relationship("service", backref=backref("professionals", lazy=True))

class customer(db.Model):

    __tablename__ = "customer"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email_id = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    fullname = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    pin_code = db.Column(db.Integer, nullable=False)


class service(db.Model):
    
    __tablename__ = "service"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    time_required = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)

    professionals = relationship("professional", backref=backref("service", lazy=True))


class service_reqest(db.Model):

    __tablename__ = "service_request"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    service_id = db.Column(db.Integer, ForeignKey('service.id'), nullable=False)
    customer_id = db.Column(db.Integer, ForeignKey('customer.id'), nullable=False)
    professional_id = db.Column(db.Integer, ForeignKey('professional.id'), nullable=False)
    date_of_request = db.Column(db.Date, nullable=False)
    date_of_completion = db.Column(db.Date, default=False)
    service_status = db.Column(db.String, default=False)
    rstars = db.Column(db.Integer, default=False)
    rfeedback = db.Column(db.String, default=False)


#------------------ Main landin route ------------------------#

@app.route("/")
def landing():
    return render_template("main_landing.html")


#------------------ Professional Login -----------------------#

@app.route("/professional_login", methods=['GET', 'POST'])
def prof_login():

    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect("/professional")
        return render_template("prof_login.html")

    elif request.method == 'POST':
        ...



if __name__ == '__main__':

    app.run(debug=True)
