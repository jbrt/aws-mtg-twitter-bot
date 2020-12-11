from unittest import mock

from src.fetching_card import *

from mtgsdk import Card


def test_strategy_fully_random_card():
    fetcher = MTGCardFetcher(strategy=FullyRandomCard())
    card = fetcher.get_card()

    assert isinstance(card, Card)


def test_strategy_random_card_from_a_given_set():
    fetcher = MTGCardFetcher(strategy=RandomCardFromAGivenSet(card_set='KLD'))
    card = fetcher.get_card()

    assert isinstance(card, Card)
    assert card.set == 'KLD'


def test_strategy_random_card_from_chris_rallis():
    fetcher = MTGCardFetcher(strategy=RandomCardFromChrisRallis())
    card = fetcher.get_card()

    assert isinstance(card, Card)
    assert card.artist == 'Chris Rallis'


def test_strategy_random_card_from_chase_stone():
    fetcher = MTGCardFetcher(strategy=RandomCardFromChaseStone())
    card = fetcher.get_card()

    assert isinstance(card, Card)
    assert card.artist == 'Chase Stone'


def test_strategy_random_card_from_johannes_voss():
    fetcher = MTGCardFetcher(strategy=RandomCardFromJohannesVoss())
    card = fetcher.get_card()

    assert isinstance(card, Card)
    assert 'Johannes Voss' in card.artist


def test_strategy_random_card_from_magali_villeneuve():
    fetcher = MTGCardFetcher(strategy=RandomCardFromMagaliVilleneuve())
    card = fetcher.get_card()

    assert isinstance(card, Card)
    assert card.artist == 'Magali Villeneuve'


def test_strategy_random_card_from_willian_murai():
    fetcher = MTGCardFetcher(strategy=RandomCardFromWillianMurai())
    card = fetcher.get_card()

    assert isinstance(card, Card)
    assert card.artist == 'Willian Murai'


def test_strategy_random_rare_card_from_a_given_set():
    fetcher = MTGCardFetcher(strategy=RandomRareCardFromAGivenSet(card_set='KLD'))
    card = fetcher.get_card()

    assert isinstance(card, Card)
    assert card.set == 'KLD'
    assert card.rarity == 'Rare'


def test_strategy_random_rare_card():
    fetcher = MTGCardFetcher(strategy=RandomRareCard())
    card = fetcher.get_card()

    assert isinstance(card, Card)
    assert card.rarity == 'Rare'


# 
# def test_strategy_random_mythic_card():
#     fetcher = MTGCardFetcher(strategy=RandomMythicCard())
#     card = fetcher.get_card()
#
#     assert isinstance(card, Card)
#     assert card.rarity == 'Mythic Rare'


def test_strategy_random_planes_walker_card():
    fetcher = MTGCardFetcher(strategy=RandomPlaneswalkerCard())
    card = fetcher.get_card()

    assert isinstance(card, Card)
    assert 'Planeswalker' in card.type


def test_strategy_random_rare_card_from_innistrad():
    fetcher = MTGCardFetcher(strategy=RandomRareCardFromInnistrad())
    card = fetcher.get_card()

    assert isinstance(card, Card)
    assert card.set in ('ISD', 'SOI', 'EMN')
    assert card.rarity in ('Rare', 'Mythic Rare')


def test_strategy_random_rare_vampire_card():
    fetcher = MTGCardFetcher(strategy=RandomVampireCard())
    card = fetcher.get_card()

    assert isinstance(card, Card)
    assert 'Vampire' in card.subtypes


def test_strategy_random_uncommon_card():
    fetcher = MTGCardFetcher(strategy=RandomUncommonCard())
    card = fetcher.get_card()

    assert isinstance(card, Card)
    assert card.rarity == 'Uncommon'


def test_random_strategy():
    strategy = random_strategy()
    assert isinstance(strategy, Strategy)


@mock.patch('src.fetching_card.MTGCardFetcher')
@mock.patch('src.fetching_card.requests')
@mock.patch('src.fetching_card.boto3')
def test_lambda_handler_when_everything_is_fine(mock_boto, mock_requests, mock_fetcher, lambda_event_publisher):
    mock_s3 = mock.MagicMock()
    mock_sqs = mock.MagicMock()
    mock_boto.client.side_effect = [mock_s3, mock_sqs]

    lambda_handler(event=lambda_event_publisher, context={})

    mock_s3.put_object.assert_called_once()
    mock_sqs.send_message.assert_called_once()
