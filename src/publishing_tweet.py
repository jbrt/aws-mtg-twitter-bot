# coding: utf-8

"""
Publishing a Tweet when a message was put into SQS Queue
(Lambda function triggered)
"""

import logging
import os

import boto3
import tweepy

from s3streaming import s3_open
from botocore.exceptions import ClientError
from tweepy.error import TweepError

BUCKET = os.environ.get('BUCKET_NAME')
QUEUE_URL = os.environ.get('QUEUE_URL')

# Twitter credentials
CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET')

# Logger
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)


def lambda_handler(event, context):
    """
    Default AWS Lambda Handler
    :return: (None)
    """
    s3 = boto3.client('s3')
    ssm = boto3.client('ssm')

    # Extract useful data from event
    image_filename = event['Records'][0]['body']
    message_attributes = event['Records'][0]['messageAttributes']

    # Extraction Twitter credentials from Parameter store
    consumer_key = ssm.get_parameter(Name=CONSUMER_KEY, WithDecryption=True)['Parameter']['Value']
    consumer_secret = ssm.get_parameter(Name=CONSUMER_SECRET, WithDecryption=True)['Parameter']['Value']
    access_token = ssm.get_parameter(Name=ACCESS_TOKEN, WithDecryption=True)['Parameter']['Value']
    access_token_secret = ssm.get_parameter(Name=ACCESS_TOKEN_SECRET, WithDecryption=True)['Parameter']['Value']

    try:
        LOGGER.info(f'Downloading image {image_filename} from S3')
        with s3_open(f's3://{BUCKET}/{image_filename}', boto_session=boto3.session.Session()) as image_file:
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
            api = tweepy.API(auth)
            media = api.media_upload(filename=image_filename, file=image_file)

            tweet_text = f"{message_attributes['Tweet']['stringValue']} \n\n" \
                         f"Card name:  {message_attributes['Name']['stringValue']} \n" \
                         f"Set:  {message_attributes['Set']['stringValue']} \n" \
                         f"Artist:  {message_attributes['Author']['stringValue']}"

            LOGGER.info(f'Sending a tweet ({tweet_text})')
            api.update_status(status=tweet_text, media_ids=[media.media_id])

    except (TweepError, ClientError) as error:
        LOGGER.error(f'Error while trying to sending a tweet ({error}')
        raise error

    finally:
        # Tidy up after sending tweet
        LOGGER.debug('Erasing useless data (local image, SQS message ans S3 object)')
        s3.delete_object(Bucket=BUCKET, Key=image_filename)
