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

global items_per_page
items_per_page=10

def index():
    redirect(URL('default','index'))
    return dict()

def echo():
    response.view = "test.html"
    return dict()

"""
This is the control function to submit takes. 
A rich text editor is provided and you get to select tags and submit the take content.
"""
@auth.requires_login()
def submitTake():
    response.view = "takes/submitTake.html"
    response.title = "Submit Take"

    topicsList = databaseQueries.getGlobalTopicsList(db)
    numOfTopics = len(topicsList)

    fields = []
    options = []

    for i in range(1, numOfTopics):
        topicMapping = topicsList[i]
        options += [topicMapping["topicName"]]

    fields += [Field('topics','string')]
    fields += [Field('takeTags','string')]
    fields += [field for field in db.takes]
    form = SQLFORM.factory(*fields, _id = "tagform-full")
    
    if form.process().accepted:
        selectedTopics = form.vars.topics
        selectedTags = form.vars.takeTags
        takeId = databaseQueries.addTake(db, form.vars.takeTitle, form.vars.takeContent)
        for i in range(1, numOfTopics):
            topicMapping = topicsList[i]
            if(topicMapping["topicName"] in selectedTopics):
                databaseQueries.addTakeTopicMapping(db, takeId, i)

        for tag in selectedTags.split(","):
            tagId = databaseQueries.getTagId(db, tag)
            if(tagId == 0):
                tagId = databaseQueries.insertTag(db, tag)
            databaseQueries.addTakeTagMapping(db, takeId, tagId)
            
            
        redirect(URL('takes','viewTake',vars=dict(takeId = takeId)))
    elif form.errors:
        response.flash = 'Errors found in the form.'
    else:
        response.flash = 'Please fill the form.'

    return dict(form=form, options = options, preSelectedTopics = [], existingTags = "")

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

    if not(utilityFunctions.isTakeIdValid(takeId,db)):
        redirect(URL('default','index'))

    if(not(databaseQueries.checkIfUserTakePairExists(db, userId, takeId))):
        redirect(URL('default','index'))

    takeTopicMappings = databaseQueries.getTopicMappings(db, takeId)
    preSelectedTopics = []
    topicsList = databaseQueries.getGlobalTopicsList(db)
    numOfTopics = len(topicsList)
    
    preSelectedTags = databaseQueries.getTakeTags(db, takeId)
    existingTags = ""
    for row in preSelectedTags:
        existingTags = existingTags + row.tags.tagName + ", "
    existingTags = existingTags + "end[]"
    existingTags = existingTags.replace(", end[]","")

    fields = []
    options = []

    for i in range(1, numOfTopics):
        topicMapping = topicsList[i]
        options += [topicMapping["topicName"]]
        if(i in takeTopicMappings):
            preSelectedTopics += [topicMapping["topicName"]]

    fields += [Field('topics','string')]
    fields += [Field('takeTags','string')]
    fields += [field for field in db.takes]
    form = SQLFORM.factory(*fields)

    takeInfo = databaseQueries.getTakeInfo(db, takeId)
    form.vars.takeTitle = takeInfo.takeTitle
    form.vars.takeContent = takeInfo.takeContent
    form.vars.topics = ['Entertainment', 'Technology', 'Friendship']

    if form.process().accepted:
        databaseQueries.updateTake(db, form.vars.takeTitle, form.vars.takeContent, takeId)
        selectedTopics = form.vars.topics
        selectedTags = form.vars.takeTags
        for i in range(1, numOfTopics):
            topicMapping = topicsList[i]
            if(topicMapping["topicName"] in selectedTopics):
                databaseQueries.addTakeTopicMapping(db, takeId, i)
            else:
                databaseQueries.removeTakeTopicMapping(db, takeId, i)

        databaseQueries.removeTakeTags(db, takeId)
        for tag in selectedTags.split(","):
            tagId = databaseQueries.getTagId(db, tag)
            if(tagId == 0):
                tagId = databaseQueries.insertTag(db, tag)
            databaseQueries.addTakeTagMapping(db, takeId, tagId)

        redirect(URL('takes','viewTake',vars=dict(takeId = request.vars.takeId)))
    elif form.errors:
        response.flash = 'Errors found in the form.'
    else:
        response.flash = 'Please fill the form.'

    return dict(form=form, options = options, preSelectedTopics = preSelectedTopics, existingTags = existingTags)

"""
This is the control function for the view take activity.
Basically, you retrieve data from the takes table and send it to the view.
"""
def viewTake():
    response.view = 'takes/viewTake.html'

    takeId = request.vars.takeId
    if not(utilityFunctions.isTakeIdValid(takeId,db)):
        redirect(URL('default','index'))

    userId = (auth.user.id) if (auth.is_logged_in()) else 0

    preSelectedTags = databaseQueries.getTakeTags(db, takeId)
    existingTags = ""
    for row in preSelectedTags:
        existingTags = existingTags + "<a href='" + URL('takes','tagFeed',vars=dict(tagId = row.tags.id)) + "'>" + row.tags.tagName + "</a>, "
    existingTags = existingTags + "end[]"
    existingTags = existingTags.replace(", end[]",".")

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
    
    authorNumberOfFollowers = databaseQueries.getNumberOfFollowers(db, authorUserId)
    authorName = databaseQueries.getUserName(db, authorUserId)
    profilePicLink = databaseQueries.getUserProfilePicture(db, authorUserId, None)

    return dict(takeId = takeId, takeContent = row.takeContent, numberOfLikes = numberOfLikes,
                editLink = editLink, deleteLink = deleteLink, isTakeLiked = isTakeLiked,
                form = form, comments = commentRows, isCommentLiked = isCommentLiked, existingTags = existingTags,
                commentLikeCount = commentLikeCount, profilePicLink = profilePicLink, authorUserId = authorUserId,
                authorNumberOfFollowers = authorNumberOfFollowers, authorName = authorName)

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
    if not(utilityFunctions.isTakeIdValid(takeId,db)):
        redirect(URL('default','index'))

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
This covers everything ! All takes. No topics.
"""
def generalFeed():
    response.view = "takes/feed.html"
    response.title = "Take Feed"
    
    sortParameter = "Date"
    if(request.vars.sortParameter!=None):
        sortParameter = request.vars.sortParameter

    pageNumber = 0
    rangeLowerLimit = pageNumber*items_per_page
    rangeUpperLimit = (pageNumber+1)*items_per_page

    alternateSortURL = ""
    
    toDate = datetime.datetime.now()
    fromDate = datetime.datetime.now() - datetime.timedelta(weeks=50*52)
    
    topicId = 0
    tagId = 0
    ignoredTakesList = []
    ignoredUserList = []
    userIdList = []
    feedCode = utilityFunctions.getRequiredTakesHTML(1, sortParameter, db, fromDate, toDate, rangeLowerLimit, rangeUpperLimit, 
                                                         ignoredTakesList, ignoredUserList, topicId, tagId, userIdList)
    
    loadContentLink = URL('ajax','getNewTakes', vars=dict(feedType = 1, sortParameter = sortParameter, pageNumber = "replaceMEPageNumber", 
                                                          ignoredTakesList = ignoredTakesList, ignoredUserList = ignoredUserList, topicId = topicId,
                                                          tagId = tagId, userIdList = userIdList))
    if(sortParameter!="Date"):
        alternateSortURL = URL('takes','generalFeed',vars=dict(sortParameter = "Date"))
    else:
        alternateSortURL = URL('takes','generalFeed',vars=dict(sortParameter = "Like"))

    return dict(feedCode = feedCode, alternateSortURL = alternateSortURL, loadContentLink = loadContentLink)


"""
The topic feed control. Given a topicId, this will give you the list of takes in paginated form.
"""
def topicFeed():
    response.view = "takes/feed.html"
    response.title = "Topic Feed"
    
    topicId = request.vars.topicId

    sortParameter = "Date"
    if(request.vars.sortParameter!=None):
        sortParameter = request.vars.sortParameter

    if not(utilityFunctions.checkIfVariableIsInt(topicId)):
        redirect(URL('default','index'))
        
    topicName = databaseQueries.getTopicName(db, topicId)
    if(topicName==None):
        redirect(URL('default','index'))

    response.title = topicName + " Feed"

    pageNumber = 0
    rangeLowerLimit = pageNumber*items_per_page
    rangeUpperLimit = (pageNumber+1)*items_per_page

    alternateSortURL = ""

    toDate = datetime.datetime.now()
    fromDate = datetime.datetime.now() - datetime.timedelta(weeks=50*52)
    
    tagId = 0
    ignoredTakesList = []
    ignoredUserList = []
    userIdList = []
    feedCode = utilityFunctions.getRequiredTakesHTML(2, sortParameter, db, fromDate, toDate, rangeLowerLimit, rangeUpperLimit, 
                                                         ignoredTakesList, ignoredUserList, topicId, tagId, userIdList)
    
    loadContentLink = URL('ajax','getNewTakes', vars=dict(feedType = 2, sortParameter = sortParameter, pageNumber = "replaceMEPageNumber", 
                                                          ignoredTakesList = ignoredTakesList, ignoredUserList = ignoredUserList, topicId = topicId,
                                                          tagId = tagId, userIdList = userIdList))
    if(sortParameter!="Date"):
        alternateSortURL = URL('takes','topicFeed',vars=dict(topicId = topicId, sortParameter = "Date"))
    else:
        alternateSortURL = URL('takes','topicFeed',vars=dict(topicId = topicId, sortParameter = "Like"))

    return dict(feedCode=feedCode, alternateSortURL=alternateSortURL, loadContentLink = loadContentLink)
    
"""
The tag feed control. Given a tagId, this will give you the list of takes in paginated form.
"""
def tagFeed():
    response.view = "takes/feed.html"
    response.title = "Tag Feed"
    
    tagId = request.vars.tagId

    sortParameter = "Date"
    
    if(request.vars.sortParameter!=None):
        sortParameter = request.vars.sortParameter

    if not(utilityFunctions.checkIfVariableIsInt(tagId)):
        redirect(URL('default','index'))
    
    tagName = databaseQueries.getTagName(db, tagId)
    if(tagName==None):
        redirect(URL('default','index'))

    response.title = tagName + " Feed"

    pageNumber = 0
    rangeLowerLimit = pageNumber*items_per_page
    rangeUpperLimit = (pageNumber+1)*items_per_page

    alternateSortURL = ""

    toDate = datetime.datetime.now()
    fromDate = datetime.datetime.now() - datetime.timedelta(weeks=50*52)
    
    topicId = 0
    ignoredTakesList = []
    ignoredUserList = []
    userIdList = []
    feedCode = utilityFunctions.getRequiredTakesHTML(3, sortParameter, db, fromDate, toDate, rangeLowerLimit, rangeUpperLimit, 
                                                         ignoredTakesList, ignoredUserList, topicId, tagId, userIdList)
    
    loadContentLink = URL('ajax','getNewTakes', vars=dict(feedType = 3, sortParameter = sortParameter, pageNumber = "replaceMEPageNumber", 
                                                          ignoredTakesList = ignoredTakesList, ignoredUserList = ignoredUserList, topicId = topicId,
                                                          tagId = tagId, userIdList = userIdList))
    
    if(sortParameter!="Date"):
        alternateSortURL = URL('takes','tagFeed',vars=dict(tagId = tagId, sortParameter = "Date"))
    else:
        alternateSortURL = URL('takes','tagFeed',vars=dict(tagId = tagId, sortParameter = "Like"))

    return dict(feedCode=feedCode, alternateSortURL=alternateSortURL, loadContentLink = loadContentLink)

"""
This is the subscription feed where you get the takes posted by the users you follow.
"""
@auth.requires_login()
def subscriptionFeed():
    response.view = "takes/feed.html"
    response.title = "Subscription Feed"

    userId = (auth.user.id) if (auth.is_logged_in()) else 0

    userIdList = databaseQueries.getFollowedUsers(db, userId)

    sortParameter = "Date"
    if(request.vars.sortParameter!=None):
        sortParameter = request.vars.sortParameter

    pageNumber = 0
    rangeLowerLimit = pageNumber*items_per_page
    rangeUpperLimit = (pageNumber+1)*items_per_page

    alternateSortURL = ""

    toDate = datetime.datetime.now()
    fromDate = datetime.datetime.now() - datetime.timedelta(weeks=50*52)
    
    topicId = 0
    tagId = 0
    ignoredTakesList = []
    ignoredUserList = []
    feedCode = utilityFunctions.getRequiredTakesHTML(4, sortParameter, db, fromDate, toDate, rangeLowerLimit, rangeUpperLimit, 
                                                         ignoredTakesList, ignoredUserList, topicId, tagId, userIdList)
    
    loadContentLink = URL('ajax','getNewTakes', vars=dict(feedType = 4, sortParameter = sortParameter, pageNumber = "replaceMEPageNumber", 
                                                          ignoredTakesList = ignoredTakesList, ignoredUserList = ignoredUserList, topicId = topicId,
                                                          tagId = tagId, userIdList = userIdList))
    if(sortParameter!="Date"):
        alternateSortURL = URL('takes','subscriptionFeed',vars=dict(sortParameter = "Date"))
    else:
        alternateSortURL = URL('takes','subscriptionFeed',vars=dict(sortParameter = "Like"))
    
    return dict(feedCode=feedCode, alternateSortURL=alternateSortURL, loadContentLink = loadContentLink)

"""
This is the user activity feed. All the user's recent activities are retrieved and displayed over here.
"""
def userActivityFeed():
    response.view = "takes/feed.html"
    response.title = "User Activity"

    userId = request.vars.userId
    
    if(not(utilityFunctions.checkIfVariableIsInt(userId))):
        redirect(URL('default','index'))

    userIdList = [userId]

    sortParameter = "Date"
    if(request.vars.sortParameter!=None):
        sortParameter = request.vars.sortParameter

    pageNumber = 0
    rangeLowerLimit = pageNumber*items_per_page
    rangeUpperLimit = (pageNumber+1)*items_per_page

    alternateSortURL = ""

    toDate = datetime.datetime.now()
    fromDate = datetime.datetime.now() - datetime.timedelta(weeks=50*52)
    
    topicId = 0
    tagId = 0
    ignoredTakesList = []
    ignoredUserList = []
    feedCode = utilityFunctions.getRequiredTakesHTML(4, sortParameter, db, fromDate, toDate, rangeLowerLimit, rangeUpperLimit, 
                                                         ignoredTakesList, ignoredUserList, topicId, tagId, userIdList)
    
    loadContentLink = URL('ajax','getNewTakes', vars=dict(feedType = 4, sortParameter = sortParameter, pageNumber = "replaceMEPageNumber", 
                                                          ignoredTakesList = ignoredTakesList, ignoredUserList = ignoredUserList, topicId = topicId,
                                                          tagId = tagId, userIdList = userIdList))
    
    if(sortParameter!="Date"):
        alternateSortURL = URL('takes','userActivityFeed',vars=dict(userId = userId, sortParameter = "Date"))
    else:
        alternateSortURL = URL('takes','userActivityFeed',vars=dict(userId = userId, sortParameter = "Like"))

    return dict(feedCode=feedCode, alternateSortURL=alternateSortURL, loadContentLink = loadContentLink)

"""
This is the tiles page. Contains a tiles list of topics that can be expanded for another layer.
"""
def topicPage():
    parentId = 0
    topics = databaseQueries.getSubTopics(db, parentId)
    if(len(topics)==0):
        redirect(URL('default','index'))

    parentTopicName = "Home"
    topicsList = []
    for topic in topics:
        topicsList.append(topic.id)
    #topicsList.append("Subscriptions")
    expandableTopics = databaseQueries.getExpandableTopics(db, topicsList)
    if(parentId!=0):
        parentTopicName = databaseQueries.getTopicName(db, parentId)
    
    htmlCode = utilityFunctions.getRequiredTilesHtmlCode(parentId, topics, expandableTopics, 0)
    tileSearchLink = URL('ajax','getTilesCodeByPrefix',vars=dict(prefix = "THISISTHEPREFIX"))
    defaultTilesLink = URL('ajax','getTilesCodeByParentId',vars=dict(parentId = 0))
    response.view = "takes/tiles.html"
    response.title = parentTopicName
    response.ignoreHeading = True
    return dict(topics = topics, expandableTopics = expandableTopics, htmlCode = htmlCode, tileSearchLink = tileSearchLink, defaultTilesLink = defaultTilesLink)


"""
The comment controller. Adds a comment and then sends you back to the page you belong to.
"""
@auth.requires_login()
def postComment():
    takeId = request.vars.takeId
    commentContent = request.vars.commentContent
    if((commentContent == None) or (commentContent.strip()=="") or (not(utilityFunctions.isTakeIdValid(takeId,db)))):
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
    commentId = request.vars.commentId
    takeId = request.vars.takeId

    if not(utilityFunctions.isTakeIdValid(takeId,db)):
        redirect(URL('default','index'))

    if not(utilityFunctions.checkIfVariableIsInt(commentId)):
        commentId = 0

    if not(databaseQueries.checkIfUserCommentPairExists(db, userId, commentId)):
        redirect(URL('default','index'))

    databaseQueries.deleteComment(db, commentId)
    redirect(URL('takes','viewTake',vars=dict(takeId = takeId)))
    return dict()