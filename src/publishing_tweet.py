# coding: utf-8

"""
Publishing a Tweet when
"""

import logging
import tweepy
import os
from botocore.exceptions import ClientError
import boto3

S3 = boto3.client('s3')
SSM = boto3.client('ssm')
BUCKET = os.environ.get('BUCKET_NAME')

# parameter = SSM.get_parameter(Name='/Prod/Db/Password', WithDecryption=True)
# print(parameter['Parameter']['Value'])
#
#
# def get_object(bucket_name, object_name):
#     """Retrieve an object from an Amazon S3 bucket
#
#     :param bucket_name: string
#     :param object_name: string
#     :return: botocore.response.StreamingBody object. If error, return None.
#     """
#
#     # Retrieve the object
#     s3 = boto3.client('s3')
#     try:
#         response = s3.get_object(Bucket=bucket_name, Key=object_name)
#     except ClientError as e:
#         # AllAccessDisabled error == bucket or object not found
#         logging.error(e)
#         return None
#     # Return an open StreamingBody object
#     return response['Body']


def lambda_handler(event, context):
    """
    Default AWS Lambda Handler
    :return: (None)
    """
    # print(event)
    consumer_key = SSM.get_parameter(Name='/twitter/credentials/consumer_key',
                                     WithDecryption=True)['Parameter']['Value']

    consumer_secret = SSM.get_parameter(Name='/twitter/credentials/consumer_secret',
                                        WithDecryption=True)['Parameter']['Value']

    access_token = SSM.get_parameter(Name='/twitter/credentials/access_token',
                                     WithDecryption=True)['Parameter']['Value']

    access_token_secret = SSM.get_parameter(Name='/twitter/credentials/access_token_secret',
                                            WithDecryption=True)['Parameter']['Value']
    os.chdir('/tmp')
    image_filename = event['Records'][0]['body']
    S3.download_file(BUCKET,
                     image_filename,
                     image_filename)

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    media = api.media_upload(filename=image_filename)

    tweet_text = f"Card name:  {event['Records'][0]['messageAttributes']['Name']['stringValue']} \n" \
                 f"Set:  {event['Records'][0]['messageAttributes']['Set']['stringValue']} \n" \
                 f"Artist:  {event['Records'][0]['messageAttributes']['Author']['stringValue']}"
    api.update_status(status=tweet_text,
                      media_ids=[media.media_id])
