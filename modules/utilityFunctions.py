#!/usr/bin/env python
# coding: utf8
from gluon import *
import databaseQueries
import re
import random

def checkIfVariableIsInt(var):
    try:
        x = int(var)
    except:
        return False
    return True

def isTakeIdValid(takeId, db):
    if not(checkIfVariableIsInt(takeId)):
        return False

    row = databaseQueries.getTakeInfo(db, takeId)
    if row == None:
        return False
    return True

def getArticlePreview(articleSource):
    articleSource.replace("<br/>","$$##$$")
    articleSource.replace("<br>","$$##$$")
    articleSource = re.sub('<[^<]+?>', ' ', articleSource)
    articleSource = articleSource[:500] + "......"
    preview = articleSource.replace("$$##$$","<br/>")
    return preview

def getMonthName(month):
    if(month==1):
        return "Jan"
    if(month==2):
        return "Feb"
    if(month==3):
        return "Mar"
    if(month==4):
        return "Apr"
    if(month==5):
        return "May"
    if(month==6):
        return "Jun"
    if(month==7):
        return "Jul"
    if(month==8):
        return "Aug"
    if(month==9):
        return "Sep"
    if(month==10):
        return "Oct"
    if(month==11):
        return "Nov"
    if(month==12):
        return "Dec"

"""
Given ALL details, this function returns the takes you need.
"""
def getRequiredTakes(feedType, sortParameter, db, fromDate, toDate, rangeLowerLimit, rangeUpperLimit, ignoredTakesList, ignoredUserList, topicId, tagId, userIdList):
    rows = None
    
    if(feedType == 1):  #General Feed
        if(sortParameter=="Date"):
            rows = databaseQueries.getAllTakes(db, fromDate, toDate, rangeLowerLimit, rangeUpperLimit, ignoredTakesList, ignoredUserList)
        else:
            rows = databaseQueries.getAllTakesLikeSorted(db, fromDate, toDate, rangeLowerLimit, rangeUpperLimit, ignoredTakesList, ignoredUserList)

    elif(feedType == 2): #Topic Feed
        if(sortParameter=="Date"):
            rows = databaseQueries.getTopicTakes(db, topicId, fromDate, toDate, rangeLowerLimit, rangeUpperLimit, ignoredTakesList, ignoredUserList)
        else:
            rows = databaseQueries.getTopicTakesLikeSorted(db, topicId, fromDate, toDate, rangeLowerLimit, rangeUpperLimit, ignoredTakesList, ignoredUserList)

    elif(feedType == 3):#Tag Feed
        if(sortParameter=="Date"):
            rows = databaseQueries.getTagTakes(db, tagId, fromDate, toDate, rangeLowerLimit, rangeUpperLimit, ignoredTakesList, ignoredUserList)
        else:
            rows = databaseQueries.getTagTakesLikeSorted(db, tagId, fromDate, toDate, rangeLowerLimit, rangeUpperLimit, ignoredTakesList, ignoredUserList)

    elif(feedType == 4):#Users Feed
        if(sortParameter=="Date"):
            rows = databaseQueries.getUserTakes(db, userIdList, fromDate, toDate, rangeLowerLimit, rangeUpperLimit, ignoredTakesList)
        else:
            rows = databaseQueries.getUserTakesLikeSorted(db, userIdList, fromDate, toDate, rangeLowerLimit, rangeUpperLimit, ignoredTakesList)

    return rows

"""
This function returns the HTML Code for a set of takes.
"""
def getRequiredTakesHTML(feedType, sortParameter, db, fromDate, toDate, rangeLowerLimit, rangeUpperLimit, ignoredTakesList, ignoredUserList, topicId, tagId, userIdList):
    rows = getRequiredTakes(feedType, sortParameter, db, fromDate, toDate, rangeLowerLimit, rangeUpperLimit,
                            ignoredTakesList, ignoredUserList, topicId, tagId, userIdList)
    if(rows==None):
        return ""
    htmlCode = ""
    for row in rows:
        numberOfFollowers = databaseQueries.getNumberOfFollowers(db, row.auth_user.id)
        displayPicture = ""
        if (row.auth_user.displayPicture!=None):
            displayPicture = row.auth_user.displayPicture

        htmlCode += '<table>\n'
        htmlCode += '<tr class="feedRow">\n'
        
        htmlCode += '<td>\n'
        htmlCode += '<a href="' + URL('users','profile',vars=dict(userId = row.auth_user.id)) + '" class="userPopToolTip">\n'
        htmlCode += str(IMG(_src=databaseQueries.getUserProfilePicture(db, row.auth_user.id, displayPicture), _width="60px",_height="60px")) + "\n"
        htmlCode += '<span>\n'
        htmlCode += row.auth_user.first_name + " " + row.auth_user.last_name + '<br/>\n'
        htmlCode += '<i>' + str(numberOfFollowers) + ' Follower' + ('s' if (numberOfFollowers!=1) else '') + '</i>\n'
        htmlCode += '</span>\n'
        htmlCode += '</a>\n'
        htmlCode += '</td>\n'
        
        htmlCode += '<td>\n'     
        htmlCode += '<a href="' + URL('takes','viewTake',vars=dict(takeId=row.takes.id)) + '">' + row.takes.takeTitle + '</a>\n'
        htmlCode += "<div class='likeCount' id = 'takeLikeCount'>\n"
        htmlCode += str(IMG(_src=URL('static','images/thumbsUpNegative.png'), _alt="thumbs", _width="25px",_height="25px")) + "\n"
        htmlCode += str(databaseQueries.getNumberOfLikes(db, row.takes.id, "Take")) + "\n" 
        htmlCode += '</div>\n'
        htmlCode += '<br/>\n'
        htmlCode += XML(getArticlePreview(row.takes.takeContent)) + "\n"
        htmlCode += '</td>\n'
        
        htmlCode += '</tr>\n'
        htmlCode += '</table>\n'
        
    return htmlCode

"""
Given a parentId, htmlCode that's used to display tiles of that topic's children is returned.
"""
def getRequiredTilesHtmlCode(parentId, topics, expandableTopics, grandParentId):
    htmlCode = "<table>"
    tileColors = [1,2,3,4,5,6,7]#,8,9,10,11,12]
    random.shuffle(tileColors)
    rowSize = 4
    i = 1
    while(i <= (len(topics) + 1)):
        topicFeedLink = ""
        topicName = ""
        topicId = i
        tileClass = "metro-tile"

        if(i == (len(topics)+1)):
            if(parentId == 0):
                topicFeedLink = URL('takes','subscriptionFeed')
                topicId = "favorites"
                topicName = "Favorites-Subscription"
                tileClass = tileClass + " " + "metro-tile-favorites"
            else:
                topicFeedLink = ""
                topicId = "levelUp"
                topicName = "levelUp"
                tileClass = tileClass + " " + "metro-tile-levelUp"
        else:
            topicFeedLink = URL('takes','topicFeed',vars=dict(topicId=topics[i-1].id))
            topicId = topics[i-1].id
            topicName = topics[i-1].topicName
            tileClass = tileClass + " " + "metro-tile-" + str(tileColors[i])

        if((i-1)%rowSize==0):
            htmlCode += '<tr>\n'
        
        htmlCode += '<td>\n'
        htmlCode += '<div id="tile-' + str(topicId) + '" class="' + str(tileClass) + '">\n'
        if(topicName=="Favorites-Subscription"):
            htmlCode += '<a href="' + topicFeedLink + '">\n'            
            htmlCode += str(IMG(_src=URL('static','images/subscriptionStar.png'), _alt="thumbs", _id="starTile")) + '\n'
        elif(topicName=="levelUp"):
            htmlCode += '<a onclick=\'loadTiles("' + URL('ajax','getTilesCodeByParentId',vars=dict(parentId = grandParentId)) + '")\'>\n'
            htmlCode += str(IMG(_src=URL('static','images/levelUpArrow.png'), _alt="thumbs", _id="starTile")) + '\n'
        else:
            htmlCode += '<a href="' + topicFeedLink + '">\n'
            htmlCode += '<br/>\n<br/>\n'
            htmlCode += topicName

        htmlCode += '</a>\n<br/>\n<br/>\n'
        if(topicId in expandableTopics):
            htmlCode += '<div align="right">\n'
            htmlCode += '<a onclick=\'loadTiles("' + URL('ajax','getTilesCodeByParentId',vars=dict(parentId=topicId)) + '")\'>\n'
            htmlCode += '+\n'
            htmlCode += '</a>\n'
            htmlCode += '</div>\n'
                    
        htmlCode += '</div>\n'
        htmlCode += '</td>\n'
        if(i%rowSize==0):
            htmlCode += '</tr>'
        i = i + 1
    if(htmlCode[-5:]!="</tr>"):
        htmlCode += "</tr>"
    htmlCode += "</table>\n"
    return htmlCode