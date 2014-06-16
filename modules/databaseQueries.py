"""
This module will contain all DB functions starting from creating a DB handler to applying every single function.
"""

from gluon import *
import databaseConnectionStrings
import datetime

"""
This function generates a db handler and returns it to you. Remember that it is your responsibility to close the db handle once you're done using it.
Important point is to send None as the userId in case you're calling this function in a page where the user need not be logged in.

Here's a snippet that can be used :

userId = (auth.user.id) if (auth.is_logged_in()) else 0
db = databaseQueries.getDBHandler(userId)

"""
def getDBHandler(userId):
    db = DAL(databaseConnectionStrings.connectionString, migrate=False)

    if(userId==None):
        userId = 0

    #Add all define_table statements in here.
    db.define_table("auth_user",
                        Field("id","integer"), Field("first_name", "string", requires=IS_NOT_EMPTY()),
                        Field("last_name", "string", requires=IS_NOT_EMPTY()),Field("email", "string", requires=IS_NOT_EMPTY()),
                        Field('Education','string'), Field('Occupation','string'), Field('Birthday','date'),
                        Field('AboutMe','text'), Field('Gender','string',requires = IS_IN_SET(['Male', 'Female', 'Other'])),
                        Field('displayPicture', 'upload' ),Field('Website','string')
                    )

    db.define_table("topics",
                        Field("id","integer"), Field("topicName","string"), Field("parentId","integer")
                    )

    db.define_table("takes",
                        Field("id","integer"), Field("takeTitle","string"), Field("takeContent","text"),
                        Field("userId","integer",writable = False, readable = False, default=userId),
                        Field("timeOfTake","datetime",writable = False,readable = False)
                    )

    db.define_table("take_topic_mapping",
                        Field("id","integer"), Field("takeId","integer"), Field("topicId","integer")
                    )

    db.define_table("followRelations",
                        Field("id","integer"), Field("userId","integer"), Field("followerId","integer")
                    )

    db.define_table("comments",
                        Field("id","integer"), Field("userId","integer",default=userId),
                        Field("takeId","integer"), Field("commentContent","text"),
                        Field("timeOfComment","datetime",writable = False,readable = False)
                    )

    db.define_table("likes",
                        Field("id","integer"), Field("articleId","integer"),
                        Field("userId","integer",default=userId),
                        Field("articleType",'string',requires = IS_IN_SET(['Take', 'Comment'])),
                        Field("timeOfLike","datetime",writable = False,readable = False)
                    )
    return db


"""
Given a userId, this function will tell you if that user actually exists.
"""
def checkIfUserExists(db, userId):
    rows = db(db.auth_user.id == userId).select()
    if len(rows) == 1:
        return True
    return False


"""
Given a <userId, followerId> tuple this function will return true if followerId follows userId.
False, otherwise.
"""
def checkIfFollowing(db,userId,followerId):
    rows = db((db.followRelations.userId==userId) & (db.followRelations.followerId==followerId)).select()
    if len(rows) == 1:
        return True
    return False


"""
Given a <userId, takeId> pair, this function returns true if userId is the author of takeId
"""
def checkIfUserTakePairExists(db, userId, takeId):
    rows = db((db.takes.userId==userId) & (db.takes.id==takeId)).select()
    if len(rows) == 1:
        return True
    return False


"""
Given a topicId, this function will tell you if a topic actually exists.
"""
def checkIfTopicExists(db, topicId):
    rows = db(db.topics.id == userId).select()
    if len(rows) == 1:
        return True
    return False


"""
Basic function that gets the list of topics. Useful when classifying a take.
The list returned, contains objects of the form:
Dictionary : {"topicName": "Anime", "parentId": 5}
"""
def getListOfTopics(db):
    rows = db(db.topics).select()
    #TopicName, parentId tuple. I'll be able to get topicId from the list index.
    topicMapping = {}
    topicMapping["topicName"] = "None"
    topicMapping["parentId"] = 0

    topicsList = []
    topicsList.append(topicMapping)
    for row in rows:
        topicMapping = {}
        topicMapping["topicName"] = str(row.topicName)
        topicMapping["parentId"] = int(row.parentId)
        topicsList.append(topicMapping)
    return topicsList


"""
Given a takeId, this guy returns all the topics that have been tagged to it.
"""
def getTakeTopicsList(db, takeId):
    rows = db(db.take_topic_mapping.takeId==takeId).select()
    topics = []
    for row in rows:
        topics.append(row.topicId)
    return topics


"""
Given a takeId, this function gets rid of everything related to that take.
Delete the following:
1) Take info from the takes table.
2) Take topic mapping from the take_topic_mapping table.
"""
def deleteTake(db, takeId):
    db(db.takes.id==takeId).delete()
    db(db.take_topic_mapping.takeId==takeId).delete()


"""
Given a topicId, this function will return all takes that fall under that category
"""
def getTopicTakes(db, topicId, rangeLowerLimit, rangeUpperLimit):
    limitby=(rangeLowerLimit,rangeUpperLimit)
    rows = db((db.take_topic_mapping.takeId==db.takes.id) & (db.take_topic_mapping.topicId == topicId)).select(limitby = limitby)
    return rows


"""
This function adds a <takeId, topicId> pair into the database
"""
def addTakeTopicMapping(db, takeId, topicId):
    db.take_topic_mapping.insert(takeId = takeId, topicId = topicId)


"""
This function removes a <takeId, topicId> pair present in the database
"""
def removeTakeTopicMapping(db, takeId, topicId):
    db((db.take_topic_mapping.takeId==takeId) & (db.take_topic_mapping.topicId==topicId)).delete()


"""
This function lets you either add a new take to the takes table.
"""
def addTake(db, takeTitle, takeContent):
    takeId = db.takes.insert(takeTitle = takeTitle, takeContent = takeContent)
    return takeId


"""
This function allows you to update the existing db record
"""
def updateTake(db, newTakeTitle, newTakeContent, takeId):
    row = db(db.takes.id==takeId).select().first()
    row.takeContent = newTakeContent
    row.takeTitle = newTakeTitle
    row.update_record()


"""
This function gets information of the take represented by takeId
"""
def getTakeInfo(db, takeId):
    row = None
    rows = db(db.takes.id == takeId).select()
    if len(rows) == 1:
        row = rows[0]
    return row

"""
This function adds a comment to the comments table.
"""
def addComment(db, takeId, commentContent):
    commentId = db.comments.insert(takeId = takeId, commentContent = commentContent)
    return commentId

"""
Given a commentId, this function returns the comment contents of the table.
"""
def getComment(db, commentId):
    row = None
    rows = db(db.comments.id == commentId).select()
    if len(rows) == 1:
        row = rows[0]
    return row

"""
Given a takeId, this function will return all the comments made on a take.
"""
def getTakeComments(db, takeId):
    limitby=(0,5000)
    rows = db((db.comments.userId==db.auth_user.id) & (db.comments.takeId == takeId)).select(limitby = limitby, orderby=db.comments.timeOfComment)
    return rows

"""
Given a <userId, commentId> pair, this function returns true if userId is the author of commentId
"""
def checkIfUserCommentPairExists(db, userId, commentId):
    rows = db((db.comments.userId==userId) & (db.comments.id==commentId)).select()
    if len(rows) == 1:
        return True
    return False

"""
Given a commentId, this function deletes the comment from the table.
"""
def deleteComment(db, commentId):
    db(db.comments.id==commentId).delete()

"""
Given an articleId and articleType, an entry is made in the DB.
"""
def like(db, articleId, articleType):
    likeId = db.likes.insert(articleId = articleId, articleType = articleType)
    return likeId

"""
Given the information about a like, this function will remove the entry from the table.
"""
def unlike(db, articleId, articleType, userId):
    db((db.likes.articleId==articleId) & (db.likes.articleType==articleType) & (db.likes.userId==userId)).delete()

"""
Given an article's info, this function returns the number of likes.
"""
def getNumberOfLikes(db, articleId, articleType):
    rows = db((db.likes.articleId==articleId) & (db.likes.articleType == articleType)).select()
    return len(rows)

"""
Given a userId and articleId, this function will tell you if that user has liked the article.
"""
def hasUserLikedArticle(db, articleId, articleType, userId):
    rows = db((db.likes.userId==userId) & (db.likes.articleId==articleId) & (db.likes.articleType==articleType)).select()
    if len(rows) == 1:
        return True
    return False

"""
This function returns true if the given take/comment actually exists.
"""
def checkIfArticleExists(db, articleId, articleType):
    if(articleType==None):
        return False

    if((articleType=="Take") & (getTakeInfo(db, articleId)!=None)):
        return True
    elif((articleType=="Comment") & (getComment(db, articleId)!=None)):
        return True

    return False
