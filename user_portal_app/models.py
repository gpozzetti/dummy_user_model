"""
Data model for the user table, User class
It defines tables as classes:
     User: stores all the registered users
     TODO: We may here encore the themes as a new table

.. moduleauthor:: Cedric Renzi, https://github.com/cedric2080
"""
import pandas as pd

from werkzeug.security import check_password_hash
from sqlalchemy import create_engine

from user_portal_app import app, db
from user_portal_app.helpers import calculate_unix_timestamp

### User class (probably better to use the flask one but still have to understand it)
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
        
        Methods:
            __init__(self, db)
            log_in(self, email, password)
            logout(self)
            get_user_table(self)
            (!) hidden (!) test_sql_inj(self)
            add_user(self, name, email, hashed_password, theme_name='default')
            add_user(self, name, email, hashed_password, theme_name='default')
            update_user(self, theme_name, next_birthday)
            
            Helper methods
            --------------
            manage_db_engine(self, active_connection=None, engine=None, mode='create_connect')
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

# Today, I found it more logical to define the current_user feature in the User data model module
# It avoids one extra import
# In the case we have the create_app() factory and the blueprints, more work to implement that as far as I know
current_user = User(app.config['SQLALCHEMY_DATABASE_URI'])