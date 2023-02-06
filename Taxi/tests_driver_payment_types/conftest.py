# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from driver_payment_types_plugins import *  # noqa: F403 F401
import pytest


class BillingContext:
    def __init__(self):
        self.balances = {('park1', 'driver1'): ('RUB', '100.0')}

    def set_driver_balance(
            self, park_id, driver_profile_id, currency, balance,
    ):
        self.balances[(park_id, driver_profile_id)] = (currency, str(balance))


@pytest.fixture(name='billing_reports', autouse=True)
def mock_billing(request, mockserver):
    if request.node.get_closest_marker('stop_billing_reports_mock'):
        return None

    context = BillingContext()

    @mockserver.json_handler('billing-reports/v1/balances/select')
    def _balances_select(request):
        def fetch_ids(account):
            entity_external_id = account['entity_external_id']
            park_id = entity_external_id.split('/')[1]

            sub_account = account['sub_account']
            driver_profile_id = sub_account.split('/')[2]

            return park_id, driver_profile_id

        def get_driver_info(account):
            park_id, driver_profile_id = fetch_ids(account)
            currency, balance = context.balances.get(
                (park_id, driver_profile_id), ('RUB', '100.0'),
            )
            return {
                'currency': currency,
                'balance': balance,
                'entity_external_id': account['entity_external_id'],
                'sub_account': account['sub_account'],
            }

        request = request.json
        accounts = request['accounts']
        drivers_info = [get_driver_info(account) for account in accounts]

        response = {}
        response['entries'] = [
            {
                'account': {
                    'account_id': 111122222,
                    'entity_external_id': driver['entity_external_id'],
                    'agreement_id': 'taxi/driver_balance',
                    'currency': driver['currency'],
                    'sub_account': driver['sub_account'],
                },
                'balances': [
                    {
                        'accrued_at': '2019-11-08T19:00:00.000000+00:00',
                        'balance': driver['balance'],
                        'last_created': '2020-01-01T12:00:00.000+00:00',
                        'last_entry_id': 12345678,
                    },
                ],
            }
            for driver in drivers_info
        ]

        return response

    return context


class TariffsContext:
    def __init__(self):
        self.payment_options = [
            'card',
            'corp',
            'coupon',
            'applepay',
            'googlepay',
            'personal_wallet',
            'coop_account',
            'cash',
        ]

    def set_payment_options(self, payments):
        self.payment_options = payments


@pytest.fixture(name='tariffs_local', autouse=True)
def mock_tariffs_bulk(mockserver, load_json):
    context = TariffsContext()

    @mockserver.json_handler('taxi-tariffs/v1/tariff_settings/bulk_retrieve')
    def _updates(request):
        zone = request.args['zone_names']
        zone_response = {'zone': zone}
        if zone == 'moscow':
            tariff_settings = load_json('tariff_settings_moscow.json')
            tariff_settings['payment_options'] = context.payment_options
            zone_response.update({'tariff_settings': tariff_settings})
        else:
            zone_response.update({'status': 'not_found'})

        response = {'zones': [zone_response]}
        return response

    return context


class ParksContext:
    def __init__(self):
        self.park_info = {}
        self.balance_info = {}

    def set_park_country(self, dbid, country):
        self.park_info[dbid] = country

    def set_balance_info(
            self, park_id, driver_profile_id, balance, balance_limit,
    ):
        self.balance_info[(park_id, driver_profile_id)] = {
            'balance': str(balance),
            'balance_limit': str(balance_limit),
            'id': driver_profile_id,
        }


@pytest.fixture(name='parks', autouse=True)
def mock_parks(mockserver):
    context = ParksContext()

    @mockserver.json_handler('/parks/driver-profiles/list')
    def _driver_profiles_list(request):
        request = request.json
        park = request['query']['park']
        dbid = park['id']
        country = context.park_info.get(dbid, 'rus')
        driver_profiles_list = park.get('driver_profile', {}).get('id', [])
        driver_profiles_ids = [i for i in driver_profiles_list]
        driver_profiles = [
            {
                'accounts': [
                    context.balance_info.get(
                        (dbid, i),
                        {'balance': '100', 'balance_limit': '100', 'id': i},
                    ),
                ],
                'driver_profile': {'id': i},
            }
            for i in driver_profiles_ids
        ]

        return {
            'parks': [{'country_id': country}],
            'driver_profiles': driver_profiles,
            'offset': 0,
            'total': 1,
            'limit': 1,
        }

    return context


class DmsContext:
    def __init__(self):
        self.mode_type = 'totally_average_mode'

    def set_mode_type(self, mode_type):
        self.mode_type = mode_type


@pytest.fixture(name='driver_mode_subscription', autouse=True)
def mock_dms(mockserver, load_json):
    context = DmsContext()

    @mockserver.json_handler('driver-mode-subscription/v1/mode/get')
    def _mode_get(request):
        response = {
            'active_mode': 'totally_average_mode',
            'active_mode_type': context.mode_type,
            'active_since': '2019-05-01T12:00:00+0300',
        }
        return response

    return context


def pytest_collection_modifyitems(config, items):
    for item in items:
        item.add_marker(pytest.mark.geoareas(filename='geoareas.json'))
        item.add_marker(pytest.mark.tariffs(filename='tariffs.json'))


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'stop_billing_reports_mock: do not mock billing reports',
    )


@pytest.fixture(name='parks_activation_dpt', autouse=True)
def _parks_activation_mocks(parks_activation_mocks):
    parks_activation_mocks.set_parks(
        [
            {
                'revision': 1,
                'last_modified': '1970-01-15T03:56:07.000',
                'park_id': 'clid0',
                'city_id': 'spb',
                'data': {
                    'deactivated': False,
                    'can_cash': True,
                    'can_card': True,
                    'can_coupon': True,
                    'can_corp': True,
                },
            },
        ],
    )
    return parks_activation_mocks


@pytest.fixture(name='mock_parks_lowbalance_drivers')
def _lowbalance_drivers_mock_parks(request, mockserver):
    @mockserver.json_handler('/parks/driver-profiles/list')
    def _lowbalance_drivers(request):
        request = request.json
        park = request['query']['park']
        driver_profiles_list = park['driver_profile']['id']
        driver_profile_id = driver_profiles_list[0]
        driver_profiles = [
            {
                'accounts': [
                    {
                        'balance': '10',
                        'balance_limit': '100',
                        'id': driver_profile_id,
                    },
                ],
                'driver_profile': {'id': driver_profile_id},
            },
        ]

        return {
            'parks': [{'country_id': 'rus'}],
            'driver_profiles': driver_profiles,
            'offset': 0,
            'total': 1,
            'limit': 1,
        }
