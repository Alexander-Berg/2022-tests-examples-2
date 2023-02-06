# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from fleet_financial_statements_plugins import *  # noqa: F403 F401

from tests_fleet_financial_statements.common import defaults
from tests_fleet_financial_statements.common import std


@pytest.fixture
async def std_handlers(load_yaml, mockserver):
    return std.all_handlers(load_yaml, mockserver)


@pytest.fixture
def pg_database(pgsql):
    return pgsql['fleet_payouts']


@pytest.fixture
def mock_parks(mockserver, load_json):
    parks = load_json('parks.json')

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def handler(request):
        park_ids = set(request.json['query']['park']['ids'])
        return {'parks': [park for park in parks if park['id'] in park_ids]}

    return handler


@pytest.fixture
async def retrieve_driver_profiles(load_json, mockserver):
    data = load_json('driver_profiles.json')

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def handler(request):
        ids = set(request.json['id_in_set'])
        return {
            'profiles': [
                {
                    'park_driver_profile_id': park_dp_id,
                    'data': data.get(park_dp_id),
                }
                for park_dp_id in ids
            ],
        }

    return handler


@pytest.fixture
async def retrieve_driver_balances(load_json, mockserver):
    data = load_json('driver_balances.json')

    @mockserver.json_handler(
        '/fleet-transactions-api/v1/parks/driver-profiles/balances/list',
    )
    def handler(request):
        query = request.json['query']
        ids = map(
            lambda dp_id: query['park']['id'] + '_' + dp_id,
            query['park']['driver_profile']['ids'],
        )
        return {
            'driver_profiles': [
                data[park_dp_id] for park_dp_id in ids if park_dp_id in data
            ],
        }

    return handler


@pytest.fixture
async def retrieve_personal_emails(load_json, mockserver):
    data = load_json('personal_emails.json')

    @mockserver.json_handler('/personal/v1/emails/bulk_retrieve')
    def handler(request):
        ids = {item['id'] for item in request.json['items']}
        return {
            'items': [
                {'id': pd_id, 'value': data[pd_id]}
                for pd_id in ids
                if pd_id in data
            ],
        }

    return handler


@pytest.fixture
async def retrieve_personal_phones(load_json, mockserver):
    data = load_json('personal_phones.json')

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def handler(request):
        ids = {item['id'] for item in request.json['items']}
        return {
            'items': [
                {'id': pd_id, 'value': data[pd_id]}
                for pd_id in ids
                if pd_id in data
            ],
        }

    return handler


@pytest.fixture
async def statement_list_view(taxi_fleet_financial_statements):
    async def execute(
            *,
            yandex_uid=defaults.YANDEX_UID,
            user_ticket=defaults.USER_TICKET,
            user_ticket_provider=defaults.USER_TICKET_PROVIDER,
            park_id=defaults.PARK_ID,
            **kwargs,
    ):
        params = dict()
        for name in ['search', 'status', 'page_size', 'page_number']:
            if name in kwargs:
                params[name] = kwargs[name]
        return await taxi_fleet_financial_statements.get(
            '/fleet/financial-statements/v1/statement-list',
            params=params,
            headers={
                'X-Yandex-UID': str(yandex_uid),
                'X-Ya-User-Ticket': user_ticket,
                'X-Ya-User-Ticket-Provider': user_ticket_provider,
                'X-Park-Id': park_id,
            },
        )

    return execute


@pytest.fixture
def statement_list_view_responses(load_json):
    return load_json('statement_list_view_responses.json')


@pytest.fixture
async def statement_status(taxi_fleet_financial_statements):
    async def execute(
            *,
            yandex_uid=defaults.YANDEX_UID,
            user_ticket=defaults.USER_TICKET,
            user_ticket_provider=defaults.USER_TICKET_PROVIDER,
            park_id=defaults.PARK_ID,
            **kwargs,
    ):
        params = {'id': defaults.STMT_EXT_ID}
        for name in ['id', 'revision']:
            if name in kwargs:
                params[name] = kwargs[name]
        return await taxi_fleet_financial_statements.get(
            '/fleet/financial-statements/v1/statement/status',
            params=params,
            headers={
                'X-Yandex-UID': str(yandex_uid),
                'X-Ya-User-Ticket': user_ticket,
                'X-Ya-User-Ticket-Provider': user_ticket_provider,
                'X-Park-Id': park_id,
            },
        )

    return execute


@pytest.fixture
def statement_status_responses(load_json):
    return load_json('statement_status_responses.json')


@pytest.fixture
async def statement_view(taxi_fleet_financial_statements):
    async def execute(
            *,
            yandex_uid=defaults.YANDEX_UID,
            user_ticket=defaults.USER_TICKET,
            user_ticket_provider=defaults.USER_TICKET_PROVIDER,
            park_id=defaults.PARK_ID,
            **kwargs,
    ):
        params = {'id': defaults.STMT_EXT_ID}
        for name in ['id', 'revision', 'page_size', 'page_number']:
            if name in kwargs:
                params[name] = kwargs[name]
        return await taxi_fleet_financial_statements.get(
            '/fleet/financial-statements/v1/statement',
            params=params,
            headers={
                'X-Yandex-UID': str(yandex_uid),
                'X-Ya-User-Ticket': user_ticket,
                'X-Ya-User-Ticket-Provider': user_ticket_provider,
                'X-Park-Id': park_id,
            },
        )

    return execute


@pytest.fixture
def statement_view_response(load_json):
    return load_json('statement_view_response.json')


@pytest.fixture
def statement_create(taxi_fleet_financial_statements):
    async def execute(
            *,
            yandex_uid=defaults.YANDEX_UID,
            user_ticket=defaults.USER_TICKET,
            user_ticket_provider=defaults.USER_TICKET_PROVIDER,
            park_id=defaults.PARK_ID,
            json=None,
            **kwargs,
    ):
        params = {'id': defaults.STMT_EXT_ID}
        for name in ['id']:
            if name in kwargs:
                params[name] = kwargs[name]
        return await taxi_fleet_financial_statements.post(
            '/fleet/financial-statements/v1/statement',
            params=params,
            headers={
                'X-Yandex-UID': str(yandex_uid),
                'X-Ya-User-Ticket': user_ticket,
                'X-Ya-User-Ticket-Provider': user_ticket_provider,
                'X-Park-Id': park_id,
            },
            json=json or {'preset': {}},
        )

    return execute


@pytest.fixture
def statement_delete(taxi_fleet_financial_statements):
    async def execute(
            *,
            yandex_uid=defaults.YANDEX_UID,
            user_ticket=defaults.USER_TICKET,
            user_ticket_provider=defaults.USER_TICKET_PROVIDER,
            park_id=defaults.PARK_ID,
            json=None,
            **kwargs,
    ):
        params = {'id': defaults.STMT_EXT_ID}
        for name in ['id', 'revision']:
            if name in kwargs:
                params[name] = kwargs[name]
        return await taxi_fleet_financial_statements.delete(
            '/fleet/financial-statements/v1/statement',
            params=params,
            headers={
                'X-Yandex-UID': str(yandex_uid),
                'X-Ya-User-Ticket': user_ticket,
                'X-Ya-User-Ticket-Provider': user_ticket_provider,
                'X-Park-Id': park_id,
            },
        )

    return execute


@pytest.fixture
def statement_edit(taxi_fleet_financial_statements):
    async def execute(
            *,
            yandex_uid=defaults.YANDEX_UID,
            user_ticket=defaults.USER_TICKET,
            user_ticket_provider=defaults.USER_TICKET_PROVIDER,
            park_id=defaults.PARK_ID,
            json=None,
            **kwargs,
    ):
        params = {'id': defaults.STMT_EXT_ID}
        for name in ['id', 'revision']:
            if name in kwargs:
                params[name] = kwargs[name]
        return await taxi_fleet_financial_statements.patch(
            '/fleet/financial-statements/v1/statement',
            params=params,
            headers={
                'X-Yandex-UID': str(yandex_uid),
                'X-Ya-User-Ticket': user_ticket,
                'X-Ya-User-Ticket-Provider': user_ticket_provider,
                'X-Park-Id': park_id,
            },
            json=json or {},
        )

    return execute


@pytest.fixture
def statement_execute(taxi_fleet_financial_statements):
    async def execute(
            *,
            yandex_uid=defaults.YANDEX_UID,
            user_ticket=defaults.USER_TICKET,
            user_ticket_provider=defaults.USER_TICKET_PROVIDER,
            park_id=defaults.PARK_ID,
            **kwargs,
    ):
        params = {'id': defaults.STMT_EXT_ID}
        for name in ['id', 'revision']:
            if name in kwargs:
                params[name] = kwargs[name]
        return await taxi_fleet_financial_statements.post(
            '/fleet/financial-statements/v1/statement/execute',
            params=params,
            headers={
                'X-Yandex-UID': str(yandex_uid),
                'X-Ya-User-Ticket': user_ticket,
                'X-Ya-User-Ticket-Provider': user_ticket_provider,
                'X-Park-Id': park_id,
            },
        )

    return execute


@pytest.fixture
def statement_export(taxi_fleet_financial_statements):
    async def execute(
            *,
            yandex_uid=defaults.YANDEX_UID,
            user_ticket=defaults.USER_TICKET,
            user_ticket_provider=defaults.USER_TICKET_PROVIDER,
            park_id=defaults.PARK_ID,
            accept=None,
            accept_language=None,
            **kwargs,
    ):
        params = {'id': defaults.STMT_EXT_ID}
        for name in ['id', 'revision']:
            if name in kwargs:
                params[name] = kwargs[name]

        headers = {
            'X-Yandex-UID': str(yandex_uid),
            'X-Ya-User-Ticket': user_ticket,
            'X-Ya-User-Ticket-Provider': user_ticket_provider,
            'X-Park-Id': park_id,
        }
        if accept is not None:
            headers['Accept'] = accept
        if accept_language is not None:
            headers['Accept-Language'] = accept_language

        return await taxi_fleet_financial_statements.get(
            '/fleet/financial-statements/v1/statement/export',
            params=params,
            headers=headers,
        )

    return execute


@pytest.fixture
async def stq_prepare_worker(stq_runner):
    async def run(
            *,
            task_id=defaults.TASK_ID,
            park_id=defaults.PARK_ID,
            stmt_id=defaults.STMT_ID,
            stmt_revision=1,
    ):
        return await stq_runner.fleet_financial_statements_prepare.call(
            task_id=task_id,
            kwargs={
                'park_id': park_id,
                'stmt_id': stmt_id,
                'stmt_revision': stmt_revision,
            },
        )

    return run


@pytest.fixture
async def stq_prepare_client(stq):
    return stq.fleet_financial_statements_prepare


@pytest.fixture
async def stq_perform_worker(stq_runner):
    async def run(
            *,
            task_id=defaults.TASK_ID,
            park_id=defaults.PARK_ID,
            stmt_id=defaults.STMT_ID,
            stmt_revision=1,
            do_revert=False,
    ):
        return await stq_runner.fleet_financial_statements_perform.call(
            task_id=task_id,
            kwargs={
                'park_id': park_id,
                'stmt_id': stmt_id,
                'stmt_revision': stmt_revision,
                'do_revert': do_revert,
            },
        )

    return run


@pytest.fixture
async def stq_perform_client(stq):
    return stq.fleet_financial_statements_perform
