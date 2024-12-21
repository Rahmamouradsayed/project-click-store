import sys
import io
from flask_login import LoginManager, login_user
from flask import Flask, render_template, session, request, redirect, url_for,flash
from flask_sqlalchemy import SQLAlchemy
import secrets
from flask_mail import Mail,Message
from authlib.integrations.flask_client import OAuth
import os
from dotenv import load_dotenv

#hope deployment works this time 
load_dotenv()

mail = Mail()
db = SQLAlchemy()
oauth = OAuth()

DB_NAME = 'EcommerceDB'

def create_database(app):
    with app.app_context():
        db.create_all()
        print('Database created successfully!')

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://202201906@zewailcity.edu.eg:Alohomora_2003@clickstore.database.windows.net/EcommerceDB?driver=ODBC+Driver+17+for+SQL+Server&authentication=ActiveDirectoryPassword'




    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  

    db.init_app(app)

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
    app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
    mail.init_app(app)

    oauth.init_app(app)
    oauth.register("ClickStore",
                   client_id=os.getenv("OAUTH_CLIENT_ID"),
                   client_secret=os.getenv("OAUTH_CLIENT_SECRET"),
                   server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
                   client_kwargs={"scope": "openid profile email"})

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(id):
        return Customer.query.get(int(id))
    

    @app.route("/google-login")
    def googleLogin():
    
        nonce = secrets.token_hex(16)
        session['nonce'] = nonce
        
        redirect_uri = url_for("googleCallback", _external=True)
        return oauth.ClickStore.authorize_redirect(redirect_uri=redirect_uri, nonce=nonce)
        
    @app.route("/signin-google")
    def googleCallback():
        token = oauth.ClickStore.authorize_access_token()
        
        nonce = session.get('nonce')

        user_info = oauth.ClickStore.parse_id_token(token, nonce=nonce)

        email = user_info.get("email")
        name = user_info.get("name")

        
        existing_customer = Customer.query.filter_by(email=email).first()
        if not existing_customer:
            new_customer = Customer(email=email, username=name, password_hash=None)
            db.session.add(new_customer)
            db.session.commit()
            login_user(new_customer)
        else:
            login_user(existing_customer)

        return redirect(url_for('UserController.home'))
    
    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            message = request.form['message']

            new_contact = Contact(name=name, email=email, message=message)
            db.session.add(new_contact)
            db.session.commit()
            msg = Message("Contact Us Message", sender=email, recipients=[os.getenv("MAIL_USERNAME")])
            msg.body = f"Message from {name} ({email}):\n\n{message}"
            mail.send(msg)

            flash("Your message has been sent successfully!", "success")
            return redirect('/contact')

        return render_template('contact.html')

    from .user_control import UserController
    from .auth import auth
    from .classes import Customer, Cart, Product, Order, Contact
    from .admin import admin

    app.register_blueprint(UserController, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/')

    create_database(app)

    return app