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