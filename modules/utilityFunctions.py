#!/usr/bin/env python
# coding: utf8
from gluon import *
import os
import databaseQueries

def checkIfVariableIsInt(var):
    try:
        x = int(var)
    except:
        return False
    return True

def isTakeIdValid(takeId):
    db = databaseQueries.getDBHandler(0)
    if not(checkIfVariableIsInt(takeId)):
        return False

    row = databaseQueries.getTakeInfo(db, takeId)
    if row == None:
        return False
    return True
