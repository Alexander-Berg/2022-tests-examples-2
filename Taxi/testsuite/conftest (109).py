# pylint: disable=redefined-outer-name
import pytest

# root conftest for service contractor-balances
pytest_plugins = ['contractor_balances_plugins.pytest_plugins']

GEODATA = {'lat': 66.1234, 'lon': 66.2345}


class BalanceUpdateContext:
    def __init__(self):
        self.set_data()

    def set_data(
            self,
            old_balance=321,
            new_balance=123,
            balance_limit=231,
            response_code=200,
            balance_last_entry_id=8484848484,
            balance_changed_at='2020-09-27T09:00:00+00:00',
            balance_deny_onlycard=False,
    ):
        self.old_balance = old_balance
        self.new_balance = new_balance
        self.balance_limit = balance_limit
        self.response_code = response_code
        self.balance_last_entry_id = balance_last_entry_id
        self.balance_changed_at = balance_changed_at
        self.balance_deny_onlycard = balance_deny_onlycard


@pytest.fixture
def balance_update_context():
    return BalanceUpdateContext()


@pytest.fixture
def mock_contractor_balance_update(mockserver, balance_update_context):
    @mockserver.json_handler('/driver-profiles/internal/v1/contractor/balance')
    def mock_callback(request):
        if balance_update_context.response_code != 200:
            return mockserver.make_response(
                json={
                    'code': str(balance_update_context.response_code),
                    'message': 'Driver\'s balance wasn\'t updated',
                },
                status=balance_update_context.response_code,
            )

        assert request.json == {
            'balance': balance_update_context.new_balance,
            'balance_last_entry_id': (
                balance_update_context.balance_last_entry_id
            ),
            'balance_changed_at': balance_update_context.balance_changed_at,
        }

        return {
            'balance': balance_update_context.old_balance,
            'balance_limit': balance_update_context.balance_limit,
            'balance_deny_onlycard': (
                balance_update_context.balance_deny_onlycard
            ),
        }

    return mock_callback


class PushContext:
    def __init__(self):
        self.check_request = False
        self.request_body = None
        self.idempotency_token = None

    def set_data(
            self,
            park_id,
            contractor_profile_id,
            intent,
            collapse_key,
            message_id,
            data=None,
            notification=None,
            locale=None,
    ):
        self.check_request = True
        self.idempotency_token = message_id
        self.request_body = {
            'service': 'taximeter',
            'client_id': f'{park_id}-{contractor_profile_id}',
            'intent': intent,
            'collapse_key': collapse_key,
            'ttl': 300,
            'message_id': message_id,
            **({} if locale is None else {'locale': locale}),
            **({} if data is None else {'data': data}),
            **({} if notification is None else {'notification': notification}),
        }


@pytest.fixture
def client_notify_v2_push_context():
    return PushContext()


@pytest.fixture
def mock_client_notify_v2_push(mockserver, client_notify_v2_push_context):
    @mockserver.json_handler('/client-notify/v2/push')
    def mock_callback(request):
        if client_notify_v2_push_context.check_request:
            assert request.json == client_notify_v2_push_context.request_body
            assert request.headers['X-Idempotency-Token'] == (
                client_notify_v2_push_context.idempotency_token
            )
        return {'notification_id': 'id'}

    return mock_callback


class ParkListContext:
    def __init__(self):
        self.set_data()

    def set_data(
            self,
            clid='1',
            city_id='msk',
            country_id='rus',
            locale='ru',
            fleet_type=None,
    ):
        self.clid = clid
        self.city_id = city_id
        self.country_id = country_id
        self.locale = locale
        self.fleet_type = fleet_type


@pytest.fixture
def parks_list_context():
    return ParkListContext()


@pytest.fixture
def mock_parks_list(mockserver, parks_list_context):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def mock_callback(request):
        return {
            'parks': [
                {
                    'id': 'park1',
                    'login': 'any login',
                    'name': 'any name',
                    'is_active': False,
                    'city_id': parks_list_context.city_id,
                    'locale': parks_list_context.locale,
                    'is_billing_enabled': False,
                    'is_franchising_enabled': False,
                    'country_id': parks_list_context.country_id,
                    'demo_mode': False,
                    'provider_config': {
                        'clid': parks_list_context.clid,
                        'apikey': '77fc38576fc8424599f737f4af8ed61f',
                        'type': 'production',
                    },
                    'geodata': {**GEODATA, 'zoom': 123},
                    'fleet_type': parks_list_context.fleet_type,
                },
            ],
        }

    return mock_callback


class PaymentMethodsContext:
    def __init__(self):
        self.available_methods = {
            'cash': True,
            'googlepay': True,
            'applepay': True,
            'personal_wallet': True,
            'coop_account': True,
            'coupon': True,
            'card': True,
            'corp': True,
        }

    def set_data(self, available_methods):
        self.available_methods.update(available_methods)


@pytest.fixture
def payment_methods_context():
    return PaymentMethodsContext()


@pytest.fixture
def mock_park_payment_methods(mockserver, payment_methods_context):
    @mockserver.json_handler('/taximeter-api/taximeter/park-payment-methods')
    def mock_callback(request):
        assert request.headers.get('YaTaxi-Api-Key') == 'supersecret'
        assert request.query.get('clid') == '1'
        assert float(request.query.get('lon')) == GEODATA['lon']
        assert float(request.query.get('lat')) == GEODATA['lat']

        return {'available_methods': payment_methods_context.available_methods}

    return mock_callback
