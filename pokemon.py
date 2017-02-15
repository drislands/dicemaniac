from pokemontcgsdk import Card
from pokemontcgsdk import Set
from pokemontcgsdk import Type
from pokemontcgsdk import Supertype
from pokemontcgsdk import Subtype
import random
import re

#functions
def getCardByName(cardName,cardSet,cardID,literal,superType):
    if not cardSet:
        card = Card.where(name=cardName).all()
    else:
        card = Card.where(name=cardName).where(set=cardSet).all()
    if literal:
        result = []
        for i in card:
            if re.findall('^' + cardName + '$',i.name):
                result.append(i)
        card = result
    if superType:
        result = []
        for i in card:
            if i.supertype[0]==superType[0]:
                result.append(i)
        card = result
    if cardID:
        result = []
        for i in card:
            if re.findall(str(cardID) + '$',i.id):
                result.append(i)
        card = result
    return card

def getRandomCard(cardList):
    if len(cardList) > 1:
        card = random.randint(0,len(cardList)-1)
        return cardList[card]
    elif len(cardList) < 1:
        return None
    else:
        return cardList[0]

def getCardURL(cardName,cardSet=None,cardID=None,literal=False,superType=None):
    card = getRandomCard(getCardByName(cardName,cardSet,cardID,literal,superType))
    if not card:
        return None
    else:
        return card.image_url
