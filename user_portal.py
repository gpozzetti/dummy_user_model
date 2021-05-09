"""
This is a small web portal, leading to customisable profile
A new user can sign-up, a registered user can log-in, access its profile, touch it up by providing its birthday
or changing the theme color of its profile page.
A logged-in user can log-out.

This file is the entry-point of the flask-app. It takes care of initializing all the Flask ecosystem, like databases
sessions, etc.

.. moduleauthor:: Cedric Renzi, https://github.com/cedric2080
"""

from user_portal_app import app, init_db

# More beautiful to have it here
init_db() # Comment for challenge only: added the double brackets

## Entry point if we do not use Flask Run - Default to localhost:5000
## TODO Investigate why they to do not use a create_app Factory (and the app=create_app() should be above not in main)
if __name__ == "__main__":
    app.run()