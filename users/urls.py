from django.urls import path
from . import views



urlpatterns = [

    path(
        'register/',
        views.registerUser,
        name='register'
    ),


    path(
        'login/',
        views.loginUser,
        name='login'
    ),


    path(
        'logout/',
        views.logoutUser,
        name='logout'
    ),

]

# register/
# Page user account ku sameeyo

# login/
# User login sameeyo

# logout/
# User ka baxo

"""
Authentication URLs

/register/ -> Register a new user
/login/    -> Login existing user
/logout/   -> Logout authenticated user
"""