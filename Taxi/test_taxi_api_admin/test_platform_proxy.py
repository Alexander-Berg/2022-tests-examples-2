import pytest


@pytest.mark.parametrize(
    ['method', 'params', 'data'],
    [
        pytest.param(
            'GET',
            {'project_name': 'taxi-support'},
            None,
            id='clowny_role_1_project_name',
        ),
        pytest.param(
            'GET',
            {'project_id': 38, 'tplatform_namespace': 'taxi'},
            None,
            id='clowny_role_2_and_3',
        ),
        pytest.param(
            'DELETE',
            {'abc_slug': 'abc-random-slug'},
            None,
            id='clowny_role_4_abc',
        ),
        pytest.param(
            'POST', None, {'service_id': 355405}, id='clowny_role_1_akeneo',
        ),
        pytest.param(
            'POST',
            None,
            {'service_id': 355298},
            id='clowny_role_1_taxi_support',
        ),
        pytest.param('put', None, None, id='common_clown_role-no_scope_check'),
        pytest.param('patch', None, {'branch_id': 296704}),
    ],
)
async def test_platform_proxy(
        taxi_api_admin_client,
        patch_aiohttp_session,
        response_mock,
        grands_retrieve_mock,
        method,
        params,
        data,
):
    @patch_aiohttp_session('http://unstable-service-host.net/send_sms/')
    def _patch_sms_request(*args, **kwargs):
        return response_mock(text='response', read=b'response')

    mock = grands_retrieve_mock()
    url = '/platform/platform/send_sms/'
    if not params:
        params = {}
    if not params.get('tplatform_namespace'):
        params['tplatform_namespace'] = 'taxi'
    response = await taxi_api_admin_client.request(
        method, url, params=params, json=data,
    )
    response_body = await response.read()
    assert response.status == 200, response_body
    assert response_body == b'response'
    assert len(_patch_sms_request.calls) == 1
    assert mock.times_called == 1


@pytest.mark.parametrize(
    [
        'method',
        'params',
        'data',
        'existed_roles',
        'expected_details',
        'no_mock',
    ],
    [
        pytest.param(
            'GET',
            {
                'project_id': 38,
                'project_name': 'taxi-infra',
                'tplatform_namespace': 'taxi',
            },
            None,
            ['clowny_role_2'],
            'Fix one of these errors: Lack of role '
            'clowny_role_1 OR Lack of role clowny_role_3',
            False,
            id='lack_of_clowny_role_3',
        ),
        pytest.param(
            'GET',
            {'project_name': 'taxi-infra'},
            None,
            None,
            'Fix one of these errors: Field value with type project_id is '
            'empty OR You need role clowny_role_1 with project taxi-infra '
            'scope',
            False,
            id='wrong_project_name',
        ),
        pytest.param(
            'GET',
            {'project_id': 38, 'tplatform_namespace': 'eda'},
            None,
            None,
            'Fix one of these errors: Field value with type project_name is '
            'empty OR You need role clowny_role_3 with namespace eda scope',
            False,
            id='wrong_namespace',
        ),
        pytest.param(
            'GET',
            {'project_id': -1, 'tplatform_namespace': 'taxi'},
            None,
            None,
            'Fix one of these errors: Field value with type project_name is '
            'empty OR Lack of role clowny_role_2',
            False,
            id='wrong_project_id',
        ),
        pytest.param(
            'POST',
            None,
            {'service_id': 354163},
            None,
            'You need role clowny_role_1 with service '
            'edaeatsauthproxy scope',
            False,
            id='clowny_role_1_not_taxi_support_and_akeneo',
        ),
        pytest.param(
            'DELETE',
            {'abc_slug': 'abc-random-slug-2'},
            None,
            None,
            'You need role clowny_role_4 with service abc-random-slug-2 scope',
            False,
            id='wrong_abc_slug',
        ),
        pytest.param(
            'DELETE',
            {},
            None,
            None,
            'Field value with type abc_slug is empty',
            True,
            id='miss_value',
        ),
        pytest.param(
            'POST',
            None,
            {'service_id': 'text'},
            None,
            'Lack of role clowny_role_1',
            False,
            id='bad_int_value',
        ),
    ],
)
async def test_bad_platform_proxy(
        taxi_api_admin_client,
        grands_retrieve_mock,
        method,
        params,
        data,
        existed_roles,
        expected_details,
        no_mock,
):
    mock = grands_retrieve_mock(existed_roles)
    url = '/platform/platform/send_sms/'
    if not params:
        params = {}
    if not params.get('tplatform_namespace'):
        params['tplatform_namespace'] = 'taxi'
    response = await taxi_api_admin_client.request(
        method, url, params=params, json=data,
    )
    response_body = await response.json()
    assert response.status == 403, response_body
    assert response_body == {
        'status': 'error',
        'message': 'Check access error',
        'details': expected_details,
        'code': 'CHECK_ACCESS_ERROR',
    }
    assert mock.times_called == (0 if no_mock else 1)


@pytest.mark.parametrize(
    ['method', 'params', 'data'],
    [pytest.param('POST', {}, None, id='clowny_role_1_namespaces_retrieve')],
)
async def test_namespaces_retrieve(
        taxi_api_admin_client,
        method,
        params,
        data,
        patch_aiohttp_session,
        response_mock,
        grands_retrieve_mock,
):
    @patch_aiohttp_session(
        'http://unstable-service-host.net/v1/namespaces/retrieve/',
    )
    def _patch_namespaces_retrieve_request(*args, **kwargs):
        return response_mock(text='response', read=b'response')

    mock = grands_retrieve_mock()
    url = '/platform/platform/v1/namespaces/retrieve/'
    params['tplatform_namespace'] = 'taxi'
    response = await taxi_api_admin_client.request(
        method, url, params=params, json=data,
    )
    response_body = await response.read()
    assert response.status == 200, response_body
    assert response_body == b'response'
    assert len(_patch_namespaces_retrieve_request.calls) == 1
    assert mock.times_called == 1


async def test_empty_platform_namespace(taxi_api_admin_client):
    url = '/platform/platform/v1/namespaces/retrieve/'
    response = await taxi_api_admin_client.request(
        'GET', url, params={}, json={},
    )
    response_body = await response.json()
    assert response.status == 400, response_body
    assert response_body == {
        'code': 'TPLATFORM_NAMESPACE_EMPTY',
        'details': 'tplatform_namespace query param is empty',
        'status': 'error',
    }
