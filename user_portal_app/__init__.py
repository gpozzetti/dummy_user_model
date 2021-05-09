"""
This is where we create and configure the app, an (create_app) app factory could well be settled here

.. moduleauthor:: Cedric Renzi, https://github.com/cedric2080
"""

from flask import Flask
# Comment only for challenge: Blueprint are not used in the orginal version, however I would really
# recommend their usage for the sake of modularization, yet it needs the create_app factory and using context
# for the current_user
#from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask import Blueprint
# We do not store data in Session here apparently
#from flask_session import Session
from sqlalchemy import create_engine, Column, MetaData
from sqlalchemy import Table, DateTime, String, Integer

# init SQLAlchemy so we can use it later both in our data models and in the create_app factory
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

# We could add a Flask application factory
# But then we need to work more with the app context to add the current_user
## Configuring the app
app = Flask(__name__, static_url_path='/')
app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///DB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Placing this import here is one solution for solving the usual suspects Flask circular import :)
# Using blueprint should solve it more efficiently and logically
from user_portal_app import views

db.init_app(app)