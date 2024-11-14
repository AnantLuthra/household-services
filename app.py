from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref,joinedload
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required


#------------ Initialisations ---------------#
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3"
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

#------------ Global Variables --------------#
ADMIN_PASS = "good123"
ADMIN_NAME = "Anant Sharma"
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
    services_completed = db.Column(db.Integer, default = 0)
    rating = db.Column(db.Float, default = 0.0)
    price = db.Column(db.Integer, default = 0)

    service_type = db.relationship('service', back_populates='professionals')
    service_requests = db.relationship('service_request', backref='professional', cascade='all, delete-orphan')

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

    service_requests = db.relationship('service_request', backref='customer', cascade='all, delete-orphan')

class service(db.Model):

    __tablename__ = "service"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    base_price = db.Column(db.Integer, nullable=False)
    time_required = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, nullable=False)
    status = db.Column(db.Boolean, default = False)
    type = db.Column(db.String, nullable=False)

    professionals = db.relationship('professional', back_populates='service_type')
    service_requests = db.relationship('service_request', backref='service', cascade='all, delete-orphan')

class service_request(db.Model):

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
        return render_template("admin_login.html", message = False)

    elif request.method == 'POST':
        
        password = request.form.get('password')

        if ADMIN_PASS == password:
            return redirect("/admin_home")
        else:
            return render_template("admin_login.html", message = "wrong_pass")


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
        price = request.form.get('price')
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
                date_created = date.today(),
                service_type_id = service_id,
                gender = gender,
                price = price,
                experience = experience,
                documents = documents,
                address = address,
                pin_code = pin_code,
                request = True
                )
            db.session.add(new_prof)
            db.session.commit()
            
            return render_template("new_professional.html", message = "req_sent", services = all_services)

#--------------------- API for base price fetch --------------------#
@app.route('/service_base_price/<int:service_id>')
def api_base_price(service_id):

    ser = service.query.filter_by(id = service_id).first()

    if ser:
        return {"base_price": f"{ser.base_price}"}

    else:
        return {"base_price": 0}


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

                    if search.blocked: # if that user is blocked
                        return render_template("customer_login.html", message = "blocked")

                    else:
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
            # Making new customer
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

    prof = professional.query.all()
    cus = customer.query.all()
    services = service.query.all()
    ser_req = service_request.query.options(joinedload(service_request.professional)).all()

    if request.method == 'GET':

        return render_template('admin_home.html', admin_name = ADMIN_NAME, professionals = prof, customers = cus, services = services, service_requests = ser_req, message = False)
    
    elif request.method == 'POST':

        service_name = request.form.get('name')
        service_type = request.form.get('type')
        base_price = request.form.get('price')
        time_required = request.form.get('time_required')
        description = request.form.get('description')
        
        search = service.query.filter_by(name = service_name).first()

        if not search: #If that new service doesn't already exists.
            new_ser = service(
                name = service_name,
                type = service_type,
                base_price = base_price,
                time_required = time_required,
                description = description
            )
            db.session.add(new_ser)
            db.session.commit()
            return redirect('/admin_home')
        
        else: # If service Exists.
            return render_template('admin_home.html', admin_name = ADMIN_NAME, professionals = prof, customers = cus, services = services, service_requests = ser_req, message = "service_exists")

#---------------------- Edit service -------------------------------------#

@app.route("/admin_home/edit_service/<int:id>", methods = ['GET', 'POST'])
def edit_service(id):

    if request.method == 'GET':

        ser = service.query.filter_by(id = id).first()

        if ser: # if service exists
            return render_template("edit_service.html", service = ser, admin_name = ADMIN_NAME)
        
        else:
            return "Invalid service id", 404
    
    elif request.method == 'POST':
        
        
        service_name = request.form.get('name')
        service_type = request.form.get('type')
        base_price = request.form.get('price')
        time_required = request.form.get('time_required')
        description = request.form.get('description')
        
        ser = service.query.filter_by(id = id).first()

        if ser:
            ser.name = service_name
            ser.type = service_type
            ser.base_price = base_price
            ser.time_required = time_required
            ser.description = description

            db.session.commit()
        
            return redirect('/admin_home')

        else:
            return "No such service id present!", 404

    
    else:
        return "This Request is not handled here.", 404


#---------------------- Activate/Deactivate Service ---------------------------#
@app.route("/admin_home/action_service/<string:action>/<int:id>")
def act_service(action, id):
    
    if request.method == 'GET':
        ser = service.query.get(id)

        if ser:  #If that service exists
            
            if action == 'deactivate':
                ser.status = True
                db.session.commit()
                return redirect(request.referrer)
            
            elif action == 'activate':
                ser.status = False
                db.session.commit()
                return redirect(request.referrer)
        
        else:   #if service doesn't exists
            return f"""
    <div>Service that you're trying to {action} doesn't exists!</div>
    <a href="/admin_home">Go Back</a>
                    """


#---------------------- Block/Unblock person -----------------------#

@app.route("/admin_home/action/<string:action>/<string:person>/<int:id>")
def block_unblock_person(action, person, id):
    
    users = ['professional', 'customer']
    
    def call_error(person):
        return f"""
            <div>{person} that you're trying to {action} doesn't exists!</div>
            <a href="/admin_home">Go Back</a>
                """
    
    if request.method == 'GET':
        
        if action not in ['block', 'unblock']:
            return f"""
            <div>This action isn't allowed</div>
            <a href="/admin_home">Go Back</a>
                """

        if person.lower() in users:
            if person.lower() == users[0]:
                prof = professional.query.get(id)

                if prof:
                    prof.blocked = True if action == "block" else False
                    db.session.commit()
                    return redirect(request.referrer)

                else:  #if person doesn't exists
                    return call_error(person)
                    
            elif person.lower() == users[1]:
                cus = customer.query.get(id)

                if cus:
                    cus.blocked = True if action == "block" else False
                    db.session.commit()
                    return redirect(request.referrer)

                else:  #if person doesn't exists
                    return call_error(person)
                
        else:
            return f"""
            <div>This type of person doesn't exists!</div>
            <a href="/admin_home">Go Back</a>
                    """

#---------------------- Approve/Reject professional ---------------#

@app.route('/admin_home/appr/<string:action>/<int:id>')
def appr(action, id):

    if request.method == 'GET':

        prof = professional.query.filter_by(id = id).first()
        actions = ['approve', 'reject']
        if prof:
            if action.lower() in actions:
                if action.lower() == actions[0]:
                    prof.request = False
                    db.session.commit()
                    return redirect(request.referrer)
                
                else:
                    db.session.delete(prof)
                    db.session.commit()
                    return redirect(request.referrer)

            else:
                return f"""
            <div>This Actions ins't allowed</div>
            <a href="/admin_home">Go Back</a>
                    """

        else:   
            return f"""
            <div>This professional doesn't exists.</div>
            <a href="/admin_home">Go Back</a>
                    """

#---------------------- View Service page ------------------------#

@app.route("/view_service/<int:id>")
def view_service(id):     

    if request.method == "GET":

        ser = service.query.filter_by(id = id).first()

        return render_template("view_service.html", service = ser, admin_name = ADMIN_NAME)

    else:
        return "Invalid Request"


#---------------------- View Professional Page --------------------#

@app.route("/view_professional/<int:id>")
def view_professional(id):

    if request.method == "GET":

        prof = professional.query.filter_by(id = id).first()
        return render_template("view_professional.html", professional = prof, admin_name = ADMIN_NAME)

    else:
        return "Invalid Request"


#---------------------- Admin Search page ------------------------#

@app.route('/admin_search', methods = ['GET', 'POST'])
def admin_search():

    if request.method == 'GET':
        return render_template('admin_search.html', admin_name = ADMIN_NAME, searched = False, message = None)
    
    elif request.method == 'POST':

        search_criteria = request.form.get('searchCriteria')
        search_by = request.form.get('searchBy')
        value_of_search = request.form.get('valueofsearch')
        
        if search_criteria == 'services':

            search = 0

            if search_by == 'service name':
                search = service.query.filter(service.name.like(f"%{value_of_search}%")).all()
            
            elif search_by == "price >=":
                search = service.query.filter(service.base_price > int(value_of_search)).all()

            if search:
                return render_template('admin_search.html',
                        admin_name = ADMIN_NAME,
                        searched = True,
                        services = search,
                        message = None,
                        searched_by = search_by,
                        searched_term = value_of_search
                    )
            else:
                return render_template('admin_search.html',
                    admin_name = ADMIN_NAME,
                    searched = True,
                    message = "no_results"
                    )


        elif search_criteria == 'customers':
            search = 0
            
            if search_by == 'email id':
                search = customer.query.filter(customer.email_id.like(f"%{value_of_search}%")).all()
            
            elif search_by == 'name':
                search = customer.query.filter(customer.fullname.like(f"%{value_of_search}%")).all()
                
            elif search_by == 'pin code':
                search = customer.query.filter_by(pin_code = int(value_of_search)).all()


            if search:
                return render_template('admin_search.html',
                        admin_name = ADMIN_NAME,
                        searched = True,
                        customers = search,
                        message = None,
                        searched_by = search_by,
                        searched_term = value_of_search
                    )
            else:
                return render_template('admin_search.html',
                    admin_name = ADMIN_NAME,
                    searched = True,
                    message = "no_results"
                    )
            
        elif search_criteria == 'professional':
            search = 0

            if search_by == 'experience >=':
                search = professional.query.filter(professional.experience > int(value_of_search)).all()
            
            elif search_by == 'name':

                search = professional.query.filter(professional.fullname.like(f"%{value_of_search}%")).all()
                
            elif search_by == 'service name':
                search = professional.query.join(service).filter(service.name.like(f"%{value_of_search}%")).all()

            if search:
                return render_template('admin_search.html',
                        admin_name = ADMIN_NAME,
                        searched = True,
                        professionals = search,
                        message = None,
                        searched_by = search_by,
                        searched_term = value_of_search
                    )
            else:
                return render_template('admin_search.html',
                    admin_name = ADMIN_NAME,
                    searched = True,
                    message = "no_results"
                    )    
            
        elif search_criteria == "service_request":
            search = 0
            
            if search_by == 'status':
                # search = service_request.query.options(joinedload(service_request.customer), joinedload(service_request.professional)).all()
                search = service_request.query.filter_by(service_status = value_of_search).all()
            
            elif search_by == 'customer requested': #joinload thing for 
                # search = service_request.query.options(joinedload(service_request.customer), joinedload(service_request.professional)).join(customer).filter(customer.fullname.like(f"%{value_of_search}%")).all()
                search = service_request.query.join(customer).filter(customer.fullname.like(f"%{value_of_search}%")).all()
                
            elif search_by == 'professional assigned':
                search = service_request.query.join(professional).filter(professional.fullname.like(f"%{value_of_search}%")).all()


            if search:
                return render_template('admin_search.html',
                        admin_name = ADMIN_NAME,
                        searched = True,
                        service_request = search,
                        message = None,
                        searched_by = search_by,
                        searched_term = value_of_search
                    )
            else:
                return render_template('admin_search.html',
                    admin_name = ADMIN_NAME,
                    searched = True,
                    message = "no_results"
                    )


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

        if prof:
            if not prof.blocked:
                if not prof.request:
                    
                    #Requests or service going on.
                    ser = service_request.query.join(professional, service_request.professional_id == professional.id).join(
                        customer, service_request.customer_id == customer.id).join(
                        service, service_request.service_id == service.id).filter(
                        service_request.professional_id == id,
                        service_request.service_status.in_(['requested', 'accepted']),
                        customer.blocked == False,
                        service.status == False
                    ).all()


                    #Service history not present
                    ser_history = service_request.query.join(
                        professional, service_request.professional_id == professional.id).join(
                        customer, service_request.customer_id == customer.id).join(service, service_request.service_id == service.id).filter(
                        service_request.professional_id == id,
                        service_request.service_status.in_(['closed', 'rejected']),
                        customer.blocked == False,
                        service.status == False
                    ).all()

                    if ser: #Requests or service going on.

                        if ser_history: #if service history present.
                                return render_template("prof_home.html",
                                    professional = prof,
                                    request_details = ser,
                                    service_history = ser_history,
                                    )

                        else: #Service history not present
                            return render_template("prof_home.html",
                                    professional = prof,
                                    request_details = ser,
                                    service_history = ser_history,
                                    )
                            
                        
                    else: #No service requests, no service_history
                        return render_template("prof_home.html",
                                    professional = prof,
                                    request_details = ser,
                                    service_history = ser_history
                                    )
                    
                else:
                    return redirect('/professional_login')
            else:
                return redirect('/professional_login')
        else:
            return redirect('/professional_login')


#----------------------- accept service request -------------------------#
@app.route('/professional_home/service_action/<string:action>/<int:service_id>')
def acc_service(action, service_id):
    
    if request.method == 'GET':

        ser = service_request.query.filter_by(id = service_id).first()

        if ser:
            if action == 'accept':
                ser.service_status = 'accepted'
                db.session.commit()
            elif action == 'reject':
                ser.service_status = 'rejected'
                db.session.commit()

            return redirect(request.referrer)

        else:
            return f"""
            <div>This action isn't allowed</div>
            <a href="/">Go Back</a>
                """


#----------------------- Professional view profile ----------------------#

@app.route('/professional_home/view_profile/<int:id>', methods=['GET', 'POST'])
def prof_view_profile(id):

    if request.method == 'GET':

        prof = professional.query.filter_by(id = id).first()

        if prof:
            if not prof.blocked:
                if not prof.request:
                    return render_template("prof_view_profile.html", professional = prof)
                else:
                    return redirect('/professional_login')
            else:
                return redirect('/professional_login')
        else:
            return redirect('/professional_login')

    elif request.method == 'POST':
        return f"form edited"
    
#----------------------- Professional Edit Profile ------------------------#

@app.route('/professional_home/edit_profile/<int:id>', methods=['GET', 'POST'])
def prof_profile_edit(id):

    if request.method == 'GET':

        prof = professional.query.filter_by(id = id).first()

        if prof: #if professional exists
            if not prof.blocked:      # if not blocked
                if not prof.request:        # if not on request period.
                    return render_template("prof_edit_profile.html", professional = prof)
                else:
                    return redirect('/professional_login')
            else:
                return redirect('/professional_login')
        else:
            return redirect('/professional_login')

    elif request.method == 'POST':
        
        password = request.form.get('password')
        fullname = request.form.get('fullname')
        experience = request.form.get('experience')
        address = request.form.get('address')
        pin_code = request.form.get('pincode')
        price = request.form.get('price')
        new_pic = request.form.get('new_pic')

        prof = professional.query.filter_by(id = id).first()
        
        prof.password = password
        prof.fullname = fullname
        prof.experience = experience
        prof.address = address
        prof.price = price
        prof.pin_code = pin_code
        # cus.pic = new_pic

        db.session.commit()

        return redirect(f"/professional_home/view_profile/{id}")
    

#------------------------ Professional Search page ---------------#

@app.route('/professional_search/<int:id>', methods = ['GET', 'POST'])
def prof_search(id):

    if request.method == 'GET':

        prof = professional.query.filter_by(id = id).first()

        if prof:
            if not prof.blocked:
                if not prof.request:
                    return render_template("prof_search.html", professional = prof)
                else:
                    return redirect('/professional_login')
            else:
                return redirect('/professional_login')
        else:
            return redirect('/professional_login')

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
        if prof:
            if not prof.blocked:
                if not prof.request:
                    return render_template("prof_summary.html", professional = prof)
                else:
                    return redirect('/professional_login')
            else:
                return redirect('/professional_login')
        else:
            return redirect('/professional_login')

    elif request.method == 'POST':
        return 'POST request made'
    
    else:
        return f"I don't know this."

#------------------------ Professional Logout --------------------#

@app.route("/professional_logout/<int:id>", methods=['GET'])
def prof_logout(id):

    if request.method == 'GET':
        prof = professional.query.get(id)

        if prof:
            if not prof.blocked:
                if not prof.request:
                    return redirect("/")
                else:
                    return redirect('/professional_login')
            else:
                return redirect('/professional_login')
        else:
            return redirect('/professional_login')

#------------------------ Customer home -------------------------#

@app.route('/customer_home/<int:id>', methods=['GET', 'POST'])
def customer_home(id):

    if request.method == 'GET':

        params = request.args
        service_name = params.get('service_name') #it will contain service name if any service is selected.


        #Customer details fetch
        cus = customer.query.filter_by(id = id).first()
        
        # service request history search.
        ser = service_request.query.join(professional).join(service).filter(
            service_request.customer_id == id,
            professional.blocked == False,
            professional.request == False,
            service.status == False
        ).all()

        #All service types name fetched distinctively and passed in list.
        all_services = [service_type[0] for service_type in db.session.query(service.type).distinct().all()]

        if cus: #if that customer exists

            if not cus.blocked:  # if that customer is not blocked
                if service_name == None:
                    return render_template("customer_home.html", service_name = False, customer = cus, service_history = ser, all_types = all_services)
                else:
                    
                    searched_professionals = professional.query.join(service).filter(
                        service.type == service_name,
                        professional.blocked == False,
                        professional.request == False,
                        service.status == False
                    ).order_by(professional.rating.desc()).all()


                    if searched_professionals:  #If results are their.

                        return render_template("customer_home.html",
                                            service_name = service_name,
                                            customer = cus,
                                            service_history = ser,
                                            searched_results = searched_professionals
                                            )
                    else:

                        return render_template("customer_home.html",
                                            service_name = service_name,
                                            customer = cus,
                                            service_history = ser,
                                            searched_results = "no_data"
                                            )

            else:
                return redirect('/customer_login')

        else:
            return redirect('/customer_login')


#----------------------- Customer view profile ----------------------#

@app.route('/customer_home/view_profile/<int:id>', methods=['GET', 'POST'])
def customer_view_profile(id):

    if request.method == 'GET':

        cus = customer.query.filter_by(id = id).first()
        
        if cus:
            if not cus.blocked:
                return render_template("customer_view_profile.html", customer = cus)
            else:
                return redirect('/customer_login')
        else:
            return redirect('/customer_login')

    elif request.method == 'POST':
        return f"form edited"
    
#----------------------- Customer Edit Profile ------------------------#

@app.route('/customer_home/edit_profile/<int:id>', methods=['GET', 'POST'])
def customer_profile_edit(id):

    if request.method == 'GET':

        
        cus = customer.query.filter_by(id = id).first()

        if cus:
            if not cus.blocked:
                return render_template("customer_edit_profile.html", customer = cus)
            else:
                return redirect('/customer_login')
        else:
            return redirect('/customer_login')

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

@app.route('/customer_home/<int:customer_id>/service_book/<int:professional_id>/<int:service_id>', methods=['GET', 'POST'])
def service_book_req(customer_id, professional_id, service_id):

    if request.method == 'GET':
        
        new_ser = service_request(
            service_id = service_id,
            customer_id = customer_id,
            professional_id = professional_id,
            date_of_request = date.today(),
            date_of_completion=date.today(),  #make change when actually completed.
            service_status = "requested",
        )
        db.session.add(new_ser)
        db.session.commit()

        return redirect(request.referrer)

    else:
        return "No post request allowed", 404


#------------------------ Customer Close Service ------------------------------------#

@app.route('/customer_home/close_service/<int:id>/<int:service_request_id>', methods=['GET', 'POST'])
def close_service_request(id, service_request_id):

    if request.method == 'GET':
        print(f"got to close- customer id: {id}, service_request_id {service_request_id}")
        cus = customer.query.filter_by(id = id).first()
        ser_req = service_request.query.filter_by(id = service_request_id).first()

        if cus:
            if not cus.blocked:
                return render_template("customer_close_service.html", customer = cus, service_request = ser_req)
            else:
                return redirect('/customer_login')
        else:
            return redirect('/customer_login')

    elif request.method == 'POST':

        print(f"got to close- customer id: {id}, service_request_id {service_request_id}")

        rating = float(request.form.get('rating'))
        remarks = request.form.get('remarks')

        ser_req = service_request.query.filter_by(id=service_request_id).first()

        if ser_req:

            ser_req.professional.services_completed += 1

            # Calculating new average rating
            new_rating = ((ser_req.professional.rating * (ser_req.professional.services_completed - 1)) + rating) / ser_req.professional.services_completed
            ser_req.professional.rating = round(new_rating, 1)


            # Updating service request status & feedback
            ser_req.service_status = 'closed'
            ser_req.rstars = rating
            ser_req.rfeedback = remarks
            ser_req.date_of_completion = date.today()

            db.session.commit()

            print(f'Redirecting to /customer_home/{id}')
            return redirect(f'/customer_home/{id}')
            
        else:
            return "Service request not found", 404


    else:
        return "I don't know about this."

#------------------------ Customer Search page ---------------#

@app.route('/customer_search/<int:id>', methods = ['GET', 'POST'])
def customer_search(id):

    if request.method == 'GET':

        cus = customer.query.filter_by(id = id).first() 
        
        if cus:
            if not cus.blocked:
                return render_template("customer_search.html", customer = cus)
            else:
                return redirect('/customer_login')
        else:
            return redirect('/customer_login')

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

        if cus:
            if not cus.blocked:
                return render_template("customer_summary.html", customer = cus)
            else:
                return redirect('/customer_login')
        else:
            return redirect('/customer_login')

    elif request.method == 'POST':
        return 'POST request made'
    
    else:
        return f"I don't know this."

#------------------------ Customer Logout --------------------#

@app.route("/customer_logout/<int:id>", methods=['GET'])
def customer_logout(id):

    if request.method == 'GET':

        cus = customer.query.get(id)

        if cus:
            if not cus.blocked:
                return redirect("/")
            else:
                return redirect('/customer_login')
        else:
            return redirect('/customer_login')


if __name__ == '__main__':

    app.run(debug=True)
