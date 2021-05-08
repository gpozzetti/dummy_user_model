"""
This is a small web portal, leading to customisable profile
A new user can sign-up, a registered user can log-in, access its profile, touch it up by providing its birthday
or changing the theme color of its profile page.
A logged-in user can log-out.

.. moduleauthor:: Cedric Renzi
"""

from flask import Flask,flash
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
# Comment only for challenge: Blueprint are not used in the orginal version, however I would really
# recommend their usage for the sake of modularization
from flask import Blueprint, render_template, redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, Column, MetaData
from sqlalchemy import Table, DateTime, String, Integer
import pandas as pd

from helpers import set_color_name, calculate_unix_timestamp
from helpers import format_date_string_ymd, create_date_from_timestamp

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

## TODO I would rather use the flask db init command and the ORM
def init_db():
    """
    A helper for initializing an empty databasem with a table 'user' and
    the correct field names as columns
    """
    engine = create_engine('sqlite:///DB.db', echo=True)
    meta = MetaData()
    user_table = Table(
        'User', meta,
        Column('name', String),
        Column('email', String),
        # Comment only for challenge: Here I rename the password hashed as hashed_password for better clariy
        Column('hashed_password', String),
        Column('theme', String),
        Column('next_birthday', Integer)
    )
    meta.create_all(engine)

### user class (probably better to use the flask one but still have to understand it)
# Comment only for challenge: Indeed, I do not like the way this data model is elaborated.
# It looks very complicated on the usage, while flask-alchemy, that we import here, is meant to make stuff
# much more pythonic
class User():
    """
    The class User defines the data model on top of a user object
    SQL table name: 'user'
    Database object SQLAlchemy instance: db

         Fields:
              name         : name of user
              email        : email of user (login), enforced unique by the logics of the rest of the code
              theme_name   : name of the chosen theme by the user, for its profile page
              next_birthday: supposed to be next_birthday date (occurs at midnight, local time on frontend)
              logged-in    : current status of login
    """
    ## Linking to the database
    def __init__(self, db):
        """ Initialize object instance """
        # Comment only for challenge: I prefer to have it here, looks like more mimicking an actual data model of an ORM :)
        ## define the name of the table in the database (the lowercase apparently required by postgrade)
        ## DB nuts and bolts
        ## define the name of the table in the database (the lowercase apparently required by postgrade)
        self.table_name = 'user'
        self.db_path = db
        ## Profile data
        self.name = None
        # Comment only for challenge: Renamed here to email to keep name-consistency with actual DB
        self.email = None
        self.theme_name = None
        # At init, the date and hour default to the day and hour when user is added
        self.next_birthday = None
        ## Status
        self.logged_in = False

    # Comment only for challenge: Renamed here to email to keep name-consistency with actual DB
    def log_in(self, email, password):
        """ Authenticate a user, from a "email" and a "password" """
        ## Authenticate the user or reject him (exist ? correct password ?)
        users = self.get_user_table()
        if email in users['email'].to_list():
            users = users.set_index('email')
            # Comment only for challenge:Here I rename the password hashed as hashed_password for better clariy
            hashed_password = users.loc[email, 'hashed_password']
            # Comment only for challenge: Here I rename the password hashed as hashed_password for better clariy
            if check_password_hash(hashed_password, password):
                self.email = email
                self.name = users.loc[email, 'name']
                self.theme_name = users.loc[email, 'theme']
                self.next_birthday = users.loc[email, 'next_birthday']
                self.logged_in = True

        return self.logged_in

    def logout(self):
        """ Log-out a user """
        self.email = None
        self.name = None
        self.theme_name = None
        self.next_birthday = None
        self.logged_in = False

    def get_user_table(self):
        """ A getter to retrieve "user" table content """
        result = False
        ## Opening and closing a db connection to register the search
        # Comment only for challenge: given the name of the helper, the above comment could be suppressed
        (engine, active_connection) = self.manage_db_engine(
            mode='create_connect')
        if engine == False or active_connection == False:
            return result

        table_name = self.table_name
        
        # TODO ORIGINAL DIRTY Change to orm and better User data model
        try:
            users_table = pd.read_sql(str('SELECT * from '+table_name),
                con=engine)
        except:
            return result

        ## killing the connection
        # Comment only for challenge: given the name of the helper, the above comment could be suppressed
        (engine, active_connection) = self.manage_db_engine(engine=engine,
                active_connection=active_connection, mode='kill')
        if engine == False or active_connection == False:
            return result

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
        """
        Add a new user, from a "email", "name", "hashed-password" and a "theme_name=default"
        Before creating the new object and committing it to database, it checked that a similar user
        does not already exist (no identical emails can coexist)
        """
        ## we return False if an user with this email is already there return false
        ## or if something bad occured with database connection
        # (TODO improvement would be based on Exception forwarding to make a distinction)
        result = False
        
        # By default, current time is used
        next_birthday = calculate_unix_timestamp()

        ##Now see if we already have the user
        users = self.get_user_table()

        ## If we don't find an user with this email
        # Comment only for challenge: I simplified the if with a standard best practice on the return
        if users[users['email']==email].empty:
            # Comment only for challenge: Take advantage of a helper function as with the direct approach we took for
            # db management, some repetition appears in the establishments, deletions of connections
            (engine, active_connection) = self.manage_db_engine(
                mode='create_connect')
            if engine == False or active_connection == False:
                return result
            
            ## preparing the sql_command
            column_name = 'email,name,hashed_password,theme,next_birthday'
            # TODO original DIRTY - Change to orm and better User data model
            # Comment only for challenge: Here I rename the password hashed as hashed_password for better clariy
            # Comment only for challenge: And rename command to sql_command: no need to comment then :)
            table_name = self.table_name
            values = email + '\',\'' + name + '\',\'' + hashed_password
            values += '\',\'' + theme_name + '\',\'' + str(next_birthday)
            values = str(values)
            sql_command = 'INSERT INTO '+table_name
            sql_command += ' ('+column_name+') VALUES (\''+values+'\') ;'
            sql_command = str(sql_command)

            ## execute SQL query
            active_connection.execute(sql_command)
            
            (engine, active_connection) = self.manage_db_engine(engine=engine,
                active_connection=active_connection, mode='kill')
            
            if engine == False or active_connection == False:
                return result
            
            ## Save the logged-in user in the User object
            self.name = name
            self.email = email
            self.theme_name = theme_name
            self.next_birthday = next_birthday
            self.logged_in = True
            
            ## Reaching this point is the only case when we return a True
            result = True
        return result
        
        # Comment only for challenge:This function being not called, I see no reason for encapsulation or even existence
        # TODO check why indentation here. I see no reason why this should be like this
        #def get_models(self):
        #    if self.logged_in:
        #        print('Accessing priviledge accounts')

    # This to update user data: next_birthday_date and preference for theme
    def update_user(self, theme_name, next_birthday):
        """
        Update user data, with a "theme_name" for chosing its color and "next_birthday"
        for storing its birthday data and feed-in the frontend counter
        """
        result = False

        next_birthday = calculate_unix_timestamp(date_to_process=next_birthday)

        (engine, active_connection) = self.manage_db_engine(
            mode='create_connect')

        ## preparing the sql_command
        column_name = 'theme,next_birthday'
        # TODO original DIRTY - Change to orm
        # Comment only for challenge: Here I rename the password hashed as hashed_password for better clariy
        # Comment only for challenge: And rename command to sql_command: no need to comment then :)
        table_name = self.table_name
        values = theme_name + '\',\'' + str(next_birthday)
        sql_command = 'UPDATE '+table_name+' SET ('+column_name
        sql_command += ') = (\''+values+'\') WHERE email =\''
        sql_command += current_user.email+'\';'
        sql_command = str(sql_command)

        ## actually adding it
        active_connection.execute(sql_command)

        (engine, active_connection) = self.manage_db_engine(engine=engine,
            active_connection=active_connection, mode='kill')
        if engine == False or active_connection == False:
            return result
        
        # update current_user to keep consistency with database content
        self.theme_name = theme_name
        self.next_birthday = next_birthday

        result = True
        return result

    # Helper functions
    def manage_db_engine(self, active_connection=None, engine=None,
        mode='create_connect'):
        """ A Database connector helper"""
        # Result is a tuple that provide insights into the status of the action performed on (engine, connection)
        # If exception occured or bad mode requested, tuple is returned as (False, False)
        result = (False, False)
        # TODO Should think of forwarding Exception here to make more proper
        # but I need a beer now, it is Week-end grillfest :|       
        ## killing the connection
        if mode == 'kill':
            try:
                active_connection.close()
                engine.dispose()
            except:
                return result
            result = (True, True)
        
        ## creating engine and actual connection
        if mode == 'create_connect':
            connection_path = self.db_path
            try:
                engine = create_engine(connection_path)
                active_connection = engine.connect()
            except:
                return result
            result = (engine, active_connection)
        
        return result

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
    return render_template('index.html')

## App route for signup, allows users to create an account
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method=='POST':
        email = request.form.get('email')
        name = request.form.get('name')
        # Comment only for challenge: Here I rename the password hashed as hashed_password for better clariy
        hashed_password = generate_password_hash(
            request.form.get('password'), method='sha256')
        if current_user.add_user(name, email, hashed_password):
            return redirect(url_for('profile'))
        else:
            flash('This user is already registered, try to login instead')

    return render_template('signup.html')

## App route to login , allows existing users to log in
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        if current_user.log_in(request.form.get('email'),
            request.form.get('password')):
            
            return redirect(url_for('profile'))
        
        else:
            flash('Incorrect email or password')

    return render_template('login.html')

## App route to logout, reset the current user
@app.route('/logout')
def logout():
    current_user.logout()
    return render_template('login.html')

## App route to get to user profile, if user logged in it provides a welcome message
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if current_user.logged_in:
        if request.method=='POST':
            # Currently, the hours default at 00:00:00
            update_next_birthday = request.form.get('next_birthday_dateformat')
            update_next_birthday = format_date_string_ymd(update_next_birthday)
            update_theme = request.form.get('update_theme')
            # Convert to UTC
            # Update current user / check it is saved in database
            # then the next render shall be correct
            current_user.update_user(theme_name=update_theme,
                                     next_birthday=update_next_birthday)
            
        name = current_user.name
        theme_name = current_user.theme_name
        next_birthday = current_user.next_birthday
        # Conversion to format "YYYY-MM-DD"
        # Because of input type=date on html
        # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/date
        next_birthday_dateformat = create_date_from_timestamp(next_birthday)
        
        theme_color_param = set_color_name(theme_name)

        # !!! Do not uncomment unless you want to see the sql injection demo !!!
        # SQL injection dirty test
        #current_user.test_sql_inj()

        return render_template('profile.html', name=name,
            theme_name=theme_name, next_birthday_unixtimestamp=next_birthday,
            next_birthday_dateformat=next_birthday_dateformat,
            theme_color_param=theme_color_param)
    else:
        return redirect(url_for('login'))

## Entry point if we do not use Flask Run - Default to localhost:5000
## TODO Investigate why they to do not use a Factory
## TODO Investigate why main app, routes and data models are not decoupled
if __name__ == "__main__":
    #app=create_app()
    app.run()
