import pytest

from tests_vgw_ya_tel_adapter import consts


@pytest.mark.now('2021-06-17T12:12:12.121212+0000')
@pytest.mark.parametrize(
    (
        'redirections',
        'provider',
        'headers',
        'expected_status',
        'expected_json',
    ),
    [
        pytest.param(
            [
                {
                    'callee': '+70003330001',
                    'expire': '2021-06-17T18:01:02.345678+0300',
                    'caller': '+79672763662',
                    'for': 'driver',
                    'id': '9b8e21c0fe99560a9670106adfd94e4b00000000',
                    'city': 'Moscow',
                },
                {
                    'callee': '+70003330002',
                    'expire': '2021-06-17T14:00:00+0000',
                    'caller': '+79672763662',
                    'for': 'mobile',
                    'id': '9f611069d039265da3f7bfb5dce9ea6502000000',
                    'city': 'Moscow',
                },
                {
                    'callee': '+70001110001',
                    'expire': '2021-06-17T15:00:00+0000',
                    'caller': '+79672763662',
                    'for': 'driver',
                    'id': '65b75eec3d8a38c9952e3cc7ec9d9d8302000000',
                    'city': 'Moscow 499',
                },
            ],
            None,
            consts.AUTH_HEADERS,
            200,
            'expected_response_ok.json',
            id='ok create + replace',
        ),
        pytest.param(
            [
                {
                    'callee': '+70003330001',
                    'expire': '2021-06-17T18:01:02.345678+0300',
                    'caller': '+79672763662',
                    'for': 'driver',
                    'id': '9b8e21c0fe99560a9670106adfd94e4b00000000',
                    'city': 'Moscow',
                },
            ],
            'beeline',
            consts.AUTH_HEADERS,
            200,
            'expected_response_ok_beeline.json',
            id='ok beeline',
        ),
        pytest.param(
            [
                {
                    'callee': '+70003330001',
                    'expire': '2021-06-17T18:01:02.345678+0300',
                    'caller': '+79672763662',
                    'for': 'driver',
                    'id': '9b8e21c0fe99560a9670106adfd94e4b00000000',
                    'city': 'Moscow',
                },
            ],
            'a1',
            consts.AUTH_HEADERS,
            200,
            'expected_response_ok_a1.json',
            id='ok a1',
        ),
        pytest.param(
            [
                {
                    'callee': '+70003330001',
                    'expire': '2021-06-17T12:00:00+0000',
                    'caller': '+79672763662',
                    'for': 'driver',
                    'id': '9b8e21c0fe99560a9670106adfd94e4b00000000',
                    'city': 'Moscow',
                },
            ],
            None,
            consts.AUTH_HEADERS,
            400,
            'expected_response_bad_request.json',
            id='bad request old expire datetime',
        ),
        pytest.param(
            [
                {
                    'callee': '+70003330001',
                    'expire': '2022-06-17T15:00:00+0000',
                    'caller': '+79672763662',
                    'for': 'driver',
                    'id': '9b8e21c0fe99560a9670106adfd94e4b00000000',
                    'city': 'Moscow',
                },
            ],
            None,
            consts.AUTH_HEADERS,
            400,
            'expected_response_bad_request.json',
            id='bad request too long expiration',
        ),
        pytest.param(
            [
                {
                    'caller': '+79672763662',
                    'callee': '+70003330001',
                    'expire': '2021-06-17T15:00:00+0000',
                    'for': 'driver',
                    'id': '9b8e21c0fe99560a9670106adfd94e4b00000000',
                    'city': 'Karaganda',
                },
            ],
            None,
            consts.AUTH_HEADERS,
            400,
            'expected_response_bad_request_unknown_region.json',
            id='bad request region without geocodes',
        ),
        pytest.param(
            [
                {
                    'caller': '+79672763662',
                    'callee': '+70003330001',
                    'expire': '2021-06-17T15:00:00+0000',
                    'for': 'driver',
                    'id': '9b8e21c0fe99560a9670106adfd94e4b00000000',
                    'city': 'Uryupinsk',
                },
            ],
            None,
            consts.AUTH_HEADERS,
            400,
            'expected_response_bad_request_unknown_region.json',
            id='bad request unknown region',
        ),
        pytest.param(
            [
                {
                    'callee': '+70003330001',
                    'expire': '2021-06-17T18:01:02.345678+0300',
                    'caller': '+79672763662',
                    'for': 'driver',
                    'id': '9b8e21c0fe99560a9670106adfd94e4b00000000',
                    'city': 'Moscow',
                },
            ],
            'voximplant',
            consts.AUTH_HEADERS,
            400,
            'expected_response_bad_request_unknown_provider.json',
            id='bad request unknown provider',
        ),
        pytest.param(
            [
                {
                    'caller': '+79672763662',
                    'callee': '+70003330001',
                    'expire': '2021-06-17T18:01:02.345678+0300',
                    'for': 'driver',
                    'id': '9b8e21c0fe99560a9670106adfd94e4b00000000',
                    'city': 'Moscow',
                },
            ],
            None,
            consts.BAD_AUTH_HEADERS,
            403,
            'expected_response_bad_auth_token.json',
            id='bad auth token',
        ),
        pytest.param(
            [
                {
                    'caller': '+79672763662',
                    'callee': '+70003330001',
                    'expire': '2021-06-17T15:00:00+0000',
                    'for': 'driver',
                    'id': '9b8e21c0fe99560a9670106adfd94e4b00000000',
                    'city': 'Moscow 499',
                },
                {
                    'caller': '+79672763662',
                    'callee': '+70003330002',
                    'expire': '2021-06-17T15:00:00+0000',
                    'for': 'driver',
                    'id': '65b75eec3d8a38c9952e3cc7ec9d9d8302000000',
                    'city': 'Moscow 499',
                },
            ],
            None,
            consts.AUTH_HEADERS,
            503,
            'expected_response_service_unavailable.json',
            id='out of ext numbers for city',
        ),
        pytest.param(
            [
                {
                    'caller': '+79672763662',
                    'callee': '+70003330001',
                    'expire': '2021-06-17T15:00:00+0000',
                    'for': 'driver',
                    'id': '9b8e21c0fe99560a9670106adfd94e4b00000000',
                    'city': 'Moscow',
                },
                {
                    'caller': '+79672763662',
                    'callee': '+70003330002',
                    'expire': '2021-06-17T15:00:00+0000',
                    'for': 'driver',
                    'id': '65b75eec3d8a38c9952e3cc7ec9d9d8302000000',
                    'city': 'Moscow',
                },
            ],
            'a1',
            consts.AUTH_HEADERS,
            503,
            'expected_response_service_unavailable.json',
            id='out of ext numbers for provider',
        ),
        pytest.param(
            [
                {
                    'caller': '+79672763662',
                    'callee': '+70003330001',
                    'expire': '2021-06-17T15:00:00+0000',
                    'for': 'driver',
                    'id': '9b8e21c0fe99560a9670106adfd94e4b00000000',
                    'city': 'Tver',
                },
            ],
            None,
            consts.AUTH_HEADERS,
            503,
            'expected_response_service_unavailable.json',
            id='unknown city',
        ),
        pytest.param(
            [
                {
                    'caller': '+79672763662',
                    'callee': '+70003330001',
                    'expire': '2021-06-17T15:00:00+0000',
                    'for': 'mobile',
                    'id': '9b8e21c0fe99560a9670106adfd94e4b00000000',
                    'city': 'Moscow 499',
                },
            ],
            None,
            consts.AUTH_HEADERS,
            503,
            'expected_response_service_unavailable.json',
            id='unknown city for label',
        ),
    ],
)
@pytest.mark.parametrize(
    'content_type', ['application/x-www-form-urlencoded', 'application/json'],
)
@pytest.mark.config(
    VGW_YA_TEL_ADAPTER_REGION_INFO_MAP={
        'Moscow': {'geocodes': ['216', '213']},
        'Moscow 499': {'geocodes': ['216']},
        'Tver': {'geocodes': ['14']},
        'Karaganda': {},
    },
    VGW_YA_TEL_ADAPTER_PROVIDER_INFO_MAP={
        'beeline': {'names': ['Beeline Provider']},
        'a1': {'names': ['A1 Provider']},
        'kcell': {'names': ['Kcell Provider']},
    },
)
@consts.mock_tvm_configs()
async def test_post_redirections(
        taxi_vgw_ya_tel_adapter,
        redirections,
        provider,
        headers,
        expected_status,
        expected_json,
        content_type,
        mock_ya_tel,
        mock_ya_tel_grpc,
        load_json,
):
    headers['Content-Type'] = content_type
    url = f'/{provider}/redirections' if provider else '/redirections'
    response = await taxi_vgw_ya_tel_adapter.post(
        url, json=redirections, headers=headers,
    )
    assert response.status_code == expected_status
    assert response.json() == load_json(expected_json)


@pytest.mark.now('2021-06-17T12:12:12.121212+0000')
@pytest.mark.parametrize(
    'redirections, callernum, headers',
    [
        pytest.param(
            [
                {
                    'callee': '+70003330001',
                    'expire': '2021-06-17T18:01:02.345678+0300',
                    'caller': '+79672763662',
                    'for': 'driver',
                    'id': '9b8e21c0fe99560a9670106adfd94e4b00000000',
                    'city': 'Moscow',
                },
            ],
            '+79672763662',
            consts.AUTH_HEADERS,
            id='normal callernum',
        ),
        pytest.param(
            [
                {
                    'callee': '+70003330001',
                    'expire': '2021-06-17T18:01:02.345678+0300',
                    'caller': 'strange_value',
                    'for': 'driver',
                    'id': '9b8e21c0fe99560a9670106adfd94e4b00000000',
                    'city': 'Moscow',
                },
            ],
            '',
            consts.AUTH_HEADERS,
            id='broken callernum',
        ),
    ],
)
@pytest.mark.parametrize(
    'content_type', ['application/x-www-form-urlencoded', 'application/json'],
)
@pytest.mark.config(
    VGW_YA_TEL_ADAPTER_REGION_INFO_MAP={
        'Moscow': {'geocodes': ['216', '213']},
    },
)
@consts.mock_tvm_configs()
async def test_post_redirections_drop_bad_callernum(
        taxi_vgw_ya_tel_adapter,
        redirections,
        headers,
        callernum,
        content_type,
        mock_ya_tel,
        mock_ya_tel_grpc,
        load_json,
        testpoint,
):
    @testpoint('callernum')
    def _testpoint(data):
        assert data['callernum'] == callernum

    headers['Content-Type'] = content_type
    response = await taxi_vgw_ya_tel_adapter.post(
        '/redirections', json=redirections, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            'callee': '+70003330001',
            'for': 'driver',
            'phone': '+74950101010',
            'ext': '1001',
            'id': '9b8e21c0fe99560a9670106adfd94e4b00000000',
            'expires': '2021-06-17T15:01:02.345678+00:00',
            'updated': '2021-06-17T12:12:12.121212+00:00',
        },
    ]
