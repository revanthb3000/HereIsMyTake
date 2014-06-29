"""
This is the users.py controller and contains all controller functions related to user actions.
"""
from applications.HereIsMyTake import modules

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
    Storage = Storage()

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
    response.view = 'users/profile.html'

    isFollowing = databaseQueries.checkIfFollowing(db,userId,auth.user.id)

    userInfo = databaseQueries.getUserInfo(db, userId)

    if (userInfo == None):
        redirect(URL('default','index'))

    response.title = userInfo.first_name + " " + userInfo.last_name;
    response.subtitle = "Joined " + utilityFunctions.getMonthName(userInfo.timeOfJoining.month) + "-" + str(userInfo.timeOfJoining.year)
    
    followURL = ""
    if(int(auth.user.id)!=int(userId)):
        followURL = URL('users','changeFollowStatus',vars=dict(userId = userId))

    profilePicLink = databaseQueries.getUserProfilePicture(db, userId, None)
    numberOfFollowers = databaseQueries.getNumberOfFollowers(db, userId)

    return dict(profilePicLink = profilePicLink , userInfo = userInfo, followURL = followURL, 
                numberOfFollowers=numberOfFollowers, isFollowing = isFollowing)

@auth.requires_login()
def editProfile():
    response.view = "users/editprofile.html"
    response.title = 'Editing Profile'

    userId = auth.user.id
    userInfo = databaseQueries.getUserInfo(db, userId)
    profilePicLink = databaseQueries.getUserProfilePicture(db, userId, userInfo.displayPicture)

    db.auth_user.first_name.writable = False
    db.auth_user.last_name.writable = False
    db.auth_user.email.writable = False
    db.auth_user.password.writable = False
    db.auth_user.email.writable = False
    db.auth_user.Birthday.writable = False
    db.auth_user.Gender.writable = False

    form = SQLFORM(db.auth_user, auth.user.id, showid = False)
    
    form.vars.Location = userInfo.Location
    form.vars.Occupation = userInfo.Occupation
    form.vars.AboutMe = userInfo.AboutMe
    form.vars.Website = userInfo.Website

    if form.process().accepted:
        response.flash = 'Changes Saved.'
        redirect(URL('users','profile',vars=dict(userId = auth.user.id)))
    elif form.errors:
        response.flash = 'Errors found in the form.'
    else:
        response.flash = 'Please fill the form.'

    return dict(form=form, userInfo=userInfo, profilePicLink=profilePicLink)

@auth.requires_login()
def changeFollowStatus():
    if(request.vars.userId==None):
        return False
        
    userId = request.vars.userId
    followerId = auth.user.id
    if (databaseQueries.checkIfUserExists(db,userId)):
        if(databaseQueries.checkIfFollowing(db, userId, followerId)):
            databaseQueries.removeFollowRelation(db, userId, followerId)
        else:
            databaseQueries.addFollowRelation(db, userId, followerId)
        return True
    return False

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
    
    db.auth_user["AboutMe"].readable = db.auth_user["AboutMe"].writable = False
    db.auth_user["Location"].readable = db.auth_user["Location"].writable = False
    db.auth_user["Occupation"].readable = db.auth_user["Occupation"].writable = False
    db.auth_user["Website"].readable = db.auth_user["Website"].writable = False
    db.auth_user["displayPicture"].readable = db.auth_user["displayPicture"].writable = False
    db.auth_user["timeOfJoining"].readable = db.auth_user["timeOfJoining"].writable = False
    
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
