# pylint: disable=unused-variable
import json

import pytest

from taxi import settings


PASSPORT_RESPONSE = bytes(
    (
        '<?xml version="1.0" encoding="windows-1251"?>'
        '<doc><message-sent id="test_id" /></doc>'
    ),
    encoding='utf-8',
)
OK_BYTES_RESPONSE = bytes('OK', encoding='utf-8')
APPROVALS_ANSWER = {
    'id': 'test_id',
    'created_by': 'test_user',
    'description': 'test_description',
    'created': '2019-02-19T18:13:41+0300',
    'run_manually': False,
    'service_name': 'random_service',
    'api_path': 'random_path',
    'data': {'a': 123},
    'updated': '2019-02-19T18:13:41+0300',
    'approvals': [],
    'version': 1,
    'comments': [],
    'summary': {'current': {'name': 'test'}, 'new': {'name': 'cool_test'}},
}
APPROVALS_RESPONSE = bytes(json.dumps(APPROVALS_ANSWER), encoding='utf-8')
SCHEME_ERROR_RESPONSE = bytes(
    json.dumps(
        {
            'status': 'error',
            'details': (
                'Service error_service has some error in the scheme: '
                '["These action ids are already exist, please fix the scheme: '
                '{\'test_action_id\'}", "These categories ids were not found '
                'in admin and api admin services: {\'test_perm_cat\'}", '
                '\'Config NOT_DECLARED_CONFIG not declared in '
                'service.yaml:config\'] '
                'or some error with admin API: None'
            ),
            'code': 'SERVICE_SCHEME_ERROR',
        },
    ),
    encoding='utf-8',
)
NOT_FOUND_IN_SCHEME_RESPONSE = bytes(
    json.dumps(
        {
            'status': 'error',
            'details': (
                'Endpoint or method was not found in service scheme: qweqwe/'
            ),
            'code': 'NOT_FOUND_IN_SCHEME',
        },
    ),
    encoding='utf-8',
)
INTERNAL_HEADER = 'WEIRD_INTERNAL_HEADER'


@pytest.mark.parametrize(
    'url,data,code,method,expected',
    [
        pytest.param(
            '/sms/send_sms/b698a54d3888450eb393332b91df57c6/?phone=%2B79646350'
            '521',
            {},
            200,
            'POST',
            PASSPORT_RESPONSE,
            id='send normal sms 200',
        ),
        pytest.param(
            '/error_service/send_sms/?phone=%2B79646350521',
            {},
            400,
            'POST',
            SCHEME_ERROR_RESPONSE,
            id='send bad sms 400',
        ),
        pytest.param(
            '/sms/qweqwe/',
            {},
            404,
            'POST',
            NOT_FOUND_IN_SCHEME_RESPONSE,
            id='send bad request - not in scheme 404',
        ),
        pytest.param(
            '/sms/send_sms/list/123123123/?phone=%2B79646350521',
            {},
            200,
            'GET',
            PASSPORT_RESPONSE,
            id='get normal sms 200',
        ),
        pytest.param(
            '/service_with_tvm_auth/check/',
            {},
            200,
            'POST',
            OK_BYTES_RESPONSE,
            id='request a server with tvm 200',
        ),
        pytest.param(
            '/service_with_tvm_auth/check',
            {},
            200,
            'POST',
            OK_BYTES_RESPONSE,
            id='request a server with tvm without a trailing slash 200',
        ),
        pytest.param(
            'service_with_approvals/approvals/path/',
            {
                'request_id': '123123',
                'run_manually': False,
                'data': {'a': 123},
                'service_name': 'random_service',
                'api_path': 'random_path',
                'mode': 'push',
            },
            200,
            'POST',
            APPROVALS_RESPONSE,
            id='request an approval from approvals service 200',
        ),
    ],
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            id='old header removal',
            marks=pytest.mark.config(API_ADMIN_RESPONSE_HEADERS_REMOVAL=0.0),
        ),
        pytest.param(
            id='new header removal',
            marks=pytest.mark.config(API_ADMIN_RESPONSE_HEADERS_REMOVAL=1.0),
        ),
    ],
)
async def test_service(
        url,
        data,
        code,
        method,
        expected,
        taxi_api_admin_client,
        patch_aiohttp_session,
        response_mock,
):
    @patch_aiohttp_session('http://unstable-service-host.net/send_sms/')
    def patch_sms_request(method, url, **kwargs):
        phone = kwargs['params'].get('phone')
        assert phone == '+79646350521'
        assert kwargs['headers']['X-Yandex-Uid'] == '0'
        assert kwargs['headers']['X-YaTaxi-Service-Name'] == 'sms'
        return response_mock(
            text=str(PASSPORT_RESPONSE),
            read=PASSPORT_RESPONSE,
            headers={'Transfer-Encoding': INTERNAL_HEADER},
        )

    @patch_aiohttp_session(
        'http://taxi-approvals.taxi.dev.yandex.net/' 'drafts/create/', 'POST',
    )
    def patch_approvals_request(method, url, **kwargs):
        if method == 'post':
            assert kwargs['headers']['X-Yandex-Uid'] == '0'
            assert (
                kwargs['headers']['X-YaTaxi-Service-Name']
                == 'service_with_approvals'
            )
            return response_mock(
                json=APPROVALS_ANSWER,
                text=json.dumps(APPROVALS_ANSWER),
                read=APPROVALS_RESPONSE,
                headers={'Transfer-Encoding': INTERNAL_HEADER},
            )
        raise Exception

    @patch_aiohttp_session('http://unstable-service-host.net/check/', 'POST')
    def patch_check_request(method, url, **kwargs):
        assert (
            kwargs['headers']['X-YaTaxi-Service-Name']
            == 'service_with_tvm_auth'
        )
        return response_mock(
            text=str(OK_BYTES_RESPONSE),
            read=OK_BYTES_RESPONSE,
            headers={'Transfer-Encoding': INTERNAL_HEADER},
        )

    response = await taxi_api_admin_client.request(
        method, url, data=json.dumps(data),
    )
    response_body = await response.read()
    assert response.status == code, response_body
    assert response_body == expected
    assert INTERNAL_HEADER != response.headers.get('Content-Encoding', None)


@pytest.mark.parametrize(
    'url,expected,environment',
    [
        ('service_with_unstable/unstable/path/', 200, 'testing'),
        ('service_with_unstable/unstable/path/', 200, 'unstable'),
        ('service_without_unstable/no_unstable/path/', 200, 'testing'),
        ('service_without_unstable/no_unstable/path/', 400, 'unstable'),
    ],
)
async def test_service_environment(
        url,
        expected,
        environment,
        monkeypatch,
        patch_aiohttp_session,
        response_mock,
        taxi_api_admin_client,
):

    monkeypatch.setattr(settings, 'ENVIRONMENT', environment)

    @patch_aiohttp_session(f'http://{environment}-service-host.net/')
    def patch_request(*args, **kwargs):
        return response_mock(read=b'ok')

    response = await taxi_api_admin_client.request('POST', url)
    assert response.status == expected
    if expected == 200:
        assert len(patch_request.calls) == 1
    else:
        assert not patch_request.calls


@pytest.mark.config(API_ADMIN_USE_SHORT_DRAFT_REQUEST=1.0)
async def test_v2_get_drafts_200(
        taxi_api_admin_client,
        taxi_api_admin_app,
        patch_aiohttp_session,
        response_mock,
):
    answer = {
        'id': 233942,
        'created_by': 'elrusso',
        'comments': [],
        'created': '2021-09-03T19:26:00+0300',
        'updated': '2021-09-03T19:27:07+0300',
        'approvals': [
            {
                'group': 'programmer',
                'login': 'elrusso',
                'created': '2021-09-03T19:26:17+0300',
            },
        ],
        'status': 'failed',
        'data': {},
    }

    @patch_aiohttp_session(
        'http://taxi-approvals.taxi.dev.yandex.net/v2/drafts/',
    )
    def patch_approvals_drafts(method, url, **kwargs):

        return response_mock(
            read=bytes(json.dumps(answer), encoding='utf-8'), status=200,
        )

    @patch_aiohttp_session(
        'http://taxi-approvals.taxi.dev.yandex.net/v2/drafts/short_info/',
    )
    def patch_approvals_short_info(method, url, **kwargs):
        answer = {
            'service_name': 'elrusso_service',
            'api_path': 'elrusso_api_path',
            'id': 5,
        }
        return response_mock(
            read=bytes(json.dumps(answer), encoding='utf-8'), status=200,
        )

    params = [{'id': 5}, {'id': 5}]
    for param in params:
        response = await taxi_api_admin_client.get(
            'taxi-approvals/v2/drafts/',
            json=None,
            params=param,
            headers={
                'X-Yandex-Login': 'test_login',
                'Content-Type': 'text/plain; charset=utf-8',
            },
        )
        assert response.status == 200
        assert await response.json() == answer
    assert len(patch_approvals_drafts.calls) == 2
    assert len(patch_approvals_short_info.calls) == 1
    assert taxi_api_admin_app.tvm.calls() == 2


@pytest.mark.config(API_ADMIN_USE_SHORT_DRAFT_REQUEST=1.0)
async def test_v2_get_drafts_404(
        taxi_api_admin_client,
        patch_aiohttp_session,
        response_mock,
        taxi_api_admin_app,
):
    answer = {
        'status': 'error',
        'message': f'Draft with id=6 was not found',
        'code': 'NOT_FOUND',
    }

    @patch_aiohttp_session(
        'http://taxi-approvals.taxi.dev.yandex.net/v2/drafts/',
    )
    def patch_approvals_drafts(method, url, **kwargs):
        return

    @patch_aiohttp_session(
        'http://taxi-approvals.taxi.dev.yandex.net/v2/drafts/short_info/',
    )
    def patch_approvals_short_info(method, url, **kwargs):
        return response_mock(
            read=bytes(json.dumps(answer), encoding='utf-8'), status=404,
        )

    params = {'id': 6}
    response = await taxi_api_admin_client.get(
        'taxi-approvals/v2/drafts/',
        json=None,
        params=params,
        headers={'X-Yandex-Login': 'test_login'},
    )
    assert response.status == 404
    assert await response.json() == answer
    assert not patch_approvals_drafts.calls
    assert len(patch_approvals_short_info.calls) == 1
    assert taxi_api_admin_app.tvm.calls() == 1
