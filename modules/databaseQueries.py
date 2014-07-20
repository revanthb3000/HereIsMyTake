"""
This module will contain all DB functions starting from creating a DB handler to applying every single function.
"""

from gluon import *
import datetime

"""
Define all your tables over here. This function is called in db.py
"""
def defineDBTables(db, userId):
    if(userId==None):
        userId = 0

    #Add all define_table statements in here.
    db.define_table("topics",
                        Field("id","integer"), Field("topicName","string"), Field("parentId","integer")
                    )
    
    db.define_table("tags",
                        Field("id","integer"), Field("tagName","string")
                    )

    db.define_table("takes",
                        Field("id","integer"), Field("takeTitle","string"), Field("takeContent","text"),
                        Field("userId","integer",writable = False, readable = False, default=userId),
                        Field("timeOfTake","datetime",writable = False,readable = False)
                    )

    db.define_table("take_topic_mapping",
                        Field("id","integer"), Field("takeId","integer"), Field("topicId","integer")
                    )
    
    db.define_table("take_tags_mapping",
                        Field("id","integer"), Field("takeId","integer"), Field("tagId","integer")
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

"""
Given a userId, this function will tell you if that user actually exists.
"""
def checkIfUserExists(db, userId):
    rows = db(db.auth_user.id == userId).select()
    if len(rows) == 1:
        return True
    return False

"""
Given a userId, this function will return the user's full name.
"""
def getUserName(db, userId):
    fullName = ""
    rows = db(db.auth_user.id == userId).select()
    if len(rows) == 1:
        row = rows[0]
        fullName = row.first_name + " " + row.last_name
    return fullName

"""
Given a userId, this function will return all the details of that user.
"""
def getUserInfo(db, userId):
    rows = db(db.auth_user.id == userId).select()
    row = None
    if len(rows) == 1:
        row = rows[0]
    return row

"""
Given information, the user's info is updated !
"""
def updateUserInfo(db, userId, Location, Occupation, Website, AboutMe, displayPicture):
    row = db(db.auth_user.id==userId).select().first()
    row.Location = Location
    row.Occupation = Occupation
    row.Website = Website
    row.AboutMe = AboutMe
    if(displayPicture.strip()!=""):
        row.displayPicture = displayPicture
    row.update_record()

"""
Given a userId, this function will return the user's profile picture link
"""
def getUserProfilePicture(db, userId, displayPicture):
    fileName = "images/displayPictures/defaultMale.png"
    if (displayPicture!=None and displayPicture.strip()!=""):
        fileName = displayPicture

    if(displayPicture == None):
        rows = db(db.auth_user.id == userId).select()
        link =""
        row = None
        if len(rows) == 1:
            row = rows[0]
            if (row.displayPicture!=None and row.displayPicture.strip()!=""):
                fileName = row.displayPicture

    if("defaultMale.png" in fileName):
        link = URL('static', fileName)
    else:
        link = URL("default","download/" + fileName)
    return link

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
Given a <userId, followerId> input, an entry is inserted into the DB (if it doesn't already exist)
"""
def addFollowRelation(db,userId, followerId):
    if (not(checkIfFollowing(db, userId, followerId))):
        db.followRelations.insert(userId=userId, followerId=followerId)

"""
Given a <userId, followerId> input, the mapping is removed from the database.
"""
def removeFollowRelation(db, userId, followerId):
    db((db.followRelations.userId==userId) & (db.followRelations.followerId==followerId)).delete()

"""
Given a userId, the list of users followed by that user is returned.
"""
def getFollowedUsers(db, userId):
    rows = db(db.followRelations.followerId==userId).select()
    users = []
    for row in rows:
        users.append(int(row.userId))
    return users

"""
Given a userId, the number of followers of that user is returned.
"""
def getNumberOfFollowers(db,userId):
    rows = db(db.followRelations.userId==userId).select()
    return len(rows)

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
    rows = db(db.topics.id == topicId).select()
    if len(rows) == 1:
        return True
    return False

"""
Given a topicId, this function will return the name of that topic.
"""
def getTopicName(db, topicId):
    rows = db(db.topics.id == topicId).select()
    if len(rows) == 1:
        return rows[0].topicName
    return None
 
"""
Given a prefix, suggestions are returned.
"""
def getTopicSuggestions(db, prefix, numberOfSuggestions):
    prefix = prefix.lower() + "%"
    rows = db(db.topics.topicName.like(prefix,case_sensitive=False)).select(limitby = (0, numberOfSuggestions))
    return rows


"""
Given a topicId, its children(sub topics) are obtained.
"""
def getSubTopics(db, parentTopicId):
    rows = db(db.topics.parentId == parentTopicId).select()
    return rows

"""
Given a topicId, its parentId is returned.
"""
def getTopicParent(db, topicId):
    rows = db(db.topics.id == topicId).select()
    parentId = 0
    if len(rows) == 1:
        parentId = int(rows[0].parentId)
    return parentId

"""
Given a topic set, the topics that can be expanded is returned
"""
def getExpandableTopics(db, topicsList):
    rows = db(db.topics.parentId.belongs(topicsList)).select()
    expandableTopics = []
    for row in rows:
        expandableTopics.append(row.parentId)
    return expandableTopics

"""
Basic function that gets the list of topics. Useful when classifying a take.
The list returned, contains objects of the form:
Dictionary : {"topicName": "Anime", "parentId": 5}
"""
def getGlobalTopicsList(db):
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
Given a tagId, the tagName is returned.
"""
def getTagName(db, tagId):
    rows = db(db.tags.id == tagId).select()
    if len(rows) == 1:
        return rows[0].tagName
    

"""
Given a tagName, the tagId is returned.
"""
def getTagId(db, tagName):
    rows = db(db.tags.tagName == tagName).select()
    if len(rows) == 1:
        return rows[0].id
    return 0
    
"""
Given a new tag, it is inserted into the database.
"""
def insertTag(db, tagName):
    tagName = tagName.lower()
    tagId = db.tags.insert(tagName=tagName)
    return tagId

"""
This function adds a <takeId, tagId> pair into the database
"""
def addTakeTagMapping(db, takeId, tagId):
    if(not(checkIfTakeTagMappingExists(db, takeId, tagId))):
        db.take_tags_mapping.insert(takeId = takeId, tagId = tagId)

"""
Given a takeId and tagId, this function tells you if the mapping exists
"""
def checkIfTakeTagMappingExists(db, takeId, tagId):
    rows = db((db.take_tags_mapping.tagId==tagId) & (db.take_tags_mapping.takeId==takeId)).select()
    if(len(rows)==1):
        return True
    return False

"""
Given a takId, the tags are returned.
"""
def getTakeTags(db, takeId):
    rows = db((db.take_tags_mapping.takeId ==takeId) & (db.take_tags_mapping.tagId == db.tags.id)).select()
    return rows

"""
Gets rid of all tags associated with this take.
"""
def removeTakeTags(db, takeId):
    db(db.take_tags_mapping.takeId == takeId).delete()
    
"""
Given a prefix, suggestions are returned.
"""
def getTagSuggestions(db, prefix, numberOfSuggestions):
    prefix = prefix.lower() + "%"
    rows = db(db.tags.tagName.like(prefix,case_sensitive=False)).select(limitby = (0, numberOfSuggestions))
    return rows

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
Given a takeId, this function gets rid of everything related to that take.
Delete the following:
1) Take info from the takes table.
2) Take topic mapping from the take_topic_mapping table.
3) Take Tag mapping from the take_tag_mapping table.
"""
def deleteTake(db, takeId):
    db(db.takes.id==takeId).delete()
    db(db.take_topic_mapping.takeId==takeId).delete()
    db((db.likes.articleId==takeId) & (db.likes.articleType=="Take")).delete()
    removeTakeTags(db, takeId)


"""
This function will retrieve all takes in the DB sorted by date.
"""
def getAllTakes(db, fromDate, toDate, rangeLowerLimit, rangeUpperLimit, ignoredTakesList, ignoredUserList):
    limitby=(rangeLowerLimit,rangeUpperLimit)
    rows = db((~(db.takes.id.belongs(ignoredTakesList))) &
              (~(db.takes.userId.belongs(ignoredUserList))) &
              (db.takes.timeOfTake >= fromDate) & 
              (db.takes.timeOfTake <= toDate) &
              (db.takes.userId == db.auth_user.id)).select(db.takes.ALL, db.auth_user.ALL, limitby = limitby, orderby = ~db.takes.timeOfTake)
    return rows


"""
Same as the above but sorts according to likes.
"""
def getAllTakesLikeSorted(db, fromDate, toDate, rangeLowerLimit, rangeUpperLimit, ignoredTakesList, ignoredUserList):
    limitby=(rangeLowerLimit,rangeUpperLimit)
    count = db.likes.articleId.count()
    result = db((~(db.takes.id.belongs(ignoredTakesList))) &
                (~(db.takes.userId.belongs(ignoredUserList))) &
                (db.likes.articleType=="Take") &
                (db.takes.id == db.likes.articleId) &  
                (db.takes.timeOfTake >= fromDate) & 
                (db.takes.timeOfTake <= toDate) &
                (db.takes.userId == db.auth_user.id)).select(
                db.likes.ALL, db.auth_user.ALL, db.takes.ALL, count, 
                groupby = db.likes.articleId, limitby = limitby, orderby = ~count)
    return result


"""
Given a topicId, this function will return all takes that fall under that category
"""
def getTopicTakes(db, topicId, fromDate, toDate, rangeLowerLimit, rangeUpperLimit, ignoredTakesList, ignoredUserList):
    limitby=(rangeLowerLimit,rangeUpperLimit)
    rows = db((~(db.takes.id.belongs(ignoredTakesList))) &
              (~(db.takes.userId.belongs(ignoredUserList))) &
              (db.take_topic_mapping.takeId==db.takes.id) & 
              (db.take_topic_mapping.topicId == topicId) & 
              (db.takes.timeOfTake >= fromDate) & 
              (db.takes.timeOfTake <= toDate) &
              (db.takes.userId == db.auth_user.id)).select(limitby = limitby, orderby = ~db.takes.timeOfTake)
    return rows


"""
Same as the previous function but sorting is done based on the number of likes.
"""
def getTopicTakesLikeSorted(db, topicId, fromDate, toDate, rangeLowerLimit, rangeUpperLimit, ignoredTakesList, ignoredUserList):
    limitby=(rangeLowerLimit,rangeUpperLimit)
    count = db.likes.articleId.count()
    result = db((~(db.takes.id.belongs(ignoredTakesList))) &
              (~(db.takes.userId.belongs(ignoredUserList))) &
                (db.likes.articleType=="Take") & 
                (db.take_topic_mapping.takeId==db.likes.articleId) & 
                (db.take_topic_mapping.topicId == topicId) & 
                (db.takes.id == db.likes.articleId) &  
                (db.takes.timeOfTake >= fromDate) & 
                (db.takes.timeOfTake <= toDate) &
                (db.takes.userId == db.auth_user.id)).select(
                db.likes.ALL, db.take_topic_mapping.ALL, db.auth_user.ALL, db.takes.ALL, count, 
                groupby = db.likes.articleId, limitby = limitby, orderby = ~count)
    return result

"""
Given a tagId, this function will return all takes that fall under that category
"""
def getTagTakes(db, tagId, fromDate, toDate, rangeLowerLimit, rangeUpperLimit, ignoredTakesList, ignoredUserList):
    limitby=(rangeLowerLimit,rangeUpperLimit)
    rows = db((~(db.takes.id.belongs(ignoredTakesList))) &
              (~(db.takes.userId.belongs(ignoredUserList))) &
              (db.take_tags_mapping.takeId==db.takes.id) & 
              (db.take_tags_mapping.tagId == tagId) & 
              (db.takes.timeOfTake >= fromDate) & 
              (db.takes.timeOfTake <= toDate) &
              (db.takes.userId == db.auth_user.id)).select(limitby = limitby, orderby = ~db.takes.timeOfTake)
    return rows


"""
Same as the previous function but sorting is done based on the number of likes.
"""
def getTagTakesLikeSorted(db, tagId, fromDate, toDate, rangeLowerLimit, rangeUpperLimit, ignoredTakesList, ignoredUserList):
    limitby=(rangeLowerLimit,rangeUpperLimit)
    count = db.likes.articleId.count()
    result = db((~(db.takes.id.belongs(ignoredTakesList))) &
                (~(db.takes.userId.belongs(ignoredUserList))) &
                (db.likes.articleType=="Take") & 
                (db.take_tags_mapping.takeId==db.likes.articleId) & 
                (db.take_tags_mapping.tagId == tagId) & 
                (db.takes.id == db.likes.articleId) &  
                (db.takes.timeOfTake >= fromDate) & 
                (db.takes.timeOfTake <= toDate) &
                (db.takes.userId == db.auth_user.id)).select(
                db.likes.ALL, db.take_tags_mapping.ALL, db.auth_user.ALL, db.takes.ALL, count, 
                groupby = db.likes.articleId, limitby = limitby, orderby = ~count)
    return result

"""
Given a list of userIds, the takes that have been posted by these guys is retrieved.
"""
def getUserTakes(db, userIdList, fromDate, toDate, rangeLowerLimit, rangeUpperLimit, ignoredTakesList):
    limitby=(rangeLowerLimit,rangeUpperLimit)
    rows = db((~(db.takes.id.belongs(ignoredTakesList))) &
              db.takes.userId.belongs(userIdList) & 
             (db.takes.timeOfTake >= fromDate) & 
             (db.takes.timeOfTake <= toDate) &
             (db.takes.userId == db.auth_user.id)).select(limitby = limitby, orderby = ~db.takes.timeOfTake)
    return rows

"""
Same as the previous function but sorting is done based on the number of likes.
"""
def getUserTakesLikeSorted(db, userIdList, fromDate, toDate, rangeLowerLimit, rangeUpperLimit, ignoredTakesList):
    limitby=(rangeLowerLimit,rangeUpperLimit)
    count = db.likes.articleId.count()
    result = db((~(db.takes.id.belongs(ignoredTakesList))) &
                (db.likes.articleType=="Take") & 
                (db.takes.id == db.likes.articleId) &  
                (db.takes.userId.belongs(userIdList)) & 
                (db.takes.timeOfTake >= fromDate) & 
                (db.takes.timeOfTake <= toDate) &
                (db.takes.userId == db.auth_user.id)).select(
                db.likes.ALL, db.takes.ALL, db.auth_user.ALL,  db.takes.ALL, count, 
                groupby = db.likes.articleId, limitby = limitby, orderby = ~count)
    return result


"""
This function adds a <takeId, topicId> pair into the database
"""
def addTakeTopicMapping(db, takeId, topicId):
    if(not(checkIfTakeTopicMappingExists(db, takeId, topicId))):
        db.take_topic_mapping.insert(takeId = takeId, topicId = topicId)


"""
This function removes a <takeId, topicId> pair present in the database
"""
def removeTakeTopicMapping(db, takeId, topicId):
    db((db.take_topic_mapping.takeId==takeId) & (db.take_topic_mapping.topicId==topicId)).delete()


"""
Given a takeId and topicId, this function tells you if the mapping exists
"""
def checkIfTakeTopicMappingExists(db, takeId, topicId):
    rows = db((db.take_topic_mapping.topicId==topicId) & (db.take_topic_mapping.takeId==takeId)).select()
    if(len(rows)==1):
        return True
    return False


"""
Given a takeId, this guy returns all the topics that have been tagged to it.
"""
def getTopicMappings(db, takeId):
    rows = db(db.take_topic_mapping.takeId==takeId).select()
    topics = []
    for row in rows:
        topics.append(row.topicId)
    return topics


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
    return db((db.likes.articleId==articleId) & (db.likes.articleType == articleType)).count()

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
