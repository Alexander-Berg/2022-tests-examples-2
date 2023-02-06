# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=unused-variable
import pytest

from grocery_p13n_plugins import *  # noqa: F403 F401

DEFAULT_PRICE = 100
DEFAULT_QUANTITY = 1


@pytest.fixture(name='cardstorage', autouse=True)
def mock_cardstorage(mockserver):
    @mockserver.json_handler('/cardstorage/v1/card')
    def _mock_v1_card(request):
        return {
            'card_id': '1',
            'billing_card_id': '1',
            'permanent_card_id': '1',
            'currency': 'RUB',
            'expiration_month': 12,
            'expiration_year': 2020,
            'owner': 'Mr',
            'possible_moneyless': False,
            'region_id': 'RU',
            'regions_checked': ['RU'],
            'system': '1',
            'valid': True,
            'bound': True,
            'unverified': False,
            'busy': False,
            'busy_with': [],
            'from_db': True,
            'number': '5100222233334444',
            'bin': '510022',
        }

    class Context:
        @property
        def times_called(self):
            return _mock_v1_card.times_called

    context = Context()
    return context


@pytest.fixture
def mock_grocery_discounts_500(mockserver):
    @mockserver.json_handler('/grocery-discounts/v4/match-discounts')
    def mock_match_discounts(request):
        return mockserver.make_response('<no data>', 500)

    return mock_match_discounts
