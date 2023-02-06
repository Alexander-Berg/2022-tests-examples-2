import pytest

from tests_vgw_ya_tel_adapter import consts


@pytest.mark.now('2021-06-17T12:12:12.121212+0000')
@pytest.mark.parametrize(
    ['request_json', 'expected_status', 'expected_not_changed_numbers'],
    [
        pytest.param(
            {
                'numbers': ['+78000003333', '+78000004444', '+78000005555'],
                'dial_code': '800',
                'action': 'activate',
            },
            200,
            [],
            id='activate, ok big request',
        ),
        pytest.param(
            {
                'numbers': ['+78000003333'],
                'dial_code': '800',
                'action': 'activate',
            },
            200,
            [],
            id='activate, ok small request',
        ),
        pytest.param(
            {
                'numbers': [
                    '+78000003333',
                    '+78000004444',
                    '+74990101010',
                    'unknown',
                ],
                'dial_code': '800',
                'action': 'activate',
            },
            200,
            ['+74990101010', 'unknown'],
            id='activate, some not found',
        ),
        pytest.param(
            {
                'numbers': ['+78000003333', '+78000006666'],
                'dial_code': '800',
                'action': 'activate',
            },
            200,
            ['+78000006666'],
            marks=pytest.mark.config(
                VGW_YA_TEL_ADAPTER_SERVICE_NUMBERS_BATCH_LIMIT=1,
            ),
            id='activate, some locked',
        ),
        pytest.param(
            {
                'numbers': ['+78000003333', '+78000004444', '+78000005555'],
                'dial_code': '800',
                'action': 'activate',
            },
            500,
            None,
            marks=pytest.mark.config(
                VGW_YA_TEL_ADAPTER_SERVICE_NUMBERS_BATCH_LIMIT=consts.SERVICE_NUM_BATCH_LIMIT  # noqa: E501
                + 1,
            ),
            id='activate, exceeded batch limit',
        ),
        pytest.param(
            {
                'numbers': [
                    '+78000003333',
                    '+78000004444',
                    '+78000005555',
                    '+78000006666',
                ],
                'dial_code': '800',
                'action': 'remove_quarantine',
            },
            200,
            ['+78000003333', '+78000004444', '+78000006666'],
            id='remove_quarantine, ok big request',
        ),
        pytest.param(
            {
                'numbers': ['+78000005555'],
                'dial_code': '800',
                'action': 'remove_quarantine',
            },
            200,
            [],
            id='remove_quarantine, ok small request',
        ),
        pytest.param(
            {
                'numbers': [
                    '+78000005555',
                    '+78000004444',
                    '+74990101010',
                    'unknown',
                ],
                'dial_code': '800',
                'action': 'remove_quarantine',
            },
            200,
            ['+78000004444', '+74990101010', 'unknown'],
            id='remove_quarantine, some not found',
        ),
        pytest.param(
            {
                'numbers': ['+78000005555', '+78000006666'],
                'dial_code': '800',
                'action': 'remove_quarantine',
            },
            200,
            ['+78000006666'],
            marks=pytest.mark.config(
                VGW_YA_TEL_ADAPTER_SERVICE_NUMBERS_BATCH_LIMIT=1,
            ),
            id='remove_quarantine, some locked',
        ),
        pytest.param(
            {
                'numbers': ['+78000003333', '+78000004444', '+78000005555'],
                'dial_code': '800',
                'action': 'remove_quarantine',
            },
            500,
            None,
            marks=pytest.mark.config(
                VGW_YA_TEL_ADAPTER_SERVICE_NUMBERS_BATCH_LIMIT=consts.SERVICE_NUM_BATCH_LIMIT  # noqa: E501
                + 1,
            ),
            id='remove_quarantine, exceeded batch limit',
        ),
    ],
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
    VGW_YA_TEL_ADAPTER_SERVICE_NUMBERS_BATCH_LIMIT=consts.SERVICE_NUM_BATCH_LIMIT,  # noqa: E501
)
@consts.mock_tvm_configs()
async def test_activate_and_remove_quarantine(
        taxi_vgw_ya_tel_adapter,
        request_json,
        expected_status,
        expected_not_changed_numbers,
        mock_ya_tel,
        mock_ya_tel_grpc,
):
    response = await taxi_vgw_ya_tel_adapter.post(
        '/v1/internal/numbers/change_state',
        headers=consts.TVM_HEADERS,
        json=request_json,
    )
    assert response.status_code == expected_status
    if response.status_code == 200:
        assert (
            response.json()['not_changed_numbers']
            == expected_not_changed_numbers
        )
        # Check numbers activated
        response = await taxi_vgw_ya_tel_adapter.post(
            '/beeline/redirections',
            headers=consts.AUTH_HEADERS,
            json=[
                {
                    'callee': '+70003330001',
                    'expire': '2021-06-17T18:01:02.345678+0300',
                    'caller': '+79672763662',
                    'for': 'driver',
                    'id': '9b8e21c0fe99560a9670106adfd94e4b00000000',
                    'city': 'Tver',
                },
            ],
        )
        assert response.status_code == 200


@pytest.mark.now('2021-06-17T12:12:12.121212+0000')
@pytest.mark.parametrize(['action'], [('deactivate',), ('set_quarantine',)])
@pytest.mark.parametrize(
    ['request_json', 'expected_status', 'expected_not_changed_numbers'],
    [
        pytest.param(
            {'numbers': ['+74950101010', '+74950202020'], 'dial_code': '495'},
            200,
            [],
            marks=pytest.mark.config(
                VGW_YA_TEL_ADAPTER_SERVICE_NUMBERS_BATCH_LIMIT=1,
            ),
            id='ok big request',
        ),
        pytest.param(
            {'numbers': ['+74950101010'], 'dial_code': '495'},
            200,
            [],
            id='ok small request',
        ),
        pytest.param(
            {
                'numbers': [
                    '+74950101010',
                    '+74950202020',
                    '+74950000000',
                    '+74990101010',
                    'unknown',
                ],
                'dial_code': '495',
            },
            200,
            ['+74950000000', '+74990101010', 'unknown'],
            id='some not found',
        ),
        pytest.param(
            {'numbers': ['+74990101010'], 'dial_code': '499'},
            200,
            ['+74990101010'],
            id='some locked',
        ),
        pytest.param(
            {
                'numbers': ['+74950101010', '+74950202020', '+74990101010'],
                'dial_code': '495',
            },
            500,
            None,
            marks=pytest.mark.config(
                VGW_YA_TEL_ADAPTER_SERVICE_NUMBERS_BATCH_LIMIT=consts.SERVICE_NUM_BATCH_LIMIT  # noqa: E501
                + 1,
            ),
            id='exceeded batch limit',
        ),
    ],
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
    VGW_YA_TEL_ADAPTER_SERVICE_NUMBERS_BATCH_LIMIT=consts.SERVICE_NUM_BATCH_LIMIT,  # noqa: E501
)
@consts.mock_tvm_configs()
async def test_deactivate_and_set_quarantine(
        taxi_vgw_ya_tel_adapter,
        request_json,
        expected_status,
        expected_not_changed_numbers,
        action,
        mock_ya_tel,
        mock_ya_tel_grpc,
):
    request_json['action'] = action
    response = await taxi_vgw_ya_tel_adapter.post(
        '/v1/internal/numbers/change_state',
        headers=consts.TVM_HEADERS,
        json=request_json,
    )
    assert response.status_code == expected_status
    response_json = response.json()
    if response.status_code == 200:
        assert (
            response_json['not_changed_numbers']
            == expected_not_changed_numbers
        )
        if len(response_json['not_changed_numbers']) < len(
                request_json['numbers'],
        ):
            # Check numbers deactivated or on quarantine
            response = await taxi_vgw_ya_tel_adapter.post(
                '/beeline/redirections',
                headers=consts.AUTH_HEADERS,
                json=[
                    {
                        'callee': '+70003330001',
                        'expire': '2021-06-17T18:01:02.345678+0300',
                        'caller': '+79672763662',
                        'for': 'driver',
                        'id': '9b8e21c0fe99560a9670106adfd94e4b00000000',
                        'city': 'Moscow',
                    },
                ],
            )
            assert response.status_code == 503
