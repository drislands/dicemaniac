from mtgsdk import Card
from mtgsdk import Set
from mtgsdk import Type
from mtgsdk import Supertype
from mtgsdk import Subtype
from mtgsdk import Changelog
import random
import re

#functions
def getCardByName(cardName,cardSet=None,literal=False,superType=None):
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
        Type = ''
        for i in card:
            Type = i.type
            if re.findall('^Legendary',Type):
                Type = Type[10:]
            if re.findall('^Basic',Type):
                Type = Type[6:]
            if re.findall('^Tribal',Type):
                Type = Type[7:]
            if Type[0]==superType[0]:
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

def getCardURL(cardName,cardSet=None,literal=False,superType=None):
    card = getRandomCard(getCardByName(cardName,cardSet,literal,superType))
    if not card:
        return None
    else:
        return card.image_url
