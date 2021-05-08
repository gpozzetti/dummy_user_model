from datetime import datetime

from flask import Flask,flash
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask import Blueprint, render_template, redirect, url_for,request
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, Column, MetaData
from sqlalchemy import Table, DateTime, String, Integer
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
        Column('next_birthday', Integer)
    )
    meta.create_all(engine)

### user class (probably better to use the flask one but still have to understand it )
class User():
    ## Linking to the database
    def __init__(self, db):
        print("HERE INIT USER")
        # I prefer to have it here, looks like more mimicking an actual data model of an ORM :)
        ## define the name of the table in the database (the lowercase apparently required by postgrade)
        ## DB nuts and bolts
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
        print("HERE LOGIN USER")
        ## Check if user exists, and has the password
        users = self.get_user_table()
        if email in users['email'].to_list():
            print('I got the user')
            users = users.set_index('email')
            # Here I rename the password hashed as hashed_password for better clariy
            hashed_password = users.loc[email, 'hashed_password']
            # Here I rename the password hashed as hashed_password for better clariy
            if check_password_hash(hashed_password, password):
                self.email = email
                self.name = users.loc[email, 'name']
                self.theme_name = users.loc[email, 'theme']
                self.next_birthday = users.loc[email, 'next_birthday']
                self.logged_in = True

        return self.logged_in

    def logout(self):
        print("HERE LOGOUT USER")
        self.logged_in = False
        self.name = None
        self.email = None
        self.theme_name = None
        self.next_birthday = None

    def get_user_table(self):
        result = False
        print("HERE get_user_table USER")
        ## Opening and closing a connection to register the search
        #connection_path = self.db_path
        ## create an engine to test the database
        #engine = create_engine(connection_path)
        (engine, active_connection) = self.manage_db_engine(
            mode='create_connect')
        if engine == False or active_connection == False:
            return result

        ## define the name of the table in the database (the lowercase apparently required by postgrade)
        table_name = self.table_name
        
        # TODO ORIGINAL DIRTY Change to orm
        try:
            users_table = pd.read_sql(str('SELECT * from '+table_name), con=engine)
        except:
            return result

        ## killing the connection
        #engine.dispose()

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

    def add_user(self, name, email, hashed_password, theme_name='default',
        next_birthday=datetime.utcnow()):
        ## we return False if an user with this email is already there return false
        ## or if something bad occured with database connection
        # (TODO improvement would be based on Exception forwarding to make a distinction)
        result = False
        print("HERE add_user USER")
        epoch = datetime(1970,1,1)
        next_birthday = (next_birthday - epoch).total_seconds()
        next_birthday = int(next_birthday)
        ##Now see if we already have the user
        users = self.get_user_table()

        ## If we don't find an user with this email
        # Comment only for challenge: I simplified the if with a standard best practice on the return
        if users[users['email']==email].empty:
            ## Opening and closing a connection to register the search
            #connection_path = self.db_path
            ## create an engine to test the database
            #engine = create_engine(connection_path)
            ## define the name of the table in the database (the lowercase apparently required by postgrade)
            #table_name = 'user'

            ## actually create the connection
            #active_connection = engine.connect()
            # Comment only for challenge: Take advantage of a helper function as with the direct approach we took for
            # db management, some repetition appears in the establishments, deletions of connections
            (engine, active_connection) = self.manage_db_engine(
                mode='create_connect')
            if engine == False or active_connection == False:
                return result
            
            ## preparing the sql_command
            column_name = 'email,name,hashed_password,theme,next_birthday'
            # TODO original DIRTY - Change to orm
            # Comment only for challenge: Here I rename the password hashed as hashed_password for better clariy
            # Comment only for challenge: And rename command to sql_command: no need to comment then :)
            table_name = self.table_name
            values = email + '\',\'' + name + '\',\'' + hashed_password + '\',\'' + theme_name + '\',\'' + str(next_birthday)
            sql_command=str('INSERT INTO '+table_name+' ('+column_name+') VALUES (\''+values+'\') ;')
            print(sql_command)

            ## actually adding it
            active_connection.execute(sql_command)
            
            (engine, active_connection) = self.manage_db_engine(engine=engine,
                active_connection=active_connection, mode='kill')
            if engine == False or active_connection == False:
                return result
            #active_connection.close()
            ## killing the connection
            #engine.dispose()

            ## log  in with the current credentials
            self.name = name
            self.email = email
            self.theme_name = theme_name
            self.next_birthday = next_birthday
            self.logged_in = True
            print(self.next_birthday)
            ## Reaching this point is the only case when we return a True
            result = True
        return result

        # TODO check why indentation here. I see no reason why this should be like this
        # This function being not called, I see no reason for encapsulation
        def get_models(self):
            if self.logged_in:
                print('Accessing priviledge accounts')

    # This to update user data: next_birthday_date and preference for theme
    def update_user(self, theme_name, next_birthday):
        result = False
        print("HERE update_user USER")
        epoch = datetime(1970,1,1)
        print(epoch)
        print(next_birthday)
        next_birthday = (next_birthday - epoch).total_seconds()
        next_birthday = int(next_birthday)
        print(next_birthday)

        (engine, active_connection) = self.manage_db_engine(
            mode='create_connect')

        ## preparing the sql_command
        column_name = 'theme,next_birthday'
        # TODO original DIRTY - Change to orm
        # Comment only for challenge: Here I rename the password hashed as hashed_password for better clariy
        # Comment only for challenge: And rename command to sql_command: no need to comment then :)
        table_name = self.table_name
        values = theme_name + '\',\'' + str(next_birthday)
        sql_command=str('UPDATE '+table_name+' SET ('+column_name+') = (\''+values+'\') WHERE email =\''+current_user.email+'\';')
        print(sql_command)

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
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    print("HERE PROFILE")
    if current_user.logged_in:
        if request.method=='POST':
            # Currently, the hours default at 00:00:00
            update_next_birthday = request.form.get('next_birthday_dateformat')
            update_next_birthday = datetime.strptime(
                update_next_birthday, '%Y-%m-%d')
            update_theme = request.form.get('update_theme')
            # Convert to UTC
            # Update current user / check it is saved in database
            # then the next render shall be correct
            print("HERE UPDATE")
            print(update_next_birthday)
            print(update_theme)
            current_user.update_user(theme_name=update_theme,
                                     next_birthday=update_next_birthday)
            
        name = current_user.name
        theme_name = current_user.theme_name
        next_birthday = current_user.next_birthday
        # Conversion to format "YYYY-MM-DD"
        # Because of input type=date on html
        # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/date
        next_birthday_dateformat = datetime.fromtimestamp(next_birthday).date()
        print("HERE RENDER")
        print(next_birthday)
        print(next_birthday_dateformat)
        
        # !!! Do not uncomment unless you want to see the sql injection demo !!!
        # SQL injection dirty test
        #current_user.test_sql_inj()

        return render_template('profile.html', name=name,
            theme_name=theme_name, next_birthday_unixtimestamp=next_birthday,
            next_birthday_dateformat=next_birthday_dateformat)
    else:
        return redirect(url_for('login'))

## Entry point if we do not use Flask Run - Default to localhost:5000
## TODO Investigate why they to do not use a Factory
## TODO Investigate why main app, routes and data models are not decoupled
if __name__ == "__main__":
    #app=create_app()
    print("HERE MAIN")
    app.run()
