"""
This module will contain all DB functions starting from creating a DB handler to applying every single function.
"""

from gluon import *
import databaseConnectionStrings

# This function generates a db handler and returns it to you. Remember that it is your responsibility to close the db handle once you're done using it.
def getDBHandler(userId):
    connectionString = "mysql://" + databaseConnectionStrings.userName + ":" + databaseConnectionStrings.password + "@" + databaseConnectionStrings.hostName + "/" + databaseConnectionStrings.dbName + ""
    db = DAL(connectionString, migrate=False)
    #Add all define_table statements in here.
    db.define_table("auth_user",
                    Field("id","integer"),
                    Field("first_name", "string", requires=IS_NOT_EMPTY()),
                    Field("last_name", "string", requires=IS_NOT_EMPTY()),
                    Field("email", "string", requires=IS_NOT_EMPTY()),
                    Field('Education','string'),
                    Field('Occupation','string'),
                    Field('Birthday','date'),
                    Field('AboutMe','text'),
                    Field('Gender','string',requires = IS_IN_SET(['Male', 'Female', 'Other'])),
                    Field('displayPicture', 'upload' ),
                    Field('Website','string'))

    db.define_table("topics",
                    Field("id","integer"),
                    Field("topicName","string"),
                    Field("parentId","integer"))

    if(userId!=None):
        db.define_table("takes",
                    Field("id","integer"),
                    Field("takeContent","text"),
                    Field("userId","integer",writable = False, readable = False, default=userId))
    else:
        db.define_table("takes",
                    Field("id","integer"),
                    Field("takeContent","text"),
                    Field("userId","integer",writable = False, readable = False))

    db.define_table("take_table_mapping",
                    Field("id","integer"),
                    Field("takeId","integer"),
                    Field("topicId","integer"))
    return db

def DBInsertTest(db):
    db.userCredentials.insert(username = "revanthb3000",passwordDigest = "1282398349sxxw2",passwordSalt = "ryanHiga")
    print db.tables()
    db.commit()
