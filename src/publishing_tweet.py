# coding: utf-8

"""
Publishing a Tweet when a message was put into SQS Queue
(Lambda function triggered)
"""

import logging
import boto3
import tweepy
import os
import sys
from botocore.exceptions import ClientError
from tweepy.error import TweepError

# Boto clients
S3 = boto3.client('s3')
SQS = boto3.client('sqs')
SSM = boto3.client('ssm')

BUCKET = os.environ.get('BUCKET_NAME')
QUEUE_URL = os.environ.get('QUEUE_URL')

# Twitter credentials
CONSUMER_KEY = os.environ.get('CONSUMER_KEY')
CONSUMER_SECRET = os.environ.get('CONSUMER_SECRET')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET')

# Logger
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
LOGGER.addHandler(stream_handler)


def lambda_handler(event, context):
    """
    Default AWS Lambda Handler
    :return: (None)
    """
    # Extract useful data from event
    image_filename = event['Records'][0]['body']
    message_attributes = event['Records'][0]['messageAttributes']
    receipt_handle = event['Records'][0]['receiptHandle']

    # Extraction Twitter credentials from Parameter store
    consumer_key = SSM.get_parameter(Name=CONSUMER_KEY, WithDecryption=True)['Parameter']['Value']
    consumer_secret = SSM.get_parameter(Name=CONSUMER_SECRET, WithDecryption=True)['Parameter']['Value']
    access_token = SSM.get_parameter(Name=ACCESS_TOKEN, WithDecryption=True)['Parameter']['Value']
    access_token_secret = SSM.get_parameter(Name=ACCESS_TOKEN_SECRET, WithDecryption=True)['Parameter']['Value']

    try:
        # Let's move where Lambda can write on disk and then download image file
        os.chdir('/tmp')
        LOGGER.info(f'Downloading image {image_filename} from S3')
        S3.download_file(BUCKET,
                         image_filename,
                         image_filename)
    except ClientError as error:
        LOGGER.error(f'Error while trying to get object from S3 ({error})')
        sys.exit(1)

    # Twitter
    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        media = api.media_upload(filename=image_filename)

        tweet_text = f"{message_attributes['Tweet']['stringValue']} \n\n" \
                     f"Card name:  {message_attributes['Name']['stringValue']} \n" \
                     f"Set:  {message_attributes['Set']['stringValue']} \n" \
                     f"Artist:  {message_attributes['Author']['stringValue']}"

        LOGGER.info(f'Sending a tweet ({tweet_text})')
        api.update_status(status=tweet_text, media_ids=[media.media_id])
    except TweepError as error:
        LOGGER.error(f'Error while trying to sending a tweet ({error}')

    finally:
        # Tidy up after sending tweet
        LOGGER.debug('Erasing useless data (local image, SQS message ans S3 object)')
        os.remove(image_filename)
        SQS.delete_message(QueueUrl=QUEUE_URL, ReceiptHandle=receipt_handle)
        S3.delete_object(Bucket=BUCKET, Key=image_filename)
