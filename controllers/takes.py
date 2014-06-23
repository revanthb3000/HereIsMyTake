"""
This is the takes.py controller and contains all controller functions related to the 'take' pages.
"""
from datetime import timedelta

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
import datetime

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
    topicsList = databaseQueries.getGlobalTopicsList(db)
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
    db = databaseQueries.getDBHandler(userId)
    
    if not(utilityFunctions.isTakeIdValid(takeId)):
        redirect(URL('default','index'))

    if(not(databaseQueries.checkIfUserTakePairExists(db, userId, takeId))):
        redirect(URL('default','index'))

    db.takes.takeTitle.default = db.takes[takeId].takeTitle
    db.takes.takeContent.default = db.takes[takeId].takeContent

    topicMappings = databaseQueries.getTopicMappings(db, takeId)
    topicsList = databaseQueries.getGlobalTopicsList(db)
    numOfTopics = len(topicsList)

    fields = []
    for i in range(1, numOfTopics):
        topicMapping = topicsList[i]
        fields += [Field(str(topicMapping["topicName"]),'boolean', label=topicMapping["topicName"], default = (i in topicMappings))]

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

    takeId = request.vars.takeId
    if not(utilityFunctions.isTakeIdValid(takeId)):
        redirect(URL('default','index'))

    userId = (auth.user.id) if (auth.is_logged_in()) else 0
    db = databaseQueries.getDBHandler(userId)

    row = databaseQueries.getTakeInfo(db, takeId)
    authorUserId = row.userId
    numberOfLikes = databaseQueries.getNumberOfLikes(db, takeId, "Take")
    isTakeLiked = databaseQueries.hasUserLikedArticle(db, takeId, "Take", userId)

    response.title = row.takeTitle
    response.subtitle = "Posted on " + str(row.timeOfTake)

    fields = [Field("commentContent","text")]
    form = SQLFORM.factory(*fields, labels = {"commentContent":""}, submit_button = "Comment")

    if form.process().accepted:
        redirect(URL('takes','postComment',vars=dict(takeId = takeId, commentContent = form.vars.commentContent)))
    elif form.errors:
        response.flash = 'Errors found in the form.'

    commentRows = databaseQueries.getTakeComments(db, takeId)
    isCommentLiked = []
    commentLikeCount = []
    for commentRow in commentRows:
        commentId = commentRow.comments.id
        isCommentLiked.append(databaseQueries.hasUserLikedArticle(db, commentId, "Comment", userId))
        commentLikeCount.append(databaseQueries.getNumberOfLikes(db, commentId, "Comment"))

    editLink = ""
    deleteLink = ""
    if(databaseQueries.checkIfUserTakePairExists(db, userId , takeId)):
        editLink = URL('takes','editTake',vars=dict(takeId = takeId))
        deleteLink = URL('takes','deleteTake',vars=dict(takeId = takeId))

    textarea = form.element('textarea')
    textarea['_cols'] = 1000
    textarea['_rows'] = 2
    
    
    isFollowing = databaseQueries.checkIfFollowing(db,authorUserId,userId)
    profilePicLink = databaseQueries.getUserProfilePicture(db, authorUserId, None)
    
    return dict(takeId = takeId, takeContent = row.takeContent, numberOfLikes = numberOfLikes,
                editLink = editLink, deleteLink = deleteLink, isTakeLiked = isTakeLiked,
                form = form, comments = commentRows, isCommentLiked = isCommentLiked, 
                commentLikeCount = commentLikeCount, profilePicLink = profilePicLink, authorUserId = authorUserId)

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
    if not(utilityFunctions.isTakeIdValid(takeId)):
        redirect(URL('default','index'))

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
The comment controller. Adds a comment and then sends you back to the page you belong to.
"""
@auth.requires_login()
def postComment():
    userId = auth.user.id
    db = databaseQueries.getDBHandler(userId)

    takeId = request.vars.takeId
    commentContent = request.vars.commentContent
    if((commentContent == None) or (commentContent.strip()=="") or (not(utilityFunctions.isTakeIdValid(takeId)))):
        redirect(URL('default','index'))

    databaseQueries.addComment(db, takeId, request.vars.commentContent)
    redirect(URL('takes','viewTake',vars=dict(takeId = takeId)))
    return dict()

"""
This controller lets you delete a comment.
"""
@auth.requires_login()
def deleteComment():
    userId = auth.user.id
    db = databaseQueries.getDBHandler(userId)

    commentId = request.vars.commentId
    takeId = request.vars.takeId

    if not(utilityFunctions.isTakeIdValid(takeId)):
        redirect(URL('default','index'))

    if not(utilityFunctions.checkIfVariableIsInt(commentId)):
        commentId = 0

    if not(databaseQueries.checkIfUserCommentPairExists(db, userId, commentId)):
        redirect(URL('default','index'))

    databaseQueries.deleteComment(db, commentId)
    redirect(URL('takes','viewTake',vars=dict(takeId = takeId)))
    return dict()

"""
This is the controller that lets you like/unlike an article.
If you call this function when an article is already liked, its unliked.
If you call it when the user hasn't liked the article, its liked.
"""
@auth.requires_login()
def changeLikeStatus():
    userId = auth.user.id
    db = databaseQueries.getDBHandler(userId)
    articleType = request.vars.articleType
    articleId = request.vars.articleId

    if (not(utilityFunctions.checkIfVariableIsInt(articleId))):
        redirect(URL('default','index'))

    if not(databaseQueries.checkIfArticleExists(db, articleId, articleType)):
        redirect(URL('default','index'))

    if(databaseQueries.hasUserLikedArticle(db, articleId, articleType, userId)) :
        databaseQueries.unlike(db, articleId, articleType, userId)
    else:
        databaseQueries.like(db, articleId, articleType)

    takeId = articleId
    if(articleType=="Comment"):
        row = databaseQueries.getComment(db, articleId)
        takeId = row.takeId

    redirect(URL('takes','viewTake',vars=dict(takeId = takeId)))
    return dict()


"""
The topic feed control. Given a topicId, this will give you the list of takes in paginated form.
"""
def topicFeed():
    response.view = "takes/feed.html"
    response.title = "Topic Feed"
    
    topicId = request.vars.topicId
    userId = (auth.user.id) if (auth.is_logged_in()) else 0
    db = databaseQueries.getDBHandler(userId)


    if not(utilityFunctions.checkIfVariableIsInt(topicId)):
        redirect(URL('default','index'))

    pageNumber = 0
    if((request.vars.page!=None) and utilityFunctions.checkIfVariableIsInt(request.vars.page)):
        pageNumber = int(request.vars.page)

    items_per_page=10
    rangeLowerLimit = pageNumber*items_per_page
    rangeUpperLimit = (pageNumber+1)*items_per_page+1

    nextUrl = URL('takes','topicFeed',vars=dict(topicId = topicId, page = pageNumber + 1))
    previousUrl = URL('takes','topicFeed',vars=dict(topicId = topicId, page = pageNumber - 1))
    
    #Example of getting articles in the last week
    toDate = datetime.datetime.now()
    fromDate = datetime.datetime.now() - datetime.timedelta(days=50)
    rows = databaseQueries.getTopicTakes(db, topicId,fromDate, toDate, rangeLowerLimit, rangeUpperLimit)

    return dict(rows=rows,page=pageNumber,items_per_page=items_per_page, nextUrl=nextUrl, previousUrl=previousUrl)


"""
This covers everything ! All takes. No topics.
"""
def generalFeed():
    response.view = "takes/feed.html"
    response.title = "Take Feed"

    userId = (auth.user.id) if (auth.is_logged_in()) else 0
    db = databaseQueries.getDBHandler(userId)

    pageNumber = 0
    if((request.vars.page!=None) and utilityFunctions.checkIfVariableIsInt(request.vars.page)):
        pageNumber = int(request.vars.page)

    items_per_page=10
    rangeLowerLimit = pageNumber*items_per_page
    rangeUpperLimit = (pageNumber+1)*items_per_page+1

    nextUrl = URL('takes','generalFeed',vars=dict(page = pageNumber + 1))
    previousUrl = URL('takes','generalFeed',vars=dict(page = pageNumber - 1))
    
    #Example of getting articles in the last week
    toDate = datetime.datetime.now()
    fromDate = datetime.datetime.now() - datetime.timedelta(days=30)
    rows = databaseQueries.getAllTakes(db, fromDate, toDate, rangeLowerLimit, rangeUpperLimit)

    return dict(rows=rows,page=pageNumber,items_per_page=items_per_page, nextUrl=nextUrl, previousUrl=previousUrl)

"""
This is the subscription feed where you get the takes posted by the users you follow.
"""
@auth.requires_login()
def subscriptionFeed():
    response.view = "takes/feed.html"
    response.title = "Subscription Feed"

    userId = (auth.user.id) if (auth.is_logged_in()) else 0
    db = databaseQueries.getDBHandler(userId)
    userIdList = databaseQueries.getFollowedUsers(db, userId)

    pageNumber = 0
    if((request.vars.page!=None) and utilityFunctions.checkIfVariableIsInt(request.vars.page)):
        pageNumber = int(request.vars.page)

    items_per_page=10
    rangeLowerLimit = pageNumber*items_per_page
    rangeUpperLimit = (pageNumber+1)*items_per_page+1

    nextUrl = URL('takes','subscriptionFeed',vars=dict(page = pageNumber + 1))
    previousUrl = URL('takes','subscriptionFeed',vars=dict(page = pageNumber - 1))
    
    #Example of getting articles in the last week
    toDate = datetime.datetime.now()
    fromDate = datetime.datetime.now() - datetime.timedelta(days=30)
    rows = databaseQueries.getUserTakes(db, userIdList, fromDate, toDate, rangeLowerLimit, rangeUpperLimit)
    return dict(rows=rows,page=pageNumber,items_per_page=items_per_page, nextUrl=nextUrl, previousUrl=previousUrl)    

def echo():
    print request.vars
    userId = auth.user.id
    db = databaseQueries.getDBHandler(userId)
    print databaseQueries.getTopicTakesLikeSorted(db, 1, 0, 10)
    print databaseQueries.getUserTakesLikeSorted(db, [2], 0, 20)
    return request.vars.name

@auth.requires_login()
def tiles():
    redirect(URL('takes','generalFeed'))
    return dict()