# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import copy
import uuid

import pytest

from user_state_plugins import *  # noqa: F403 F401


@pytest.fixture(autouse=True)
def territories_countries_list(mockserver, load_json):
    @mockserver.json_handler('/territories/v1/countries/list')
    def _mock_countries_list(request):
        request.get_data()
        return load_json('countries.json')


@pytest.fixture(autouse=True, name='mock_userphones')
def _mock_userphones(mockserver):
    @mockserver.json_handler('/user-api/user_phones/get')
    def _mock_user_phones_get(request):
        return {
            'id': 'user_id',
            'personal_phone_id': request.json['id'],
            'stat': {
                'big_first_discounts': 1,
                'complete': 1,
                'complete_card': 1,
                'complete_apple': 1,
                'complete_google': 1,
                'total': 1,
                'fake': 1,
            },
            'type': 'yandex',
            'is_loyal': False,
            'is_yandex_staff': False,
            'is_taxi_staff': False,
            'phone': '+70000000000',
            'last_payment_method': {'type': 'card', 'id': 'card-x7698'},
        }


@pytest.fixture(autouse=True, name='mock_cardstorage')
def _mock_cardstorage(mockserver):
    @mockserver.json_handler('/cardstorage/v1/payment_methods')
    def _mock_payment_methods(request):
        sample_card_1 = {
            'card_id': 'card-x7698',
            'billing_card_id': 'x7698',
            'permanent_card_id': '',
            'currency': 'RUB',
            'number': '510126****5010',
            'owner': '4003514353',
            'possible_moneyless': False,
            'region_id': '225',
            'regions_checked': ['{\'id\': 225}'],
            'system': 'MasterCard',
            'valid': True,
            'bound': True,
            'unverified': False,
            'busy': False,
            'busy_with': [],
            'from_db': False,
            'expiration_month': 4,
            'expiration_year': 2020,
            'persistent_id': '5bddb286de204cee886d687a505b5d0b',
            'bin': '',
            'service_labels': [
                'taxi:persistent_id:5bddb286de204cee886d687a505b5d0b',
            ],
            'aliases': [],
            'blocking_reason': '',
        }
        return {'available_cards': [sample_card_1]}


class RideDiscountsContext:
    def __init__(self):
        self.calls = 0
        self.discounts = []

    def set_discounts(self, discounts):
        self.discounts = discounts


@pytest.fixture(autouse=True, name='mock_ride_discounts')
def _mock_ride_discounts(mockserver):
    context = RideDiscountsContext()

    @mockserver.json_handler('/ride-discounts/v1/match-discounts/by-cards')
    def _handler(request):
        context.calls += 1
        return {'discounts': context.discounts}

    return context


class FeedsContext:
    _store: dict = {}
    _default_content: dict = {}
    _mock = None
    _is_failing: bool = False

    def __init__(self, content):
        self._default_content = content
        self._store = {}

    @property
    def mock(self):
        return self._mock

    @mock.setter
    def mock(self, mock):
        self._mock = mock

    def __getattr__(self, item):
        return getattr(self._mock, item)

    @property
    def failing(self):
        return self._is_failing

    def set_failing(self):
        self._is_failing = True

    def add_payload(self, discount, payload):
        feed_data = copy.deepcopy(self._default_content['feed'][0])

        feed_data['feed_id'] = str(uuid.uuid4())
        feed_data['payload'] = payload.copy()
        # convenience payload adjustment
        feed_data['payload']['discount'] = discount

        self._store[discount] = feed_data

    def get_response(self, channels):
        feeds = []
        for channel in channels:
            prefix, discount = channel.split(':', 1)
            assert prefix == 'discount'
            if discount in self._store:
                feeds.append(self._store[discount])

        response = copy.deepcopy(self._default_content)
        response['feed'] = feeds
        return response


@pytest.fixture
def mock_feeds(mockserver, load_json):
    ctx = FeedsContext(load_json('feeds.json'))

    @mockserver.json_handler('/feeds/v1/fetch')
    def _handle_feeds(request):
        if ctx.failing:
            raise mockserver.NetworkError('expected network error')

        assert request.json['service'] == 'taxi-summary-promo'
        return ctx.get_response(request.json['channels'])

    ctx.mock = _handle_feeds
    return ctx
