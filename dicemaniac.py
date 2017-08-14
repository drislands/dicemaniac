# -*- coding: utf-8 -*-
from slackbot.bot import respond_to
from slackbot.bot import listen_to
from slackbot.dispatcher import Message
from os.path import dirname
from slackbot.bot import Bot
import inspect
import re
import random
import pymysql
#import mysql.connector
import os
import sys
import string

#### local files
import pokemon
import magic
#import wartent
from macros import *
from orcwarrior import *

####

# FOR TESTING!
bot = None
#

# MYSQL connector data. 
DB_PASSWORD = os.environ['DB_PASSWORD']
SECRET_ADMIN = os.environ['SECRET_ADMIN']
MYSQL_USER = 'dicemaniac'
MYSQL_DB = 'dicemaniac'
IM_BACK = False
BACKSTRING = "https://goo.gl/DlN2jd"
BACK_CHAN = None
BACK_CONT = False
#
if len(sys.argv) > 1:
    if(sys.argv[1] == 'AJDkud'):
        IM_BACK = True
        BACK_CHAN = sys.argv[2]
        BACK_CONT = len(sys.argv) > 2
#
# some default info
DEFAULT_REPLY = "Sorry but I'm a complete tosser"
ERRORS_TO = 'jeremy'
MAX_DICE = 200  # just to prevent insane scenarios
MAX_SIDES = 9002 #
MAX_MOD = 200
TOTAL_FRONT = False
ADMIN_SET = False
CURRENT_MODE = ""
DEFAULT_CHANNEL = ""
ALLOW_MADNESS = False
TESTING = False
DEBUG_LOG = 0
#
WARTENT = ""
# some joke values, hidden from public view
MAGIC_ROSS = False
MAGIC_CHEAT,CHEAT_ROLL = False,0
#PLUGINS = [
#    'slackbot.plugins',
#    'mybot.plugins',
#]
#

# Initializing connections and making sure it all works.
conn = pymysql.connect(user=MYSQL_USER,password=DB_PASSWORD,host='localhost',database=MYSQL_DB)
c = conn.cursor()
print("Connected to database.")
print("Setting session timeout to 3 days.")
try:
    c.execute("SET SESSION wait_timeout = 259200")
    conn.commit()
    print("Session timeout successfully changed.")
except:
    print("Could not change timeout.")
# setting up connection for giphy score.
GIPHY_STABLE = True
c.execute("SELECT val FROM stats WHERE pkey='giphy score'")
giphy = c.fetchall()
if not giphy:
    DEBUG_LOG += 1
    c.execute("INSERT INTO stats VALUES('0','giphy score')")
    print(str(DEBUG_LOG) + ": " + "Initializing giphy score.")
else:
    DEBUG_LOG += 1
    giphy = int(giphy[0][0])
    print(str(DEBUG_LOG) + ": " + "Obtaining giphy score: " + str(giphy))
conn.commit()

# Initializing the list of viable controllers. As of writing, there can be only one.
CONTROLLERS=[]

if BACK_CONT:
    for i in sys.argv[3:]:
        CONTROLLERS.append(i)
    if len(CONTROLLERS) > 1:
        ADMIN_SET = True

#####
### custom icon/username bot responses
def customSend(message,text,icon=None,user=None):
    if icon:
        message._client.bot_emoji=icon
    if user:
        message._client.login_data['self']['name'] = user
    message.send_webapi(text,as_user=False)
###
def conchSend(message,text):
    customSend(message,text,':shell:','Magic Conch')
###
def giphySend(message,text):
    customSend(message,text,':aw_yeah:','Scorekeeper')
###
def pokeSend(message,text):
    #customSend(message,message.body['user'] + ": " + text,':poke:','PokéFetcher') 
    customSend(message,text,':poke:','PokéFetcher')
###
def magicSend(message,text):
    customSend(message,text,':mtg:','MagicFetcher')
###
def backSend(message,text):
    customSend(message,text,':video_game:','Backronym Host Bot')
###
def orcSend(message,text):
    customSend(message,text,':orc:','Orc Warrior Bot')
###
def warSend(message,text):
    customSend(message,text,':scroll:','War Tent Courier')
#####

#####
### miscellaneous
@listen_to('^rm -rf / --no-preserve-root$')
def burnItAllSudo(message):
    message.reply("Uh, no.")
## ^^ This is to make sure people use sudo.
@listen_to('^sudo rm -rf /$')
def burnItAllPreserve(message):
    burnItAllSudo(message)
## ^^ This is to make sure people use the right flags.
@listen_to('^rm -rf /$')
def burnItAllAll(message):
    burnItAllSudo(message)
#
@listen_to('^sudo rm -rf / --no-preserve-root$')
def burnItAll(message):
    ##message.reply("DOWN FOR FIRE MAINTENANCE")
    if not isAdmin(message,CONTROLLERS):
        burnItAllSudo(message)
    else:
        print("Starting burn")
        message.reply("Alright then. BURNING IT ALL")
        #os.fsync()
        os.execv(sys.executable, ['python3'] + [sys.argv[0],'AJDkud',message.body['channel']] + CONTROLLERS)
        ## ^ Starts the whole thing all over again, hopefully.
###
#NO_COUNT = 0
@listen_to('^magic conch.*\?',re.IGNORECASE)
def magicConch(message):
    i = random.randint(1,100)
    text = ''
    #global NO_COUNT
    if i < 11:
        text = 'Maybe someday.'
    elif i < 31:
        text = 'I don\'t think so.'
    elif i < 51:
        #if NO_COUNT < 3:
            text = 'No.'
        #    NO_COUNT += 1
        #else:
        #    text = '_sassily_ No.'
    elif i < 91:
        text = 'Yes.'
    elif i < 101:
        text = 'Try asking again.'
    else:
        global DEBUG_LOG
        DEBUG_LOG += 1
        print (str(DEBUG_LOG) + ": " + "Error...random function out of range. i = " + str(i))

    conchSend(message,'_zzzzzzip_ ' + text)
###
@listen_to('giphy \+1',re.IGNORECASE)
def giphyUp(message):
    global giphy,conn,GIPHY_STABLE
    if GIPHY_STABLE:
        GIPHY_STABLE = False
        conn = testdb(conn,c,MYSQL_USER,DB_PASSWORD,MYSQL_DB)
        giphy += 1
        c.execute("UPDATE stats SET val='%s' WHERE pkey='%s'"%(str(giphy),"giphy score"))
        giphySend(message,"Good job giphy! +1 point for you. Total of " + str(giphy) + " so far!")
        conn.commit()
        GIPHY_STABLE = True
###
@listen_to('giphy -1',re.IGNORECASE)
def giphyDown(message):
    global giphy,conn,GIPHY_STABLE
    if GIPHY_STABLE:
        GIPHY_STABLE = False
        conn = testdb(conn,c,MYSQL_USER,DB_PASSWORD,MYSQL_DB)
        giphy -= 1
        c.execute("UPDATE stats SET val='%s' WHERE pkey='%s'"%(str(giphy),"giphy score"))
        giphySend(message,"God dammit giphy. -1 point for you. Total of " + str(giphy) + " so far.")
        conn.commit()
        GIPHY_STABLE = True
###
@listen_to('\[\[(.*)\]\]')
def pokeFetch(message,name):
    global DEBUG_LOG
    DEBUG_LOG += 1
    ## To prevent the thing from pulling down the entire database:
    if not name:
        pokeSend(message,"I'm very unhappy with you.")
        return
    if re.findall('L\[\[.*\]\]',tx(message)):
        literal = True
        print(str(DEBUG_LOG) + ": " + "Literal L found.")
    else:
        literal = False
    superType = re.findall('\[\[.*\]\]([PET])',tx(message))

    print(str(DEBUG_LOG) + ": " + "Content of name variable: \"" + name + "\".")
    if '][' in name:
        if len(re.findall('\]\[',name)) == 2:
            print (str(DEBUG_LOG) + ": " + "Set/ID search identified.")
            inData = re.findall('(.*)\]\[(.*)\]\[(.*)',name).pop(0)
            cName,cSet,cID = inData[0],inData[1],inData[2]
            if not cName or not cSet or not cID:
                pokeSend(message,"You must specify all of the following to search by ID: [[Name][Set][ID]]\nOtherwise, just use [[Name][Set]] or just [[Name]].")
                return
            else:
                card = pokemon.getCardURL(cName,cSet,cID,literal,superType)
        elif len(re.findall('\]\[',name)) == 1:
            print (str(DEBUG_LOG) + ": " + "Set search identified.")
            inData = re.findall('(.*)\]\[(.*)',name).pop(0)
            cName,cSet = inData[0],inData[1]
            if not cName or not cSet:
                pokeSend(message,"Please either specify both the card and the set with [[Cardname][Set]] or just the card with [[Cardname]].")
                return
            else:
                card = pokemon.getCardURL(cName,cSet,None,literal,superType)
    else:
        card = pokemon.getCardURL(name,None,None,literal,superType)
    if not card:
        pokeSend(message,"No card with that name found.")
    else:
        pokeSend(message,card)
###
@listen_to(r"{{" + '(.*)' + r"}}")
def magicFetch(message,name):
    global DEBUG_LOG
    DEBUG_LOG += 1
    # debug stuff.
    print(str(DEBUG_LOG) + ": " + "magic fetch triggered. name text = \"" + name + "\"")
    if re.findall(r"L{{" + '.*' + r"}}",tx(message)):
        literal = True
    else:
        literal = False
    superType = re.findall(r'{{' + '.*' + r'}}' + '([CEISPAL])',tx(message))

    if r'}{' in name:
        print(str(DEBUG_LOG) + ": " + "set search identified.")
        inData = re.findall('(.*)' + r"}{" + '(.*)',name).pop(0)
        cName,cSet = inData[0],inData[1]
        if not cName or not cSet:
            pokeSend(message,"Please either specify both the card and the set with [[Cardname][Set]] or just the card with [[Cardname]].")
            print(str(DEBUG_LOG) + ": " + "One or both not properly named.")
            return
        else:
            print(str(DEBUG_LOG) + ": " + "card/set identified. Beginning card search with card name \"" + cName + "\" and set name \"" + cSet + "\".")
            card = magic.getCardURL(cName,cSet,literal,superType)
            print(str(DEBUG_LOG) + ": " + "search complete.")
    else:
        print(str(DEBUG_LOG) + ": " + "card (no set) identifed. Beginning card search.")
        card = magic.getCardURL(name,None,literal,superType)
        print(str(DEBUG_LOG) + ": " + "search complete.")
    if not card:
        magicSend(message,"No card with that name found.")
    else:
        print(str(DEBUG_LOG) + ": " + "sending card results.")
        magicSend(message,card)
        print(str(DEBUG_LOG) + ": " + "card results sent.")
#####

#####
### testing stuff
@listen_to('^testing$')
def testing(message):
    global DEBUG_LOG
    DEBUG_LOG += 1
    if TESTING:
        message.reply('Printing contents.')
        print(str(DEBUG_LOG) + ": " + message.body)
###
@listen_to('^icon test$')
def testIcon(message):
    if TESTING:
        message._client.bot_emoji=':godmode:'
        message._client.login_data['self']['name'] = 'Godmode'
        message.send_webapi('Icon test',as_user=False)
###
@listen_to('magic conch',re.IGNORECASE)
def testConch(message):
    if TESTING:
        message._client.bot_emoji=':shell:'
        message._client.login_data['self']['name'] = 'Magic Conch'
        message.send_webapi('_ziiiiip_ Nothing.',as_user=False)
###
@listen_to('^testing on$')
def testOn(message):
    if isAdmin(message,CONTROLLERS):
        global TESTING
        TESTING = True
        message.reply("Testing mode on.")
###
@listen_to('^testing off$')
def testOff(message):
    if isAdmin(message,CONTROLLERS):
        global TESTING
        TESTING = False
        message.reply("Testing mode off.")
###
#####
### admin stuff
@listen_to('^\.adminup (.*)')
def admin_activate(message,something):
    global ADMIN_SET
    if not ADMIN_SET:
        if something == SECRET_ADMIN:
            CONTROLLERS.append(message.body['user'])
            message.reply('You are set as a controller!')
            if len(CONTROLLERS) > 1:
                ADMIN_SET = True
    else:
        message.reply("Admin user already set.")
### alternative method for authenticating
@listen_to('^' + SECRET_ADMIN + '$')
def altAdmin(message):
    if not ADMIN_SET:
        admin_activate(message,SECRET_ADMIN)
#### establishing cheat mode
#@respond_to('^it is time$',re.IGNORECASE)
#def cheatOn(message):
#    global MAGIC_CHEAT,ADMIN_SET
#    if ADMIN_SET and isAdmin(message,CONTROLLERS):
#        message.reply("Fairness protocol override activated.")
#        MAGIC_CHEAT = True
#### setting the next value
#@respond_to('^prepare me a (.*)$')
#def cheatSet(message,val):
#    global MAGIC_CHEAT,ADMIN_SET,CHEAT_ROLL
#    if MAGIC_CHEAT and ADMIN_SET and isAdmin(message,CONTROLLERS):
#        try:
#            CHEAT_ROLL = int(val)
#            message.reply("Next roll set.")
#        except ValueError:
#            message.reply("ERROR: need an integer.")
###
@listen_to('^\.getmode$')
def getMode(message):
    if not CURRENT_MODE:
        noModeSet(message)
    elif isAdmin(message,CONTROLLERS):
        message.reply("The current mode is `" + CURRENT_MODE + "`.")
###
@listen_to('^\.getmodes$')
def getAllModes(message):
    if isAdmin(message,CONTROLLERS) or ALLOW_MADNESS:
        conn = testdb(conn,c,MYSQL_USER,DB_PASSWORD,MYSQL_DB)
        c.execute("SELECT mode FROM settings GROUP BY mode")
        results = c.fetchall()
        if results:
            modes = []
            modeList = ""
            for i in results:
                modes.append(i[0])
            if len(modes) > 1:
                modeList = ', '.join(modes)
            else:
                modeList = modes[0]
            message.reply("These are all available modes: " + modeList)
        else:
            message.reply("No modes have been stored.")
###
@listen_to('^\.setmode (.*)$')
def setMode(message,mode):
    global CURRENT_MODE
    if isAdmin(message,CONTROLLERS) and CURRENT_MODE != mode:
        CURRENT_MODE = mode
        message.reply("Current mode has been updated.")
    elif isAdmin(message,CONTROLLERS) and CURRENT_MODE == mode:
        message.reply("That is already the current mode.")
###
@listen_to('^\.getp (.*)$')
def getPlayerStats(message,player):
    if isAdmin(message,CONTROLLERS) or ALLOW_MADNESS:
        if CURRENT_MODE:
            conn = testdb(conn,c,MYSQL_USER,DB_PASSWORD,MYSQL_DB)
            c.execute("SELECT pkey,val FROM settings WHERE mode='%s' AND player='%s'"%(CURRENT_MODE,player))
            returns = c.fetchall()
            results = []
            if returns:
                for i in returns:
                    results.append(': '.join([i[0],i[1]])) # this makes a key:value pair of the returned pkey and val for each row
                message.reply("For player `%s` in mode `%s`, the following values are set:\n```%s```" % (player,CURRENT_MODE,'\n'.join(results)))
            else:
                message.reply("No results found for player `%s` in mode `%s`." % (player,CURRENT_MODE))
        else:
            noModeSet(message)
###
@listen_to('^\.get (.*) (.*)$')
def getStat(message,player,stat,quiet=False):
    if isAdmin(message,CONTROLLERS) or ALLOW_MADNESS:
        if CURRENT_MODE:
            conn = testdb(conn,c,MYSQL_USER,DB_PASSWORD,MYSQL_DB)
            c.execute("SELECT val FROM settings WHERE mode='%s' AND player='%s' AND pkey='%s'"%
                (CURRENT_MODE,player,stat))
            returns = c.fetchall()
            results = []
            if returns:
                for i in returns:
                    if i[0] == None:
                        i[0] = "n/a"
                    results.append(i[0])
                if len(results) > 1:
                    global DEBUG_LOG
                    DEBUG_LOG += 1
                    # this really shouldn't happen lol but here it is
                    print(str(DEBUG_LOG) + ": " +  ' AND '.join(results))
                    if not quiet:
                        message.reply("ERROR: MULTIPLE SET. CHECK DEBUG LOG AND/OR DATABASE.")
                    else:
                        return -1
                else:
                    if not quiet:
                        message.reply("`%s` has a `%s` value of `%s`." % 
                            (player,stat,results[0]))
                    else:
                        return 1
            else:
                if not quiet:
                    message.reply("`%s` does not have a value set for `%s` in mode `%s`. Consider setting it with `.set %s %s VAL`" % 
                        (player,stat,CURRENT_MODE,player,stat))
                else:
                    return 0
        else:
            if not quiet:
                noModeSet(message)
            else:
                return -2
###
@listen_to('^\.set (.*) (.*) (.*)$')
def setStat(message,player,stat,val):
    if isAdmin(message,CONTROLLERS):
        if CURRENT_MODE:
            conn = testdb(conn,c,MYSQL_USER,DB_PASSWORD,MYSQL_DB)
            status = getStat(message,player,stat,True)
            if status == 0:
                c.execute("INSERT INTO settings VALUES('%s','%s','%s','%s')"%
                    (CURRENT_MODE,player,val,stat))
                message.reply("New stat `%s` created for player `%s` with value `%s`." % 
                    (stat,player,val))
                conn.commit()
            elif status == 1:
                c.execute("UPDATE settings SET val='%s' WHERE mode='%s' AND player='%s' AND pkey='%s'"%
                    (val,CURRENT_MODE,player,stat))
                message.reply("Stat `%s` for player `%s` updated to value `%s`." % 
                    (stat,player,val))
                conn.commit()
            elif status == -1:
                message.reply("ERROR: MULTIPLE INSTANCES SET. CHECK DEBUG LOG AND/OR DATABASE.")
            elif status == -2:
                message.reply("This is complete madness. How did you even get this message to print?")
                # Because it should only return -2 if CURRENT_MODE isn't set, and if
                #  it isn't set you should have gotten this far in the first place...
            else:
                message.reply("This is a placeholder. There are no values besides 1, 0, -1 and -2 that can be returned so you shouldn't be able to get here at all.")
        else:
            noModeSet(message)
###
@listen_to('^\.setchannel (.*)$')
def setChannel(message,channel):
    global DEFAULT_CHANNEL
    if isAdmin(message,CONTROLLERS):
        DEFAULT_CHANNEL = re.findall('\#(C.{8})',channel)[0]
        if DEFAULT_CHANNEL:
            message.reply("Default channel set to %s, ID %s." %
                (channel,DEFAULT_CHANNEL))
        else:
            message.reply("That doesn't appear to be a link to a channel. Try again with a #-linked channel name.")
        #print(channel,message.body['channel'])
        #message.reply("This is a test. You said %s, and this channel is %s." %
        #    (channel,message.body['channel']))
###
@listen_to('^\.setchannel$')
def setThisChannel(message):
    setChannel(message,'#'+message.body['channel'])
### Turning on the madness
@listen_to('^LET MADNESS REIGN$')
def activateMadess(message):
    if isAdmin(message,CONTROLLERS):
        global ALLOW_MADNESS
        if not ALLOW_MADNESS:
            ALLOW_MADNESS = True
            message.reply("I hope you know what you're doing...")
        else:
            message.reply("HOW MUCH MADNESS CAN WE TAKE?!")
#####
### Adding players to The Game. (gotcha)
@listen_to('^enchant (.*) (.*)$')
def enchantPlayer(message,player,pID):
    if isAdmin(message,CONTROLLERS):
        global DEBUG_LOG
        DEBUG_LOG += 1
        conn = testdb(conn,c,MYSQL_USER,DB_PASSWORD,MYSQL_DB)
        #message.reply("This is a test. The player is: %s. The player ID is: %s." % (player,pID))
        print(str(DEBUG_LOG) + ": " + "Player: %s. PID: %s." % (player,pID))
        c.execute("SELECT * FROM players WHERE name='%s' OR id='%s'"% (player,pID))
        results = c.fetchall()
        if not results:
            c.execute("INSERT INTO players VALUES('%s','%s')"%(player,pID))
            conn.commit()
            message.send("%s: You've been enchanted!" % (pID))
        elif len(results) > 1:
            message.reply("Issue with DB; multiple entries exist. Check for inconsistencies.")
        elif results[0][0] != player or results[0][1] != pID:
            message.reply("Issue with DB, mismatching entry. Stored username/ID is: %s %s" % 
                (results[0][0],results[0][1]))
        else:
            message.reply("That player is already enchanted!")
### This is just to test the ability of the bot to ping users other than the message originator.
@listen_to('^sparkle (.*)$',re.IGNORECASE)
def sparklePlayer(message,player):
    if isAdmin(message,CONTROLLERS) or ALLOW_MADNESS:
        c.execute("SELECT id FROM players WHERE name='%s'" % player)
        results = c.fetchall()
        if not results:
            message.reply("That player hasn't been enchanted yet! Gosh! You can't just sparkle unenchanted people, y'know!")
        elif len(results) > 1:
            message.reply("Issue with DB; multiple entries exist. Check for inconsistencies.")
        else:
            message.send("%s: You've been sparkled! Bam!" % (results[0][0]))
### This is to test the ability to ping other players, triggered by a DM, and checking to make sure it only works in DM form.
@respond_to('demolish (.*)$')
def demolishPlayer(message,player):
    if isAdmin(message,CONTROLLERS) or ALLOW_MADNESS:
        if message.body['channel'][:1] == 'D':
            c.execute("SELECT id FROM players WHERE name='%s'" % player)
            results = c.fetchall()
            if not results:
                message.reply("That player hasn't been enchanted yet! Gosh! You can't just demolish unenchanted people, y'know!")
            elif len(results) > 1:
                message.reply("Issue with DB; multiple entries exist. Check for inconsistencies.")
            else:
                if DEFAULT_CHANNEL:
                    message.body['channel'] = DEFAULT_CHANNEL
                    message.send("%s: You've been DEMOLISHED! :boom:" % (results[0][0]))
                else:
                    message.reply("The channel to respond to hasn't been set.")
        else:
            message.reply("Are you insane?! You can't just demolish someone in a public channel!")
### This is to charm other players, in the same vein as sparkling.
@listen_to('^charm (.*)$')
def charmPlayer(message,player):
    if isAdmin(message,CONTROLLERS) or ALLOW_MADNESS:
        c.execute("SELECT id FROM players WHERE name='%s'" % player)
        results = c.fetchall()
        if not results:
            message.reply("That player hasn't been enchanted yet! Gosh! You can't just charm unenchanted people, y'know!")
        elif len(results) > 1:
            message.reply("Issue with DB; multiple entries exist. Check for inconsistencies.")
        else:
            message.send("%s: You've been charmed! BWAGH CHARM ACTIVATED" % (results[0][0]))
#####
########

########
#####
### Setting up the game here
conn = testdb(conn,c,MYSQL_USER,DB_PASSWORD,MYSQL_DB)
c.execute("SELECT name,val1,val2 FROM default_moves")
(FAST,STRN,DFND) = c.fetchall()
###
# TODO: need to create the flow of the game.
# TODO: need to create ability to challenge players and accept challenges.
# TODO: need to create getters and setters for basic values. settings table will be very useful for this!!!
#####
########

########
#####
### custom plugins. let's see if this actually works.
@respond_to('hi', re.IGNORECASE)
def hi(message):
    global DEBUG_LOG
    DEBUG_LOG += 1
    message.reply('I can understand hi or HI!')
    # react with thumb up emoji
    message.react('+1')
    print(str(DEBUG_LOG) + ": " + message.body['channel'])
    print(str(DEBUG_LOG) + ": " + message.body['user'])

@listen_to('greetings,? humans?', re.IGNORECASE)
def beepboop(message):
    message.reply('_BEEP_ *DEPLOY GREETING* _BOOP_ *HELLO* _BEEP_ *GREETING DEPLOYED* _BOOP_')

@listen_to('love', re.IGNORECASE)
def love(message):
    global DEBUG_LOG
    DEBUG_LOG += 1
    print(str(DEBUG_LOG) + ": " + message.body['user'])
    message.react('heart')
    print(str(DEBUG_LOG) + ": " + message.body['channel'])

@listen_to('CAW')
def caw(message):
    message.react('bird')

@listen_to('poop')
def poop(message):
    message.react('samonfire')

@listen_to('dick')
def dick(message):
    message.react('richards')

@listen_to('^printtest')
def printtest(message):
    global DEBUG_LOG
    DEBUG_LOG += 1
    print(str(DEBUG_LOG) + ": " + message.body['text'])
    message.reply('Contents of message printed.')

#@listen_to(MOST_COMMON_PHRASE,re.IGNORECASE)
#def emojiParty(message):
#

@listen_to('sweet, summer child', re.IGNORECASE)
def summerchild(message):
    message.reply('http://i.imgur.com/qsSj2L6.gif')

@listen_to('relevant xkcd', re.IGNORECASE)
def relevant(message):
    message.reply('I no work yet!')

# Revamped roll function. Checking for + and - modifiers at the end. Maybe separate functions per scenario?
@listen_to('[dD]\d+')
def roll(message):
    global DEBUG_LOG
    DEBUG_LOG += 1
    if (re.search('\\b(\d+)?[dD](\d+[\+-])?\d+\\b',tx(message))): 
        resString = None
        total = 0
        catch = re.findall('\\b(\d+)?[dD]((\d+)([\+-]))?(\d+)\\b',tx(message)).pop(0)
        ONE_TRIG = False
        

        legend = 'Rolls: '
#Created seperate roller function because it was repeated code
        def roller(dice, sides, buff, mod, total, legend):
            print("TESTING: WE ARE ROLLING!")
            global CHEAT_ROLL, MAGIC_CHEAT
            results = []
            ## this part is for the easter egg of cheating. Teehee.
            if(MAGIC_CHEAT and CHEAT_ROLL and isAdmin(message,CONTROLLERS) and not dice and CHEAT_ROLL < sides + 1):
                total += CHEAT_ROLL
                results.append(CHEAT_ROLL)
                print(str(DEBUG_LOG) + ": " + "Cheat roll applied: " + str(CHEAT_ROLL))
                CHEAT_ROLL = 0
            ## The elif below should be an "if" if the above part is commented out.
            elif(dice and dice > 1):
                for i in range(0,dice):
                    roll = random.randrange(1,sides+1)
                    results.append(roll)
                    total += roll
            else:
                roll = random.randrange(1,sides+1)
                results.append(roll)
                total += roll
            resString = ', '.join(map(str,results))
            if(dice and total == dice*sides):
                legend = 'Legendary rolls! '
            elif(not dice and total == sides):
                legend = 'Legendary roll! Nat '
            if (buff == '+'):
                total += mod
            elif (buff == '-'):
                total -= mod
            resString = legend + resString
            return resString,total,legend

        if (getDice(catch) is not None):
            print("TESTING: DICE IS: " + str(getDice(catch)))
            print(getDice(catch))
            if (getDice(catch) == 0):
                message.reply("You're hilarious.")
#            elif (getDice(catch) == 1):
#                message.reply("Why even bother specifying one die? Are you crazy?")
            elif (getDice(catch) > MAX_DICE):
                message.reply("That's a few more than I'm willing to roll. My hands aren't nearly big enough!")
            elif (getSides(catch) == 0):
                message.reply("Why do you hate me?")
            elif (getSides(catch) == 1):
                ONE_TRIG = True
                #resString, total, legend = roller(getDice(catch), getSides(catch), getBuff(catch), getMod(catch), total, legend)
                message.reply("1. The answer is 1. I don't care what you were expecting.")
            elif (getSides(catch) > MAX_SIDES):
                message.reply("That's basically a ball at this point.")
            elif (getBuff(catch) and getMod(catch) == 0):
                message.reply("This joke is really overplayed.")
            elif (getBuff(catch) and getMod(catch) > MAX_MOD):
                message.reply("Can't have that big of a mod, I'm afraid. Try something lower.")
            else:
                print("TESTING: doing a multi-dice roll.")
                resString, total, legend = roller(getDice(catch), getSides(catch), getBuff(catch), getMod(catch), total, legend)
        else:
            print("TESTING: DICE IS: " + str(getDice(catch)))
            if (getSides(catch) == 0):
                message.reply("Why do you hate me?")
            elif (getSides(catch) == 1):
                ONE_TRIG = True
                message.reply("1. The answer is 1. I don't care what you were expecting.")
            elif (getSides(catch) > MAX_SIDES):
                message.reply("That's basically a ball at this point.")
            elif (getBuff(catch) and getMod(catch) == 0):
                message.reply("This joke is really overplayed.")
            elif (getBuff(catch) and getMod(catch) > MAX_MOD):
                message.reply("Can't have that big of a mod, I'm afraid. Try something lower.")
            else:
                if(MAGIC_ROSS and getSides(catch)==20 and not getBuff(catch) and re.search('[rR][oO][sS][sS]',tx(message))):
                    resString = 'Legendary roll! Nat 20!'
                    print (str(DEBUG_LOG) + ": " + "Anti ross:")
                    print (str(DEBUG_LOG) + ": " + str(MAGIC_ROSS))
                    print (str(DEBUG_LOG) + ": " + " getSides(catch):")
                    print (str(DEBUG_LOG) + ": " + str(getSides(catch)))
                    print (str(DEBUG_LOG) + ": " + " Message:")
                    print (str(DEBUG_LOG) + ": " + tx(message))
                #elif (getSides(catch)==2 and not getBuff(catch)):
                #    if (random.randrange(1,3) == 1):
                #        result = 'Heads!'
                #    else:
                #        result = 'Tails!'
                else:
                    print("TESTING: doing a single-die roll.")
                    resString, total, legend = roller(getDice(catch), getSides(catch), getBuff(catch), getMod(catch), total, legend)
        if (resString and ONE_TRIG == False):
            if (getBuff(catch) or (getDice(catch) and getDice(catch) > 1)):
                if (TOTAL_FRONT):
                    resString = 'Total: ' + str(total) + '. ' + resString
                else:
                    resString = resString + '. Total: ' + str(total)
            message.reply("Your results:   " + resString)
    #else:
    #    print ("Unmatching message caught.") # this is just for debugging.
##
 

#    message.reply('You said: ' + message._body.get('text'))
#    print(tx(message))
#    message.reply('You want me to roll a ' + re.findall('[\d]+',re.findall('[dD][\d]+$',tx(message)).pop(0)).pop(0))
###

######
## Backronyms!
###
# game_mode is to specify which part of the game we are in. 0 is inactive, 1 is
#  game prep, 2 is waiting for word, 3 is waiting for answers, 4 is waiting for
#  winner.
BACKRONYMS_GAME_MODE = 0
# host is to specify the person who is hosting the game.
BACKRONYMS_HOST = None
# waiting is a list of players who want to join next round
BACKRONYMS_WAITING = []
# words is a list of players and their answers
BACKRONYMS_WORDS = {}
# scores are changed to negative if the person is not playing. a score of 0 is changed to None when inactive.
BACKRONYMS_SCORES = {}
# key is the keyword to trigger backronyms commands
BACKRONYMS_KEY = "bk"
# WORD is the word being used as the point for backronyms
BACKRONYMS_word = ""
# family is a boolean determining if the Backronyms bot is family-friendly.
BACKRONYMS_FAMILY = True
###
### General functions.
def backronymsDeactivatePlayer(player):
    global BACKRONYMS_SCORES
    if player in BACKRONYMS_SCORES:
        if BACKRONYMS_SCORES[player] == 0:
            BACKRONYMS_SCORES[player] = None
        elif BACKRONYMS_SCORES[player] > 0:
            BACKRONYMS_SCORES[player] = 0 - BACKRONYMS_SCORES[player]
        else:
            return 1
        return BACKRONYMS_SCORES[player]
    else:
        return 0
#
def backronymsActivatePlayer(player):
    global BACKRONYMS_SCORES
    if player in BACKRONYMS_SCORES:
        if BACKRONYMS_SCORES[player] == None:
            BACKRONYMS_SCORES[player] = 0
        elif BACKRONYMS_SCORES[player] < 0:
            BACKRONYMS_SCORES[player] = 0 - BACKRONYMS_SCORES[player]
        else:
            return -1
        return BACKRONYMS_SCORES[player]
    else:
        BACKRONYMS_SCORES[player] = 0
        return None
#
def backronymsEndGame():
    global BACKRONYMS_SCORES,BACKRONYMS_GAME_MODE,BACKRONYMS_HOST,BACKRONYMS_WAITING,BACKRONYMS_word,BACKRONYMS_WORDS
    BACKRONYMS_GAME_MODE = 0
    BACKRONYMS_HOST = None
    BACKRONYMS_WAITING = []
    BACKRONYMS_word = ""
    BACKRONYMS_WORDS = {}
    for i in zUp(BACKRONYMS_SCORES):
        backronymsDeactivatePlayer(i)
###
@listen_to("^" + BACKRONYMS_KEY + ": get ready!$",re.IGNORECASE)
def backronymsStart(message):
    global BACKRONYMS_GAME_MODE,BACKRONYMS_HOST,BACKRONYMS_SCORES
    global DEBUG_LOG
    DEBUG_LOG = DEBUG_LOG + 1
    
    print (str(DEBUG_LOG) + ": " +
            "Trying to sign up." +
            " Current game mode: %s.\nCurrent host is %s.\nCurrent active player count is %s.\nActivating player is %s." %
            (str(BACKRONYMS_GAME_MODE),BACKRONYMS_HOST if BACKRONYMS_HOST else "not set",str(len(zUp(BACKRONYMS_SCORES))),uWrap(message)))

    if BACKRONYMS_GAME_MODE == 0:
        BACKRONYMS_GAME_MODE = 1
        BACKRONYMS_HOST = uWrap(message)
        backronymsActivatePlayer(uWrap(message))
        backSend(message,"Who's ready for a game of BACKRONYMS" + 
                (", bitches" if not BACKRONYMS_FAMILY else "") + 
                "!\nLet's see a show of " + 
                ("fuckin' " if not BACKRONYMS_FAMILY else "") + 
                "hands! Say `" +
                BACKRONYMS_KEY + ": I'm in` if you want to play!\nIf you want to see a list of commands, type `"+
                BACKRONYMS_KEY + ": help`!" +
                (" Hopefully you're not stupid enough to need it!" if not BACKRONYMS_FAMILY else ""))
    elif BACKRONYMS_GAME_MODE == 1:
        backSend(message,"We're still prepping for a game! No need to start another one! Gosh!")
    else:
        backSend(message,"There's already a game underway" + 
                (", dipshit!" if not BACKRONYMS_FAMILY else "! Gosh!"))
###
@listen_to('^' + BACKRONYMS_KEY + ': get players$',re.IGNORECASE)
def backronymsGetPlayers(message):
    global DEBUG_LOG
    DEBUG_LOG = DEBUG_LOG + 1
    
    print (str(DEBUG_LOG) + ": " +
            "Trying to sign up." +
            " Current game mode: %s.\nCurrent host is %s.\nCurrent active player count is %s.\nActivating player is %s." %
            (str(BACKRONYMS_GAME_MODE),BACKRONYMS_HOST if BACKRONYMS_HOST else "not set",str(len(zUp(BACKRONYMS_SCORES))),uWrap(message)))

    if uWrap(message) == BACKRONYMS_HOST:
        if BACKRONYMS_SCORES:
            retVal = ', '.join(list(BACKRONYMS_SCORES.keys()))
            backSend(message,"These are the current registered players: " + retVal)
        else:
            backSend(message,"There are no registered players.")
            return
        if zUp(BACKRONYMS_SCORES):
            retVal = ', '.join(zUp(BACKRONYMS_SCORES))
            backSend(message,"These are the current active players: " + retVal)
        else:
            backSend(message,"There are no active players at this time.")
###
@listen_to("^" + BACKRONYMS_KEY + ": nudge players$",re.IGNORECASE)
def backronymsNudge(message):
    global DEBUG_LOG
    DEBUG_LOG = DEBUG_LOG + 1
    
    print (str(DEBUG_LOG) + ": " +
            "Trying to sign up." +
            " Current game mode: %s.\nCurrent host is %s.\nCurrent active player count is %s.\nActivating player is %s." %
            (str(BACKRONYMS_GAME_MODE),BACKRONYMS_HOST if BACKRONYMS_HOST else "not set",str(len(zUp(BACKRONYMS_SCORES))),uWrap(message)))

    if uWrap(message) == BACKRONYMS_HOST and BACKRONYMS_GAME_MODE == 3:
        resLis = []
        for i in zUp(BACKRONYMS_SCORES):
            if i not in BACKRONYMS_WORDS:
                resLis.append(i)
        backSend(message,', '.join(resLis) + 
                (": for fuck's sake hurry it up and put in your goddamn answer! It's probably going to be shit anyway!" if not BACKRONYMS_FAMILY else ": you have yet to enter your words for this round! If you've forgotten the word, you can get it with `" +
                BACKRONYMS_KEY + ": get word`!"))
    elif uWrap(message) == BACKRONYMS_HOST:
        backSend(message,( "Calm the fuck down sparky, it's not time for that!" if not BACKRONYMS_FAMILY else "You can only nudge the other players when you are waiting for them to enter their answers!"))
###
@listen_to("^" + BACKRONYMS_KEY + ": get score$",re.IGNORECASE)
def backronymsGetScore(message):
    global DEBUG_LOG
    DEBUG_LOG = DEBUG_LOG + 1
    
    print (str(DEBUG_LOG) + ": " +
            "Trying to sign up." +
            " Current game mode: %s.\nCurrent host is %s.\nCurrent active player count is %s.\nActivating player is %s." %
            (str(BACKRONYMS_GAME_MODE),BACKRONYMS_HOST if BACKRONYMS_HOST else "not set",str(len(zUp(BACKRONYMS_SCORES))),uWrap(message)))

    if uWrap(message) in BACKRONYMS_SCORES:
        if BACKRONYMS_SCORES[uWrap(message)] == None:
            score = str(0) + ". You are currently listed as inactive"
        elif BACKRONYMS_SCORES[uWrap(message)] < 0:
            score = str(0 - BACKRONYMS_SCORES[uWrap(message)]) + ". You are currently listed as inactive"
        else:
            score = BACKRONYMS_SCORES[uWrap(message)]
        backSend(message,uWrap(message) + ", your score is %s." % score)
###
@listen_to("^" + BACKRONYMS_KEY + ": I'?m in$",re.IGNORECASE)
def backronymsSignUp(message):
    global BACKRONYMS_SCORES,BACKRONYMS_GAME_MODE
    global DEBUG_LOG
    DEBUG_LOG = DEBUG_LOG + 1
    print (str(DEBUG_LOG) + ": " +
            "Trying to sign up." +
            " Current game mode: %s.\nCurrent host is %s.\nCurrent active player count is %s.\nActivating player is %s." %
            (str(BACKRONYMS_GAME_MODE),BACKRONYMS_HOST if BACKRONYMS_HOST else "not set",str(len(zUp(BACKRONYMS_SCORES))),uWrap(message)))
    if BACKRONYMS_GAME_MODE == 1 and uWrap(message) not in zUp(BACKRONYMS_SCORES):
        backronymsActivatePlayer(uWrap(message))
        backSend(message,"You have been added to the game, " + uWrap(message) + "!" +
                (" Try not to fuck it up, idiot!"if not BACKRONYMS_FAMILY else "") )
    elif BACKRONYMS_GAME_MODE > 1:
        backronymsJoinQueue(message)
    elif uWrap(message) in zUp(BACKRONYMS_SCORES):
        backSend(message,"You're already in the game, " + 
                ("fuckstick!" if not BACKRONYMS_FAMILY else "silly!"))
###
@listen_to("^" + BACKRONYMS_KEY + ": game on!?$",re.IGNORECASE)
def backronymsStartGame(message):
    global BACKRONYMS_GAME_MODE,BACKRONYMS_HOST,BACKRONYMS_SCORES,BACKRONYMS_word
    global DEBUG_LOG
    DEBUG_LOG = DEBUG_LOG + 1
    print (str(DEBUG_LOG) + ": " +
            "Trying to sign up." +
            " Current game mode: %s.\nCurrent host is %s.\nCurrent active player count is %s.\nActivating player is %s." %
            (str(BACKRONYMS_GAME_MODE),BACKRONYMS_HOST if BACKRONYMS_HOST else "not set",str(len(zUp(BACKRONYMS_SCORES))),uWrap(message)))
    if uWrap(message) == BACKRONYMS_HOST and BACKRONYMS_GAME_MODE == 1:
        if len(zUp(BACKRONYMS_SCORES)) < 2:
            backSend(message,"You can't just play Backronyms with only one person! " + 
                    ("How thick are you?!" if not BACKRONYMS_FAMILY else "Gosh!"))
        else:
            BACKRONYMS_GAME_MODE = 2
            pList = ', '.join(zUp(BACKRONYMS_SCORES))
            BACKRONYMS_word = ""
            backSend(message,("About fuckin' time! " if not BACKRONYMS_FAMILY else "And away we go! ") + pList + ", we are starting the game" + 
                    (" so turn your god damn brains on!" if not BACKRONYMS_FAMILY else "!") + 
                    " The host for the first round is: " + BACKRONYMS_HOST + "! Start us off with `" +
                    BACKRONYMS_KEY + ": set WORD`" + 
                    (", and try not to pick something completely retarded!" if not BACKRONYMS_FAMILY else "!") )
    else:
        print("User is: " + uWrap(message))
        if BACKRONYMS_HOST:
            print("Host is: " + BACKRONYMS_HOST)
        print("Game mode is: " + str(BACKRONYMS_GAME_MODE))
###
@listen_to("^" + BACKRONYMS_KEY + ": set (.*)$")
def backronymsSetWord(message,word):
    global BACKRONYMS_GAME_MODE,BACKRONYMS_HOST,BACKRONYMS_WORDS,BACKRONYMS_SCORES,BACKRONYMS_word
    global DEBUG_LOG
    DEBUG_LOG = DEBUG_LOG + 1
    print (str(DEBUG_LOG) + ": " +
            "Trying to sign up." +
            " Current game mode: %s.\nCurrent host is %s.\nCurrent active player count is %s.\nActivating player is %s." %
            (str(BACKRONYMS_GAME_MODE),BACKRONYMS_HOST if BACKRONYMS_HOST else "not set",str(len(zUp(BACKRONYMS_SCORES))),uWrap(message)))
    if uWrap(message) not in BACKRONYMS_SCORES:
        backSend(message,"Uh, you aren't even registered, fucktard." if not BACKRONYMS_FAMILY else "Sorry, but you are not a registered player.")
        return
    if uWrap(message) == BACKRONYMS_HOST and BACKRONYMS_GAME_MODE == 2:
        BACKRONYMS_word = word
        backSend(message,"Alright " + 
                (" losers, " if not BACKRONYMS_FAMILY else "then! ") + word + " is the word! " +
                ', '.join([i for i in zUp(BACKRONYMS_SCORES) if i != BACKRONYMS_HOST]) +
                ", send in your answers with `" +
                BACKRONYMS_KEY + ": set ANSWER`" + 
                (" and for the love of god keep it interesting, you boring fucks." if not BACKRONYMS_FAMILY else "!")) # Consider adding ability to reset word?
        BACKRONYMS_GAME_MODE = 3
    elif BACKRONYMS_GAME_MODE == 2:
        backSend(message,"Real fuckin' smart, guy. There isn't even a word to answer to yet. Or did you think you were the host or something? Jesus." if not BACKRONYMS_FAMILY else "You may not send an answer until the host has picked a word, sorry!")
    elif uWrap(message) == BACKRONYMS_HOST and BACKRONYMS_GAME_MODE == 3:
        backSend(message,"Yeah, you already put a god damn word in, genius. Maybe wait a couple fucking minutes for the answers to come in?" if not BACKRONYMS_FAMILY else "It is time for the others to post their answers, gosh!")
    elif BACKRONYMS_GAME_MODE == 3 and uWrap(message) not in BACKRONYMS_WORDS:
        BACKRONYMS_WORDS[uWrap(message)] = word
        backSend(message,uWrap(message) + ": Your answer has been received!" +
                (" Yeugh." if not BACKRONYMS_FAMILY else ""))
        done = True
        for i in zUp(BACKRONYMS_SCORES):
            if not i == BACKRONYMS_HOST and not i in BACKRONYMS_WORDS:
                done = False
        if done:
            backSend(message,"All answers have been put in! " + 
                    ("If you can call them that. " if not BACKRONYMS_FAMILY else "") +
                    BACKRONYMS_HOST + ", it is time to pick a" + 
                    (", ahem, _winner_." if not BACKRONYMS_FAMILY else "winner!") + " Type `" +
            BACKRONYMS_KEY + ": get answers` to see a list of all answers and who picked them" + 
            (", since you probably fucking forgot already" if not BACKRONYMS_FAMILY else "") + 
            ". To pick a winner, type `" +
            BACKRONYMS_KEY + ": pick @user`" + 
            (". Good luck, with these answers." if not BACKRONYMS_FAMILY else "!"))
            BACKRONYMS_GAME_MODE = 4
    elif BACKRONYMS_GAME_MODE == 3:
        backSend(message,"You've already sent in your answer! Too late to change it now" + 
            (", cockmunch!" if not BACKRONYMS_FAMILY else "!")) # maybe add in a feature to let them change it?
    else:
        backSend(message,"This is neither the time to specify a word nor to send in an answer! " + 
            ("Jesus Christ dude, what the fuck?!" if not BACKRONYMS_FAMILY else "C'mon!"))
###
@listen_to("^" + BACKRONYMS_KEY + ": get word$",re.IGNORECASE)
def backronymsGetWord(message):
    global DEBUG_LOG
    DEBUG_LOG = DEBUG_LOG + 1
    print (str(DEBUG_LOG) + ": " +
            "Trying to sign up." +
            " Current game mode: %s.\nCurrent host is %s.\nCurrent active player count is %s.\nActivating player is %s." %
            (str(BACKRONYMS_GAME_MODE),BACKRONYMS_HOST if BACKRONYMS_HOST else "not set",str(len(zUp(BACKRONYMS_SCORES))),uWrap(message)))
    if BACKRONYMS_word:
        backSend(message,"The current word is: \"" + BACKRONYMS_word + "\".")
    else:
        backSend(message,"There is no word set at this time.")
###
@listen_to("^" + BACKRONYMS_KEY + ": get answers$",re.IGNORECASE)
def backronymsGetAnswers(message):
    global DEBUG_LOG
    DEBUG_LOG = DEBUG_LOG + 1
    print (str(DEBUG_LOG) + ": " +
            "Trying to sign up." +
            " Current game mode: %s.\nCurrent host is %s.\nCurrent active player count is %s.\nActivating player is %s." %
            (str(BACKRONYMS_GAME_MODE),BACKRONYMS_HOST if BACKRONYMS_HOST else "not set",str(len(zUp(BACKRONYMS_SCORES))),uWrap(message)))
    if BACKRONYMS_WORDS:
        answer = "```"
        for i in BACKRONYMS_WORDS:
            answer = answer + i + ": " + BACKRONYMS_WORDS[i] + "\n"
        answer = answer + "```"
        backSend(message,answer)
    else:
        backSend(message,"There are no stored answers at this time." +
            (" What, did you completely forget what the fuck was going on or something?" if not BACKRONYMS_FAMILY else ""))
###
@listen_to("^" + BACKRONYMS_KEY + ": pick (.*)$",re.IGNORECASE)
def backronymsPickWinner(message,winner):
    global BACKRONYMS_GAME_MODE,BACKRONYMS_HOST,BACKRONYMS_WORDS,BACKRONYMS_SCORES,BACKRONYMS_WAITING,BACKRONYMS_word
    global DEBUG_LOG
    DEBUG_LOG = DEBUG_LOG + 1
    
    print (str(DEBUG_LOG) + ": " +
            "Trying to sign up." +
            " Current game mode: %s.\nCurrent host is %s.\nCurrent active player count is %s.\nActivating player is %s." %
            (str(BACKRONYMS_GAME_MODE),BACKRONYMS_HOST if BACKRONYMS_HOST else "not set",str(len(zUp(BACKRONYMS_SCORES))),uWrap(message)))

    if uWrap(message) == BACKRONYMS_HOST:
        if BACKRONYMS_GAME_MODE != 4:
            backSend(message,"Oh yeah? You're just gonna pick a winner right now, huh? It's not even close to the right time for that, you thick-skulled neanderthal!" if not BACKRONYMS_FAMILY else "It's not time to pick a winner yet, silly!")
        elif winner not in BACKRONYMS_SCORES:
            backSend(message,"Oh sure, let's just pick fucking' *anyone* to be a winner now, right? Doesn't matter if they're playing! Try again, douchebag." if not BACKRONYMS_FAMILY else "That person isn't even playing! C'mon!")
        elif uWrap(message) == winner:
            backSend(message,"Not on my watch, you ball-gargling cumdumpster. Try the fuck again." if not BACKRONYMS_FAMILY else "You can't pick yourself, you goof!")
        else:
            if winner in zUp(BACKRONYMS_SCORES):
                score = BACKRONYMS_SCORES[winner] = BACKRONYMS_SCORES[winner] + 1
            else:
                if not BACKRONYMS_SCORES[winner]:
                    BACKRONYMS_SCORES[winner] = -1
                else:
                    BACKRONYMS_SCORES[winner] = BACKRONYMS_SCORES[winner] - 1
                score = 0 - BACKRONYMS_SCORES[winner]
            backSend(message,winner + ": Congratulations! Your entry, \"" + 
                    BACKRONYMS_WORDS[winner] + "\", is the winner! +1 point for you, for a total of %s!" %
                    str(score) + 
                    (" Don't let it go to your head though, assface." if not BACKRONYMS_FAMILY else ""))
            BACKRONYMS_GAME_MODE = 2
            BACKRONYMS_WORDS = {}
            BACKRONYMS_word = ""
            if winner in zUp(BACKRONYMS_SCORES):
                BACKRONYMS_HOST = winner
                backSend(message,winner + ": You are now the host for this next round! " + 
                        ("And I just cannot *WAIT* to see how you're going to fuck this up. " if not BACKRONYMS_FAMILY else "") + "Type `"+ 
                        BACKRONYMS_KEY + ": set WORD` to pick your word for this round!")
            else:
                backSend(message,uWrap(message) + ", you will reamin the host. " + 
                        ("Oh joy of all fucking joys. " if not BACKRONYMS_FAMILY else "") + "Type `" +
                        BACKRONYMS_KEY + ": set WORD` to pick your word for this round!")
            if BACKRONYMS_WAITING:
                for i in BACKRONYMS_WAITING:
                    backronymsActivatePlayer(i)
                backSend(message,"Those of you in the waiting list: " +
                        ', '.join(BACKRONYMS_WAITING) + 
                        " have been added to the game! " + 
                        ("Your deaths will be swift. " if not BACKRONYMS_FAMILY else "") + "You may enter your answers once the word has been picked!")
                BACKRONYMS_WAITING = []
    else:
        backSend(message,"If that's what it takes to make you feel special, sure. Just kidding; fuck you." if not BACKRONYMS_FAMILY else "You're not the host, silly!")
###
@listen_to("^" + BACKRONYMS_KEY + ": me next$")
def backronymsJoinQueue(message):
    global BACKRONYMS_WAITING,BACKRONYMS_SCORES
    global DEBUG_LOG
    DEBUG_LOG = DEBUG_LOG + 1
    
    print (str(DEBUG_LOG) + ": " +
            "Trying to sign up." +
            " Current game mode: %s.\nCurrent host is %s.\nCurrent active player count is %s.\nActivating player is %s." %
            (str(BACKRONYMS_GAME_MODE),BACKRONYMS_HOST if BACKRONYMS_HOST else "not set",str(len(zUp(BACKRONYMS_SCORES))),uWrap(message)))

    if uWrap(message) in BACKRONYMS_WAITING:
        backSend(message,"You're already in the damn queue, how did you already forget? Did you get thrown around the back of a moving truck as an infant?" if not BACKRONYMS_FAMILY else "You're already in the queue!")
    elif BACKRONYMS_GAME_MODE == 1:
        backronymsSignUp(message)
    elif BACKRONYMS_GAME_MODE == 0:
        backSend(message,"I'm trying to take a nap over here, for the love of god. Bother somebody else." if not BACKRONYMS_FAMILY else "There isn't a game in progress!")
    elif uWrap(message) in zUp(BACKRONYMS_SCORES):
        backSend(message,"Do I really need to tell you why this is stupid? Did you seriously forget you're already playing? God damn I need a break from this bullshit." if not BACKRONYMS_FAMILY else "You're already playing! C'mon!")
    else:
        BACKRONYMS_WAITING.append(uWrap(message))
        backSend(message,uWrap(message) + ", you have been added to the queue. See you next round" + 
                (" -- if you live that long." if not BACKRONYMS_FAMILY else "!"))
###
@listen_to("^" + BACKRONYMS_KEY + ": drop out$")
def backronymsDropOut(message,player=None):
    global BACKRONYMS_WAITING,BACKRONYMS_SCORES,BACKRONYMS_WORDS,BACKRONYMS_HOST,BACKRONYMS_GAME_MODE
    global DEBUG_LOG
    DEBUG_LOG = DEBUG_LOG + 1
    
    print (str(DEBUG_LOG) + ": " +
            "Trying to sign up." +
            " Current game mode: %s.\nCurrent host is %s.\nCurrent active player count is %s.\nActivating player is %s." %
            (str(BACKRONYMS_GAME_MODE),BACKRONYMS_HOST if BACKRONYMS_HOST else "not set",str(len(zUp(BACKRONYMS_SCORES))),uWrap(message)))

    if not player:
        if uWrap(message) == BACKRONYMS_HOST:
#            backSend(message,"You're the host! At least pick a winner first!")
            # instead we're kicking everyone out if it's the host.
            backronymsDeactivatePlayer(uWrap(message))
            if len(zUp(BACKRONYMS_SCORES)) > 0:
                backSend(message,', '.join(zUp(BACKRONYMS_SCORES)) +
                        ": as the host has left, the game has ended. Your scores have been saved." +
                        (" Sorry to have wasted your precious time." if not BACKRONYMS_FAMILY else ""))
            else:
                backSend(message,"Oh sure, just wake me up for nothing. Thanks a whole fucking lot, dickweed." if not BACKRONYMS_FAMILY else "Well nevermind then. See you next time!")
            backronymsEndGame()
            return
        elif uWrap(message) in BACKRONYMS_WAITING:
            BACKRONYMS_WAITING.remove(uWrap(message))
            backSend(message,"You have been removed from the waiting list.")
        elif uWrap(message) in zUp(BACKRONYMS_SCORES):
            backronymsDeactivatePlayer(uWrap(message))
            backSend(message,"You have been removed from the active list. Your score has been saved!" + 
                    (" Your soul won't be, though." if not BACKRONYMS_FAMILY else "" ))
            if len(zUp(BACKRONYMS_SCORES)) < 2:
                backSend(message,"Great, everyone's left. Just great. Whatever. I'm going to sleep. See if you fucks can leave me be." if not BACKRONYMS_FAMILY else "There are now too few people to play right now. The game will be ended, but your scores will be saved! Play again some time!")
                backronymsEndGame()
                return
            done = True
            for i in zUp(BACKRONYMS_SCORES):
                if i not in BACKRONYMS_WORDS:
                    done = False
            if done:
                backSend(message,"With this dropping-out, all " + 
                        ("sorry excuses for " if not BACKRONYMS_FAMILY else "") + "answers have been put in!\n" +
                        BACKRONYMS_HOST + ", it is time to pick a winner! Type `" +
                        BACKRONYMS_KEY + ": get answers` to see a list of all answers " + 
                        ("(since your fat stupid head probably already forgot) " if not BACKRONYMS_FAMILY else "") + "and who picked them. To pick a winner, type `" +
                        BACKRONYMS_KEY + ": pick @user`!" +
                        (" Using the word 'winner' lightly, of course." if not BACKRONYMS_FAMILY else ""))
                BACKRONYMS_GAME_MODE = 4
        else:
            backSend(message,"Yeah, you're not even playing, dipshit. God." if not BACKRONYMS_FAMILY else "You aren't on either the active or the waiting list. No dropping out needed!")
    # targeted kicking section"
    else:
        if player == uWrap(message):
            backSend(message,"I know words must be terribly confusing for you, given how much of a blithering idiot you are, but targeting yourself makes zero sense. Got it?" if not BACKRONYMS_FAMILY else "You can't target yourself. You goof!")
        elif player in BACKRONYMS_WAITING:
            BACKRONYMS_WAITING.remove(player)
            backSend(message,"%s has been graciously freed from this miserable 'game' before they could suffer. How gracious of you." % player if not BACKRONYMS_FAMILY else "Ok, %s has been removed from the waiting list." % player)
        elif player in zUp(BACKRONYMS_SCORES):
            backronymsDeactivatePlayer(player)
            backSend(message,player + " has been removed from the active list, and their score has been saved." + 
                    (" It's far too late for their soul, however." if not BACKRONYMS_FAMILY else  ""))
            if len(zUp(BACKRONYMS_SCORES)) < 2:
                backSend(message,"Great. Now there aren't enough people to even play. Thanks for wasting my fucking time." if not BACKRONYMS_FAMILY else "There are now too few people to play right now. The game will be ended, but your scores will be saved! Play again some time!")
                backronymsEndGame()
                return
            done = True
            for i in zUp(BACKRONYMS_SCORES):
                if i not in BACKRONYMS_WORDS:
                    done = False
            if done:
                backSend(message,"With this " + 
                        ("sadly bloodless " if not BACKRONYMS_FAMILY else "") + 
                        "kicking-out, all answers have been put in! " +
                        BACKRONYMS_HOST + ", it is time to pick a " + 
                        ("~sucker~ " if not BACKRONYMS_FAMILY else "") + 
                        "winner! Type `" +
                        BACKRONYMS_KEY + ": get answers` to see a list of all answers" + 
                        (" -- if you can even call them that --" if not BACKRONYMS_FAMILY else "") + 
                        " and who picked them. To pick a winner, type `" +
                        BACKRONYMS_KEY + ": pick @user`!")
                BACKRONYMS_GAME_MODE = 4
        else:
            backSend(message,"Sure, that makes perfect sense. Kick the person not even playing. God you people suck." if not BACKRONYMS_FAMILY else player + " isn't on either the active or the waiting list. No kicking out needed!")

### For the kicking-out function, we call the Drop-Out function because it uses
###  a lot of the same code -- but with the player flag set.
@listen_to("^" + BACKRONYMS_KEY + ": kick (.*)$",re.IGNORECASE)
def backronymsKickUser(message,player):
    global DEBUG_LOG
    DEBUG_LOG = DEBUG_LOG + 1
    
    print (str(DEBUG_LOG) + ": " +
            "Trying to sign up." +
            " Current game mode: %s.\nCurrent host is %s.\nCurrent active player count is %s.\nActivating player is %s." %
            (str(BACKRONYMS_GAME_MODE),BACKRONYMS_HOST if BACKRONYMS_HOST else "not set",str(len(zUp(BACKRONYMS_SCORES))),uWrap(message)))

    if uWrap(message) == BACKRONYMS_HOST:
        backronymsDropOut(message,player)
    else:
        backSend(message,"As much as I'd like to be rid of every single one of you, only the host can kick people, shit-for-brains." if not BACKRONYMS_FAMILY else "You can only kick out people when you're the host!")
### Functions for enabling and disabling family-friendly mode.
@listen_to("^" + BACKRONYMS_KEY + ": calm down$")
def backronymsFamilyToggle(message,on=True):
    global BACKRONYMS_FAMILY
    if on:
        backSend(message,"Alright, I'm sorry. I definitely got carried away there. I hope we can all have fun together!")
        BACKRONYMS_FAMILY = True
    else:
        backSend(message,"Fuck you too, bitch!")
        BACKRONYMS_FAMILY = False
###
@listen_to("^" + BACKRONYMS_KEY + ": fuck you$")
def backronymsFamilyNope(message):
    backronymsFamilyToggle(message,False)
###
@listen_to("^" + BACKRONYMS_KEY + ": help$")
def backronymsHelp(message):
    global DEBUG_LOG
    DEBUG_LOG = DEBUG_LOG + 1
    
    print (str(DEBUG_LOG) + ": " +
            "Trying to sign up." +
            " Current game mode: %s.\nCurrent host is %s.\nCurrent active player count is %s.\nActivating player is %s." %
            (str(BACKRONYMS_GAME_MODE),BACKRONYMS_HOST if BACKRONYMS_HOST else "not set",str(len(zUp(BACKRONYMS_SCORES))),uWrap(message)))

    backSend(message,"The following commands can be given by typing `" +
            BACKRONYMS_KEY + ": COMMAND`. The list of commands is as follows:" +
            """```"get ready!" -- Starts a game of Backronyms. Only usable by admin users.
"get players" -- Provides a list of all players registered for the current game.
"get score" -- Provides your score.
"I'm in" -- Registers yourself for the current game. Only usable during the pre-game period.
"game on" -- Starts the game once players have been registered. Only usable by the host pre-game.
"set WORD/Answer" -- When used as the host, specifies the word for this round. When used as another player, locks in your answer for this round.
"get answers" -- Provides all answers given this round.
"get word" -- Provides the word that has been picked this round.
"nudge players" -- Pings the players who have yet to provide an answer this round. Only usable by the host.
"pick @user" -- Picks the winner for this round.
"me next" -- Adds you to the waiting list for the next round, if you aren't in the game yet.
"drop out" -- Removes you from the game, but saves your score. You can come back later with "me next".
"kick PLAYER" -- Removes target player from the game, and saves their score. Only usable by the current host.
"fuck you" -- Disables family-friendly mode.
"calm down" -- Enables family-friendly mode.
"help" -- Print this help message.```""")
######
## WebDiplomacy / Wartent functions
###
@listen_to('^\.setwartent (.*)$')
def setWarTent(message, channel):
    global WARTENT
    if isAdmin(message,CONTROLLERS):
        WARTENT = re.findall('\#(C.{8})',channel)[0]
        if WARTENT:
            message.reply("Default channel set to %s, ID %s." %
                (channel,WARTENT))
        else:
            message.reply("That doesn't appear to be a link to a channel. Try again with a #-linked channel name.")

@respond_to('^wartent (.*)$')
def sendWarMessage(message,mReal): 
    if not WARTENT:
        message.reply("Sorry, the WarTent channel hasn't been set. If the default channel is set, I'll try sending there.")
        if DEFAULT_CHANNEL or BACK_CHAN:
            temp = message.body['channel']
            if DEFAULT_CHANNEL:
                message.body['channel'] = DEFAULT_CHANNEL
            else:
                message.body['channel'] = BACK_CHAN
            message.send("Hey admins, please set the WarTent channel! Someone would like to use it!")
            message.body['channel'] = temp
        else:
            message.reply("I'm sorry, the default channel wasn't set either. See if you can discreetly get an admin's attention to set it.")
    if message.body['channel'][:1] == 'D':
        temp = message.body['channel']
        message.body['channel'] = WARTENT
        warSend(message,"`BEGIN WARTENT MESSAGE`\n%s\n`END WARTENT MESSAGE`" % mReal)
        message.body['channel'] = temp
    else:
        message.reply("I'd advise against trying that in a public channel..kind of defeats the whole point of the War Tent, no?")
###
#####
### Country-to-country anonymous communication functions
MIN_COUNTRIES = 7
MAX_COUNTRIES = 7
COUNTRIES_SET = c.execute("SELECT * from countries") # the execute function returns the number of results found.
PREVENT_SEND_PRE_MIN = True # no one will be allowed to send messages until all countries have been set. This will help prevent sneaky people from trying to determine who's who.
COUNTRY_SAFETY = True
##
@listen_to('^.countrySafetyOff$')
def countrySafetyOff(message):
    global COUNTRY_SAFETY
    if isAdmin(message,CONTROLLERS):
        COUNTRY_SAFETY = False
        message.reply("Warning! Country delete safety has been turned off. All country data may now be deleted. Handle with care!")
#
@listen_to('^.clearCountryData$')
def clearCountryData(message):
    global COUNTRY_SAFETY
    if isAdmin(message,CONTROLLERS) and not COUNTRY_SAFETY:
        c.execute('DELETE FROM countries')
        conn.commit()
        COUNTRY_SAFETY = True
        message.reply("All country data has been deleted and the deletion safety has been reset. Please have everyone re-register themselves by DM'ing me the phrase `setcountry CountryName` (case insensitive).") 
#
def getCountryData():
    c.execute("SELECT country,id FROM countries")
    result = ([],[])
    data = c.fetchall()
    if data:
        for i in data:
            result[0].append(i[0].lower())
            result[1].append(i[1])
    return result
#
@respond_to('^setcountry (.*)$', re.IGNORECASE)
def setCountry(message,country):
    global COUNTRIES_SET
    data = getCountryData()
    if message.body['channel'] in data[1]:
        message.reply("You've already set a country for yourself, you know. It's %s, in case you've forgotten." % (data[0][data[1].index(message.body['channel'])])) # this gets the associated country with the channel in question.
    elif country in data[0]:
        message.reply("The country has already been set. Is there trickery afoot...?")
    elif not COUNTRIES_SET < MAX_COUNTRIES:
        message.reply("Uh oh, the max number of countries has already been set. Did someone steal your spot?")
    elif not message.body['channel'][:1] == 'D':
        message.reply("You should really only set your country in a private message to me.")
    else:
        c.execute("INSERT INTO countries VALUES('%s','%s')" % (country,message.body['channel']))
        conn.commit()
        COUNTRIES_SET = COUNTRIES_SET + 1
        message.reply("Your country has been set as %s per your request. Messages sent addressed to it will be sent to you by me in this channel." % (country))
#
@respond_to('^tocountry (.*)$', re.IGNORECASE)
def sendCountryMessage(message,mReal):
    if PREVENT_SEND_PRE_MIN and MIN_COUNTRIES > COUNTRIES_SET:
        message.reply("Sorry, all countries need to be set before you can message anyone. Consider sending a wartent announcement to the wartent channel to get the other countries' attention!")
        return
    data = getCountryData()
    result = re.findall("^(\w+)\s+(.*)$",mReal)
    country = ""
    if result:
        (country,mReal) = result[0]
        country = country.lower()
    else:
        message.reply("You need to specify a country first, and then a message.")
        return
    if not data[0]:
        message.reply("There don't appear to be any countries set yet. You should set yours with `setcountry CountryName` and then use a WarTent announcement to ask your target to set theirs!")
    elif message.body['channel'] not in data[1]:
        message.reply("It doesn't look like you've set your country. Set yours by messaging me with `setcountry CountryName`!")
    elif country not in data[0]:
        message.reply("There doesn't seem to be a country by that name. Check spelling maybe?")
    elif not message.body['channel'][:1] == 'D':
        message.reply("You may want to send that to me privately, mate.")
    else:
        sendingCountry = data[0][data[1].index(message.body['channel'])]
        originalChannel = message.body['channel']
        message.body['channel'] = data[1][data[0].index(country)]
        warSend(message,"`BEGIN MESSAGE FROM %s`\n%s\n`END MESSAGE`" % (sendingCountry,mReal))
        message.body['channel'] = originalChannel
#####
##########
## TESTING! TURN _*OFF*_ WHEN NOT TESTING@
######
#@listen_to('.')
#def printAll(message):
#    print(message.body['user'] + ": " + tx(message))
#    pokeSend(message,"This is the speaker: <@" + message.body['user'] + ">")
##@listen_to('^please die$')
##def killBot(message):
##    global bot
##    message.reply("Ok...")
##    bot._dispatcher._killIt = True
######
## END TEST SEGMENT
##########


# main loop
def main():
    global bot
    bot = Bot()
    if IM_BACK:
        print("IT SHOULD WORK")
        m = Message(bot._client,{'channel':BACK_CHAN})
        m.send(BACKSTRING)
        #sys.argv = [sys.argv[0]]
        #print("PRINTING ARGS")
        #for i in sys.argv:
        #    print(i)
        #print("ARGS PRINTED")
        print("IT SHOULD HAVE WORKED")
    print("THE BOT IS ABOUT TO RUN")
    bot.run()
    print("THE BOT DONE RUN") # never prints

if __name__ == "__main__":
    main()
