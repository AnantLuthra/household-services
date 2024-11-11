from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
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
ADMIN_NAME = "Anant Luthra"
DUMMY_PROFESSION_PASS = ADMIN_PASS
DUMMY_CUSTOMER_PASS = ADMIN_PASS

#------------ Database classes ---------------#

class professional(db.Model):

    __tablename__ = "professional"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email_id = db.Column(db.String, nullable=False)
    fullname = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    date_created = db.Column(db.Date, nullable=False)
    service_type_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    pin_code = db.Column(db.Integer, nullable=False)
    #user bytesIO
    documents = db.Column(db.String, nullable=False)
    request = db.Column(db.Boolean, default=None)
    blocked = db.Column(db.Boolean, default=False)

    service_type = db.relationship('service', back_populates='professionals')

class customer(db.Model):

    __tablename__ = "customer"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email_id = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    fullname = db.Column(db.String, nullable=False)
    gender = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    pin_code = db.Column(db.Integer, nullable=False)
    blocked = db.Column(db.Boolean, default=False)


class service(db.Model):

    __tablename__ = "service"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    time_required = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)

    professionals = db.relationship('professional', back_populates='service_type')

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
        return render_template("prof_login.html", message = None)

    elif request.method == 'POST':
        
        email = request.form.get('mail')
        password = request.form.get('password')


        search = professional.query.filter_by(email_id = email).first()
        
        if not search:
            return render_template("prof_login.html", message = "no_account")
        
        else:
            if search.email_id == email:

                if search.password == password:

                    if search.request:
                        return render_template("prof_login.html", message = "req_pending")
                    
                    elif search.blocked:
                        return render_template("prof_login.html", message = "blocked")
                        
                    else:
                        return redirect(f"/professional_home/{search.id}")
                        
                else:
                    return render_template("prof_login.html", message = "wrong_pass")


#-------------------- New Professional Page -----------------------#

@app.route("/new_professional", methods = ['GET', 'POST'])
def new_professional():

    all_services = service.query.all()

    if request.method == 'GET':    

        return render_template("new_professional.html", message = None, services = all_services)
    
    elif request.method == 'POST':

        email = request.form.get('mail')
        password = request.form.get('password')
        fullname = request.form.get('fullname')
        service_id = request.form.get('service_id')
        experience = request.form.get('experience')
        gender = request.form.get('gender')
        documents = request.form.get('documents')
        address = request.form.get('address')
        pin_code = request.form.get('pincode')

        check = professional.query.filter_by(email_id = email).first()
        
        if check:  # if email already exists - user already their.

            if not check.request:   
                return render_template("new_professional.html", message = "acc_exists", services = all_services)
            
            else:       #if account is not pending for approval by admin.
                return render_template("new_professional.html", message = "req_pending", services = all_services)
                
        
        else:
            # Making new professional
            new_prof = professional(
                email_id = email, 
                password = password, 
                fullname = fullname,
                date_created = datetime.now(),
                service_type_id = service_id,
                gender = gender,
                experience = experience,
                documents = documents,
                address = address,
                pin_code = pin_code,
                request = True
                )
            db.session.add(new_prof)
            db.session.commit()
            
            return render_template("new_professional.html", message = "req_sent", services = all_services)


#-------------------- Customer Login page --------------------------#

@app.route("/customer_login", methods=['GET', 'POST'])
def customer_login():

    if request.method == 'GET':
        # if current_user.is_authenticated:
            # return redirect("/professional")
        return render_template("customer_login.html", message = None)

    elif request.method == 'POST':
        
        email = request.form.get('mail')
        password = request.form.get('password')

        search = customer.query.filter_by(email_id = email).first()
        
        if not search:
            return render_template("customer_login.html", message = "no_account")
        
        else:
            if search.email_id == email:
                if search.password == password:
                    return redirect(f"/customer_home/{search.id}")
                else:
                    return render_template("customer_login.html", message = "wrong_pass")

 


#--------------------- New Customer Page --------------------------#

@app.route("/new_customer", methods = ['GET', 'POST'])
def new_customer():

    if request.method == 'GET':
        return render_template("new_customer.html", message = None)
    
    elif request.method == 'POST':

        email = request.form.get('mail')
        password = request.form.get('password')
        fullname = request.form.get('fullname')
        gender = request.form.get('gender')
        address = request.form.get('address')
        pin_code = request.form.get('pincode')

        check = customer.query.filter_by(email_id = email).first()
        
        if check:  # if email already exists - user already their.
            return render_template("new_customer.html", message = "acc_exists")
        
        else:
            # Making new cutomer
            new_cust = customer(
                email_id = email, 
                password = password, 
                fullname = fullname,
                gender = gender,
                address = address,
                pin_code = pin_code
                )
            db.session.add(new_cust)
            db.session.commit()
            
            return render_template("new_customer.html", message = "acc_created")


#-------------------- Admin Home page -------------------------#

@app.route('/admin_home', methods = ['GET', 'POST'])
def admin_home():

    if request.method == 'GET':
        return render_template('admin_home.html', admin_name = ADMIN_NAME)
    
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
        return render_template('admin_search.html', admin_name = ADMIN_NAME)
    
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
        return render_template('admin_summary.html', admin_name = ADMIN_NAME)
    
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

        prof = professional.query.filter_by(id = id).first()

        return render_template("prof_home.html", professional = prof)


#----------------------- Professional view profile ----------------------#

@app.route('/professional_home/view_profile/<int:id>', methods=['GET', 'POST'])
def prof_view_profile(id):

    if request.method == 'GET':

        prof = professional.query.filter_by(id = id).first()
        return render_template("prof_view_profile.html", professional = prof)

    elif request.method == 'POST':
        return f"form edited"
    
#----------------------- Professional Edit Profile ------------------------#

@app.route('/professional_home/edit_profile/<int:id>', methods=['GET', 'POST'])
def prof_profile_edit(id):

    if request.method == 'GET':

        prof = professional.query.filter_by(id = id).first()
        return render_template("prof_edit_profile.html", professional = prof)

    elif request.method == 'POST':
        
        password = request.form.get('password')
        fullname = request.form.get('fullname')
        experience = request.form.get('experience')
        address = request.form.get('address')
        pin_code = request.form.get('pincode')
        new_pic = request.form.get('new_pic')

        prof = professional.query.filter_by(id = id).first()
        
        prof.password = password
        prof.fullname = fullname
        prof.experience = experience
        prof.address = address
        prof.pin_code = pin_code
        # cus.pic = new_pic

        db.session.commit()

        return redirect(f"/professional_home/view_profile/{id}")
    

#------------------------ Professional Search page ---------------#

@app.route('/professional_search/<int:id>', methods = ['GET', 'POST'])
def prof_search(id):

    if request.method == 'GET':

        prof = professional.query.filter_by(id = id).first()

        return render_template("prof_search.html", professional = prof)

    elif request.method == 'POST':
        search_by = request.form.get('searchBy')
        value_of_search = request.form.get('valueofsearch')
    
        # Process the data as needed
        return f"Received: {search_by}, {value_of_search}"

#------------------------ Professional Summary --------------------#

@app.route('/professional_summary/<int:id>', methods = ['GET', 'POST'])
def prof_summary(id):
    
    if request.method == 'GET':

        prof = professional.query.filter_by(id = id).first()
        return render_template("prof_summary.html", professional = prof)

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

        cus = customer.query.filter_by(id = id).first()

        if service_id == None:
            return render_template("customer_home.html", service_name = False, customer = cus)
        else:
            return render_template("customer_home.html", service_name = service_name, customer = cus)
            
#----------------------- Customer view profile ----------------------#

@app.route('/customer_home/view_profile/<int:id>', methods=['GET', 'POST'])
def customer_view_profile(id):

    if request.method == 'GET':

        cus = customer.query.filter_by(id = id).first()

        return render_template("customer_view_profile.html", customer = cus)

    elif request.method == 'POST':
        return f"form edited"
    
#----------------------- Customer Edit Profile ------------------------#

@app.route('/customer_home/edit_profile/<int:id>', methods=['GET', 'POST'])
def customer_profile_edit(id):

    if request.method == 'GET':

        cus = customer.query.filter_by(id = id).first()

        return render_template("customer_edit_profile.html", customer = cus)

    elif request.method == 'POST':
        
        password = request.form.get('password')
        fullname = request.form.get('fullname')
        address = request.form.get('address')
        pin_code = request.form.get('pincode')
        new_pic = request.form.get('new_pic')
        
        # Fetching the user.
        cus = customer.query.filter_by(id = id).first() 
        
        cus.password = password
        cus.fullname = fullname
        cus.address = address
        cus.pin_code = pin_code
        # cus.pic = new_pic

        db.session.commit()

        return redirect(f"/customer_home/view_profile/{id}")


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


#------------------------ Customer Close Service ------------------------------------#

@app.route('/customer_home/close_service/<int:id>/<int:service_request_id>', methods=['GET', 'POST'])
def close_service_request(id, service_request_id):

    if request.method == 'GET':
        return render_template("customer_close_service.html")

    elif request.method == 'POST':

        rating = request.form.get('rating')
        remarks = request.form.get('remarks')

        
        return {
            "id": id,
            "service_request_id": service_request_id,
            "Rating": rating,
            "Remarks": remarks
        }


    else:
        return "I don't know about this."

#------------------------ Customer Search page ---------------#

@app.route('/customer_search/<int:id>', methods = ['GET', 'POST'])
def customer_search(id):

    if request.method == 'GET':

        cus = customer.query.filter_by(id = id).first() 

        return render_template("customer_search.html", customer = cus)

    elif request.method == 'POST':
        search_by = request.form.get('searchBy')
        value_of_search = request.form.get('valueofsearch')
    
        # Process the data as needed
        return f"Received: {search_by}, {value_of_search}"


#------------------------ Customer Summary --------------------#

@app.route('/customer_summary/<int:id>', methods = ['GET', 'POST'])
def customer_summary(id):
    
    if request.method == 'GET':

        cus = customer.query.filter_by(id = id).first() 

        return render_template("customer_summary.html", customer = cus)

    elif request.method == 'POST':
        return 'POST request made'
    
    else:
        return f"I don't know this."

#------------------------ Customer Logout --------------------#

@app.route("/customer_logout/<int:id>", methods=['GET'])
def customer_logout(id):

    if request.method == 'GET':
        return redirect("/")


if __name__ == '__main__':

    app.run(debug=True)
