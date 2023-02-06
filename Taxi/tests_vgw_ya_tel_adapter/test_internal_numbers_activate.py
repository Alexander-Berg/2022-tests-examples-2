import pytest

from tests_vgw_ya_tel_adapter import consts


def make_request(numbers, before_playbacks=True, dial_timeout=None):
    request_json = {
        'numbers': numbers,
        'dial_code': '800',
        'label': 'new_pool',
        'prompt_playback_id': 'prompt_playback_id',
        'incorrect_input_playback_id': 'incorrect_input_playback_id',
        'correct_input_playback_id': 'correct_input_playback_id',
    }
    if before_playbacks:
        request_json.update(
            {
                'before_connected_playback_id': 'before_connected_playback_id',
                'before_conversation_playback_id': (
                    'before_conversation_playback_id'
                ),
            },
        )
    if dial_timeout is not None:
        request_json['dial_timeout'] = dial_timeout
    return request_json


@pytest.mark.now('2021-06-17T12:12:12.121212+0000')
@pytest.mark.parametrize(
    ['request_json', 'expected_status', 'expected_not_changed_numbers'],
    [
        pytest.param(
            make_request(['+78000003333', '+78000004444', '+78000005555']),
            200,
            [],
            id='ok full request',
        ),
        pytest.param(
            make_request(['+78000003333'], before_playbacks=False),
            200,
            [],
            id='ok minimal request',
        ),
        pytest.param(
            make_request(
                ['+78000003333', '+78000004444', '+74990101010', 'unknown'],
            ),
            200,
            ['+74990101010', 'unknown'],
            id='some not found',
        ),
        pytest.param(
            make_request(['+78000003333', '+78000006666']),
            200,
            ['+78000006666'],
            marks=pytest.mark.config(
                VGW_YA_TEL_ADAPTER_SERVICE_NUMBERS_BATCH_LIMIT=1,
            ),
            id='some locked',
        ),
        pytest.param(
            make_request(['+78000003333', '+78000004444', '+78000005555']),
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
async def test_activate_numbers(
        taxi_vgw_ya_tel_adapter,
        request_json,
        expected_status,
        expected_not_changed_numbers,
        mock_ya_tel,
        mock_ya_tel_grpc,
):
    response = await taxi_vgw_ya_tel_adapter.post(
        '/v1/internal/numbers/activate',
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
                    'for': 'new_pool',
                    'id': '9b8e21c0fe99560a9670106adfd94e4b00000000',
                    'city': 'Tver',
                },
            ],
        )
        assert response.status_code == 200


@pytest.mark.now('2021-06-17T12:12:12.121212+0000')
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
async def test_send_dial_timeout(
        taxi_vgw_ya_tel_adapter, mock_ya_tel, mock_ya_tel_grpc,
):
    response = await taxi_vgw_ya_tel_adapter.post(
        '/v1/internal/numbers/activate',
        headers=consts.TVM_HEADERS,
        json=make_request(
            ['+78000003333', '+78000004444', '+78000005555'], dial_timeout=30,
        ),
    )
    assert response.status_code == 200
    if response.status_code == 200:
        assert response.json()['not_changed_numbers'] == []
        # Check numbers activated
        response = await taxi_vgw_ya_tel_adapter.post(
            '/beeline/redirections',
            headers=consts.AUTH_HEADERS,
            json=[
                {
                    'callee': '+70003330001',
                    'expire': '2021-06-17T18:01:02.345678+0300',
                    'caller': '+79672763662',
                    'for': 'new_pool',
                    'id': '9b8e21c0fe99560a9670106adfd94e4b00000000',
                    'city': 'Tver',
                },
            ],
        )
        assert response.status_code == 200
