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
Description of the existing functionalities

###
Definition of functional unit tests

###
How-To-Run
 - Development version
  * 
  
 - Staging
 [nc]
 - Production
 [nc]
