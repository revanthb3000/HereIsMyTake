"""
This module will contain all DB functions starting from creating a DB handler to applying every single function.
"""

from gluon import *
import databaseConnectionStrings

# This function generates a db handler and returns it to you. Remember that it is your responsibility to close the db handle once you're done using it.
def getDBHandler():
    connectionString = "mysql://" + databaseConnectionStrings.userName + ":" + databaseConnectionStrings.password + "@" + databaseConnectionStrings.hostName + "/" + databaseConnectionStrings.dbName + ""
    db = DAL(connectionString, migrate=False)
    #Add all define_table statements in here.
    db.define_table("userCredentials",Field("username", "string", length=255),Field("passwordDigest", "string", length=255),Field("passwordSalt", "string", length=255))
    print "Gave a DB Handler"
    return db

def DBInsertTest(db):
    db.userCredentials.insert(username = "revanthb3000",passwordDigest = "1282398349sxxw2",passwordSalt = "ryanHiga")
    print db.tables()
    db.commit()
