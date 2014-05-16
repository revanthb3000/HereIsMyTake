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
    print "Gave a DB Handler"
    return db

def DBTest(db):
    db.define_table("users", Field("username", "string", length=255), Field("password", "string", length=255));
    db.users.insert(username="revanth", password="jj21k423h3n2jhj5jn")
    print db.tables()
    db.commit()
    db.close()
