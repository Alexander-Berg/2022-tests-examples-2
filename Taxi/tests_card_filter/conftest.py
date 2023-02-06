# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from card_filter_plugins import *  # noqa: F403 F401

from tests_card_filter import helpers


@pytest.fixture
def mock_cardstorage(mockserver, load_binary, load_json):
    cardstorage_request_data = None
    cardstorage_cards = [
        helpers.make_card('card_id'),
        helpers.make_card('unverified_card', unverified=True),
    ]

    @mockserver.json_handler('/cardstorage/v1/payment_methods')
    def _handler(request):
        if cardstorage_request_data is not None:
            assert request.json == cardstorage_request_data
        return {'available_cards': cardstorage_cards}

    def _mock_cardstorage(cards=None, request_data=None):
        nonlocal cardstorage_request_data
        cardstorage_request_data = request_data
        if cards is None:
            return
        cardstorage_cards.clear()
        cardstorage_cards.extend(cards)

    return _mock_cardstorage


@pytest.fixture(name='invoke_handler')
def _invoke_handler(taxi_card_filter):
    async def _run(uri, request, headers):
        await taxi_card_filter.post(uri, json=request, headers=headers)

    return _run
