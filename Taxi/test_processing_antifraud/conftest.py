# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import pytest

from taxi.util import context_timings
from taxi.util import performance

import processing_antifraud.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['processing_antifraud.generated.service.pytest_plugins']


@pytest.fixture
def mock_cardstorage_service(mock_cardstorage):
    class Context:
        cards = []

        def __init__(self):
            self.cards = [self.mock_card()]

        @staticmethod
        def mock_card(card_id=None, regions_checked=None):
            return {
                'billing_card_id': 'x988b7513b1b4235fb392377a',
                'card_id': card_id or 'card-x988b7513b1b4235fb392377a',
                'permanent_card_id': 'card-xc4c9cc5d9f054e9785792b7b',
                'persistent_id': '9d0039989b590206b82dc8ac5d0ab281',
                'region_id': '225',
                'owner': '4020890530',
                'bound': True,
                'from_db': False,
                'unverified': False,
                'possible_moneyless': False,
                'regions_checked': regions_checked or [],
                'expiration_month': 12,
                'expiration_year': 19,
                'currency': 'RUB',
                'number': '4214******3143',
                'system': 'sys',
                'valid': True,
                'busy': False,
                'busy_with': [],
            }

    ctx = Context()

    @mock_cardstorage('/v1/payment_methods')
    async def _mock_payment_methods(request):
        return {'available_cards': ctx.cards}

    @mock_cardstorage('/v1/update_card')
    async def _mock_update_card(request):
        return {}

    return ctx


class NeedAcceptTaxiRequest:
    def __init__(self, taxi_processing_antifraud_web):
        self.client = taxi_processing_antifraud_web

    async def make_request(self, **override_data):
        data = {
            'order_id': 'test_order_id',
            'zone': 'moscow',
            'cost': '100',
            'currency': 'RUB',
            'tariff_class': 'econom',
            'payment_method_type': 'card',
            'fixed_price': True,
        }
        data.update(override_data)
        return await self.client.post('/v1/need-accept/taxi', json=data)


class FakeRideRequest:
    def __init__(self, taxi_processing_antifraud_web):
        self.client = taxi_processing_antifraud_web

    async def make_request(self, **override_data):
        data = {
            'order_id': 'test_order_id',
            'tariff_class': 'econom',
            'order_status': 'finished',
            'taxi_status': 'complete',
            'travel_time': 120,
        }
        data.update(override_data)
        return await self.client.post('/v1/fake-ride', json=data)


class AntifraudSumRequest:
    def __init__(self, taxi_processing_antifraud_web):
        self.client = taxi_processing_antifraud_web

    async def make_request(self, order_id):
        params = {'order_id': order_id}
        return await self.client.get('/v1/antifraud/sum-to-pay', params=params)


@pytest.fixture
def web_processing_antifraud(taxi_processing_antifraud_web):
    class Ctx:
        def __init__(self, taxi_processing_antifraud_web):
            self.need_accept_taxi = NeedAcceptTaxiRequest(
                taxi_processing_antifraud_web,
            )
            self.fake_ride = FakeRideRequest(taxi_processing_antifraud_web)
            self.antifraud_sum = AntifraudSumRequest(
                taxi_processing_antifraud_web,
            )

    return Ctx(taxi_processing_antifraud_web)


@pytest.fixture
def order_core_mock(mockserver, load_json):
    def mock(response_filename):
        @mockserver.json_handler('/order-core/v1/tc/order-fields')
        def _order_core(request):
            return load_json(response_filename)

    return mock


@pytest.fixture(autouse=True)
def mock_time_storage():
    handler_time_storage = performance.TimeStorage('test_mock')
    context_timings.time_storage.set(handler_time_storage)


@pytest.fixture(autouse=True)
def individual_tariffs_mockserver(mockserver):
    class IndividualTariffsHandlers:
        @staticmethod
        @mockserver.json_handler('/individual-tariffs/v1/tariff/by_category')
        def v1_tariff_by_category(_):
            return mockserver.make_response(
                status=200,
                json={
                    'id': '0cda5880ec3b4b4b9079635d3faf8566',
                    # required properties for response
                    'activation_zone': 'activation_zone',
                    'categories': [
                        {
                            'id': '0cda5880ec3b4b4b9079635d3faf8566',
                            'minimal': 30.0,
                            # required properties for category
                            'category_name': 'category_name',
                            'category_type': 'application',
                            'currency': 'currency',
                            'day_type': 0,
                            'name_key': 'name_key',
                            'time_from': '00:00',
                            'time_to': '23:59',
                        },
                    ],
                    'date_from': '2020-01-01T21:00:00+03:00',
                    'home_zone': 'home_zone',
                },
            )

    return IndividualTariffsHandlers()
