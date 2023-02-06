import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from contractor_instant_payouts_plugins import *  # noqa: F403 F401

from tests_contractor_instant_payouts import mock_api_impl
from tests_contractor_instant_payouts import utils


DEFAULT_PARK_ID = '48b7b5d81559460fb1766938f94009c1'

DEFAULT_CONTRACTOR_ID = '48b7b5d81559460fb176693800000001'


@pytest.fixture
async def contractors_payouts_options(taxi_contractor_instant_payouts):
    async def execute(
            *,
            park_id=DEFAULT_PARK_ID,
            contractor_id=DEFAULT_CONTRACTOR_ID,
            **kwargs,
    ):
        params = {'park_id': park_id, 'contractor_id': contractor_id}
        return await taxi_contractor_instant_payouts.get(
            '/v1/contractors/payouts/options', params=params,
        )

    return execute


@pytest.fixture
async def contractors_payouts_preview(taxi_contractor_instant_payouts):
    async def execute(
            *,
            park_id=DEFAULT_PARK_ID,
            contractor_id=DEFAULT_CONTRACTOR_ID,
            withdrawal_amount=None,
            **kwargs,
    ):
        params = {'park_id': park_id, 'contractor_id': contractor_id}
        if withdrawal_amount is not None:
            params['withdrawal_amount'] = withdrawal_amount
        return await taxi_contractor_instant_payouts.get(
            '/v1/contractors/payouts/preview', params=params,
        )

    return execute


@pytest.fixture
async def contractors_payouts_withdrawal(taxi_contractor_instant_payouts):
    async def execute(
            *,
            park_id=DEFAULT_PARK_ID,
            contractor_id=DEFAULT_CONTRACTOR_ID,
            idempotency_token='TESTSUITE',
            json=None,
            **kwargs,
    ):
        params = {'park_id': park_id, 'contractor_id': contractor_id}
        return await taxi_contractor_instant_payouts.post(
            '/v1/contractors/payouts/withdrawal',
            headers={'X-Idempotency-Token': idempotency_token},
            params=params,
            json={'amount': '100'} if json is None else json,
        )

    return execute


@pytest.fixture
async def contractors_payouts_list(taxi_contractor_instant_payouts):
    async def execute(
            *,
            park_id=DEFAULT_PARK_ID,
            contractor_id=DEFAULT_CONTRACTOR_ID,
            **kwargs,
    ):
        params = {'park_id': park_id, 'contractor_id': contractor_id}
        for name in ['cursor', 'limit']:
            if name in kwargs:
                params[name] = kwargs[name]
        return await taxi_contractor_instant_payouts.get(
            '/v1/contractors/payouts/list', params=params,
        )

    return execute


@pytest.fixture
async def contractors_rules_list(taxi_contractor_instant_payouts):
    async def execute(*, park_id=DEFAULT_PARK_ID, **kwargs):
        params = {'park_id': park_id}
        json = {'contractor_ids': kwargs['contractor_ids']}
        return await taxi_contractor_instant_payouts.post(
            'v1/contractors/rules/list', params=params, json=json,
        )

    return execute


@pytest.fixture
async def set_contractor_rule(taxi_contractor_instant_payouts):
    async def execute(
            *,
            park_id=DEFAULT_PARK_ID,
            contractor_id=DEFAULT_CONTRACTOR_ID,
            rule_id=None,
            **kwargs,
    ):
        params = {'park_id': park_id, 'contractor_id': contractor_id}
        json = {'rule_id': rule_id}
        return await taxi_contractor_instant_payouts.put(
            'v1/contractors/rules/by-id', params=params, json=json,
        )

    return execute


@pytest.fixture
async def set_contractor_default_rule(taxi_contractor_instant_payouts):
    async def execute(
            *,
            park_id=DEFAULT_PARK_ID,
            contractor_id=DEFAULT_CONTRACTOR_ID,
            **kwargs,
    ):
        params = {'park_id': park_id, 'contractor_id': contractor_id}
        return await taxi_contractor_instant_payouts.put(
            'v1/contractors/rules/default', params=params,
        )

    return execute


@pytest.fixture
async def get_default_rule(taxi_contractor_instant_payouts):
    async def execute(*, park_id=DEFAULT_PARK_ID, **kwargs):
        params = {'park_id': park_id}
        return await taxi_contractor_instant_payouts.get(
            'v1/rules/default', params=params,
        )

    return execute


@pytest.fixture
async def stock(load_json, mockserver):
    data = load_json('stock.json')

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def handler1(request):
        parks = []

        for park_id in request.json['query']['park']['ids']:
            park = data.get(park_id)
            if park:
                attributes = park['attributes']
                parks.append(
                    {
                        'id': park_id,
                        'login': 'TESTSUITE',
                        'name': 'TESTSUITE',
                        'is_active': True,
                        'is_billing_enabled': False,
                        'is_franchising_enabled': False,
                        'demo_mode': False,
                        'country_id': 'TESTSUITE',
                        'city_id': 'TESTSUITE',
                        'locale': 'TESTSUITE',
                        'driver_partner_source': attributes[
                            'driver_partner_source'
                        ],
                        'tz_offset': attributes['tz'],
                        'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                    },
                )

        return {'parks': parks}

    @mockserver.json_handler('/parks/driver-profiles/list')
    def handler2(request):
        parks = []
        driver_profiles = []

        park_id = request.json['query']['park']['id']
        park = data.get(park_id)
        if park:
            attributes = park['attributes']
            parks.append(
                {
                    'id': park_id,
                    'tz': attributes['tz'],
                    'driver_partner_source': attributes[
                        'driver_partner_source'
                    ],
                },
            )
            for contractor_id, contractor in park['contractors'].items():
                account = contractor['account']
                balance = contractor['balance']
                driver_profiles.append(
                    {
                        'accounts': [
                            {
                                'currency': account['currency'],
                                'balance': balance['amount'],
                            },
                        ],
                        'driver_profile': {'id': contractor_id},
                    },
                )

        return {
            'limit': 0,
            'offset': 0,
            'total': 0,
            'parks': parks,
            'driver_profiles': driver_profiles,
        }

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def handler3(request):
        driver_profiles = []

        query = request.json['query']
        park = data.get(query['park']['id'])
        if park:
            for contractor_id in query['park']['driver_profile']['ids']:
                contractor = park['contractors'].get(contractor_id)
                if contractor:
                    balance = contractor['balance']
                    driver_profiles.append(
                        {
                            'driver_profile_id': contractor_id,
                            'balances': [
                                {
                                    'accrued_at': balance['time'],
                                    'total_balance': balance['amount'],
                                },
                            ],
                        },
                    )

        return {'driver_profiles': driver_profiles}

    @mockserver.json_handler('/fleet-antifraud/v1/park-check/blocked-balance')
    def handler4(request):
        return {'blocked_balance': '0'}

    return (handler1, handler2, handler3, handler4)


@pytest.fixture(name='mock_driver_profiles')
def _mock_driver_profiles(mockserver, load_json):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _mock_retrieve(request):
        def make_not_found(park_driver_profile_id):
            return {
                'revision': '0_1234567_0',
                'park_driver_id': park_driver_profile_id,
                'park_driver_profile_id': park_driver_profile_id,
            }

        profiles = {
            profile['park_driver_profile_id']: profile
            for profile in load_json('driver_profiles.json')
        }
        ids = request.json['id_in_set']
        return {
            'profiles': [profiles.get(id, make_not_found(id)) for id in ids],
        }


@pytest.fixture
def pg_dump(pgsql):
    def execute():
        with pgsql['contractor_instant_payouts'].cursor() as cursor:
            return utils.pg_dump_all(cursor)

    return execute


@pytest.fixture
def mock_api(load_yaml, mockserver):
    return mock_api_impl.setup(load_yaml, mockserver)


@pytest.fixture
def fleet_v2(taxi_contractor_instant_payouts):
    class FleetV2:
        async def get_account_list(
                self,
                *,
                yandex_uid=1000,
                user_ticket='TESTSUITE-USER-TICKET',
                user_ticket_provider='yandex',
                park_id='PARK-01',
        ):
            return await taxi_contractor_instant_payouts.get(
                '/fleet/instant-payouts/v2/accounts',
                headers={
                    'X-Yandex-UID': str(yandex_uid),
                    'X-Ya-User-Ticket': user_ticket,
                    'X-Ya-User-Ticket-Provider': user_ticket_provider,
                    'X-Park-Id': park_id,
                },
            )

        async def create_account(
                self,
                *,
                yandex_uid=1000,
                user_ticket='TESTSUITE-USER-TICKET',
                user_ticket_provider='yandex',
                park_id='PARK-01',
                json,
        ):
            return await taxi_contractor_instant_payouts.post(
                '/fleet/instant-payouts/v2/accounts',
                headers={
                    'X-Yandex-UID': str(yandex_uid),
                    'X-Ya-User-Ticket': user_ticket,
                    'X-Ya-User-Ticket-Provider': user_ticket_provider,
                    'X-Park-Id': park_id,
                },
                json=json,
            )

        async def update_account(
                self,
                *,
                yandex_uid=1000,
                user_ticket='TESTSUITE-USER-TICKET',
                user_ticket_provider='yandex',
                park_id,
                account_id,
                json,
        ):
            params = {'account_id': account_id}
            return await taxi_contractor_instant_payouts.patch(
                '/fleet/instant-payouts/v2/accounts/by-id',
                params=params,
                headers={
                    'X-Yandex-UID': str(yandex_uid),
                    'X-Ya-User-Ticket': user_ticket,
                    'X-Ya-User-Ticket-Provider': user_ticket_provider,
                    'X-Park-Id': park_id,
                },
                json=json,
            )

        async def delete_account(
                self,
                *,
                yandex_uid=1000,
                user_ticket='TESTSUITE-USER-TICKET',
                user_ticket_provider='yandex',
                park_id,
                account_id,
        ):
            params = {'account_id': account_id}
            return await taxi_contractor_instant_payouts.delete(
                '/fleet/instant-payouts/v2/accounts/by-id',
                params=params,
                headers={
                    'X-Yandex-UID': str(yandex_uid),
                    'X-Ya-User-Ticket': user_ticket,
                    'X-Ya-User-Ticket-Provider': user_ticket_provider,
                    'X-Park-Id': park_id,
                },
            )

        async def get_rule(
                self,
                *,
                yandex_uid=1000,
                user_ticket='TESTSUITE-USER-TICKET',
                user_ticket_provider='yandex',
                park_id,
                rule_id,
        ):
            params = {'rule_id': rule_id}
            return await taxi_contractor_instant_payouts.get(
                '/fleet/instant-payouts/v2/rules/by-id',
                params=params,
                headers={
                    'X-Yandex-UID': str(yandex_uid),
                    'X-Ya-User-Ticket': user_ticket,
                    'X-Ya-User-Ticket-Provider': user_ticket_provider,
                    'X-Park-Id': park_id,
                },
            )

        async def get_rule_list(
                self,
                *,
                yandex_uid=1000,
                user_ticket='TESTSUITE-USER-TICKET',
                user_ticket_provider='yandex',
                park_id,
        ):
            return await taxi_contractor_instant_payouts.get(
                '/fleet/instant-payouts/v2/rules',
                headers={
                    'X-Yandex-UID': str(yandex_uid),
                    'X-Ya-User-Ticket': user_ticket,
                    'X-Ya-User-Ticket-Provider': user_ticket_provider,
                    'X-Park-Id': park_id,
                },
            )

        async def create_rule(
                self,
                *,
                yandex_uid=1000,
                user_ticket='TESTSUITE-USER-TICKET',
                user_ticket_provider='yandex',
                park_id,
                json,
        ):
            return await taxi_contractor_instant_payouts.post(
                '/fleet/instant-payouts/v2/rules',
                headers={
                    'X-Yandex-UID': str(yandex_uid),
                    'X-Ya-User-Ticket': user_ticket,
                    'X-Ya-User-Ticket-Provider': user_ticket_provider,
                    'X-Park-Id': park_id,
                },
                json=json,
            )

        async def get_default_rule(
                self,
                *,
                yandex_uid=1000,
                user_ticket='TESTSUITE-USER-TICKET',
                user_ticket_provider='yandex',
                park_id,
        ):
            return await taxi_contractor_instant_payouts.get(
                '/fleet/instant-payouts/v2/rules/default',
                headers={
                    'X-Yandex-UID': str(yandex_uid),
                    'X-Ya-User-Ticket': user_ticket,
                    'X-Ya-User-Ticket-Provider': user_ticket_provider,
                    'X-Park-Id': park_id,
                },
            )

        async def update_rule(
                self,
                *,
                yandex_uid=1000,
                user_ticket='TESTSUITE-USER-TICKET',
                user_ticket_provider='yandex',
                park_id,
                rule_id,
                json,
        ):
            params = {'rule_id': rule_id}
            return await taxi_contractor_instant_payouts.patch(
                '/fleet/instant-payouts/v2/rules/by-id',
                params=params,
                headers={
                    'X-Yandex-UID': str(yandex_uid),
                    'X-Ya-User-Ticket': user_ticket,
                    'X-Ya-User-Ticket-Provider': user_ticket_provider,
                    'X-Park-Id': park_id,
                },
                json=json,
            )

        async def delete_rule(
                self,
                *,
                yandex_uid=1000,
                user_ticket='TESTSUITE-USER-TICKET',
                user_ticket_provider='yandex',
                park_id,
                rule_id,
        ):
            params = {'rule_id': rule_id}
            return await taxi_contractor_instant_payouts.delete(
                '/fleet/instant-payouts/v2/rules/by-id',
                params=params,
                headers={
                    'X-Yandex-UID': str(yandex_uid),
                    'X-Ya-User-Ticket': user_ticket,
                    'X-Ya-User-Ticket-Provider': user_ticket_provider,
                    'X-Park-Id': park_id,
                },
            )

        async def get_contractor_rule_list(
                self,
                *,
                yandex_uid=1000,
                user_ticket='TESTSUITE-USER-TICKET',
                user_ticket_provider='yandex',
                park_id,
                **kwargs,
        ):
            return await taxi_contractor_instant_payouts.get(
                '/fleet/instant-payouts/v2/contractor-rules',
                params=kwargs,
                headers={
                    'X-Yandex-UID': str(yandex_uid),
                    'X-Ya-User-Ticket': user_ticket,
                    'X-Ya-User-Ticket-Provider': user_ticket_provider,
                    'X-Park-Id': park_id,
                },
            )

        async def set_contractor_rule(
                self,
                *,
                yandex_uid=1000,
                user_ticket='TESTSUITE-USER-TICKET',
                user_ticket_provider='yandex',
                park_id,
                contractor_id,
                json,
        ):
            params = {'contractor_id': contractor_id}
            return await taxi_contractor_instant_payouts.put(
                '/fleet/instant-payouts/v2/contractor-rules/by-id',
                params=params,
                headers={
                    'X-Yandex-UID': str(yandex_uid),
                    'X-Ya-User-Ticket': user_ticket,
                    'X-Ya-User-Ticket-Provider': user_ticket_provider,
                    'X-Park-Id': park_id,
                },
                json=json,
            )

        async def set_all_contractors_rule(
                self,
                *,
                yandex_uid=1000,
                user_ticket='TESTSUITE-USER-TICKET',
                user_ticket_provider='yandex',
                park_id,
                idempotency_token='token',
                json,
        ):
            headers = {
                'X-Yandex-UID': str(yandex_uid),
                'X-Ya-User-Ticket': user_ticket,
                'X-Ya-User-Ticket-Provider': user_ticket_provider,
                'X-Park-Id': park_id,
                'X-Idempotency-Token': idempotency_token,
            }
            return await taxi_contractor_instant_payouts.post(
                '/fleet/instant-payouts/v2/contractor-rules/by-park-id',
                headers=headers,
                json=json,
            )

        async def get_park_operation_status(
                self,
                *,
                yandex_uid=1000,
                user_ticket='TESTSUITE-USER-TICKET',
                user_ticket_provider='yandex',
                park_id,
        ):
            return await taxi_contractor_instant_payouts.get(
                '/fleet/instant-payouts/v2/park-operations',
                params={'park_id': park_id},
                headers={
                    'X-Yandex-UID': str(yandex_uid),
                    'X-Ya-User-Ticket': user_ticket,
                    'X-Ya-User-Ticket-Provider': user_ticket_provider,
                    'X-Park-Id': park_id,
                },
            )

    return FleetV2()


@pytest.fixture
def pro_v1(taxi_contractor_instant_payouts):
    class ProV1:
        async def create_card_token_session(
                self, *, park_id, contractor_id, json,
        ):
            return await taxi_contractor_instant_payouts.post(
                '/internal/pro/v1/card-token-sessions',
                params={'park_id': park_id, 'contractor_id': contractor_id},
                json=json,
            )

        async def get_cards(self, *, park_id, contractor_id):
            return await taxi_contractor_instant_payouts.get(
                '/internal/pro/v1/cards',
                params={'park_id': park_id, 'contractor_id': contractor_id},
            )

    return ProV1()
