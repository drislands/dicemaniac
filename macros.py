import random
import string
import mysql.connector

######
# IMPORTANT MACROS
###
def testdb(connection,cursor,dbus,dbpw,dbdb):
    try:
        cursor.execute("SHOW TABLES")
        cursor.fetchall()
    except:
        connection = mysql.connector.connect(user=dbus,password=dbpw,host='localhost',database=dbdb)
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
#####