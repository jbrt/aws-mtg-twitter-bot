import pytest


@pytest.fixture
def lambda_event_publisher():
    return {
        'Records': [
            {
                'body': 'no_matters',
                'messageAttributes': {
                    'Tweet': {'stringValue': 'tweet_text'},
                    'Name': {'stringValue': 'card_name'},
                    'Set': {'stringValue': 'set_name'},
                    'Author': {'stringValue': 'author_name'},
                },
                'receiptHandle': 'no_matters'
            }
        ]
    }
