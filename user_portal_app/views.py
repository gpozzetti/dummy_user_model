"""
Assign views to routes
No blueprints in current version

    Routes:
         home()   : @app.route('/')
         signup() : @app.route('/signup', methods=['GET', 'POST'])
         login()  : @app.route('/login', methods=['GET', 'POST'])
         logout() : @app.route('/logout')
         profile(): @app.route('/profile', methods=['GET', 'POST'])

.. moduleauthor:: Cedric Renzi, https://github.com/cedric2080
"""

from flask import flash
from flask import render_template, redirect, url_for, request
from werkzeug.security import generate_password_hash

from user_portal_app.models import current_user
from user_portal_app.helpers import format_date_string_ymd, create_date_from_timestamp
from user_portal_app.helpers import set_color_name

from user_portal import app

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