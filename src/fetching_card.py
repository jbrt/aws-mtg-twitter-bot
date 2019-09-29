# coding: utf-8

"""
A Lambda function based on MTG SDK (Magic The Gathering)
"""

import abc
import boto3
import logging
import os
import random
import requests
from tenacity import retry, stop_after_attempt
from mtgsdk import Card
from mtgsdk import Set

# Define the global logger
LOGGER = logging.getLogger('fetching-card')
LOGGER.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
LOGGER.addHandler(stream_handler)

# Extract AWS resources from Lambda environment variables
BUCKET_NAME = os.environ.get('BUCKET_NAME')
QUEUE_URL = os.environ.get('QUEUE_URL')

# AWS SDK
S3 = boto3.client('s3')
SQS = boto3.client('sqs')

# Constant
NUMBER_OF_RETRIES = 30


class Strategy(metaclass=abc.ABCMeta):
    """
    Interface for the Strategy pattern
    """

    @abc.abstractmethod
    def fetch_a_card(self) -> Card:
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

    def fetch_a_card(self) -> Card:
        return random.choice(Card.where(set=random.choice(Set.all()).code)
                                 .all())


class RandomCardFromAGivenSet(Strategy):
    """
    Return a random card from a given set
    """

    def __str__(self):
        return f"Let's fetch a random card from a given set " \
               f"(here: {self._card_set})"

    def __init__(self, card_set: str):
        self._card_set = card_set

    def fetch_a_card(self) -> Card:
        return random.choice(Card.where(set=self._card_set)
                                 .all())


class RandomCardFromMagaliVilleneuve(Strategy):
    """
    Return a random card design by Magali Villeneuve
    """

    def __str__(self):
        return f"Let's fetch a card from Magali Villeneuve (@Cathaoir1), " \
               f"so talented !"

    def fetch_a_card(self) -> Card:
        return random.choice(Card.where(artist="Magali Villeneuve")
                                 .all())


class RandomRareCardFromAGivenSet(Strategy):
    """
    Return a random rare card from a given set
    """

    def __str__(self):
        return f"Let's fetch a random Rare card from a given set " \
               f"(here: {self._card_set})"

    def __init__(self, card_set: str):
        self._card_set = card_set

    def fetch_a_card(self) -> Card:
        return random.choice(Card.where(set=self._card_set)
                                 .where(rarity='Rare')
                                 .all())


class RandomRareCard(Strategy):
    """
    Return a random rare card from a random set
    """

    def __str__(self):
        return "Let's fetch a random Rare card from a random set"

    def fetch_a_card(self) -> Card:
        return random.choice(Card.where(set=random.choice(Set.all()).code)
                                 .where(rarity='Rare')
                                 .all())


class RandomMythicCard(Strategy):
    """
    Return a random mythic card from a random set
    """

    def __str__(self):
        return "Let's fetch a random Mythic card from a random set"

    def fetch_a_card(self) -> Card:
        return random.choice(Card.where(rarity='Mythic Rare')
                                 .all())


class RandomRareCardFromInnistrad(Strategy):
    """
    Return a random rare card from Innistrad sets
    """

    def __str__(self):
        return "Let's fetch a random rare cards from Innistrad sets"

    def fetch_a_card(self) -> Card:
        return random.choice(Card.where(set='isd|soi|emn')
                                 .where(rarity='Rare|Mythic Rare')
                                 .all())


class RandomUncommonCard(Strategy):
    """
    Return a random uncommon card from a random set
    """

    def __str__(self):
        return "Let's fetch a random Uncommon card from a random set"

    def fetch_a_card(self) -> Card:
        return random.choice(Card.where(set=random.choice(Set.all()).code)
                                 .where(rarity='Uncommon')
                                 .all())


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

    @retry(reraise=True, stop=stop_after_attempt(NUMBER_OF_RETRIES))
    def get_card(self) -> Card:
        returned_card = self._strategy.fetch_a_card()
        if returned_card.image_url is None:
            LOGGER.error(f'No image URL for card {returned_card.name}, '
                         f'{returned_card.set_name}, pick a new one.')
            raise ValueError
        return returned_card


def random_strategy() -> Strategy:
    """
    Return a random strategy
    :return: (Strategy) returned a random Strategy
    """
    strategies = [FullyRandomCard(),
                  RandomRareCard(),
                  RandomMythicCard(),
                  RandomUncommonCard(),
                  RandomRareCardFromInnistrad(),
                  RandomCardFromMagaliVilleneuve()]
    return random.choice(strategies)


def lambda_handler(event, context):
    """
    Default AWS Lambda Handler
    :return: (None)
    """
    LOGGER.info('Starting this Lambda by fetching a MTG card')
    strategy = random_strategy()
    card = MTGCardFetcher(strategy=strategy).get_card()
    card_key = f'{card.id}.jpg'

    LOGGER.info(f'Saving card image ({card.name}) into S3')
    S3.put_object(Bucket=BUCKET_NAME,
                  Key=card_key,
                  Body=requests.get(f'{card.image_url}').content)

    LOGGER.info(f'Saving meta-data into SQS')
    SQS.send_message(QueueUrl=QUEUE_URL,
                     MessageBody=card_key,
                     MessageAttributes={
                         'S3Bucket': {'StringValue': BUCKET_NAME,
                                      'DataType': 'String'},
                         'Name': {'StringValue': card.name,
                                  'DataType': 'String'},
                         'Author': {'StringValue': card.artist,
                                    'DataType': 'String'},
                         'Set': {'StringValue': card.set_name,
                                 'DataType': 'String'},
                         'Tweet': {'StringValue': f'{strategy} #Magic #MTG !',
                                   'DataType': 'String'},
                     })


if __name__ == '__main__':
    lambda_handler(event=None, context=None)
