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
DUMMY_PROFESSION_PASS = ADMIN_PASS
DUMMY_CUSTOMER_PASS = ADMIN_PASS

#------------ Database classes ---------------#

class professional(db.Model):

    __tablename__ = "professional"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    date_created = db.Column(db.Date, nullable=False)
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


#------------------- Admin Login -----------------------------#

@app.route("/admin_login", methods=['GET', 'POST'])
def admin_login():

    if request.method == 'GET':
        # if current_user.is_authenticated:
        #     return redirect("/professional")
        return render_template("admin_login.html")

    elif request.method == 'POST':
        
        password = request.form.get('password')

        if ADMIN_PASS == password:
            return redirect("/admin_home")
        else:
            return f"Wrong password"


#------------------ Professional Login -----------------------#

@app.route("/professional_login", methods=['GET', 'POST'])
def prof_login():

    if request.method == 'GET':
        # if current_user.is_authenticated:
        #     return redirect("/professional")
        return render_template("prof_login.html")

    elif request.method == 'POST':
        
        email = request.form.get('mail')
        password = request.form.get('password')

        return f"Email: {email}, Password: {password}"



#-------------------- New Professional Page -----------------------#

@app.route("/new_professional", methods = ['GET', 'POST'])
def new_professional():

    if request.method == 'GET':
        return render_template("new_professional.html")
    
    elif request.method == 'POST':

        email = request.form.get('mail')
        password = request.form.get('password')
        fullname = request.form.get('fullname')
        service_type = request.form.get('service_type')
        experience = request.form.get('experience')
        documents = request.form.get('documents')
        address = request.form.get('address')
        pin_code = request.form.get('pincode')

        return f"Email: {email}, Password: {password}, Fullname: {fullname}, Service Type: {service_type}, Experience: {experience}, Documents: {documents}, Address: {address}, Pin Code: {pin_code}"
    

#-------------------- Customer Login page --------------------------#

@app.route("/customer_login", methods=['GET', 'POST'])
def customer_login():

    if request.method == 'GET':
        # if current_user.is_authenticated:
            # return redirect("/professional")
        return render_template("customer_login.html")

    elif request.method == 'POST':
        
        email = request.form.get('mail')
        password = request.form.get('password')

        return f"Email: {email}, Password: {password}"


#--------------------- New Customer Page --------------------------#

@app.route("/new_customer", methods = ['GET', 'POST'])
def new_customer():

    if request.method == 'GET':
        return render_template("new_customer.html")
    
    elif request.method == 'POST':

        email = request.form.get('mail')
        password = request.form.get('password')
        fullname = request.form.get('fullname')
        address = request.form.get('address')
        pin_code = request.form.get('pincode')

        return f"Email: {email}, Password: {password}, Fullname: {fullname}, Address: {address}, Pin Code: {pin_code}"

#-------------------- Admin Home page -------------------------#

@app.route('/admin_home', methods = ['GET', 'POST'])
def admin_home():

    if request.method == 'GET':
        return render_template('admin_home.html')
    
    elif request.method == 'POST':

        service_name = request.form.get('name')
        base_price = request.form.get('price')
        time_required = request.form.get('time_required')
        description = request.form.get('description')
    
        return f"Service name: {service_name}, Price: {base_price}, Time Req: {time_required}, Description: {description}"

#---------------------- View Service page ------------------------#

@app.route("/view_service")
def view_service():     

    if request.method == "GET":
        return render_template("view_service.html")

    else:
        return "Invalid Request"


#---------------------- View Professional Page --------------------#

@app.route("/view_professional")
def view_professional():

    if request.method == "GET":
        return render_template("view_professional.html")

    else:
        return "Invalid Request"


#---------------------- Admin Search page ------------------------#

@app.route('/admin_search', methods = ['GET', 'POST'])
def admin_search():

    if request.method == 'GET':
        return render_template('admin_search.html')
    
    elif request.method == 'POST':

        search_criteria = request.form.get('searchCriteria')
        search_by = request.form.get('searchBy')
        value_of_search = request.form.get('valueofsearch')
    
    # Process the data as needed
    return f"Received: {search_criteria}, {search_by}, {value_of_search}"


#----------------------- Admin Summary -----------------------------#

@app.route('/admin_summary', methods = ['GET', 'POST'])
def admin_summary():

    if request.method == 'GET':
        return render_template('admin_summary.html')
    
    elif request.method == 'POST':

        return f"You did a post request"



#---------------------- Admin Logout -------------------------------#

@app.route('/admin_logout', methods = ['GET', 'POST'])
def admin_logout():

    if request.method == 'GET':
        return redirect("/")


#----------------------- Professional Home ---------------------------#

@app.route('/professional_home/<int:id>', methods=['GET', 'POST'])
def prof_home(id):

    if request.method == 'GET':
        return render_template("prof_home.html")

#----------------------- Professional view profile ----------------------#

@app.route('/professional_home/view_profile/<int:id>', methods=['GET', 'POST'])
def prof_view_profile(id):

    if request.method == 'GET':
        return render_template("prof_view_profile.html")

    elif request.method == 'POST':
        return f"form edited"
    
#----------------------- Professional Edit Profile ------------------------#

@app.route('/professional_home/edit_profile/<int:id>', methods=['GET', 'POST'])
def prof_profile_edit(id):

    if request.method == 'GET':
        return render_template("prof_edit_profile.html")

    elif request.method == 'POST':
        
        password = request.form.get('password')
        fullname = request.form.get('fullname')
        experience = request.form.get('experience')
        address = request.form.get('address')
        pin_code = request.form.get('pincode')
        new_pic = request.form.get('new_pic')

        return {
        "Id": id,
        "Password": password,
        "Fullname": fullname,
        "Experience": experience,
        "Address": address,
        "Pin Code": pin_code,
        "New_pic": new_pic
    }

#------------------------ Professional Search page ---------------#

@app.route('/professional_search/<int:id>', methods = ['GET', 'POST'])
def prof_search(id):

    if request.method == 'GET':
        return render_template("prof_search.html")

    elif request.method == 'POST':
        search_by = request.form.get('searchBy')
        value_of_search = request.form.get('valueofsearch')
    
        # Process the data as needed
        return f"Received: {search_by}, {value_of_search}"

#------------------------ Professional Summary --------------------#

@app.route('/professional_summary/<int:id>', methods = ['GET', 'POST'])
def prof_summary(id):
    
    if request.method == 'GET':
        return render_template("prof_summary.html")

    elif request.method == 'POST':
        return 'POST request made'
    
    else:
        return f"I don't know this."

#------------------------ Professional Logout --------------------#

@app.route("/professional_logout/<int:id>", methods=['GET'])
def prof_logout(id):

    if request.method == 'GET':
        return redirect("/")

#------------------------ Customer home -------------------------#

@app.route('/customer_home/<int:id>', methods=['GET', 'POST'])
def customer_home(id):

    if request.method == 'GET':

        params = request.args
        service_id = params.get('service_id')
        service_name = "Cleaning"

        if service_id == None:
            return render_template("customer_home.html", service_name = False)
        else:
            return render_template("customer_home.html", service_name = service_name)
            
#----------------------- Professional view profile ----------------------#

@app.route('/customer_home/view_profile/<int:id>', methods=['GET', 'POST'])
def customer_view_profile(id):

    if request.method == 'GET':
        return render_template("customer_view_profile.html")

    elif request.method == 'POST':
        return f"form edited"
    
#----------------------- Professional Edit Profile ------------------------#

@app.route('/customer_home/edit_profile/<int:id>', methods=['GET', 'POST'])
def customer_profile_edit(id):

    if request.method == 'GET':
        return render_template("customer_edit_profile.html")

    elif request.method == 'POST':
        
        password = request.form.get('password')
        fullname = request.form.get('fullname')
        address = request.form.get('address')
        pin_code = request.form.get('pincode')
        new_pic = request.form.get('new_pic')

        return {
        "Id": id,
        "Password": password,
        "Fullname": fullname,
        "Address": address,
        "Pin Code": pin_code,
        "New_pic": new_pic
    }


#------------------------ Customer Book Service request ---------------------------#

@app.route('/customer_home/<int:id>/service_book/<int:service_id>', methods=['GET', 'POST'])
def service_book_req(id, service_id):

    if request.method == 'GET':

        return {
            "id": id,
            "service_id": service_id
        }

    else:
        return "I don't know about this"



if __name__ == '__main__':

    app.run(debug=True)
