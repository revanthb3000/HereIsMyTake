# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

if 0:
    from modules import *
    from gluon import *
    request, session, response, T, cache = current.request, current.session, current.response, current.t, current.cache
    from gluon.tools import Auth, Service, Crud
    db = DAL('mysql://username:password@localhost/test')
    auth = Auth()
    service = Service()
    crud = Crud()

import databaseConnectionStrings
import databaseQueries
import utilityFunctions
import MySQLdb

def tester():
    if (auth.is_logged_in()):
        db = databaseQueries.getDBHandler(auth.user.id)
    else:
        db = databaseQueries.getDBHandler(None)
    db.topics.insert(topicName="Football",parentId=0)
    db.close()
    return "What is this ?"

def index():
    response.view = "index.html"
    response.title = 'Welcome to h-M-t.'
    username = 'Log in fella !'
    if(auth.is_logged_in()):
        username = auth.user.first_name + " " + auth.user.last_name
    sampleViewTakeURL = URL('viewTake',vars=dict(takeId='1'))
    return dict(sampleViewTakeURL = sampleViewTakeURL,username = username)

@auth.requires_login()
def profile():
    if(request.vars.userId==None):
        redirect(URL('index'))

    userId = request.vars.userId
    imagePrefix = "images/displayPictures/"
    imageFileName = "defaultMale.png"
    fileName = imagePrefix + imageFileName

    response.view = 'profile.html'

    db = databaseQueries.getDBHandler(userId)
    isFollowing = databaseQueries.checkIfFollowing(db,userId,auth.user.id)

    rows = db(db.auth_user.id == userId).select()
    row = None
    if len(rows) == 1:
        row = rows[0]
        db.close()
    else:
        db.close()
        redirect(URL('index'))

    response.title = row.first_name + " " + row.last_name;
    followURL = ""
    if(int(auth.user.id)!=int(userId)):
        if(isFollowing):
            followURL = URL('unfollow',vars=dict(userId = userId))
        else:
            followURL = URL('follow',vars=dict(userId = userId))

    if (row.displayPicture!=None and row.displayPicture.strip()!=""):
        fileName = row.displayPicture
    return dict(fileName = fileName , userInfo = row, followURL = followURL, isFollowing = isFollowing)

@auth.requires_login()
def editDisplayPicture():
    response.view = "editpicture.html"
    response.title = "Change your DP"
    form=FORM(INPUT(_name='image',_id='image', _type='file'))
    return dict(form = form)

@auth.requires_login()
def editProfile():
    response.view = "editprofile.html"
    response.title = 'Editing Profile'
    db = databaseQueries.getDBHandler(auth.user.id)

    form=SQLFORM(db.auth_user, auth.user.id, showid = False)
    if form.process().accepted:
        response.flash = 'Changes Saved.'
        redirect(URL('profile'))
    elif form.errors:
        response.flash = 'Errors found in the form.'
    else:
        response.flash = 'Please fill the form.'
    db.close()
    return dict(form=form, username = auth.user.first_name + " " + auth.user.last_name)

@auth.requires_login()
def submitTake():
    response.view = "submitTake.html"
    response.title = "Submit Take"
    db = databaseQueries.getDBHandler(auth.user.id)
    takeContent = ""

    topicsList = databaseQueries.getListOfTopics(db)

    fields = []
    i = 1
    while(i<len(topicsList)):
        topicMapping = topicsList[i]
        fields += [Field(str(topicMapping["topicName"]),'boolean', label=topicMapping["topicName"])]
        i = i + 1

    fields += [field for field in db.takes]

    form = SQLFORM.factory(*fields)

    if form.process().accepted:
        takeContent = form.vars.takeContent
        takeId = db.takes.insert(takeTitle = form.vars.takeTitle ,takeContent = form.vars.takeContent)
        i = 1
        while(i<len(topicsList)):
            topicMapping = topicsList[i]
            if(form.vars[topicMapping["topicName"]]):
                db.take_topic_mapping.insert(takeId = takeId, topicId = i)
            i = i + 1

        redirect(URL('viewTake',vars=dict(takeId = takeId)))
    elif form.errors:
        response.flash = 'Errors found in the form.'
    else:
        response.flash = 'Please fill the form.'
    db.close()

    textarea = form.element('textarea')
    textarea['_cols'] = 1000
    return dict(form=form, takeContent = takeContent)

@auth.requires_login()
def editTake():
    response.view = "submitTake.html"
    response.title = "Edit Take"
    db = databaseQueries.getDBHandler(auth.user.id)

    userId = auth.user.id
    takeId = request.vars.takeId

    if(takeId==None or not(databaseQueries.checkIfUserTakePairExists(db, userId, takeId)) ):
        redirect(URL('index'))

    db.takes.takeTitle.default = db.takes[takeId].takeTitle
    db.takes.takeContent.default = db.takes[takeId].takeContent

    topicsList = databaseQueries.getListOfTopics(db)
    takeTopicsList = databaseQueries.getTakeTopicsList(db, takeId)

    fields = []
    i = 1
    while(i<len(topicsList)):
        topicMapping = topicsList[i]
        fields += [Field(str(topicMapping["topicName"]),'boolean', label=topicMapping["topicName"], default = (i in takeTopicsList))]
        i = i + 1

    fields += [field for field in db.takes]

    form = SQLFORM.factory(*fields)

    takeContent = ""
    if form.process().accepted:
        takeContent = form.vars.takeContent
        takeTitle = form.vars.takeTitle
        row = db(db.takes.id==takeId).select().first()
        row.takeContent = takeContent
        row.takeTitle = takeTitle
        row.update_record()

        i = 1
        while(i<len(topicsList)):
            topicMapping = topicsList[i]
            if(form.vars[topicMapping["topicName"]]):
                db.take_topic_mapping.insert(takeId = takeId, topicId = i)
            else:
                db((db.take_topic_mapping.takeId==takeId) & (db.take_topic_mapping.topicId==i)).delete()
            i = i + 1

        redirect(URL('viewTake',vars=dict(takeId = request.vars.takeId)))
    elif form.errors:
        response.flash = 'Errors found in the form.'
    else:
        response.flash = 'Please fill the form.'

    db.close()

    textarea = form.element('textarea')
    textarea['_cols'] = 1000
    return dict(form=form, takeContent = takeContent)

def viewTake():
    response.view = 'viewTake.html'

    userId = 0
    if (auth.is_logged_in()):
        db = databaseQueries.getDBHandler(auth.user.id)
        userId = auth.user.id
    else:
        db = databaseQueries.getDBHandler(None)

    takeId = request.vars.takeId
    if not(utilityFunctions.checkIfVariableIsInt(takeId)):
        takeId = None

    takeContent = ""
    takeTitle = "View Take"
    timeOfTake = ""
    if(takeId!=None):
        rows = db(db.takes.id == int(request.vars.takeId)).select()
        if len(rows) == 1:
            row = rows[0]
            takeContent = row.takeContent
            takeTitle = row.takeTitle
            timeOfTake = row.timeOfTake

    response.title = takeTitle
    response.subtitle = "Posted on " + str(timeOfTake)

    editLink = ""
    if(databaseQueries.checkIfUserTakePairExists(db, userId , takeId)):
        editLink = URL('editTake',vars=dict(takeId = takeId))

    db.close()

    if(takeContent==""):
        redirect(URL('index'))

    return dict(takeContent = takeContent, editLink = editLink)

@auth.requires_login()
def follow():
    if(request.vars.userId==None):
        redirect(URL('index'))

    userId = request.vars.userId
    db = databaseQueries.getDBHandler(auth.user.id)
    if (databaseQueries.checkIfUserExists(db,userId)):
        db.followRelations.insert(userId=userId,followerId=auth.user.id)
        db.close()
        redirect(URL('profile',vars=dict(userId = userId)))
    else:
        db.close()
        redirect(URL('index'))

    return dict()

@auth.requires_login()
def unfollow():
    if(request.vars.userId==None):
        redirect(URL('index'))

    userId = request.vars.userId
    db = databaseQueries.getDBHandler(auth.user.id)
    if (databaseQueries.checkIfUserExists(db,userId)):
        db((db.followRelations.userId==userId) & (db.followRelations.followerId==auth.user.id)).delete()
        db.close()
        redirect(URL('profile',vars=dict(userId = userId)))
    else:
        db.close()
        redirect(URL('index'))

    return dict()

def login():
    if(auth.is_logged_in()):
        redirect(URL('index'))
    response.view = 'login.html'
    response.title = 'Login'
    form = auth.login()
    return dict(form=form)

def register():
    if(auth.is_logged_in()):
        redirect(URL('index'))
    response.view = 'register.html'
    response.title = 'Registration'
    form = auth.register()
    return dict(form=form)

@auth.requires_login()
def changePassword():
    response.view = 'changepassword.html'
    response.title = 'Change Password'
    form = auth.change_password()
    return dict(form=form)

def retrievePassword():
    if(auth.is_logged_in()):
        redirect(URL('index'))
    response.view = 'retrievepassword.html'
    response.title = 'Retrieve Password'
    form = auth.retrieve_password()
    return dict(form = form)

def logout():
    if(auth.is_logged_in()):
        auth.logout()
    redirect(URL('index'))
    return dict()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    db = databaseQueries.getDBHandler(auth.user.id)
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
