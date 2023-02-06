import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from contractor_merch_payments_plugins import *  # noqa: F403 F401


@pytest.fixture
def mock_merchant_profiles(mockserver):
    def _prepare_merchant():
        merchant = {
            'merchant_name': context.merchant_name,
            'payment_scheme': context.payment_scheme,
            'enable_requisites_check_on_draft': (
                context.enable_requisites_check
            ),
            'enable_balance_check_on_pay': (
                context.enable_balance_check_on_pay
            ),
        }

        if context.park_id is not None:
            merchant['park_id'] = context.park_id

        if context.payment_ttl_sec is not None:
            merchant['payment_ttl_sec'] = context.payment_ttl_sec

        return merchant

    @mockserver.json_handler(
        'merchant-profiles/internal/merchant-profiles/v1/merchant',
    )
    async def _merchant(request):
        return _prepare_merchant()

    @mockserver.json_handler(
        'merchant-profiles/internal/'
        'merchant-profiles/v1/merchants/bulk-retrieve',
    )
    async def _merchants_bulk_retrieve(request):
        merchant_ids = request.json['merchant_ids']

        return {
            'merchants': [
                {'merchant_id': merchant_id, 'merchant': _prepare_merchant()}
                for merchant_id in merchant_ids
            ],
        }

    class Context:
        def __init__(self):
            self.merchant = _merchant
            self.merchants_bulk_retrieve = _merchants_bulk_retrieve

            self.merchant_name = 'Bloodseeker'
            self.park_id = None

            self.payment_scheme = 'remittance'

            self.enable_requisites_check = False
            self.enable_balance_check_on_pay = True
            self.payment_ttl_sec = None

    context = Context()

    return context


@pytest.fixture
def mock_billing_orders(mockserver, load_json):
    @mockserver.json_handler('/billing-orders/v2/process/async')
    def _billing_orders(request):
        return load_json('process_async_response.json')

    return _billing_orders


@pytest.fixture
def mock_fleet_transactions_api(mockserver):
    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def _balances_list(request):
        return {
            'driver_profiles': [
                {
                    'driver_profile_id': 'driver-profile-id-0',
                    'balances': [
                        {
                            'accrued_at': '2020-03-03T18:00:00+00:00',
                            'total_balance': (context.balance),
                        },
                    ],
                },
            ],
        }

    class FleetTransactionsContext:
        def __init__(self):
            self.balances_list = _balances_list

            self.balance = '1000'

    context = FleetTransactionsContext()

    return context


@pytest.fixture
def mock_billing_replication(mockserver, load_json):
    @mockserver.json_handler('/billing-replication/v1/active-contracts/')
    def _billing_replication(request):
        clid_to_billing_id = {
            'buyer-client-id': 124124,
            'merchant-client-id': 222222,
        }
        return [
            {
                **context.response,
                'ID': clid_to_billing_id.get(
                    request.query['client_id'], 100500,
                ),
            },
        ]

    class Context:
        def __init__(self):
            self.billing_replication = _billing_replication
            self.response = load_json('active_contracts_response.json')

    context = Context()

    return context


@pytest.fixture
def mock_parks_replica(mockserver, load_json):
    @mockserver.json_handler(
        '/parks-replica/v1/parks/billing_client_id/retrieve',
    )
    def _parks_replica(request):
        clid_to_billing_id = {
            'buyer-clid': 'buyer-client-id',
            'merchant-clid': 'merchant-client-id',
        }
        return {
            'billing_client_id': clid_to_billing_id.get(
                request.query['park_id'], 'some-billing-client-id',
            ),
        }

    return _parks_replica


@pytest.fixture
def mock_payments_bot(mockserver):
    @mockserver.json_handler(
        'contractor-merch-payments-bot/internal/'
        'contractor-merch-payments-bot/v1/notify-on-payment-completion',
    )
    async def _notify_on_payment_completion(request):
        return {}

    class Context:
        def __init__(self):
            self.notify_on_payment_completion = _notify_on_payment_completion

    context = Context()

    return context


@pytest.fixture
def mock_integration_api(mockserver):
    @mockserver.json_handler(
        'contractor-merch-integration-api/'
        'contractor-merchants/v1/internal/v1/notify',
    )
    async def _notify(request):
        return {}

    class Context:
        def __init__(self):
            self.notify = _notify

    context = Context()

    return context


@pytest.fixture
def mock_fleet_parks(mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    async def _park_list(request):
        park_id = request.json['query']['park']['ids'][0]
        return {
            'parks': [
                {
                    'city_id': 'city1',
                    'country_id': 'rus',
                    'demo_mode': False,
                    'id': park_id,
                    'is_active': True,
                    'is_billing_enabled': True,
                    'is_franchising_enabled': False,
                    'locale': 'locale1',
                    'login': 'login1',
                    'name': 'super_park1',
                    'provider_config': {
                        'clid': context.clids_mapping.get(park_id, 'clid1'),
                        'type': 'production',
                    },
                    'tz_offset': 3,
                    'geodata': {'lat': 12, 'lon': 23, 'zoom': 0},
                    'driver_partner_source': 'selfemployed_fns',
                    **context.fields_update,
                },
            ],
        }

    class Context:
        def __init__(self):
            self.park_list = _park_list
            self.fields_update = {}
            self.clids_mapping = {'some_park_id': 'some_clid'}

    context = Context()

    return context


@pytest.fixture
def mock_parks_activation(mockserver):
    @mockserver.json_handler('/parks-activation/v1/parks/activation/retrieve')
    def _handler(request):
        return {
            'parks_activation': [
                {
                    'revision': 1,
                    'last_modified': '1970-01-15T03:56:07.000',
                    'park_id': 'park1',
                    'city_id': 'spb',
                    'data': {
                        'deactivated': False,
                        'can_cash': context.can_cash,
                        'can_card': False,
                        'can_coupon': True,
                        'can_corp': False,
                    },
                },
            ],
        }

    class ParksActivationContext:
        def __init__(self):
            self.handler = _handler
            self.can_cash = True

    context = ParksActivationContext()

    return context


@pytest.fixture
def mock_driver_tags(mockserver):
    @mockserver.json_handler('driver-tags/v1/drivers/match/profile')
    def _driver_tags(request):
        return {'tags': ['tag1', 'tag2', 'tag3'], **context.fields_update}

    class Context:
        def __init__(self):
            self.fields_update = {}

    context = Context()

    return context


@pytest.fixture
def mock_driver_profiles(mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def _driver_profiles(request):
        context.response['profiles'][0][
            'park_driver_profile_id'
        ] = request.json['id_in_set'][0]
        context.response['profiles'][0]['data'][
            'balance_limit'
        ] = context.balance_limit
        return context.response

    class Context:
        def __init__(self):
            self.driver_profiles = _driver_profiles
            self.balance_limit = '0'
            self.response = {
                'profiles': [
                    {
                        'data': {'balance_limit': self.balance_limit},
                        'park_driver_profile_id': (
                            'change this in _driver_profiles'
                        ),
                    },
                ],
            }

    context = Context()
    return context


@pytest.fixture
def mock_fleet_antifraud(mockserver):
    @mockserver.json_handler('/fleet-antifraud/v1/park-check/blocked-balance')
    async def _fleet_antifraud(request):
        context.response['blocked_balance'] = context.fleet_antifraud_limit
        return context.response

    class Context:
        def __init__(self):
            self.fleet_antifraud = _fleet_antifraud
            self.fleet_antifraud_limit = '0'
            self.response = {'blocked_balance': '0'}

    context = Context()
    return context


@pytest.fixture
def mock_taxi_tariffs(mockserver, load_json):
    @mockserver.json_handler('/taxi-tariffs/v1/tariff_zones')
    def _tariffs(request):
        return context.tariffs_response

    class Context:
        def __init__(self):
            self.tariffs = _tariffs
            self.tariffs_response = load_json('tariff_zones_response.json')

    context = Context()

    return context


@pytest.fixture
def mock_taxi_agglomerations(mockserver, load_json):
    @mockserver.json_handler(
        '/taxi-agglomerations/v1/geo_nodes/get_mvp_oebs_id',
    )
    def _agglomerations(request):
        return load_json('get_mvp_oebs_id_response.json')

    return _agglomerations
