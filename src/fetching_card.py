# coding: utf-8

"""
A Lambda function based on MTG SDK (Magic The Gathering)
"""

import abc
import logging
import os
import secrets

from dataclasses import dataclass
from typing import List

import boto3
import requests
import scrython

from aws_xray_sdk.core import patch_all
from tenacity import retry, stop_after_attempt, wait_random
from mtgsdk import Card
from mtgsdk import Set

# Define the global logger
LOGGER = logging.getLogger('fetching_card')
LOGGER.setLevel(logging.DEBUG)

# Extract AWS resources from Lambda environment variables
BUCKET_NAME = os.environ.get('BUCKET_NAME')
QUEUE_URL = os.environ.get('QUEUE_URL')

# Constant
NUMBER_OF_RETRIES = 30


@dataclass
class MTGCard:
    """
    Dataclass for aggregating MTG card info
    """
    name: str
    artist: str
    rarity: str
    set: str
    set_name: str
    subtypes: List[str]
    type: str
    card_data: bytes
    card_filename: str


class Strategy(metaclass=abc.ABCMeta):
    """
    Interface for the Strategy pattern
    """

    def _fetch_from_scryfall(self, card: Card) -> MTGCard:
        """
        Fetch card illustration from ScryFall website (which have highres illustration)
        :param card: (Card) card extracted from MTG SDK
        :return: (MTGCard)
        """
        scry_card = scrython.cards.Named(exact=card.name, set=card.set)
        return MTGCard(name=card.name,
                       artist=card.artist,
                       rarity=card.rarity,
                       set=card.set,
                       set_name=card.set_name,
                       subtypes=card.subtypes,
                       type=card.type,
                       card_data=requests.get(f'{scry_card.image_uris(image_type="png")}').content,
                       card_filename=f'{scry_card.id()}.png')

    @abc.abstractmethod
    def fetch_a_card(self) -> MTGCard:
        """
        Abstract method that will return a card (by using the right strategy)
        :return: (Card)
        """
        raise NotImplementedError


class FullyRandomCard(Strategy):
    """
    Return a fully random card
    """

    def __str__(self):
        return "Let's fetch a random card from a random set"

    def fetch_a_card(self) -> MTGCard:
        card = secrets.choice(Card.where(set=secrets.choice(Set.all()).code).all())
        return self._fetch_from_scryfall(card)


class RandomCardFromAGivenSet(Strategy):
    """
    Return a random card from a given set
    """

    def __str__(self):
        return f"Let's fetch a random card from a given set (here: {self._card_set})"

    def __init__(self, card_set: str):
        self._card_set = card_set

    def fetch_a_card(self) -> MTGCard:
        card = secrets.choice(Card.where(set=self._card_set).all())
        return self._fetch_from_scryfall(card)


class RandomCardFromChrisRallis(Strategy):
    """
    Return a random card design by Chris Rallis
    """

    def __str__(self):
        return "Let's fetch a card from Chris Rallis, I love this artist"

    def fetch_a_card(self) -> MTGCard:
        card = secrets.choice(Card.where(artist="Chris Rallis").all())
        return self._fetch_from_scryfall(card)


class RandomCardFromChaseStone(Strategy):
    """
    Return a random card design by Chase Stone
    """

    def __str__(self):
        return "Let's fetch a card from Chase Stone I love this artist !"

    def fetch_a_card(self) -> MTGCard:
        card = secrets.choice(Card.where(artist="Chase Stone").all())
        return self._fetch_from_scryfall(card)


class RandomCardFromJohannesVoss(Strategy):
    """
    Return a random card design by Johannes Voss
    """

    def __str__(self):
        return "Let's fetch a card from Johannes Voss (@algenpfleger), I love this artist !"

    def fetch_a_card(self) -> MTGCard:
        card = secrets.choice(Card.where(artist="Johannes Voss").all())
        return self._fetch_from_scryfall(card)


class RandomCardFromMagaliVilleneuve(Strategy):
    """
    Return a random card design by Magali Villeneuve
    """

    def __str__(self):
        return "Let's fetch a card from Magali Villeneuve (@Cathaoir1), so talented !"

    def fetch_a_card(self) -> MTGCard:
        card = secrets.choice(Card.where(artist="Magali Villeneuve").all())
        return self._fetch_from_scryfall(card)


class RandomCardFromWillianMurai(Strategy):
    """
    Return a random card design by Willian Murai
    """

    def __str__(self):
        return "Let's fetch a card from Willian Murai, I love this artist"

    def fetch_a_card(self) -> MTGCard:
        card = secrets.choice(Card.where(artist="Willian Murai").all())
        return self._fetch_from_scryfall(card)


class RandomRareCardFromAGivenSet(Strategy):
    """
    Return a random rare card from a given set
    """

    def __str__(self):
        return f"Let's fetch a random Rare card from a given set " \
               f"(here: {self._card_set})"

    def __init__(self, card_set: str):
        self._card_set = card_set

    def fetch_a_card(self) -> MTGCard:
        card = secrets.choice(Card.where(set=self._card_set).where(rarity='Rare').all())
        return self._fetch_from_scryfall(card)


class RandomRareCard(Strategy):
    """
    Return a random rare card from a random set
    """

    def __str__(self):
        return "Let's fetch a random Rare card from a random set"

    def fetch_a_card(self) -> MTGCard:
        card = secrets.choice(Card.where(set=secrets.choice(Set.all()).code).where(rarity='Rare').all())
        return self._fetch_from_scryfall(card)


class RandomMythicCard(Strategy):
    """
    Return a random mythic card from a random set
    """

    def __str__(self):
        return "Let's fetch a random Mythic card from a random set"

    def fetch_a_card(self) -> MTGCard:
        card = secrets.choice(Card.where(set=secrets.choice(Set.all()).code).where(rarity='Mythic Rare').all())
        return self._fetch_from_scryfall(card)


class RandomPlaneswalkerCard(Strategy):
    """
    Return a random Planeswalker card
    """

    def __str__(self):
        return "Let's fetch a random Planeswalker card"

    def fetch_a_card(self) -> MTGCard:
        card = secrets.choice(Card.where(type="Planeswalker").all())
        return self._fetch_from_scryfall(card)


class RandomRareCardFromInnistrad(Strategy):
    """
    Return a random rare card from Innistrad sets
    """

    def __str__(self):
        return "Let's fetch a random rare cards from Innistrad sets"

    def fetch_a_card(self) -> MTGCard:
        card = secrets.choice(Card.where(set='isd|soi|emn').where(rarity='Rare|Mythic Rare').all())
        return self._fetch_from_scryfall(card)


class RandomVampireCard(Strategy):
    """
    Return a random Vampire card
    """

    def __str__(self):
        return "Let's fetch a random Vampire card"

    def fetch_a_card(self) -> MTGCard:
        card = secrets.choice(Card.where(subtypes="Vampire").all())
        return self._fetch_from_scryfall(card)


class RandomUncommonCard(Strategy):
    """
    Return a random uncommon card from a random set
    """

    def __str__(self):
        return "Let's fetch a random Uncommon card from a random set"

    def fetch_a_card(self) -> MTGCard:
        card = secrets.choice(Card.where(set=secrets.choice(Set.all()).code).where(rarity='Uncommon').all())
        return self._fetch_from_scryfall(card)


class MTGCardFetcher:
    """
    Fetch a card from MTG API following a given strategy
    Maintain a reference to a Strategy object.
    """

    def __init__(self, strategy: Strategy):
        """
        Initialization
        :param strategy: (Strategy) A specific strategy
        """
        self._strategy = strategy

    @retry(reraise=True, wait=wait_random(min=3, max=6), stop=stop_after_attempt(NUMBER_OF_RETRIES))
    def get_card(self) -> MTGCard:
        returned_card = self._strategy.fetch_a_card()
        if not returned_card.card_data:
            LOGGER.error(f'No image URL for card {returned_card.name}, {returned_card.set_name}, pick a new one.')
            raise ValueError
        return returned_card


def random_strategy() -> Strategy:
    """
    Return a random strategy
    :return: (Strategy) returned a random Strategy
    """
    strategies = [FullyRandomCard(),
                  RandomMythicCard(),
                  RandomPlaneswalkerCard(),
                  RandomRareCard(),
                  RandomRareCardFromInnistrad(),
                  RandomUncommonCard(),
                  RandomVampireCard(),
                  RandomCardFromChrisRallis(),
                  RandomCardFromChaseStone(),
                  RandomCardFromJohannesVoss(),
                  RandomCardFromMagaliVilleneuve()]
    return secrets.choice(strategies)


def lambda_handler(event, context):
    """
    Default AWS Lambda Handler
    :return: (None)
    """
    patch_all()

    s3 = boto3.client('s3')
    sqs = boto3.client('sqs')

    LOGGER.info('Starting this Lambda by fetching a MTG card')
    strategy = random_strategy()
    card = MTGCardFetcher(strategy=strategy).get_card()

    LOGGER.info(f'Saving card image ({card.name}) into S3')
    s3.put_object(Bucket=BUCKET_NAME,
                  Key=card.card_filename,
                  Body=card.card_data)

    LOGGER.info('Saving meta-data into SQS')
    sqs.send_message(QueueUrl=QUEUE_URL,
                     MessageBody=card.card_filename,
                     MessageAttributes={
                         'S3Bucket': {'StringValue': BUCKET_NAME, 'DataType': 'String'},
                         'Name': {'StringValue': card.name, 'DataType': 'String'},
                         'Author': {'StringValue': card.artist, 'DataType': 'String'},
                         'Set': {'StringValue': card.set_name, 'DataType': 'String'},
                         'Tweet': {'StringValue': f'{strategy} #Magic #MTG !', 'DataType': 'String'},
                     })
