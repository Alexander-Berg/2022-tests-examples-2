# pylint: disable=wildcard-import, unused-wildcard-import, import-error, C0411
import copy

from driver_money_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture(
    autouse=True,
    scope='function',
    params=[
        pytest.param(
            'use_billing_order_cost',
            marks=[
                pytest.mark.experiments3(
                    filename='experiments3_use_billing_order_cost.json',
                ),
            ],
        ),
    ],
)
def use_billing_order_cost():
    pass


@pytest.fixture(name='payments', autouse=True)
def payments(mockserver):
    @mockserver.json_handler('/billing-bank-orders/v1/parks/payments/search')
    def _mock_payments(request):
        return {'payments': [], 'cursor': {}}


@pytest.fixture
def mock_parks_replica(mockserver, load_json):
    @mockserver.json_handler(
        '/parks-replica/v1/parks/billing_client_id/retrieve',
    )
    def _parks_replica(request):
        return load_json('billing_client_id_retrieve_response.json')

    return _parks_replica


@pytest.fixture
def mock_billing_replication(mockserver, load_json):
    @mockserver.json_handler('/billing-replication/v1/active-contracts/')
    def _billing_replication(request):
        return load_json('active_contracts_response.json')

    return _billing_replication


@pytest.fixture(name='driver_feedback', autouse=True)
def driver_feedback(mockserver):
    @mockserver.json_handler('/driver-feedback/driver-feedback/v1/feedback')
    async def _driver_feedback(request):
        return {
            'feedback': {'score': 5, 'choices': ['1', '2']},
            'editable': False,
        }

    @mockserver.json_handler('/driver-feedback/driver-feedback/v2/feedback')
    async def _driver_feedback_v2(request):
        return {
            'feedback': [
                {'feed_type': 'passenger', 'score': 5, 'choices': ['1', '2']},
            ],
            'editable': False,
        }


@pytest.fixture(name='driver_auth_request', autouse=True)
def _driver_auth_request(mockserver, driver_authorizer):
    driver_authorizer.set_client_session(
        client_id='taximeter',
        park_id='park_id_0',
        session='test_session',
        driver_id='driver',
    )


class DriverProfilesContext:
    def __init__(self):
        self.response_not_self_signed = {
            'driver_profiles': [
                {
                    'accounts': [
                        {
                            'balance': '2444216.6162',
                            'currency': 'RUB',
                            'id': 'driver',
                        },
                    ],
                    'driver_profile': {
                        'id': 'driver',
                        'created_date': '2020-12-12T22:22:00.1231Z',
                        'first_name': 'Ivan',
                        'last_name': 'Ivanov',
                        'payment_service_id': '123456',
                    },
                },
            ],
            'offset': 0,
            'parks': [
                {
                    'id': 'park_id_0',
                    'country_id': 'rus',
                    'city': 'Москва',
                    'tz': 3,
                    'provider_config': {'yandex': {'clid': 'clid_0'}},
                },
            ],
            'total': 1,
            'limit': 1,
        }
        response_self_signed = copy.deepcopy(self.response_not_self_signed)
        response_self_signed['parks'][0]['driver_partner_source'] = 'yandex'
        self.response_self_signed = response_self_signed

        self.is_self_signed = False

    def make_self_signed_response(self):
        self.is_self_signed = True

    def set_created_date(self, created_date):
        response = (
            self.response_self_signed
            if self.is_self_signed
            else self.response_not_self_signed
        )
        if created_date is None:
            response['driver_profiles'][0]['driver_profile'].pop(
                'created_date',
            )
        else:
            response['driver_profiles'][0]['driver_profile'][
                'created_date'
            ] = str(created_date)


@pytest.fixture(name='parks_driver_profiles', autouse=True)
def _parks_request(mockserver):
    context = DriverProfilesContext()

    @mockserver.json_handler('/parks/driver-profiles/list')
    def _mock_parks(request):
        assert {
            'fields': {
                'account': ['balance', 'currency'],
                'park': [
                    'country_id',
                    'tz',
                    'city',
                    'driver_partner_source',
                    'provider_config',
                ],
                'driver_profile': [
                    'created_date',
                    'first_name',
                    'last_name',
                    'payment_service_id',
                ],
            },
            'query': {
                'park': {
                    'driver_profile': {'id': ['driver']},
                    'id': 'park_id_0',
                },
            },
            'limit': 1,
            'offset': 0,
        } == request.json
        if context.is_self_signed:
            return context.response_self_signed
        return context.response_not_self_signed

    return context


@pytest.fixture
def service_client_default_headers():
    return {'Accept-Language': 'en'}


@pytest.fixture(name='fleet_rent_request', autouse=True)
def _fleet_rent_request(mockserver):
    @mockserver.json_handler(
        '/fleet-rent/fleet-rent/v1/sys/driver-balance/total',
    )
    def _mock_fleet_rent(request):
        assert request.query['park_id'] == 'park_id_0'
        assert request.query['driver_id'] == 'driver'
        assert request.query['currency'] == 'RUB'
        return {'amount': '65.11'}


@pytest.fixture(name='fleet_payouts_request', autouse=True)
def _fleet_payouts_request(mockserver):
    @mockserver.json_handler(
        '/fleet-payouts/internal/payouts/v1/balance-total',
    )
    def _mock_fleet_payouts(request):
        return {'amount': '65.11', 'accrued_at': '2020-05-03T12:00:00+00:00'}


class FleetRentExpensesContext:
    def __init__(self):
        self.response = {
            'expenses': [
                {
                    'begin_time': '2019-05-05T21:00:00+00:00',
                    'end_time': '2019-05-12T21:00:00+00:00',
                    'value': {'amount': '-1232.25', 'currency': 'RUB'},
                },
            ],
        }
        self.response_azn_currency = {
            'expenses': [
                {
                    'begin_time': '2019-05-05T21:00:00+00:00',
                    'end_time': '2019-05-12T21:00:00+00:00',
                    'value': {'amount': '-12.12', 'currency': 'AZN'},
                },
            ],
        }
        self.other_currency_flag = False
        self.split_response = False
        self.request_counter = 0

    def set_az_currency_response(self):
        self.other_currency_flag = True

    def set_split_response(self, *responses):
        if self.other_currency_flag:
            raise Exception('Already set to az currency response')
        self.response = [response for response in responses]
        self.split_response = True

    def get_response(self):
        if self.other_currency_flag:
            return self.response_azn_currency
        if not self.split_response:
            return self.response
        assert isinstance(self.response, list)
        result = self.response[self.request_counter]
        self.request_counter += 1
        return result


@pytest.fixture(name='fleet_rent_expenses', autouse=True)
def mock_dup(mockserver):
    context = FleetRentExpensesContext()

    @mockserver.json_handler(
        '/fleet-rent/fleet-rent/v1/sys/driver-expenses/totals',
    )
    def _post(request):
        return context.get_response()

    return context


@pytest.fixture(name='selfreg', autouse=True)
def mock_selfreg(mockserver):
    @mockserver.json_handler('/selfreg/internal/selfreg/v1/validate')
    def _mock_selfreg(request):
        assert request.query['token'] == 'some_token'
        return {
            'city_id': 'Moscow',
            'selfreg_id': 'some_selfreg_id',
            'phone_pd_id': 'some_phone_pd_id',
            'country_id': 'rus',
        }


@pytest.fixture(scope='session')
def regenerate_config_hooks(regenerate_stat_client_config):
    return [regenerate_stat_client_config]
