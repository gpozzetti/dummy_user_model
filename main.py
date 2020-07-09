from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask import Blueprint, render_template, redirect, url_for,request
# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


############ AUTH BLUEPRINT

from werkzeug.security import generate_password_hash, check_password_hash

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        the_email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')

        #the_password=User.query.filter_by(email=the_email).first().password
        user = User.query.filter_by(email=the_email).first()
        if user:
            print('got the user')

        #if check_password_hash( user.password,password ):
        if check_password_hash(generate_password_hash('ciccio', method='sha256'),password):
            return 'You are logged in!'
        return 'You tried to log in with emal '+the_email+' but you did not have the right password'
    return render_template('login.html')#'Login'

@auth_blueprint.route('/signup',methods=['GET','POST'])
def signup():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        return redirect(url_for('auth.signup'))
    if request.method=='POST':

        # create new user with the form data. Hash the password so plaintext version isn't saved.
        new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        return 'You are signed UP!!! :)'
    return render_template('signup.html')


@auth_blueprint.route('/logout')
def logout():
    return 'Logout'

######## MAIN BLUEPRINT

main_blueprint = Blueprint('main', __name__)

@main_blueprint.route('/')
def index():
    return render_template('index.html')#'Index'

@main_blueprint.route('/profile')
def profile():
    return render_template('profile.html')



########### APP

def create_app():

    app = Flask(__name__,static_url_path='/')
    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///DB.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # blueprint for auth routes in our app
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    app.register_blueprint(main_blueprint)

    return app






if __name__ == "__main__":
    app=create_app()

    app.run()
