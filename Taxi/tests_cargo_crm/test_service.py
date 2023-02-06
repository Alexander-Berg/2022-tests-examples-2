import aiohttp
import pytest
import json

from tests_cargo_crm import const

# flake8: noqa
# pylint: disable=import-error,wildcard-import
from cargo_crm_plugins.generated_tests import *

# Feel free to provide your custom implementation to override generated tests.


@pytest.fixture(autouse=True)
def proxy_pipe_get_deal(mockserver):
    url = r'/pipedrive-api/v1/deals/(?P<_id>\w+)'

    @mockserver.json_handler(url, regex=True)
    async def handler(request, _id):
        base_url = 'https://api.pipedrive.com'
        url_path = '/v1/deals/{}'.format(_id)
        url = '{}{}'.format(base_url, url_path)
        params = {'api_token': request.query['api_token']}

        async with aiohttp.ClientSession() as session:
            if request.method == 'GET':
                async with session.get(url, params=params) as response:
                    body = await response.json()
                    return mockserver.make_response(
                        status=response.status, json=body,
                    )
            elif request.method == 'PUT':
                # raise ValueError(request.get_data(), dir(request))
                async with session.put(
                        url,
                        params=params,
                        json=json.loads(request.get_data()),
                ) as response:
                    body = await response.json()
                    return mockserver.make_response(
                        status=response.status, json=body,
                    )

    return handler


@pytest.fixture(autouse=True)
def proxy_pipe_get_org(mockserver):
    url = r'/pipedrive-api/v1/organizations/(?P<org_id>\w+)'

    @mockserver.json_handler(url, regex=True)
    async def handler(request, org_id):
        base_url = 'https://api.pipedrive.com'
        url_path = '/v1/organizations/{}'.format(org_id)
        url = '{}{}'.format(base_url, url_path)
        params = {'api_token': request.query['api_token']}

        async with aiohttp.ClientSession() as session:
            if request.method == 'GET':
                async with session.get(url, params=params) as response:
                    body = await response.json()
                    return mockserver.make_response(
                        status=response.status, json=body,
                    )
            elif request.method == 'PUT':
                # raise ValueError(request.get_data())
                async with session.put(
                        url,
                        params=params,
                        json=json.loads(request.get_data()),
                ) as response:
                    body = await response.json()
                    return mockserver.make_response(
                        status=response.status, json=body,
                    )

    return handler


@pytest.fixture(autouse=True)
def proxy_pipe_get_person(mockserver):
    url = r'/pipedrive-api/v1/persons/(?P<_id>\w+)'

    @mockserver.json_handler(url, regex=True)
    async def handler(request, _id):
        base_url = 'https://api.pipedrive.com'
        url_path = '/v1/persons/{}'.format(_id)
        url = '{}{}'.format(base_url, url_path)
        params = {'api_token': request.query['api_token']}

        async with aiohttp.ClientSession() as session:
            if request.method == 'GET':
                async with session.get(url, params=params) as response:
                    body = await response.json()
                    return mockserver.make_response(
                        status=response.status, json=body,
                    )
            elif request.method == 'PUT':
                # raise ValueError(request.get_data(), dir(request))
                async with session.put(
                        url,
                        params=params,
                        json=json.loads(request.get_data()),
                ) as response:
                    body = await response.json()
                    return mockserver.make_response(
                        status=response.status, json=body,
                    )

    return handler


@pytest.fixture(autouse=True)
def proxy_pipe_make_person(mockserver):
    url = r'/pipedrive-api/v1/persons'

    @mockserver.json_handler(url, regex=True)
    async def handler(request):
        base_url = 'https://api.pipedrive.com'
        url_path = '/v1/persons'
        url = f'{base_url}{url_path}'
        params = {'api_token': request.query['api_token']}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url, params=params, data=json.loads(request.get_data()),
            ) as response:
                body = await response.json()
                return mockserver.make_response(
                    status=response.status, json=body,
                )

    return handler


@pytest.fixture(autouse=True)
def proxy_pipe_make_org(mockserver):
    url = r'/pipedrive-api/v1/organizations'

    @mockserver.json_handler(url, regex=True)
    async def handler(request):
        base_url = 'https://api.pipedrive.com'
        url_path = '/v1/organizations'
        url = f'{base_url}{url_path}'
        params = {'api_token': request.query['api_token']}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url, params=params, data=json.loads(request.get_data()),
            ) as response:
                body = await response.json()
                return mockserver.make_response(
                    status=response.status, json=body,
                )

    return handler


@pytest.fixture(autouse=True)
def proxy_pipe_make_deal(mockserver):
    url = r'/pipedrive-api/v1/deals'

    @mockserver.json_handler(url, regex=True)
    async def handler(request):
        base_url = 'https://api.pipedrive.com'
        url_path = '/v1/deals'
        url = f'{base_url}{url_path}'
        params = {'api_token': request.query['api_token']}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url, params=params, data=json.loads(request.get_data()),
            ) as response:
                body = await response.json()
                return mockserver.make_response(
                    status=response.status, json=body,
                )

    return handler


@pytest.fixture(autouse=True)
def proxy_pipe_make_activity(mockserver):
    url = r'/pipedrive-api/v1/activities'

    @mockserver.json_handler(url, regex=True)
    async def handler(request):
        base_url = 'https://api.pipedrive.com'
        url_path = '/v1/activities'
        url = f'{base_url}{url_path}'
        params = {'api_token': request.query['api_token']}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url, params=params, data=json.loads(request.get_data()),
            ) as response:
                body = await response.json()
                return mockserver.make_response(
                    status=response.status, json=body,
                )

    return handler


@pytest.fixture(autouse=True)
def proxy_pipe_make_note(mockserver):
    url = r'/pipedrive-api/v1/notes'

    @mockserver.json_handler(url, regex=True)
    async def handler(request):
        base_url = 'https://api.pipedrive.com'
        url_path = '/v1/notes'
        url = f'{base_url}{url_path}'
        params = {'api_token': request.query['api_token']}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url, params=params, data=json.loads(request.get_data()),
            ) as response:
                body = await response.json()
                return mockserver.make_response(
                    status=response.status, json=body,
                )

    return handler


@pytest.fixture(autouse=True)
def proxy_pipe_bulk_retrieve(mockserver):
    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _handler2(request):
        return mockserver.make_response(
            status=200,
            json={
                'items': [
                    {'id': '997722', 'value': '+79002222220'},
                    {'id': 'random_id_2', 'value': '+70001112233'},
                ],
            },
        )


@pytest.fixture(autouse=True)
def proxy_pipe_events(mockserver, procaas_ctx):
    @mockserver.json_handler('/cargo-crm/procaas/caching-proxy/events')
    async def handler(request):
        scope = request.query['scope'][0]
        queue = request.query['queue'][0]
        procaas_ctx.events = [
            {
                'event_id': 'ev_1',
                'created': '2021-06-20T10:00:00+00:00',
                'payload': {
                    'kind': 'initial_form_request',
                    'data': {
                        'operation_id': 'opid_1',
                        'revision': 0,
                        'requester_uid': const.UID,
                        'requester_login': const.LOGIN,
                        'form_data': {'contact_phone': ''},
                        'form_pd': {'contact_phone_pd_id': const.PHONE_PD_ID},
                    },
                },
            },
            {
                'event_id': 'ev_2',
                'created': '2021-06-20T10:00:01+00:00',
                'payload': {
                    'kind': 'initial_form_result',
                    'data': {'operation_id': 'opid_1'},
                },
            },
            {
                'event_id': 'ev_3',
                'created': '2021-06-20T10:01:00+00:00',
                'payload': {
                    'kind': 'user_info_form_request',
                    'data': {
                        'operation_id': 'opid_3',
                        'revision': 2,
                        'requester_uid': const.UID,
                        'requester_login': const.LOGIN,
                        'form_data': {'name': 'James', 'surname': 'Hopkins'},
                        'form_pd': {'contact_phone_pd_id': const.PHONE_PD_ID},
                    },
                },
            },
            {
                'event_id': 'ev_4',
                'created': '2021-06-20T10:01:01+00:00',
                'payload': {
                    'kind': 'user_info_form_result',
                    'data': {'operation_id': 'opid_3'},
                },
            },
            {
                'event_id': 'ev_5',
                'created': '2021-06-20T10:02:00+00:00',
                'payload': {
                    'kind': 'company_created_notification',
                    'data': {
                        'form_data': {'corp_client_id': const.CORP_CLIENT_ID},
                        'form_pd': {},
                    },
                },
            },
            {
                'event_id': 'ev_6',
                'created': '2021-06-20T10:03:00+00:00',
                'payload': {
                    'kind': 'company_info_form_request',
                    'data': {
                        'operation_id': 'opid_6',
                        'revision': 2,
                        'requester_uid': const.UID,
                        'requester_login': const.LOGIN,
                        'form_data': {
                            'name': 'Camomile Ltd.',
                            'country': 'Россия',
                            'segment': 'Аптеки',
                            'city': 'Москва',
                            'email': '',
                            'phone': '',
                            'website': 'camomile.ru',
                        },
                        'form_pd': {
                            'phone_pd_id': const.PHONE_PD_ID,
                            'email_pd_id': const.EMAIL_PD_ID,
                        },
                    },
                },
            },
            {
                'event_id': 'ev_7',
                'created': '2021-06-20T10:03:01+00:00',
                'payload': {
                    'kind': 'company_info_form_result',
                    'data': {'operation_id': 'opid_6'},
                },
            },
            {
                'event_id': 'ev_8',
                'created': '2021-06-20T10:04:00+00:00',
                'payload': {
                    'kind': 'card_bound_notification',
                    'data': {
                        'form_data': {
                            'corp_client_id': const.CORP_CLIENT_ID,
                            'yandex_uid': const.UID,
                            'card_id': const.CARD_ID,
                        },
                        'form_pd': {},
                    },
                },
            },
        ]
        return procaas_ctx.get_read_events_response(request, scope, queue)

    return handler
