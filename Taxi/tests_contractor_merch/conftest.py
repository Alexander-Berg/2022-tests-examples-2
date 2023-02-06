import copy
import datetime
import hashlib
import json

import aiohttp
import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from contractor_merch_plugins import *  # noqa: F403 F401


@pytest.fixture
def mock_contractor_merch_payments(mockserver, load_json):
    @mockserver.json_handler(
        '/contractor-merch-payments/internal/'
        'contractor-merch-payments/v1/transactions/list',
    )
    def _transactions_list(request):
        return context.transaction_list_response

    @mockserver.json_handler(
        '/contractor-merch-payments/internal/'
        'contractor-merch-payments/v1/completed_payments',
    )
    def _completed_payments(request):
        responses = load_json(context.completed_payments)

        payment_id = request.query['id']

        if payment_id in responses:
            return responses[payment_id]

        return mockserver.make_response(
            status=404,
            json={'code': 'payment_not_found', 'message': 'payment_not_found'},
        )

    @mockserver.json_handler(
        '/contractor-merch-payments/internal/v1/payment/draft',
    )
    def _draft(request):
        if context.draft_failed:
            return mockserver.make_response(
                status=400,
                json={
                    'code': '400',
                    'message': 'not_enough_money_on_drivers_balance',
                    'problem_description': {
                        'code': 'not_enough_money_on_drivers_balance',
                        'localized_message': (
                            f'На вашем балансе недостаточно '
                            f'средств для совершения покупки'
                        ),
                    },
                },
            )
        return {
            'payment_id': 'payment_id',
            'qr_code': 'https://keker.com/payment_id',
            'ttl_sec': 600,
        }

    class Context:
        def __init__(self):
            self.transactions_list = _transactions_list
            self.transaction_list_response = None
            self.draft = _draft
            self.draft_failed = False

            self.response_json = 'transactions_list_response.json'
            self.completed_payments = 'completed_payments_responses.json'

        def set_response_list(
                self, limit=0, all_transactions=None, after_cursor=None,
        ):
            if all_transactions is None:
                all_transactions = load_json(self.response_json)[
                    'transactions'
                ]

            class Cursor:
                def __init__(self, transaction):
                    self._event_at = self._from_iso(transaction['event_at'])
                    self._id = transaction['id']

                def is_greater(self, event_at_: str, id_: str):
                    return (self._event_at, self._id) > (
                        self._from_iso(event_at_),
                        id_,
                    )

                def _from_iso(self, date: str):
                    return datetime.datetime.strptime(
                        date, '%Y-%m-%dT%H:%M:%S%z',
                    )

            if after_cursor is not None:
                cursor = Cursor(json.loads(after_cursor))

                all_transactions = list(
                    filter(
                        lambda x: cursor.is_greater(x['created_at'], x['id']),
                        all_transactions,
                    ),
                )

            all_transactions = all_transactions[:limit]

            self.transaction_list_response = {'transactions': all_transactions}

        def fail_draft(self):
            self.draft_failed = True

    context = Context()

    return context


@pytest.fixture
def mock_unique_drivers(mockserver):
    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _retrieve_by_profiles(request):
        return context.retrieve_by_profiles_response

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/profiles/retrieve_by_uniques',
    )
    def _retrieve_by_uniques(request):
        return context.retrieve_by_uniques_response

    class FixtureContext:
        def __init__(self):
            self.retrieve_by_profiles = _retrieve_by_profiles
            self.retrieve_by_profiles_response = None
            self.retrieve_by_uniques = _retrieve_by_uniques
            self.retrieve_by_uniques_response = None

    context = FixtureContext()

    return context


@pytest.fixture
def mock_taximeter_xservice(mockserver):
    @mockserver.json_handler(
        '/taximeter-xservice/utils/qc/driver/exams/retrieve',
    )
    def _driver_exams_retrieve(request):
        return context.driver_exams_retrieve_response

    class FixtureContext:
        def __init__(self):
            self.driver_exams_retrieve = _driver_exams_retrieve
            self.driver_exams_retrieve_response = None

    context = FixtureContext()

    return context


@pytest.fixture
def mock_fleet_parks(mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    async def _park_list(request):
        response = {
            'parks': [
                {
                    'city_id': 'city1',
                    'country_id': context.country_id,
                    'demo_mode': False,
                    'id': 'park_id',
                    'is_active': True,
                    'is_billing_enabled': context.is_billing_enabled,
                    'is_franchising_enabled': False,
                    'locale': 'locale1',
                    'login': 'login1',
                    'name': 'super_park1',
                    'provider_config': {'clid': 'clid1', 'type': 'production'},
                    'tz_offset': 3,
                    'geodata': {'lat': 12, 'lon': 23, 'zoom': 0},
                    **context.updates,
                },
            ],
        }
        return response

    class Context:
        def __init__(self):
            self.park_list = _park_list
            self.is_billing_enabled = True
            self.country_id = 'rus'
            self.updates = {}

    context = Context()

    return context


@pytest.fixture
def mock_driver_profiles(mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    async def _driver_profiles(request):
        context.response['profiles'][0][
            'park_driver_profile_id'
        ] = request.json['id_in_set'][0]
        return context.response

    class Context:
        def __init__(self):
            self.driver_profiles = _driver_profiles

            self.response = {
                'profiles': [
                    {
                        'data': {
                            'full_name': {
                                'first_name': 'Питер',
                                'last_name': 'Паркер',
                            },
                            'license_driver_birth_date': (
                                '2001-08-10T00:00:00.000'
                            ),
                            'license': {'pd_id': 'license_pd_id_private'},
                            'email_pd_ids': [{'pd_id': 'email_pd_id_private'}],
                            'phone_pd_ids': [{'pd_id': 'phone_pd_id_private'}],
                        },
                    },
                ],
            }

    context = Context()
    return context


@pytest.fixture
def mock_personal(mockserver):
    @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
    async def _personal_driver_licenses(request):
        assert request.json == {
            'id': 'license_pd_id_private',
            'primary_replica': False,
        }

        return context.responses['driver_licenses']

    @mockserver.json_handler('/personal/v1/emails/retrieve')
    async def _personal_emails(request):
        assert request.json == {
            'id': 'email_pd_id_private',
            'primary_replica': False,
        }

        return context.responses['emails']

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    async def _personal_phones(request):
        assert request.json == {
            'id': 'phone_pd_id_private',
            'primary_replica': False,
        }

        return mockserver.make_response(
            json=context.responses['phones'],
            status=context.phones_response_status,
        )

    class Context:
        def __init__(self):
            self.personal_driver_licenses = _personal_driver_licenses
            self.personal_emails = _personal_emails
            self.personal_phones = _personal_phones

            self.responses = {
                'driver_licenses': {
                    'id': 'driver_licenses_id',
                    'value': '5124123666',
                },
                'emails': {
                    'id': 'emails_id',
                    'value': 'chelovek_pavuk@yandex.ru',
                },
                'phones': {'id': 'phones_id', 'value': '+79999999999'},
            }

            self.phones_response_status = 200

    context = Context()

    return context


@pytest.fixture
def mock_driver_tags(mockserver):
    @mockserver.json_handler('driver-tags/v1/drivers/match/profile')
    def _driver_tags(request):
        return {'tags': context.tags}

    class DriverTagsContext:
        def __init__(self):
            self.tags = ['bronze', 'silver', 'gold']

    context = DriverTagsContext()

    return context


@pytest.fixture
def mock_billing_replication(mockserver, load_json):
    @mockserver.json_handler('/billing-replication/v1/active-contracts/')
    def _active_contracts(request):
        return context.active_contracts_response

    class BillingReplicationContext:
        def __init__(self):
            self.active_contracts_response = load_json(
                'responses/active_contracts_response.json',
            )

            self.active_contracts = _active_contracts

        def set_currency(self, currency):
            self.active_contracts_response[0]['CURRENCY'] = currency.upper()

    context = BillingReplicationContext()

    return context


@pytest.fixture
def mock_feeds(mockserver, load_json):
    @mockserver.json_handler('feeds/v1/fetch')
    async def _fetch(request):
        if context.tags_param_for_fetch:
            filtered_response = copy.deepcopy(context.response)
            filtered_response['feed'] = []
            for tag in context.tags_param_for_fetch:
                for feed in context.response['feed']:
                    if tag in feed['tags']:
                        filtered_response['feed'].append(feed)
            return filtered_response
        return context.response

    @mockserver.json_handler('/feeds/v1/fetch_by_id')
    async def _fetch_by_id(request):
        return context.response

    @mockserver.json_handler('/feeds/v1/fetch_by_package_id')
    async def _fetch_by_package_id(request):
        return context.response

    class FeedsContext:
        def __init__(self):
            self.response = load_json('responses/feeds_response.json')

            self.fetch = _fetch
            self.fetch_by_id = _fetch_by_id
            self.fetch_by_package_id = _fetch_by_package_id
            self.tags_param_for_fetch = []

        def set_response(self, response):
            self.response = response

    context = FeedsContext()

    return context


@pytest.fixture
def mock_parks_replica(mockserver, load_json):
    @mockserver.json_handler(
        '/parks-replica/v1/parks/billing_client_id/retrieve',
    )
    def _billing_client_id_retrieve(request):
        return {'billing_client_id': context.billing_client_id}

    class ParksReplicaContext:
        def __init__(self):
            self.billing_client_id_retrieve = _billing_client_id_retrieve

            self.billing_client_id = '187701087'

    context = ParksReplicaContext()

    return context


@pytest.fixture
def mock_tariffs(mockserver, load_json):
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
def mock_agglomerations(mockserver, load_json):
    @mockserver.json_handler(
        '/taxi-agglomerations/v1/geo_nodes/get_mvp_oebs_id',
    )
    def _agglomerations(request):
        return load_json('get_mvp_oebs_id_response.json')

    return _agglomerations


@pytest.fixture
def mock_billing_orders(mockserver, load_json):
    @mockserver.json_handler('/billing-orders/v2/process/async')
    def _billing_orders(request):
        return load_json('process_async_response.json')

    return _billing_orders


@pytest.fixture
def mock_driver_wall(mockserver):
    @mockserver.json_handler('/driver-wall/internal/driver-wall/v1/add')
    def _driver_wall(request):
        return {'id': 'id'}

    return _driver_wall


@pytest.fixture
def mock_umlaas_contractors(mockserver, load_json):
    @mockserver.json_handler(
        '/umlaas-contractors/umlaas-contractors/contractor-merch/v1/offers_list',  # noqa: E501
    )
    def _umlaas_contractors_offers_list(request):
        return {
            'selection_id': request.json['selection_id'],
            'offers': request.json['offers'],
        }

    @mockserver.json_handler(
        '/umlaas-contractors/umlaas-contractors/contractor-merch/v1/offer',
    )
    def _umlaas_contractors_offer(request):
        return {
            'selection_id': request.json['selection_id'],
            'offer': request.json['offer'],
        }

    @mockserver.json_handler(
        f'/umlaas-contractors/umlaas-contractors'
        f'/contractor-merch/v1/offers_list_flutter',
    )
    def _umlaas_contractors_offers_list_flutter(request):
        if not context.failure_flutter:
            return {
                'selection_id': request.json['selection_id'],
                'pinned_with_ranked_offers': (
                    load_json('umlaas/pinned_with_ranked_offers.json')
                    if not context.custom_pinned_with_ranked_offers_json
                    else context.custom_pinned_with_ranked_offers_json
                ),
                'fully_ranked_offers': load_json(
                    'umlaas/fully_ranked_offers.json',
                ),
            }
        return aiohttp.web.json_response(status=500)

    class UmlaasContractorsContext:
        def make_flutter_list_failure(self):
            self.failure_flutter = True

        def __init__(self):
            self.failure_flutter = False
            self.umlaas_contractors_offers_list = (
                _umlaas_contractors_offers_list
            )
            self.umlaas_contractors_offer = _umlaas_contractors_offer
            self.umlaas_contractors_offers_list_flutter = (  # pylint: disable=C0103 # noqa: E501
                _umlaas_contractors_offers_list_flutter
            )
            self.custom_pinned_with_ranked_offers_json = (  # pylint: disable=C0103 # noqa: E501
                None
            )

    context = UmlaasContractorsContext()

    return context


@pytest.fixture
def mock_fleet_transactions_api(mockserver):
    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def _balances_list(request):
        return {
            'driver_profiles': [
                {
                    'driver_profile_id': 'driver1',
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
            self.balance = '100500'

    context = FleetTransactionsContext()

    return context


@pytest.fixture
def mock_parks_activation(mockserver):
    @mockserver.json_handler('/parks-activation/v1/parks/activation/retrieve')
    def _handler_retrieve(request):
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

    @mockserver.json_handler('parks-activation/v2/parks/activation/balances')
    def _handler_balances(request):
        balances = []
        contract_v2_balance = {}
        if context.balance or context.threshold or context.threshold_dynamic:
            if context.balance:
                contract_v2_balance.update({'balance': context.balance})
            if context.threshold:
                contract_v2_balance.update({'threshold': context.threshold})
            if context.threshold_dynamic:
                contract_v2_balance.update(
                    {'threshold_dynamic': context.threshold_dynamic},
                )
            contract_v2_balance.update({'service_id': context.service_id})

        if contract_v2_balance:
            contract_v2_balance.update({'contract_id': '1'})
            balances.append(contract_v2_balance)

        return {'balances': balances}

    class ParksActivationContext:
        def __init__(self):
            self.handler_retrieve = _handler_retrieve
            self.handler_balances = _handler_balances
            self.balance = '500000'
            self.threshold = '0'
            self.threshold_dynamic = '0'
            self.can_cash = True
            self.service_id = 111

    context = ParksActivationContext()

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
def mock_metro_vouchers(mockserver):
    def generate_signature(unixtime: str, body: str, secret: str):
        string_to_hash = unixtime + secret + body + secret
        return hashlib.sha1(string_to_hash.encode()).hexdigest()

    @mockserver.json_handler(
        r'/metro-vouchers/api/1/json/'
        r'(?P<api_login>\w+)/(?P<unixtime>\w+)/(?P<signature>\w+)',
        regex=True,
    )
    async def _metro_endpoint(request, api_login, unixtime, signature):

        if context.request:
            assert request.json == context.request

        if context.unixtime:
            assert unixtime == context.unixtime

        if context.check_signature:
            assert signature == generate_signature(
                context.unixtime,
                request.get_data().decode(),
                context.secret_key,
            )

        return context.response

    class Context:
        def __init__(self):
            self.metro_endpoint = _metro_endpoint
            self.barcode = '(255)4607070057079'
            self.response = {
                'request_proc': 'ok',
                'ops': [
                    {
                        'proc': 'ok',
                        'data': {
                            'barcode': f'{self.barcode}',
                            'result': 'success',
                            'message': 'new_card',
                        },
                    },
                ],
            }

            self.request = None
            self.unixtime = None
            self.secret_key = 'KEKING_ONLINE'
            self.check_signature = False

    context = Context()

    return context


@pytest.fixture
def mock_tags(mockserver):
    @mockserver.json_handler('/tags/v2/upload')
    def _handler(request):
        return {'status': 'ok'}

    class TagsContext:
        def __init__(self):
            self.handler = _handler

    context = TagsContext()

    return context


@pytest.fixture
def mock_fleet_vehicles(mockserver):
    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/cache-retrieve')
    def _get_car(request):
        return {
            'vehicles': [
                {
                    'data': {'number': 'А001МР97'},
                    'park_id_car_id': request.json['id_in_set'][0],
                },
            ],
        }

    class Context:
        def __init__(self):
            self.get_car = _get_car

    context = Context()
    return context


@pytest.fixture
def mock_driver_trackstory(mockserver):
    @mockserver.json_handler('/driver-trackstory/position')
    def _position(request):
        if context.has_position:
            return mockserver.make_response(
                json={
                    'position': {
                        'direction': 0,
                        'lat': 37.5,
                        'lon': 55.7654321,
                        'speed': 0,
                        'timestamp': 100,
                    },
                    'type': 'raw',
                },
                status=200,
            )

        return mockserver.make_response(json={'message': 'msg'}, status=404)

    class Context:
        def __init__(self):
            self.position = _position
            self.has_position = True

        def set_has_position(self, has_position):
            self.has_position = has_position

    context = Context()
    return context
