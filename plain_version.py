from flask import Flask,flash
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask import Blueprint, render_template, redirect, url_for,request
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine
import pandas as pd
# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()


### user class (probably better to use the flask one but still have to understand it )
class User():
    ## Linking to the database
    def __init__(self,db):
        self.db_path=db
        self.logged_in=False
        self.name=None
        self.mail=None

    def log_in(self,mail, password):
        ## Check if user exists, and has the password
        users=self.get_user_table()
        if mail in users['email'].to_list():
            print('I got the user')
            users=users.set_index('email')
            password_challenge=users.loc[mail,'password']
            if check_password_hash(password_challenge,password):
                self.mail=mail
                self.name=users.loc[mail,'name']
                self.logged_in=True

        return self.logged_in

    def logout(self):
        self.logged_in=False
        self.name=None
        self.mail=None


    def get_user_table(self):
        ## Opening and closing a connection to register the search
        connection_path=self.db_path
        ## create an engine to test the database
        engine = create_engine(connection_path)
        ## define the name of the table in the database (the lowercase apparently required by postgrade)
        table_name='user'

        users_table=pd.read_sql(str('SELECT * from '+table_name),con=engine)

        ## killing the connection
        engine.dispose()
        return users_table



    def add_user(self,name, email,password):
        ##Now see if we already have the user
        users=self.get_user_table()

        ## If we don't find an user with this email
        if users[users['email']==email].empty:
            ## Opening and closing a connection to register the search
            connection_path=self.db_path
            ## create an engine to test the database
            engine = create_engine(connection_path)
            ## define the name of the table in the database (the lowercase apparently required by postgrade)
            table_name='user'

            ## actually create the connection
            active_connection =engine.connect()
            ## preparing the command
            column_name='email,name,password'
            value=email+'\',\''+name+'\',\''+password
            ## A string with the sql command
            command=str('INSERT INTO '+table_name+' ('+column_name+') VALUES (\''+value+'\') ;')
            ## actually adding it
            active_connection.execute(command)
            active_connection.close()
            ## killing the connection
            engine.dispose()

            ## log  in with the current credentials
            self.name=name
            self.email=email
            self.logged_in=True
            return True
        ## if an user with this email is already there return false
        else:
            return False


app = Flask(__name__,static_url_path='/')
app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///DB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
current_user=User(app.config['SQLALCHEMY_DATABASE_URI'])

@app.route('/')
def home():
    print(current_user.name)
    return render_template('index.html')


@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        email= request.form.get('email')
        name=request.form.get('name')
        password=generate_password_hash(request.form.get('password'), method='sha256')
        if current_user.add_user(name,email,password):

            return redirect(url_for('profile'))
        else:
            print('User Already Existing')
            flash('This user is already registered, try to login instead')

    return render_template('signup.html')


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        
        if current_user.log_in(request.form.get('email'),request.form.get('password')):
            print('i should be signed in ')
            return redirect(url_for('profile'))

        else:
            flash('Incorrect email or password')

    return render_template('login.html')


@app.route('/logout')
def logout():
    current_user.logout()
    return render_template('login.html')

@app.route('/profile')
def profile():
    if current_user.logged_in:
        name=current_user.name
        return render_template('profile.html',name=name)
    else:
        return redirect(url_for('login'))




if __name__ == "__main__":
    #app=create_app()

    app.run()
