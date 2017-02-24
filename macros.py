import random
import string
import pymysql
#import mysql.connector

######
# IMPORTANT MACROS
###
def testdb(connection,cursor,dbus,dbpw,dbdb):
    if connection.open:
        return connection
    else:
        c = pymysql.connect(user=dbus,password=dbpw,host='localhost',database=dbdb)
        return c
###
def tx(message):
    return message.body['text']
###
def getDice(message,default=None):
    print("TEST: message[0] is reported as \"" + str(message[0]) + "\"")
    if (message[0] is not ''):
        return int(message[0])
    else:
        return default
###
def getSides(message,default=None):
    if (message[2]):
        return int(message[2])
    elif (message[4]):
        return int(message[4])
    else:
        return default
###
def getMod(message,default=None):
    if (message[3] and message[4]):
        return int(message[4])
    else:
        return default
###
def getBuff(message,default=None):
    if (message[3]):
        return (message[3])
    else:
        return default
###
def noModeSet(message):
    message.reply("Current mode not set. Set it with `.setmode MODE` before getting player stats.")
###
def isAdmin(message,controllers):
    return message.body['user'] in controllers
###
def genRand32():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(32))
### Wraps the userID into a mention.
def userWrap(UID):
    return '<@' + UID + '>'
###
def uWrap(message):
    return userWrap(message.body['user'])
### Returns a list of the keys in a dictionary that correspond to numbers 0 or higher.
###  NOTE: zUp refers to the fact that it only gets values of 0 or up. _Z_ero or _Up_.
def zUp(dic):
    retVal = []
    for i in dic:
        if dic[i] != None and dic[i] > -1:
            retVal.append(i)
    return retVal
#####
