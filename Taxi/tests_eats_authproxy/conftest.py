# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import json

import aiohttp
from eats_authproxy_plugins import *  # noqa: F403 F401
import pytest


def pytest_configure(config):
    config.addinivalue_line('markers', 'eater: eater')
    config.addinivalue_line('markers', 'eater_session: eater session')


@pytest.fixture
async def _request(taxi_eats_authproxy):
    async def _wrapper(url_path, request_body=None, headers=None):
        if request_body is None:
            request_body = {}
        if headers is None:
            headers = {}
        if 'Origin' not in headers:
            headers['Origin'] = 'localhost'
        elif headers['Origin'] is None:
            del headers['Origin']
        response = await taxi_eats_authproxy.post(
            url_path, json=request_body, headers=headers,
        )
        return response

    return _wrapper


@pytest.fixture
def _mock_remote(mockserver):
    def _wrapper(url_path, response_code=200, response_body=None):
        if response_body is None:
            response_body = {}

        @mockserver.json_handler('/%s' % url_path)
        def handler(request):
            assert request.json == {}
            return aiohttp.web.json_response(
                status=response_code, data=response_body,
            )

        return handler

    return _wrapper


@pytest.fixture
def mock_eater_authorizer(mockserver, request):
    @mockserver.json_handler('/eater-authorizer/v2/eater/sessions')
    def _mock_sessions(req):
        markers = request.node.iter_markers('eater_session')
        outer = req.json['outer_session_id']
        if outer is None:
            outer = 'None'
        for marker in markers:
            data = marker.kwargs.get(outer or '__empty')
            if data:
                resp = {
                    'inner_session_id': data['inner'],
                    'outer_session_id': outer,
                    'ttl': 60,
                    'session_type': 'native',
                }
                if 'eater_id' in data:
                    resp['eater_id'] = data['eater_id']
                if 'partner_user_id' in data:
                    resp['partner_user_id'] = data['partner_user_id']
                    resp['session_type'] = 'partner'

                return resp
        assert False, 'outer session not found: ' + outer
        return ''


@pytest.fixture
def mock_eaters_search(mockserver, request):
    def _mock_eater_search(data_marker):
        markers = request.node.iter_markers('eater')
        for marker in markers:
            print('kwargs', marker.kwargs)
            eater = {
                'created_at': '2019-12-31T10:59:59+03:00',
                'updated_at': '2019-12-31T10:59:59+03:00',
            }
            data = marker.kwargs.get(data_marker)
            if data is None:
                continue

        if not data:
            return mockserver.make_response(
                json={'code': 'eater_not_found', 'message': 'eater not found'},
                headers={'X-YaTaxi-Error-Code': 'eater_not_found'},
                status=404,
            )

        assert isinstance(data['id'], str)

        eater.update(data)
        if 'uuid' not in eater:
            eater['uuid'] = eater['id']
        return {'eater': eater}

    return _mock_eater_search


# pylint: disable=redefined-outer-name
@pytest.fixture
def mock_core_eater(mockserver, mock_eaters_search):
    @mockserver.json_handler('/eats-core-eater/find-by-passport-uid')
    def _mock_core_find_by_passport_uid(req):
        uid = req.json['passport_uid']
        return mock_eaters_search('u' + str(uid))

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-passport-uid')
    def _mock_eaters_find_by_passport_uid(req):
        uid = req.json['passport_uid']
        return mock_eaters_search('u' + str(uid))

    @mockserver.json_handler('/eats-core-eater/find-by-id')
    def _mock_core_find_by_id(req):
        eater_id = req.json['id']
        return mock_eaters_search('i' + eater_id)

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-id')
    def _mock_eaters_find_by_id(req):
        eater_id = req.json['id']
        return mock_eaters_search('i' + eater_id)


@pytest.fixture
def request_proxy(taxi_eats_authproxy):
    async def _request_proxy(
            auth_method,
            url='test/123',
            no_session=False,
            headers=None,
            cookies=None,
    ):
        await taxi_eats_authproxy.invalidate_caches()

        request_headers = {'X-Host': 'localhost'}
        if headers:
            request_headers.update(headers)

        if not no_session:
            request_headers['X-Eats-Session'] = 'outer'

        cookie_str = ''
        if cookies:
            cookie_str = ''.join(
                '{}={};'.format(k, v) for k, v in cookies.items()
            )
        if auth_method == 'session':
            cookie_str += 'Session_id=session;'
        if cookie_str:
            request_headers['Cookie'] = cookie_str

        extra = {'headers': request_headers}
        if auth_method == 'token':
            extra['bearer'] = 'token'

        return await taxi_eats_authproxy.post(
            url, data=json.dumps({}), **extra,
        )

    return _request_proxy


@pytest.fixture
def am_proxy_name():
    return 'eats-authproxy'


@pytest.fixture(
    autouse=True,
    scope='function',
    params=[pytest.param('old'), pytest.param('new')],
)
def new_personal_header_module_mode(taxi_config, request):
    config = taxi_config.get('EATS_AUTHPROXY_FEATURE_FLAGS')

    if request.param == 'old':
        config['use_new_validate_eater_id'] = False
    if request.param == 'new':
        config['use_new_validate_eater_id'] = True

    taxi_config.set_values({'EATS_AUTHPROXY_FEATURE_FLAGS': config})
