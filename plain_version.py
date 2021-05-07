from flask import Flask,flash
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask import Blueprint, render_template, redirect, url_for,request
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, Table, Integer, String, Column, MetaData
import pandas as pd
# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

## TODO check this db_url -> deleted
## TODO I would rather use the flask db init command and the ORM
def init_db():
    print("HERE INIT_DB")
    engine = create_engine('sqlite:///DB.db', echo=True)
    meta = MetaData()
    user_table = Table(
        'User', meta,
        Column('name', String),
        Column('email', String),
        # Here I rename the password hashed as hashed_password for better clariy
        Column('hashed_password', String),
        Column('theme', String),
    )
    meta.create_all(engine)

### user class (probably better to use the flask one but still have to understand it )
class User():
    ## Linking to the database
    def __init__(self, db):
        print("HERE INIT USER")
        self.db_path = db
        self.logged_in = False
        self.name = None
        self.mail = None
        self.theme_name = None

    def log_in(self, mail, password):
        print("HERE LOGIN USER")
        ## Check if user exists, and has the password
        users = self.get_user_table()
        if mail in users['email'].to_list():
            print('I got the user')
            users = users.set_index('email')
            # Here I rename the password hashed as hashed_password for better clariy
            hashed_password = users.loc[mail, 'hashed_password']
            # Here I rename the password hashed as hashed_password for better clariy
            if check_password_hash(hashed_password, password):
                self.mail = mail
                self.name = users.loc[mail, 'name']
                self.theme_name = users.loc[mail, 'theme']
                self.logged_in = True

        return self.logged_in

    def logout(self):
        print("HERE LOGOUT USER")
        self.logged_in = False
        self.name = None
        self.mail = None


    def get_user_table(self):
        print("HERE get_user_table USER")
        ## Opening and closing a connection to register the search
        connection_path = self.db_path
        ## create an engine to test the database
        engine = create_engine(connection_path)
        ## define the name of the table in the database (the lowercase apparently required by postgrade)
        table_name = 'user'
        
        # TODO DIRTY Change to orm
        users_table = pd.read_sql(str('SELECT * from '+table_name), con=engine)

        ## killing the connection
        engine.dispose()
        return users_table

    # !!! Do not uncomment unless you want to see the sql injection demo !!!
    # SQL injection dirty test
    #def test_sql_inj(self):
        # SQL injection dirty test
    #    pandas_test = False
    #    connection_path = self.db_path
    #    engine = create_engine(connection_path)
    #    active_connection = engine.raw_connection()
    #    cursor = active_connection.cursor()
    #    command=str('SELECT * from user WHERE name = ' + self.name + ';')
    #    print(command)
    #    if pandas_test==True:
    #      pd.read_sql(command, con=engine)
    #    else:
    #      cursor.executescript(command)
    #      active_connection.close()
    #    engine.dispose()

    def add_user(self, name, email, hashed_password, theme_name='default'):
        print("HERE add_user USER")
        ##Now see if we already have the user
        users = self.get_user_table()

        ## If we don't find an user with this email
        if users[users['email']==email].empty:
            ## Opening and closing a connection to register the search
            connection_path = self.db_path
            ## create an engine to test the database
            engine = create_engine(connection_path)
            ## define the name of the table in the database (the lowercase apparently required by postgrade)
            table_name = 'user'

            ## actually create the connection
            active_connection = engine.connect()
            ## preparing the command
            column_name = 'email,name,hashed_password,theme'
            # TODO DIRTY - Change to orm
            # Here I rename the password hashed as hashed_password for better clariy
            value = email + '\',\'' + name + '\',\'' + hashed_password + '\',\'' + theme_name
            ## A string with the sql command
            command=str('INSERT INTO '+table_name+' ('+column_name+') VALUES (\''+value+'\') ;')
            print(command)
            ## actually adding it
            active_connection.execute(command)
            active_connection.close()
            ## killing the connection
            engine.dispose()

            ## log  in with the current credentials
            self.name = name
            self.email = email
            self.logged_in = True
            self.theme_name = theme_name
            return True
        ## if an user with this email is already there return false
        else:
            return False
        # TODO check why indentation here. I see no reason why this should be like this
        # This function being not called, I see no reason for encapsulation
        def get_models(self):
            if self.logged_in:
                print('Accessing priviledge accounts')

## Configuring the app
app = Flask(__name__,static_url_path='/')
app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///DB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
init_db() # TODO added the double brackets

db.init_app(app)
current_user = User(app.config['SQLALCHEMY_DATABASE_URI'])

## App route for home directory, reshows the index
@app.route('/')
def home():
    print("HOME")
    print(current_user.name)
    return render_template('index.html')

## App route for signup, allows users to create an account
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    print("SIGNUP")
    if request.method=='POST':
        print(1)
        email = request.form.get('email')
        print(2)
        name = request.form.get('name')
        print(3)
        # Here I rename the password hashed as hashed_password for better clariy
        hashed_password = generate_password_hash(
            request.form.get('password'), method='sha256')
        print(4)
        if current_user.add_user(name, email, hashed_password):
            print(5)
            return redirect(url_for('profile'))
        else:
            print(6)
            print('User Already Existing')
            flash('This user is already registered, try to login instead')

    print(10)
    return render_template('signup.html')

## App route to login , allows existing users to log in
@app.route('/login', methods=['GET', 'POST'])
def login():
    print("HERE LOGIN")
    if request.method=='POST':
        print('I should be signed in ')

        if current_user.log_in(
            request.form.get('email'), request.form.get('password')):
            print('I should be signed in ')
            return redirect(url_for('profile'))

        else:
            flash('Incorrect email or password')

    return render_template('login.html')

## App route to logout, reset the current user
@app.route('/logout')
def logout():
    print("HERE LOGOUT")
    current_user.logout()
    return render_template('login.html')

## App route to get to user profile, if user logged in it provides a welcome message
@app.route('/profile')
def profile():
    print("HERE PROFILE")
    if current_user.logged_in:
        name = current_user.name
        theme_name = current_user.theme_name
        # !!! Do not uncomment unless you want to see the sql injection demo !!!
        # SQL injection dirty test
        #current_user.test_sql_inj()

        return render_template('profile.html', name=name, theme_name=theme_name)
    else:
        return redirect(url_for('login'))

## Entry point if we do not use Flask Run - Default to localhost:5000
## TODO Investigate why they to do not use a Factory
## TODO Investigate why main app, routes and data models are not decoupled
if __name__ == "__main__":
    #app=create_app()
    print("HERE MAIN")
    app.run()
