from slackbot.bot import respond_to
from slackbot.bot import listen_to
from os.path import dirname
from slackbot.bot import Bot
import inspect
import re
import random
import pymysql
#import mysql.connector
import os
import string

#### local files
import pokemon
import magic
from macros import *
from orcwarrior import *

####

# MYSQL connector data. 
DB_PASSWORD = os.environ['DB_PASSWORD']
SECRET_ADMIN = os.environ['SECRET_ADMIN']
MYSQL_USER = 'dicemaster'
MYSQL_DB = 'dicemaniac'
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
#####

#####
### miscellaneous
#NO_COUNT = 0
@listen_to('^magic conch.*\?',re.IGNORECASE)
def magicConch(message):
    i = random.randint(1,5)
    text = ''
    #global NO_COUNT
    if i == 1:
        text = 'Maybe someday.'
    elif i == 2:
        text = 'I don\'t think so.'
    elif i == 3:
        #if NO_COUNT < 3:
            text = 'No.'
        #    NO_COUNT += 1
        #else:
        #    text = '_sassily_ No.'
    elif i == 4:
        text = 'Yes.'
    elif i == 5:
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
    message.reply('BEEP DEPLOY GREETING BOOP HELLO BEEP GREETING DEPLOYED')

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
            elif(dice):
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
            elif (getDice(catch) == 1):
                message.reply("Why even bother specifying one die? Are you crazy?")
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
            if (getBuff(catch) or getDice(catch)):
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
# game_prep is to determine if we're in the stage of getting people signed up.
BACKRONYMS_GAME_PREP = False
# game_live is to determine if there is currently an active game.
BACKRONYMS_GAME_LIVE = False
# game_mode is to specify which part of the game we are in. 0 is inactive, 1 is
#  game prep, 2 is waiting for word, 3 is waiting for answers, 4 is waiting for
#  winner.
BACKRONYMS_GAME_MODE = 0
# host is to specify the person who is hosting the game.
BACKRONYMS_HOST = None
# players is a list of players as mentions
BACKRONYMS_PLAYERS = []
# waiting is a list of players who want to join next round
BACKRONYMS_WAITING = []
# words is a list of players and their answers
BACKRONYMS_WORDS = {}
# scores is a list of the scores of all players. NOTE: in the process of changing to NOT use PLAYERS variable
#  NOTE: scores are changed to negative if the person is not playing. a score of 0 is changed to None when inactive.
BACKRONYMS_SCORES = {}
# key is the keyword to trigger backronyms commands
BACKRONYMS_KEY = "bk"
###
@listen_to("^" + BACKRONYMS_KEY + ": get ready!$",re.IGNORECASE)
def backronymsStart(message):
    if isAdmin(message,CONTROLLERS):
        global BACKRONYMS_GAME_MODE,BACKRONYMS_HOST,BACKRONYMS_PLAYERS,BACKRONYMS_SCORES
        if not BACKRONYMS_GAME_MODE:
            BACKRONYMS_GAME_MODE = 1
            BACKRONYMS_HOST = uWrap(message)
            backSend(message,"Who's ready for a game of BACKRONYMS!\nLet's see a show of hands! Say `" +
                    BACKRONYMS_KEY + ": I'm in` if you want to play!")
#            if uWrap(message) not in BACKRONYMS_PLAYERS:
            if uWrap(message) not in BACKRONYMS_SCORES:
                #BACKRONYMS_PLAYERS.append(uWrap(message))
                BACKRONYMS_SCORES[uWrap(message)] = 0
        elif BACKRONYMS_GAME_MODE == 1:
            backSend(message,"We're still prepping for a game! No need to start another one! Gosh!")
        else:
            backSend(message,"There's already a game underway! Gosh!")
###
@listen_to('^' + BACKRONYMS_KEY + ': get players$',re.IGNORECASE)
def backronymsGetPlayers(message):
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
@listen_to("^" + BACKRONYMS_KEY + ": get score$",re.IGNORECASE)
def backronymsGetScore(message):
    if uWrap(message) in BACKRONYMS_SCORES:
        if BACKRONYMS_SCORES[uWrap(message)] == None:
            score = str(0) + ". You are currently listed as inactive."
        elif BACKRONYMS_SCORES[uWrap(message)] < 0:
            score = str(0 - BACKRONYMS_SCORES[uWrap(message)]) + ". You are currently listed as inactive."
        else:
            score = BACKRONYMS_SCORES[uWrap(message)]
        backSend(message,uWrap(message) + ", your score is %s." % score)
###
@listen_to("^" + BACKRONYMS_KEY + ": I'm in$",re.IGNORECASE)
def backronymsSignUp(message):
    global BACKRONYMS_PLAYERS,BACKRONYMS_SCORES,BACKRONYMS_GAME_MODE
    #if BACKRONYMS_GAME_MODE == 1 and uWrap(message) not in BACKRONYMS_PLAYERS:
    if BACKRONYMS_GAME_MODE == 1 and (uWrap(message) not in BACKRONYMS_SCORES or BACKRONYMS_SCORES[uWrap(winner)] == None):
        #BACKRONYMS_PLAYERS.append(uWrap(message))
        BACKRONYMS_SCORES[uWrap(message)] = 0
        backSend(message,"You have been added to the game, " + uWrap(message) + "!")
    elif BACKRONYMS_GAME_MODE > 1:
        backSend(message,"The game's already started, silly!")
    elif BACKRONYMS_GAME_MODE == 1 and uWrap(winner) in zUp(BACKRONYMS_SCORES):
        backSend(message,"You're already in the game, silly!")
    elif BACKRONYMS_GAME_MODE == 1:
        BACKRONYMS_SCORES[uWrap(winner)] = 0 - BACKRONYMS_SCORES[uWrap(winner)]
        backSend(message,"You have been added to the game, " + uWrap(message) + "!")
###
@listen_to("^" + BACKRONYMS_KEY + ": game on$")
def backronymsStartGame(message):
    global BACKRONYMS_GAME_MODE,BACKRONYMS_PLAYERS,BACKRONYMS_HOST,BACKRONYMS_SCORES
    if uWrap(message) == BACKRONYMS_HOST and BACKRONYMS_GAME_MODE == 1:
#        if len(BACKRONYMS_PLAYERS) < 2:
        if len(BACKRONYMS_SCORES) < 2:
            backSend(message,"You can't just play Backronyms with only one person! Gosh!")
        else:
            BACKRONYMS_GAME_MODE = 2
#            pList = ', '.join(BACKRONYMS_PLAYERS)
            pList = ', '.join(list(BACKRONYMS_SCORES.keys()))
            backSend(message,"And away we go! " + pList + ", we are starting the game! The host for the first round is: " + BACKRONYMS_HOST + "! Start us off with `" +
                    BACKRONYMS_KEY + ": set WORD`!")
    else:
        print("User is: " + uWrap(message))
        print("Host is: " + BACKRONYMS_HOST)
        print("Game mode is: " + str(BACKRONYMS_GAME_MODE))
###
@listen_to("^" + BACKRONYMS_KEY + ": set (.*)$")
def backronymsSetWord(message,word):
    global BACKRONYMS_GAME_MODE,BACKRONYMS_PLAYERS,BACKRONYMS_HOST,BACKRONYMS_WORDS,BACKRONYMS_SCORES
    if uWrap(message) not in BACKRONYMS_SCORES:
        backSend(message,"Sorry, but you are not a registered player.")
        return
    if uWrap(message) == BACKRONYMS_HOST and BACKRONYMS_GAME_MODE == 2:
        backSend(message,"Alright then! " + word + " is the word! Players, send in your answers with `" +
        BACKRONYMS_KEY + ": set ANSWER`!") # Consider adding ability to reset word?
        BACKRONYMS_GAME_MODE = 3
    elif BACKRONYMS_GAME_MODE == 2:
        backSend(message,"You may not send an answer until the host has picked a word, sorry!")
    elif uWrap(message) == BACKRONYMS_HOST and BACKRONYMS_GAME_MODE == 3:
        backSend(message,"It is time for the others to post their answers, gosh!")
    elif BACKRONYMS_GAME_MODE == 3 and uWrap(message) not in BACKRONYMS_WORDS:
        BACKRONYMS_WORDS[uWrap(message)] = word
        backSend(message,uWrap(message) + ": Your answer has been received!")
        done = True
#        for i in BACKRONYMS_PLAYERS:
        for i in zUp(BACKRONYMS_SCORES):
            if not i == BACKRONYMS_HOST and not i in BACKRONYMS_WORDS:
                done = False
        if done:
            backSend(message,"All answers have been put in! " + BACKRONYMS_HOST + ", it is time to pick a winner! Type `" +
            BACKRONYMS_KEY + ": get answers` to see a list of all answers and who picked them. To pick a winner, type `" +
            BACKRONYMS_KEY + ": pick @user`!")
            BACKRONYMS_GAME_MODE = 4
    elif BACKRONYMS_GAME_MODE == 3:
        backSend(message,"You've already sent in your answer! Too late to change it now!") # maybe add in a feature to let them change it?
    else:
        backSend(message,"This is neither the time to specify a word or to send in an answer! C'mon!")
###
@listen_to("^" + BACKRONYMS_KEY + ": get answers$",re.IGNORECASE)
def backronymsGetAnswers(message):
    if BACKRONYMS_WORDS:
        answer = "```"
        for i in BACKRONYMS_WORDS:
            answer = answer + i + ": " + BACKRONYMS_WORDS[i] + "\n"
        answer = answer + "```"
        backSend(message,answer)
    else:
        backSend(message,"There are no stored answers at this time.")
###
@listen_to("^" + BACKRONYMS_KEY + ": pick (.*)$",re.IGNORECASE)
def backronymsPickWinner(message,winner):
    global BACKRONYMS_GAME_MODE,BACKRONYMS_HOST,BACKRONYMS_WORDS,BACKRONYMS_SCORES,BACKRONYMS_WAITING
    if uWrap(message) == BACKRONYMS_HOST:
        if BACKRONYMS_GAME_MODE != 4:
            backSend(message,"It's not time to pick a winner yet, silly!")
        elif winner not in BACKRONYMS_SCORES:
            backSend(message,"That person isn't even playing! C'mon!")
        elif uWrap(message) == winner:
            backSend(message,"You can't pick yourself, you goof!")
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
                    str(score))
            BACKRONYMS_GAME_MODE = 2
            BACKRONYMS_WORDS = {}
            if winner in zUp(BACKRONYMS_SCORES):
                BACKRONYMS_HOST = winner
                backSend(message,winner + ": You are now the host for this next round! Type `"+ 
                        BACKRONYMS_KEY + ": set WORD` to pick your word for this round!")
            else:
                backSend(message,uWrap(message) + ", you will reamin the host. Type `" +
                        BACKRONYMS_KEY + ": set WORD` to pick your word for this round!")
            if BACKRONYMS_WAITING:
                for i in BACKRONYMS_WAITING:
                    if i not in BACKRONYMS_SCORES or not BACKRONYMS_SCORES[i]:
                        BACKRONYMS_SCORES[i] = 0
                    else:
                        BACKRONYMS_SCORES[i] = 0 - BACKRONYMS_SCORES[i]
                BACKRONYMS_WAITING = []
                backSend(message,"Those of you in the waiting list: " +
                        ', '.join(BACKRONYMS_WAITING) + 
                        " have been added to the game! You may enter your answers once the word has been picked!")
    else:
        backSend(message,"You're not the host, silly!")
###
@listen_to("^" + BACKRONYMS_KEY + ": me next$")
def backronymsJoinQueue(message):
    global BACKRONYMS_WAITING,BACKRONYMS_SCORES
    if uWrap(message) in BACKRONYMS_WAITING:
        backSend(message,"You're already in the queue!")
    elif BACKRONYMS_GAME_MODE == 1:
        backSend(message,"We're still in prep mode! You can join the game by typing `" +
                BACKRONYMS_KEY + ": I'm in`!")
    elif BACKRONYMS_GAME_MODE == 0:
        backSend(message,"There isn't a game in progress!")
    elif uWrap(message) in zUp(BACKRONYMS_SCORES):
        backSend(message,"You're already playing! C'mon!")
    else:
        BACKRONYMS_WAITING.append(uWrap(message))
        backSend(message,uWrap(message) + ", you have been added to the queue. See you next round!")
###
@listen_to("^" + BACKRONYMS_KEY + ": drop out$")
def backronymsDropOut(message):
    global BACKRONYMS_WAITING,BACKRONYMS_SCORES,BACKRONYMS_WORDS,BACKRONYMS_HOST
    if uWrap(message) == BACKRONYMS_HOST:
        backSend(message,"You're the host! At least pick a winner first!")
    elif uWrap(message) in BACKRONYMS_WAITING:
        BACKRONYMS_WAITING.remove(uWrap(message))
        backSend(message,"You have been removed from the waiting list.")
    elif uWrap(message) in zUp(BACKRONYMS_SCORES):
        if BACKRONYMS_SCORES[uWrap(message)] == 0:
            BACKRONYMS_SCORES[uWrap(message)] = None
        else:
            BACKRONYMS_SCORES[uWrap(message)] = 0 - BACKRONYMS_SCORES[uWrap(message)]
        backSend(message,"You have been removed from the active list. Your score has been saved!")
        if len(zUp(BACKRONYMS_SCORES)) < 2:
            backSend(message,"There are now too few people to play right now. The game will be ended, but your scores will be saved! Play again some time!")
            if BACKRONYMS_SCORES[BACKRONYMS_HOST] == 0:
                BACKRONYMS_SCORES[BACKRONYMS_HOST] = None
            else:
                BACKRONYMS_SCORES[BACKRONYMS_HOST] = 0 - BACKRONYMS_SCORES[BACKRONYMS_HOST]
            BACKRONYMS_GAME_MODE = 0
            BACKRONYMS_HOST = None
            BACKRONYMS_WAITING = [] # TODO: if there are waiting players maybe just start another game?
            return
        done = True
        for i in zUp(BACKRONYMS_SCORES):
            if i not in BACKRONYMS_WORDS:
                done = False
        if done:
            backSend(message,"With this dropping-out, all answers have been put in! " +
                    BACKRONYMS_HOST + ", it is time to pick a winner! Type `" +
                    BACKRONYMS_KEY + ": get answers` to see a list of all answers and who picked them. To pick a winner, type `" +
                    BACKRONYMS_KEY + ": pick @user`!")
            BACKRONYMS_GAME_MODE = 4
    else:
        backSend(message,"You aren't on either the active or the waiting list. No dropping out needed!")
###
@listen_to("^" + BACKRONYMS_KEY + ": help$")
def backronymsHelp(message):
    backSend(message,"The following commands can be given by typing `" +
            BACKRONYMS_KEY + ": COMMAND`. The list of commands is as follows:" +
            """```"get ready!" -- Starts a game of Backronyms. Only usable by admin users.
"get players" -- Provides a list of all players registered for the current game.
"get score" -- Provides your score.
"I'm in" -- Registers yourself for the current game. Only usable during the pre-game period.
"game on" -- Starts the game once players have been registered. Only usable by the host pre-game.
"set WORD/Answer" -- When used as the host, specifies the word for this round. When used as another player, locks in your answer for this round.
"get answers" -- Provides all answers given this round.
"pick @user" -- Picks the winner for this round.
"me next" -- Adds you to the waiting list for the next round, if you aren't in the game yet.
"drop out" -- Removes you from the game, but saves your score. You can come back later with "me next".
"help" -- Print this help message.```""")
######
##########
## TESTING! TURN _*OFF*_ WHEN NOT TESTING@
######
#@listen_to('.')
#def printAll(message):
#    print(message.body['user'] + ": " + tx(message))
#    pokeSend(message,"This is the speaker: <@" + message.body['user'] + ">")
######
## END TEST SEGMENT
##########


# main loop
def main():
    bot = Bot()
    bot.run()

# no idea why this is necesary but the docs said to put this here lol
if __name__ == "__main__":
    main()
