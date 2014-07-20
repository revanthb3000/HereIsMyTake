"""
This is the ajax.py controller that's contains controllers used to perform backgroun functions (like generating html code) used by ajax functions.
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
import datetime

global items_per_page
items_per_page=10

"""
This is the controller that lets you like/unlike an article.
If you call this function when an article is already liked, its unliked.
If you call it when the user hasn't liked the article, its liked.
"""
@auth.requires_login()
def changeLikeStatus():
    userId = auth.user.id
    articleType = request.vars.articleType
    articleId = request.vars.articleId

    if (not(utilityFunctions.checkIfVariableIsInt(articleId))):
        return "Invalid"

    if not(databaseQueries.checkIfArticleExists(db, articleId, articleType)):
        return "Invalid"

    if(databaseQueries.hasUserLikedArticle(db, articleId, articleType, userId)) :
        databaseQueries.unlike(db, articleId, articleType, userId)
    else:
        databaseQueries.like(db, articleId, articleType)

    return databaseQueries.getNumberOfLikes(db, articleId, articleType)


@auth.requires_login()
def changeFollowStatus():
    if(request.vars.userId==None):
        return "Invalid"
        
    userId = request.vars.userId
    followerId = auth.user.id
    if (databaseQueries.checkIfUserExists(db,userId)):
        if(databaseQueries.checkIfFollowing(db, userId, followerId)):
            databaseQueries.removeFollowRelation(db, userId, followerId)
        else:
            databaseQueries.addFollowRelation(db, userId, followerId)
        numberOfFollowers = databaseQueries.getNumberOfFollowers(db, userId)
        returnString = str(numberOfFollowers) + " Follower" + ("s" if (numberOfFollowers!=1) else "")
        return returnString
    return "Invalid"


"""
This is used for the tags suggestions. This function will return the tag suggestions for a prefix string.
"""
def autoComplete():
    term = request.vars.term
    tags = databaseQueries.getTagSuggestions(db, term, 20)
    jsonOutput = "["
    for row in tags:
        jsonOutput += "{"
        jsonOutput += '"id": "' + row.tagName + '",'
        jsonOutput += '"label": "' + row.tagName + '",'
        jsonOutput += '"value": "' + row.tagName + '"'
        jsonOutput += "},"
    jsonOutput = jsonOutput + "]"
    jsonOutput = jsonOutput.replace(",]", "]")
    return jsonOutput

"""
This is used for the endless scroll part. You send args to this bad boy and he will tell you what to load.
"""
def getNewTakes():
    feedType = int(request.vars.feedType)
    sortParameter = str(request.vars.sortParameter)
    pageNumber = int(request.vars.pageNumber)
    topicId = int(request.vars.topicId)
    tagId = int(request.vars.tagId)
    
    ignoredTakesList = []
    ignoredTakesListStr = request.vars.ignoredTakesList
    if(ignoredTakesListStr != None):
        for element in ignoredTakesListStr:
            ignoredTakesList.append(int(element))
    
    ignoredUserList = []
    ignoredUserListStr = request.vars.ignoredUserList
    if(ignoredUserListStr != None):
        for element in ignoredUserListStr:
            ignoredUserList.append(int(element))
    
    userIdList = []
    userIdListStr = request.vars.userIdList
    if(userIdListStr != None):
        for element in userIdListStr:
            userIdList.append(int(element))

    toDate = datetime.datetime.now()
    fromDate = datetime.datetime.now() - datetime.timedelta(weeks=50*52)
    rangeLowerLimit = pageNumber*items_per_page + 1
    rangeUpperLimit = (pageNumber+1)*items_per_page
    
    """    
    print feedType
    print sortParameter
    print pageNumber
    print topicId
    print tagId
    print ignoredTakesList
    print ignoredUserList
    print userIdList
    print rangeLowerLimit
    print rangeUpperLimit
    print toDate
    print fromDate
    print utilityFunctions.getRequiredTakes(feedType, sortParameter, db, fromDate, toDate, rangeLowerLimit, rangeUpperLimit, ignoredTakesList, ignoredUserList, topicId, tagId, userIdList)
    """
    
    htmlCode = utilityFunctions.getRequiredTakesHTML(feedType, sortParameter, db, fromDate, toDate, rangeLowerLimit, rangeUpperLimit, 
                                                     ignoredTakesList, ignoredUserList, topicId, tagId, userIdList)
    return htmlCode

"""
Given a tileId, this function will generate code for all that tile's children.
"""
def getTilesCodeByParentId():
    parentId = int(request.vars.parentId)
    topics = databaseQueries.getSubTopics(db, parentId)
    topicsList = []
    for topic in topics:
        topicsList.append(topic.id)
    expandableTopics = databaseQueries.getExpandableTopics(db, topicsList)
    grandParentId = databaseQueries.getTopicParent(db, parentId)
    htmlCode = utilityFunctions.getRequiredTilesHtmlCode(parentId, topics, expandableTopics, grandParentId)
    return htmlCode

"""
Given a prefix string, the tiles matching that prefix are returned.
"""
def getTilesCodeByPrefix():
    prefix = str(request.vars.prefix)
    topics = databaseQueries.getTopicSuggestions(db, prefix, 12)
    htmlCode = utilityFunctions.getPrefixTilesHtmlCode(topics)
    if (htmlCode == "<table></table>\n"):
        htmlCode = "<p><i><b>No Results Found</b></i></p>"
    return htmlCode
