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