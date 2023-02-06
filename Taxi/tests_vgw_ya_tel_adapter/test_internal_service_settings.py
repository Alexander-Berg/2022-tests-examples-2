import pytest

from tests_vgw_ya_tel_adapter import consts


@pytest.mark.now('2021-06-17T12:12:12.121212+0000')
@pytest.mark.parametrize(
    ['request_json', 'expected_status'],
    [
        pytest.param(
            {
                'quarantine_duration_sec': 1234,
                'dial_playback_settings': {
                    'enabled': True,
                    'dial_actions': [
                        {
                            'dial_result': 'rejected',
                            'action_type': 'playback',
                            'playback_id': 'rejected_playback_id',
                        },
                        {
                            'dial_result': 'rejected',
                            'action_type': 'unspecified',
                            'playback_id': 'redundant_playback_id',
                        },
                        {
                            'dial_result': 'unavailable',
                            'action_type': 'playback',
                            'playback_id': 'unavailable_playback_id',
                        },
                        {
                            'dial_result': 'no_answer',
                            'action_type': 'tone_busy',
                        },
                        {
                            'dial_result': 'payment_required',
                            'action_type': 'playback',
                            'playback_id': 'payment_required_playback_id',
                        },
                        {
                            'dial_result': 'invalid_number',
                            'action_type': 'tone_busy_overload',
                        },
                    ],
                },
            },
            200,
            id='full request',
        ),
        pytest.param(
            {'dial_playback_settings': {'enabled': True}},
            200,
            id='only dial_playback_settings.enable flag',
        ),
        pytest.param({}, 200, id='empty request'),
        pytest.param(
            {
                'dial_playback_settings': {
                    'enabled': True,
                    'dial_actions': [
                        {
                            'dial_result': 'unavailable',
                            'action_type': 'playback',
                        },
                    ],
                },
            },
            400,
            id='missing playback_id',
        ),
    ],
)
@pytest.mark.config()
@consts.mock_tvm_configs()
async def test_service_settings(
        taxi_vgw_ya_tel_adapter,
        mock_ya_tel,
        mock_ya_tel_grpc,
        request_json,
        expected_status,
):
    response = await taxi_vgw_ya_tel_adapter.post(
        '/v1/internal/service_settings',
        headers=consts.TVM_HEADERS,
        json=request_json,
    )
    assert response.status_code == expected_status
