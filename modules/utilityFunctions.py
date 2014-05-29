#!/usr/bin/env python
# coding: utf8
from gluon import *
import os

def getUserImageFileName(appName, imagePrefix, userId):
    fileName = imagePrefix + str(userId)
    jpgFileName = os.getcwd() + "/applications/" + appName + "/static/" +  fileName + ".jpg"
    pngFileName = os.getcwd() + "/applications/" + appName + "/static/" +  fileName + ".png"
    if(os.path.isfile(jpgFileName)):
        return fileName + ".jpg"
    if(os.path.isfile(pngFileName)):
        return fileName + ".png"
    return None

def checkIfVariableIsInt(var):
    try:
        x = int(var)
    except:
        return False
    return True
