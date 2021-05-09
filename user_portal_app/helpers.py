"""
This is a helper module:
 - wrapper to assign theme names to CSS style parameters
 - wrapper to deal with dates 

.. moduleauthor:: Cedric Renzi
"""

from datetime import datetime

def set_color_name(theme_name):
    # This could have been put into a helper table on the database, with 1-1 RS to the user
    theme_color_param = "is-primary"
    if theme_name == "spring":
        theme_color_param = "is-success"
    if theme_name == "summer":
        theme_color_param = "is-warning"
    if theme_name == "autumn":
        theme_color_param = "is-danger"
    if theme_name == "winter":
        theme_color_param = "is-info"
    
    return theme_color_param

def calculate_unix_timestamp(date_to_process=datetime.utcnow()):
    epoch = datetime(1970,1,1)
    date_timestamp = (date_to_process - epoch).total_seconds()
    return int(date_timestamp)

def format_date_string_ymd(date):
    return datetime.strptime(date, '%Y-%m-%d')

def create_date_from_timestamp(date):
    return datetime.fromtimestamp(date).date()