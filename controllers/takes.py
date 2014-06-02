"""
This is the takes.py controller and contains all controller functions related to the 'take' pages.
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
def submitTake():
    response.view = "takes/submitTake.html"
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

        redirect(URL('takes','viewTake',vars=dict(takeId = takeId)))
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
    response.view = "takes/submitTake.html"
    response.title = "Edit Take"
    db = databaseQueries.getDBHandler(auth.user.id)

    userId = auth.user.id
    takeId = request.vars.takeId

    if(takeId==None or not(databaseQueries.checkIfUserTakePairExists(db, userId, takeId)) ):
        redirect(URL('default','index'))

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

        redirect(URL('takes','viewTake',vars=dict(takeId = request.vars.takeId)))
    elif form.errors:
        response.flash = 'Errors found in the form.'
    else:
        response.flash = 'Please fill the form.'

    db.close()

    textarea = form.element('textarea')
    textarea['_cols'] = 1000
    return dict(form=form, takeContent = takeContent)

def viewTake():
    response.view = 'takes/viewTake.html'

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
    deleteLink = ""
    if(databaseQueries.checkIfUserTakePairExists(db, userId , takeId)):
        editLink = URL('takes','editTake',vars=dict(takeId = takeId))
        deleteLink = URL('takes','deleteTake',vars=dict(takeId = takeId))

    db.close()

    if(takeContent==""):
        redirect(URL('default','index'))

    return dict(takeContent = takeContent, editLink = editLink, deleteLink = deleteLink)

@auth.requires_login()
def deleteTake():
    response.view = "takes/deleteTake.html"
    response.title = "Delete Take"
    db = databaseQueries.getDBHandler(auth.user.id)

    userId = auth.user.id
    takeId = request.vars.takeId

    if(takeId==None or not(databaseQueries.checkIfUserTakePairExists(db, userId, takeId))):
        redirect(URL('default','index'))

    rows = db(db.takes.id == int(takeId)).select()
    takeTitle = ""
    if len(rows) == 1:
        row = rows[0]
        takeTitle = row.takeTitle

    form = FORM(INPUT(_type='submit', _value='Yes', _name='yesDelete'), INPUT(_type='submit', _value="No", _name='noDelete'))

    if form.process().accepted:
        response.flash = 'Form Accepted.'
        if(request.vars.yesDelete):
            databaseQueries.deleteTake(db, takeId)
        db.close()
        redirect(URL('default','index'))
    elif form.errors:
        response.flash = 'Errors found in the form.'
    else:
        response.flash = 'Please fill the form.'

    db.close()
    return dict(form = form, takeTitle = takeTitle)

def topicFeed():
    response.view = "takes/topicFeed.html"
    response.title = "Topic Feed"
    topicId = request.vars.topicId
    if not(utilityFunctions.checkIfVariableIsInt(takeId)):
        topicId = None
    return dict()
