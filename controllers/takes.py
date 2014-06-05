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

"""
This is the control function to submit takes. 
A rich text editor is provided and you get to select tags and submit the take content.
"""
@auth.requires_login()
def submitTake():
    response.view = "takes/submitTake.html"
    response.title = "Submit Take"
    db = databaseQueries.getDBHandler(auth.user.id)

    takeContent = ""
    topicsList = databaseQueries.getListOfTopics(db)
    numOfTopics = len(topicsList)

    fields = []

    for i in range(1, numOfTopics):
        topicMapping = topicsList[i]
        fields += [Field(str(topicMapping["topicName"]),'boolean', label=topicMapping["topicName"])]

    fields += [field for field in db.takes]
    form = SQLFORM.factory(*fields)

    if form.process().accepted:
        takeContent = form.vars.takeContent
        takeId = databaseQueries.addTake(db, form.vars.takeTitle, form.vars.takeContent)
        for i in range(1, numOfTopics):
            topicMapping = topicsList[i]
            if(form.vars[topicMapping["topicName"]]):
                databaseQueries.addTakeTopicMapping(db, takeId, i)

        redirect(URL('takes','viewTake',vars=dict(takeId = takeId)))
    elif form.errors:
        response.flash = 'Errors found in the form.'
    else:
        response.flash = 'Please fill the form.'

    textarea = form.element('textarea')
    textarea['_cols'] = 1000
    return dict(form=form, takeContent = takeContent)

"""
This is the control function to let a user edit a take he has previously submitted.
Can edit content, title and tags.
"""
@auth.requires_login()
def editTake():
    response.view = "takes/submitTake.html"
    response.title = "Edit Take"

    userId = auth.user.id
    takeId = request.vars.takeId
    if not(utilityFunctions.checkIfVariableIsInt(takeId)):
        takeId = 0

    db = databaseQueries.getDBHandler(userId)

    if(not(databaseQueries.checkIfUserTakePairExists(db, userId, takeId))):
        redirect(URL('default','index'))

    db.takes.takeTitle.default = db.takes[takeId].takeTitle
    db.takes.takeContent.default = db.takes[takeId].takeContent

    takeTopicsList = databaseQueries.getTakeTopicsList(db, takeId)
    topicsList = databaseQueries.getListOfTopics(db)
    numOfTopics = len(topicsList)

    fields = []
    for i in range(1, numOfTopics):
        topicMapping = topicsList[i]
        fields += [Field(str(topicMapping["topicName"]),'boolean', label=topicMapping["topicName"], default = (i in takeTopicsList))]

    fields += [field for field in db.takes]
    form = SQLFORM.factory(*fields)

    takeContent = ""
    if form.process().accepted:
        databaseQueries.updateTake(db, form.vars.takeTitle, form.vars.takeContent, takeId)
        for i in range(1, numOfTopics):
            topicMapping = topicsList[i]
            if(form.vars[topicMapping["topicName"]]):
                databaseQueries.addTakeTopicMapping(db, takeId, i)
            else:
                databaseQueries.removeTakeTopicMapping(db, takeId, i)

        redirect(URL('takes','viewTake',vars=dict(takeId = request.vars.takeId)))
    elif form.errors:
        response.flash = 'Errors found in the form.'
    else:
        response.flash = 'Please fill the form.'

    textarea = form.element('textarea')
    textarea['_cols'] = 1000
    return dict(form=form, takeContent = takeContent)

"""
This is the control function for the view take activity.
Basically, you retrieve data from the takes table and send it to the view.
"""
def viewTake():
    response.view = 'takes/viewTake.html'

    userId = (auth.user.id) if (auth.is_logged_in()) else 0
    db = databaseQueries.getDBHandler(userId)

    takeId = request.vars.takeId
    if not(utilityFunctions.checkIfVariableIsInt(takeId)):
        takeId = 0

    row = databaseQueries.getTakeInfo(db, takeId)
    if row == None:
        redirect(URL('default','index'))

    response.title = row.takeTitle
    response.subtitle = "Posted on " + str(row.timeOfTake)

    editLink = ""
    deleteLink = ""
    if(databaseQueries.checkIfUserTakePairExists(db, userId , takeId)):
        editLink = URL('takes','editTake',vars=dict(takeId = takeId))
        deleteLink = URL('takes','deleteTake',vars=dict(takeId = takeId))

    return dict(takeContent = row.takeContent, editLink = editLink, deleteLink = deleteLink)

"""
This control function is used to delete a take.
Flow is as follows:
(click delete) -> (click yes) -> eliminate from DB
"""
@auth.requires_login()
def deleteTake():
    response.view = "takes/deleteTake.html"
    response.title = "Delete Take"

    userId = auth.user.id
    takeId = request.vars.takeId
    if not(utilityFunctions.checkIfVariableIsInt(takeId)):
        takeId = 0

    db = databaseQueries.getDBHandler(userId)

    if(not(databaseQueries.checkIfUserTakePairExists(db, userId, takeId))):
        redirect(URL('default','index'))

    #No need to check if row == None. The above checkIfUserTakePairExists function does that for you !
    row = databaseQueries.getTakeInfo(db, takeId)

    form = FORM(
                    INPUT(_type='submit', _value='Yes', _name='yesDelete'),
                    INPUT(_type='submit', _value="No", _name='noDelete')
                )

    if form.process().accepted:
        if(request.vars.yesDelete):
            databaseQueries.deleteTake(db, takeId)
        redirect(URL('default','index'))
    elif form.errors:
        response.flash = 'Errors found in the form.'

    return dict(form = form, takeTitle = row.takeTitle)

"""
The topic feed control. Given a topicId, this will give you the list of takes in paginated form.
"""
@auth.requires_login()
def topicFeed():
    response.view = "takes/topicFeed.html"
    response.title = "Topic Feed"

    topicId = request.vars.topicId
    if not(utilityFunctions.checkIfVariableIsInt(topicId)):
        redirect(URL('default','index'))
    pageNumber = 0
    if((request.vars.page!=None) and utilityFunctions.checkIfVariableIsInt(request.vars.page)):
        pageNumber = int(request.vars.page)

    items_per_page=5
    rangeLowerLimit = pageNumber*items_per_page
    rangeUpperLimit = (pageNumber+1)*items_per_page+1

    nextUrl = URL('takes','topicFeed',vars=dict(topicId = topicId, page = pageNumber + 1))
    previousUrl = URL('takes','topicFeed',vars=dict(topicId = topicId, page = pageNumber - 1))

    db = databaseQueries.getDBHandler(auth.user.id)
    rows = databaseQueries.getTopicTakes(db, topicId, rangeLowerLimit, rangeUpperLimit)
    return dict(rows=rows,page=pageNumber,items_per_page=items_per_page, nextUrl=nextUrl, previousUrl=previousUrl)
