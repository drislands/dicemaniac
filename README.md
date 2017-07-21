# dicemaniac
A slackbot for rolling dice, fetching Pokemon cards, and more.

This bot uses the following libraries: <br>
https://github.com/lins05/slackbot  
https://github.com/MagicTheGathering/mtg-sdk-python  
https://github.com/PokemonTCG/pokemon-tcg-sdk-python  

This bot also uses the following modules:
 * inspect
 * re
 * random
 * mysql.connector
 * os
 * string
 
This bot runs on python 3.6 on Arch-linux, and python 3.5 on Ubuntu. I have not tested it on any earlier versions or any other platforms. I will update this as I test on other platforms and determine where else this is supported.

Most recently, commented out lines 161-162 in /usr/local/lib/python3.5/dist-packages/slackbot/dispatcher.py to turn off default reply, which interferes sometimes with the Wartent functionality.

========
##First-time Setup

After downloading the project and installing any missing libraries/modules listed above, create a blank file in the project directory called "slackbot_settings.py" and put the following line in it:

```API_TOKEN = "your-token-here"```

...putting your actual bot token from Slack in the quotes. For info on how to get the bot API token, read [here](https://api.slack.com/bot-users). Keep in mind that you'll need to have permissions granted to you to be able to make a bot user in your Slack team.

=====

For keeping track of giphy scores, enchanted players and game modes/scores (and for future game developments as I find time/motivation to complete them), you will need MySQL or MariaDB. After you've installed one (and started the server [and enabled it to autostart at boot]) and have a root user and password ([documentation on how to do so found here](https://dev.mysql.com/doc/refman/5.7/en/resetting-permissions.html)), run the following commands from the terminal in the project directory, making sure to replace `newuser` with the new user you want to create, `password` with a secure password, and `customdatabase` with the name for your database:

```
mysql -u root -p -e "CREATE USER 'newuser'@'localhost' IDENTIFIED BY 'password'"
mysql -u root -p -e "CREATE DATABASE customdatabase"
mysql -u root -p -e "GRANT ALL PRIVILEGES ON customdatabase.* TO 'newuser'@'localhost'"
mysql -u root -p schema.sql
```
This will create the user that dicemaniac will use to interface with the database, create the database that it will be interfacing with, grant permissions to the user on that database, and then shape the database with the tables defined in the project.

Now that you have everything set up on the MySQL end, you will need to configure one final thing: the username and database name will need to be put into the main `dicemaniac.py`. You can do this by editing the lines that read:

```
MYSQL_USER = 'dicemaster'
MYSQL_DB = 'dicemaniac'
```
You'll want to change them to reflect the username and database that you picked in the step above.

=====
##Running the Bot

Now that you've got all the above steps complete, you need only run the following command from the project directory and the bot will begin:
```
DB_PASSWORD='password' SECRET_ADMIN='secret admin phrase' python dicemaniac.py
```
Replace `password` with the password you defined in the above step, and 'secret admin phrase' with a trigger phrase that, the first time it is said after the bot is started, will add the person speaking to the list of bot-admins (so pick something that isn't likely to come up in normal conversation). 

Now the bot is running!

=====
##Using the Bot

There are a few features currently built into dicemaniac, with more on the way as I get requests that I like and am able to implement. 

Currently, the following features are available:

```
* Magic Conch
  - Triggered by:   "magic conch...?", ignores case, whole message has to start with "magic conch" and end with "?"
  - Randomly chooses between Yes, No, I don't think so, Try asking again, and Maybe someday. Responds with a conch icon and the name 'Magic Conch'.

* Giphy Scorekeeper
  - Triggered by:   "giphy +/-1", ignores case, can appear anywhere in message
  - Adds or subtracts 1 from the current giphy score. Requires database access. Says "God dammit" when decreasing, just as a heads-up.

* PokeFetcher
  - Triggered by: "[[cardname]]" or "[[cardname][setname]]" or "[[cardname][setname][number]]", can add L immediately to the front of the brackets to do an exact name search, can add P or E or T to the end to specify Pokemon or Energy or Trainer card
  - Searches for all Pokemon cards that match the criteria, and if one or more is found will link to a picture of one of the matched cards.

* MagicFetcher
  - Triggered by: "{{cardname}}" or "{{cardname}{setname}}", can add L immediately to the front of the braces to do an exact name search, can add CEISPAL to the end to specify Creature/Enchantment/Instant/Sorcery/Planeswalker/Artifact/Land
  - Searches for all Magic: The Gathering cards that match the criteria, and if one or more is found will link to a picture of one of the matched cards.

TODO: finish updating this lol
```

=====
##Things Left TODO

 * Move from MySQL to SQLite.
  - This requires finishing all features that use the DB, including migrating Backronyms to it.
 * Fully finish Backronyms bot.
  - Ability to quit, by admins.
  - Ability to start game, by anyone.
  - Timeout for people taking too long.
  - Ability to pass turn when Host.
  - Ability to kick players when Host.
 * Finish Magic Duelling game (still in brainstorming phase).
  - This is very very much a WIP. No functionality exists right now, just entries in the schema.
 * Installation script.
  - ncurses, most likely. Will be written primarily for linux, but I hope to get this installable on all platforms.
  - Obviously no point in starting this until the bot is done. At the very least, not until migration to SQLite is complete.
