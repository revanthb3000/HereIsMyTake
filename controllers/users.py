"""
This is the users.py controller and contains all controller functions related to user actions.
"""

# Stuff to get eclipse autocomplete to work. Dead code !
if 0:
    from modules import *
    from gluon import *
    request, session, response, T, cache = current.request, current.session, current.response, current.t, current.cache
    from gluon.tools import Auth, Service, Crud
    db = DAL('mysql://username:password@localhost/test')
    auth = Auth()
    service = Service()
    crud = Crud()

#All the required imports.
import databaseConnectionStrings
import databaseQueries
import utilityFunctions
import MySQLdb

def index():
    redirect(URL('default','index'))
    return dict()

@auth.requires_login()
def profile():
    if(request.vars.userId==None):
        redirect(URL('default','index'))

    userId = request.vars.userId
    imagePrefix = "images/displayPictures/"
    imageFileName = "defaultMale.png"
    fileName = imagePrefix + imageFileName

    response.view = 'users/profile.html'

    db = databaseQueries.getDBHandler(userId)
    isFollowing = databaseQueries.checkIfFollowing(db,userId,auth.user.id)

    rows = db(db.auth_user.id == userId).select()
    row = None
    if len(rows) == 1:
        row = rows[0]
    else:
        redirect(URL('default','index'))

    response.title = row.first_name + " " + row.last_name;
    followURL = ""
    if(int(auth.user.id)!=int(userId)):
        if(isFollowing):
            followURL = URL('users','unfollow',vars=dict(userId = userId))
        else:
            followURL = URL('users','follow',vars=dict(userId = userId))

    if (row.displayPicture!=None and row.displayPicture.strip()!=""):
        fileName = row.displayPicture
    return dict(fileName = fileName , userInfo = row, followURL = followURL, isFollowing = isFollowing)

@auth.requires_login()
def editDisplayPicture():
    response.view = "users/editpicture.html"
    response.title = "Change your DP"
    form=FORM(INPUT(_name='image',_id='image', _type='file'))
    return dict(form = form)

@auth.requires_login()
def editProfile():
    response.view = "users/editprofile.html"
    response.title = 'Editing Profile'
    db = databaseQueries.getDBHandler(auth.user.id)

    form=SQLFORM(db.auth_user, auth.user.id, showid = False)
    if form.process().accepted:
        response.flash = 'Changes Saved.'
        redirect(URL('users','profile'))
    elif form.errors:
        response.flash = 'Errors found in the form.'
    else:
        response.flash = 'Please fill the form.'
    return dict(form=form, username = auth.user.first_name + " " + auth.user.last_name)

@auth.requires_login()
def follow():
    if(request.vars.userId==None):
        redirect(URL('default','index'))

    userId = request.vars.userId
    db = databaseQueries.getDBHandler(auth.user.id)
    if (databaseQueries.checkIfUserExists(db,userId)):
        db.followRelations.insert(userId=userId,followerId=auth.user.id)
        redirect(URL('users','profile',vars=dict(userId = userId)))
    else:
        redirect(URL('default','index'))

    return dict()

@auth.requires_login()
def unfollow():
    if(request.vars.userId==None):
        redirect(URL('default','index'))

    userId = request.vars.userId
    db = databaseQueries.getDBHandler(auth.user.id)
    if (databaseQueries.checkIfUserExists(db,userId)):
        db((db.followRelations.userId==userId) & (db.followRelations.followerId==auth.user.id)).delete()
        redirect(URL('users','profile',vars=dict(userId = userId)))
    else:
        redirect(URL('default','index'))

    return dict()

def login():
    if(auth.is_logged_in()):
        redirect(URL('default','index'))
    response.view = 'users/login.html'
    response.title = 'Login'
    form = auth.login()
    return dict(form=form)

def register():
    if(auth.is_logged_in()):
        redirect(URL('default','index'))
    response.view = 'users/register.html'
    response.title = 'Registration'
    form = auth.register()
    return dict(form=form)

@auth.requires_login()
def changePassword():
    response.view = 'users/changepassword.html'
    response.title = 'Change Password'
    form = auth.change_password()
    return dict(form=form)

def retrievePassword():
    if(auth.is_logged_in()):
        redirect(URL('default','index'))
    response.view = 'users/retrievepassword.html'
    response.title = 'Retrieve Password'
    form = auth.retrieve_password()
    return dict(form = form)

def logout():
    if(auth.is_logged_in()):
        auth.logout()
    redirect(URL('default','index'))
    return dict()
