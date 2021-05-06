# dummy_user_model
A dummy login interface for users
A bare-bone script to handle user log-in. It currently allows a user to register and it greets the user by name in the profile picture
The backbone of the script is a Flask application.
It is supposed to run under Linux Ubuntu 18.04 LTS

Development environment:
 - Windows WSL Ubuntu 18.04 LTS
 - so it should be fine on a native or VM Linux Ubuntu 18.04 LTS
 - however, because of the use of shell scripts:
   * some adaptation may be required for running on macOs (bash -> zsh ?)
   * not tested on a pure Windows environment

### Challenge
# TODO - 05/05/2021
- to give the user the possibility of choosing a colour in the profile page
- to change the theme accordingly
- to to ask the user for his/her birthday
- to create a countdown again in the profile page
- bugs and security analyses:
  * IT security team is scared that this would make us vulnerable to sql injection.
  * Some of them claim there are bugs when adding users.
##

# Priorities in order of importance:
 - The version is running and existing functionalities are preserved
 - Changes are documented ( git commits quality and comments in the code)
 - The  new functionalities (user-customized color, birthday countdown) are implemented
 - Possible security issues  and bugs reported or fixed
 - General improvements in the code
###

### Description of the existing functionalities
 - localhost:5000/ serves a home page with a central title: Flask Login Example and a short description. Background color is green/blue. On right banner, a Home, a Profile, a Login, a Signup and a Logout links.
 
 - if not logged-in clicking the Profile button redirect to Login (/login)
    * After correcting the init_db bug, I could see that login directly redirect to the profile page. And here the Facebook was born :)
 
 - clicking the Sign Up button redirect to Sign Up (/signup)
    * a user is email, name, credentials
    * there is apparently an email validator
    * clicking on password field, frontend proposes a secured password, I can also type in myself, frontend does not check that my password is complex though...
 
 - clicking the Logout button redirect to Login page (through /logout)
 
 - my first SignUp attempt led to an error 500:
   "Internal Server Error
    The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application"
    * after solving the init_db bug, I could correctly sign-up an account
###

### Critics and room for improvements
 Project
 -------
 - I see no README.MD on the project. Therefore, I am not sure how to launch properly the app.
   * the modern way with 'flask db init', 'flask run' does not work because of the current structure of the single script
   * so I have no other way than launching the app with the command 'env/bin/python3 plain_version.py'. My observation are the following:
     -> flask development server is running
     -> but database was not initialized properly so user table does not exist. Actually, the .db sqlite3 files is just created after the missed attemps of a sign-up.
     Using sqlite editor to watch inside, I see an empty database file, without even the tables declared.

     The absence of the README.MD is annoying because it can confuse the user which may ask himself if he needs to run some extra commands or different commands.
     After solving the init_db bug, I noticed my approach to call the python script directly, as for very simple Flask example, is correct.
 
 - some "typos-formatting" made the code non PEP-8 and difficult to read.
 
 SQL Injections
 --------------
 - I do not like to read the SQL code in such applications:
   * to me, it is red flag to see that because it may indicate SQL injection vulnerabilities (https://xkcd.com/327/)
     -> they are read using pandas readsql feature so it is supposed to be safe (https://github.com/pandas-dev/pandas/blob/v1.2.4/pandas/io/sql.py#L426-L528
     -> but some concerns are not closed on pandas issue tracker (https://github.com/pandas-dev/pandas/issues/10899)
   * nevertheless, this approach looks more error prone as we may have to test many potentialities because the SQL command is assembled based on strings and parameters strings concatenation, the code is more difficult to read like that; so I would tend to replace that using completely the ORM of SQLAlchemy. Doing so, I am sure I am safe wrt SQL injections flaws.
      
 - I would say the most dangerous existing line is this one: command=str('INSERT INTO '+table_name+' ('+column_name+') VALUES (\''+value+'\') ;')
 It is also the ugliest one. Because 'value' expands data entered by a user, I could well see ';' somewhere and a 'DROP TABLE USER' theoritically.
 Not sure I will spend time to test around that because in the end I see this as not the best practices to do it like this.
   -> after correcting the init_db bug, I could create an account with a name "* FROM USER;DROP TABLE USER;SELECT *" which may look like annoying...
   -> fortunately, the related SQL command is an insert so the 'DROP TABLE' does not execute
   -> fortunately, the SQLAlchemy is used to create the engine and it does not allow to run multi-query statements if we had SELECT somewhere
 - (!)(!)(!)
  however, building on these bricks, with a more complicated app, we could well imagine that some heavy day we forget the risk and create a 'SELECT * from user WHERE name = 0;DROP TABLE user;' by choosing carefully the name. This would happened by using for example 'cursor=db.cursor()' and 'cursor.executescript(command)' (see my dirty test method test_sql_inj on User class), because we have already made half the trip by choosing to connect to the database the direct way (and not with the ORM for example).
   (!)(!)(!)
 
 Flask app structure
 -------------------
 - the structure of the app is very monolithic and already complicated (not complex :) ). It will extremely difficult to maintain and extend, even for a simple example.
 It is better to keep things simpler, shorter and more approachable so I would at least decouple the script in between data models, routes , app code.

 - I noticed in the main entry point of the script that a call to a potential factory for the app has been commented. I do not really know why this app does not use a factory while it would make it more configurable and easy to extend as a good practice.

 - For the datasystem, direct execution is used. SQLAlchemy is normally recommended with the ORM (using Sessions). Flask-SqlAlchemy makes this even easier.

 Frontend
 --------
 - I see the CSS style is directly downloaded from the website. I would not do that because who know what can happen: the website is down, file get hacked or corrupted, it may be difficult to configure the firewalls in production. Then I would prefer to download the chosen style. It will also allow me to dupplicate the file easily locally
 in order to make variations for the profile, for example.

 Various
 -------
 - I noticed that the init_db is not called with the double brackets.
 - I noticed a url_db parameter making stuff crashing when calling init_db()
 - I noticed the change to database were no persistent: if we restart flask server, the .db file is empty even if we signed up some people in

###

### Definition of functional unit tests
SQL Injection
-------------
 - Uncomment the line in profile()
 - Create the user in the order below (table will be dropped, while it contained both user at some time)
credentials for tests:
user1
ced2@google.com
0
ced

user2
ced@google.com
0;DROP TABLE user
ced
###

### How-To-Run
 - Development version
  * 
  
 - Staging
 [nc]
 - Production
 [nc]
###
https://github.com/cedric2080
### END