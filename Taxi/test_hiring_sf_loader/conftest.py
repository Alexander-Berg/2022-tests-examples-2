# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import copy
import functools
import random
import typing
import uuid

from aiohttp import web
import pytest
import regex
from submodules.testsuite.testsuite.utils import http

import hiring_sf_loader.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['hiring_sf_loader.generated.service.pytest_plugins']

DOCUMENTS_COUNT = 50
COMMON_SYNC_DELETE_RESPONSE = {'deleted': 1}
COMMON_SYNC_UPSERT_RESPONSE = {'updated': 1, 'created': 1}
ZD_SYNC_UPDATE_RESPONSE = {
    'code': 'SUCCESS',
    'message': 'Данные приняты.',
    'details': {},
}


def hex_uuid():
    return uuid.uuid4().hex


def generate_documents(template, names):
    def generate_personal():
        phone = {
            'field_name': 'phone',
            'type': 'phones',
            'value': '+79{:0>9}'.format(random.randint(0, 10 ** 9 - 1)),
        }
        email = {
            'field_name': 'email',
            'type': 'emails',
            'value': 'someone{:0>4}@example.com'.format(
                random.randint(0, 9999),
            ),
        }
        personal_data = [phone, email]
        if random.random() > 0.5:
            random.shuffle(personal_data)
        return personal_data

    def generate_ordinary():
        info = {}
        sex = random.choice(('female', 'male'))
        first = random.choice(names[sex]['first_names'])
        second = random.choice(names[sex]['second_names'])
        info['fullname'] = ' '.join((first, second))
        info['sex'] = sex
        return info

    ticket = copy.deepcopy(template)
    while True:
        lead_id = hex_uuid()
        ticket['request_id'] = hex_uuid()
        ticket['task_id'] = hex_uuid()
        ticket['line_id'] = hex_uuid()
        ticket['lead_id'] = lead_id
        ticket['document']['ordinary']['lead_id'] = lead_id
        ticket['document']['personal'] = generate_personal()
        ticket['document']['ordinary'].update(generate_ordinary())
        yield ticket


@pytest.fixture  # noqa: F405
def get_documents(web_app_client):
    async def _wrapper(cursor: str, *, status=200) -> dict:
        query = {'cursor': cursor}
        async with web_app_client.get(
                '/v1/documents-for-call', params=query,
        ) as response:
            assert response.status == status
            response_body = await response.json()
        return response_body

    return _wrapper


@pytest.fixture  # noqa: F405
def get_all_documents_and_cursor(get_documents):
    async def _wrapper() -> typing.Tuple[list, str]:
        documents: typing.List[dict] = []
        cursor = '1970-01-01'
        while True:
            chunk = await get_documents(cursor)
            cursor = chunk['cursor']
            if not chunk['documents']:
                break
            documents.extend(chunk['documents'])
        return documents, cursor

    return _wrapper


@functools.lru_cache(None)
def personal_response(string):
    response = {'value': string, 'id': hex_uuid()}
    return response


@pytest.fixture  # noqa: F405
def personal(mockserver):
    # pylint: disable=unused-variable
    @mockserver.json_handler(
        r'/personal/v1/(?P<pd_type>[a-zA-Z_]+)/store', regex=True,
    )
    def _handler(request, pd_type):
        return personal_response(request.json['value'])

    return _handler


@pytest.fixture
def mock_territories_api(mockserver):
    @mockserver.json_handler('/territories/v1/countries/list')
    async def _territories(request, **kwargs):
        return {
            'countries': [
                {
                    '_id': 'rus',
                    'national_access_code': '8',
                    'phone_code': '7',
                    'phone_max_length': 11,
                    'phone_min_length': 11,
                },
            ],
        }


def main_configuration(func):
    @pytest.mark.usefixtures('personal', 'mock_territories_api')  # noqa: F405
    @functools.wraps(func)
    async def patched(*args, **kwargs):
        await func(*args, **kwargs)

    return patched


@pytest.fixture
def mock_salesforce_auth(mock_salesforce):
    @mock_salesforce('/services/oauth2/token')
    async def _handler(request):
        return web.json_response(
            {
                'access_token': 'TOKEN',
                'instance_url': 'URL',
                'id': 'ID',
                'token_type': 'TYPE',
                'issued_at': '2019-01-01',
                'signature': 'SIGN',
            },
            status=200,
        )

    return _handler


@pytest.fixture
def mock_salesforce_deleted(mock_salesforce):
    def _wrapper(response):
        @mock_salesforce(
            r'/services/data/v50.0/sobjects/(?P<sobject>\w+)/deleted/',
            regex=True,
        )
        async def _handler(request, sobject):
            return response

        return _handler

    return _wrapper


@pytest.fixture
def mock_salesforce_make_query(mock_salesforce):
    def _wrapper(response):
        @mock_salesforce('/services/data/v50.0/query/')
        async def _handler(request):
            return response

        return _handler

    return _wrapper


@pytest.fixture
def mock_salesforce_query_next(mock_salesforce):
    @mock_salesforce(
        r'/services/data/v50.0/query/(?P<cursor>\w+-\d+)', regex=True,
    )
    async def _handler(request, cursor):
        return {'done': True, 'records': []}

    return _handler


@pytest.fixture
def mock_partners_app_sync(mock_hiring_partners_app):
    def _wrapper(handle, response):
        @mock_hiring_partners_app(f'/v1/organizations/{handle}')
        def _handler(request):
            return response

        return _handler

    return _wrapper


@pytest.fixture
def mock_candidates_sync(mock_hiring_candidates_py3):
    def _wrapper(handle, response):
        @mock_hiring_candidates_py3(f'/v1/salesforce/{handle}')
        def _handler(request):
            return response

        return _handler

    return _wrapper


@pytest.fixture
def mock_api_sync(mock_hiring_api):
    def _wrapper(handle, response):
        @mock_hiring_api(f'/v1/tickets/{handle}')
        def _handler(request):
            return response

        return _handler

    return _wrapper


@pytest.fixture
def mock_partners_app_sync_delete(mock_partners_app_sync):
    return mock_partners_app_sync('delete', COMMON_SYNC_DELETE_RESPONSE)


@pytest.fixture
def mock_partners_app_sync_upsert(mock_partners_app_sync):
    return mock_partners_app_sync('upsert', COMMON_SYNC_UPSERT_RESPONSE)


@pytest.fixture
def mock_api_sync_update(mock_api_sync):
    return mock_api_sync('update', ZD_SYNC_UPDATE_RESPONSE)


@pytest.fixture
def mock_candidates_sync_delete(mock_candidates_sync):
    return mock_candidates_sync('delete-leads', COMMON_SYNC_DELETE_RESPONSE)


@pytest.fixture
def mock_candidates_sync_upsert(mock_candidates_sync):
    return mock_candidates_sync('upsert-leads', COMMON_SYNC_UPSERT_RESPONSE)


@pytest.fixture
def mock_candidates_sync_raise(mockserver, mock_hiring_candidates_py3):
    state = {'is_called': False}

    def _wrapper(state):
        @mock_hiring_candidates_py3('/v1/salesforce/upsert-leads')
        def _handler(request):
            if not state['is_called']:
                state['is_called'] = True
                return COMMON_SYNC_UPSERT_RESPONSE
            return mockserver.make_response(
                status=400,
                json={
                    'code': '400',
                    'message': 'Bad Request',
                    'details': {'occurred_at': '2021-01-01T00:00:00'},
                },
            )

        return _handler

    return _wrapper(state)


@pytest.fixture
def mock_candid_sync_delete_assets(mock_candidates_sync):
    return mock_candidates_sync('delete-assets', COMMON_SYNC_DELETE_RESPONSE)


@pytest.fixture
def mock_candid_sync_upsert_assets(mock_candidates_sync):
    return mock_candidates_sync('upsert-assets', COMMON_SYNC_UPSERT_RESPONSE)


@pytest.fixture
def mock_candid_sync_raise_assets(mockserver, mock_hiring_candidates_py3):
    state = {'is_called': False}

    def _wrapper(state):
        @mock_hiring_candidates_py3('/v1/salesforce/upsert-assets')
        def _handler(request):
            if not state['is_called']:
                state['is_called'] = True
                return COMMON_SYNC_UPSERT_RESPONSE
            return mockserver.make_response(
                status=400,
                json={
                    'code': '400',
                    'message': 'Bad Request',
                    'details': {'occurred_at': '2021-01-01T00:00:00'},
                },
            )

        return _handler

    return _wrapper(state)


@pytest.fixture
def match_sf_query():
    query_regexp = regex.compile(
        r'SELECT (?P<fields>(?:\w+.?,?)+) FROM (?P<sobject>\w+) '
        'WHERE (?P<clause>.+)',
    )

    def _wrapper(query):
        match = query_regexp.search(query)
        if match is None:
            return None

        query_dict = match.groupdict()
        fields = query_dict.pop('fields')
        query_dict['fields'] = sorted(fields.split(','))
        return query_dict

    return _wrapper


@pytest.fixture
def get_mock_calls_json():
    def _wrapper(mock):
        return [
            mock.next_call()['request'].json for _ in range(mock.times_called)
        ]

    return _wrapper


@pytest.fixture
def mock_bulk_cancel_tasks(mock_hiring_telephony_oktell_callback):
    def _wrapper(response: dict):
        @mock_hiring_telephony_oktell_callback('/v1/tasks/bulk-cancel')
        def _handler(request: http.Request):
            assert request
            return response

        return _handler

    return _wrapper


@pytest.fixture
def mock_upsert_tasks(mock_hiring_telephony_oktell_callback):
    def _wrapper(response: dict):
        @mock_hiring_telephony_oktell_callback('/v1/tasks/upsert')
        def _handler(request: http.Request):
            assert request
            return response

        return _handler

    return _wrapper


@pytest.fixture
def mock_bulk_delete_cars(mock_hiring_taxiparks_gambling):
    def _wrapper(response: dict):
        @mock_hiring_taxiparks_gambling('/v2/cars/bulk/delete')
        def _handler(request: http.Request):
            return response

        return _handler

    return _wrapper


@pytest.fixture
def mock_upsert_cars(mock_hiring_taxiparks_gambling):
    def _wrapper(response: dict):
        @mock_hiring_taxiparks_gambling('/v2/cars/upsert')
        def _handler(request: http.Request):
            return response

        return _handler

    return _wrapper
