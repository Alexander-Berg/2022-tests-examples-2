# pylint: disable=redefined-outer-name
from aiohttp import web
import pytest

import document_templator.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['document_templator.generated.service.pytest_plugins']


@pytest.fixture
def simple_secdist(simple_secdist):
    settings_override = simple_secdist['settings_override']
    settings_override['API_ADMIN_SERVICES_TOKENS'][
        'document_templator'
    ] = 'secret'
    robot_tokens = settings_override.setdefault(
        'ADMIN_ROBOT_LOGIN_BY_TOKEN', {},
    )
    robot_tokens['robot_secret'] = 'robot-document-templator'
    return simple_secdist


def check_headers(headers):
    assert headers.get('X-YaRequestId') is not None
    assert headers['X-YaTaxi-Api-Key'] == 'robot_secret'


@pytest.fixture
def requests_handlers(mockserver):
    @mockserver.json_handler('/tariff/moscow/econom/')
    def _req1(request):
        check_headers(request.headers)
        value = 'body: %s; queries: q1=%s, q2=%s' % (
            str(request.json),
            request.query['q1'],
            request.query['q2'],
        )
        return {'r1': value}

    @mockserver.json_handler('/pinstats/')
    async def _req2(request):
        check_headers(request.headers)
        if request.query:
            return web.json_response(
                status=402, reason='unexpected query param', text='error text',
            )
        return {'arr': [1, 2, 3]}

    @mockserver.json_handler('/get_surge/')
    async def _req3(request):
        check_headers(request.headers)
        return {'num': 10.0, 'bool': False}

    @mockserver.json_handler('/tariff/moscow')
    async def _req4(request):
        check_headers(request.headers)
        return {'activation_zone': 'moscow_activation', 'home_zone': 'moscow'}

    @mockserver.json_handler('/double-number/')
    async def _double_number_handler(request):
        check_headers(request.headers)
        number = request.query['number']
        try:
            number = int(number)
        except ValueError:
            pass
        return {'number': number * 2}
