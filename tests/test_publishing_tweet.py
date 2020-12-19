from unittest import mock

import pytest

from src.publishing_tweet import lambda_handler
from botocore.exceptions import ClientError
from tweepy.error import TweepError


@mock.patch('src.publishing_tweet.tweepy')
@mock.patch('src.publishing_tweet.boto3')
def test_publishing_when_everything_is_ok(mock_boto, mock_tweepy, lambda_event_publisher):
    # A dumb test where we just check if everything is well called
    mock_s3 = mock.MagicMock()
    mock_s3.download_fileobj.side_effect = None
    mock_ssm = mock.MagicMock()
    mock_boto.client.side_effect = [mock_s3, mock_ssm]

    mock_s3.delete_object.side_effect = None
    mock_tweepy.API.return_value.media_upload.side_effect = None
    mock_tweepy.API.return_value.update_status.side_effect = None

    lambda_handler(event=lambda_event_publisher, context={})
    assert mock_ssm.get_parameter.call_count == 4
    mock_s3.download_fileobj.assert_called_once()
    mock_tweepy.API.return_value.media_upload.assert_called_once()
    mock_tweepy.API.return_value.update_status.assert_called_once()
    mock_s3.delete_object.assert_called_once()


@mock.patch('src.publishing_tweet.boto3')
def test_publishing_when_an_error_occur_with_s3_dl(mock_boto, lambda_event_publisher, caplog):
    mock_s3 = mock.MagicMock()
    mock_s3.download_fileobj.side_effect = ClientError(error_response={}, operation_name='')
    mock_s3.delete_object.side_effect = None
    mock_ssm = mock.MagicMock()
    mock_boto.client.side_effect = [mock_s3, mock_ssm]
    mock_ssm.get_parameter.side_effect = None

    with pytest.raises(ClientError):
        lambda_handler(event=lambda_event_publisher, context={})

    assert mock_ssm.get_parameter.call_count == 4
    assert 'Error while trying to sending a tweet' in caplog.text
    mock_s3.delete_object.assert_called_once()


@mock.patch('src.publishing_tweet.tweepy')
@mock.patch('src.publishing_tweet.boto3')
def test_publishing_when_an_error_occur_with_tweepy_api(mock_boto, mock_tweepy, lambda_event_publisher, caplog):
    mock_s3 = mock.MagicMock()
    mock_s3.download_fileobj.side_effect = None
    mock_ssm = mock.MagicMock()
    mock_boto.client.side_effect = [mock_s3, mock_ssm]
    mock_ssm.get_parameter.side_effect = None
    mock_tweepy.OAuthHandler.side_effect = TweepError(reason='something goes wrong')

    with pytest.raises(TweepError, match='something goes wrong'):
        lambda_handler(event=lambda_event_publisher, context={})

    assert mock_ssm.get_parameter.call_count == 4
    assert 'Error while trying to sending a tweet' in caplog.text
    mock_s3.download_fileobj.assert_called_once()
