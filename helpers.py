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