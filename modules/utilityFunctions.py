#!/usr/bin/env python
# coding: utf8
from gluon import *
import os
import databaseQueries
import re

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
