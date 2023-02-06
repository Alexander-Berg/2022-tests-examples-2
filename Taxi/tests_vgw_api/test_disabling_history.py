import pytest

ENTRY_1 = {
    'id': 1,
    'gateway_id': 'gateway_1',
    'reason': 'too many errors',
    'disabled_at': '2020-09-22T05:10:13+00:00',
    'enabled_at': '2020-09-22T06:10:13+00:00',
    'disabled_by': 'GatewayChecker',
    'enable_after': '2020-09-22T06:10:00+00:00',
    'relapse_count': 0,
}
ENTRY_2 = {
    'id': 2,
    'gateway_id': 'gateway_1',
    'reason': 'too many errors',
    'disabled_at': '2020-09-21T01:10:13+00:00',
    'enabled_at': '2020-09-21T10:20:13+00:00',
    'disabled_by': 'GatewayChecker',
    'enabled_by': 'mazgutov',
    'relapse_count': 1,
}
ENTRY_3 = {
    'id': 3,
    'gateway_id': 'gateway_2',
    'reason': 'too many errors',
    'disabled_at': '2020-09-22T07:10:13+00:00',
    'disabled_by': 'GatewayChecker',
}
ENTRY_4 = {
    'id': 4,
    'gateway_id': 'gateway_2',
    'reason': 'too many errors',
    'disabled_at': '2020-04-25T07:10:13+00:00',
    'enabled_at': '2020-05-01T10:10:13+00:00',
    'disabled_by': 'GatewayChecker',
    'enabled_by': 'mazgutov',
    'additional_disable_data': {'message': 'some text'},
    'additional_enable_data': {'message': 'they fixed errors'},
    'enable_after': '2020-05-01T10:10:00+00:00',
    'relapse_count': 5,
}


async def test_get_disabling_history(taxi_vgw_api):
    response = await taxi_vgw_api.get('v1/disabling_history/')
    assert response.json() == {
        'disabling_history': [ENTRY_3, ENTRY_1, ENTRY_2, ENTRY_4],
    }
    assert response.status_code == 200


@pytest.mark.parametrize(
    'params,expected_response',
    [
        (
            {'voice_gateway_id': 'gateway_1'},
            {'disabling_history': [ENTRY_1, ENTRY_2]},
        ),
        ({'limit': 1}, {'disabling_history': [ENTRY_3]}),
        (
            {
                'voice_gateway_id': 'gateway_1',
                'from': '2020-09-22T01:10:13+00:00',
            },
            {'disabling_history': [ENTRY_1]},
        ),
        (
            {'to': '2020-04-25T07:10:13+00:00'},
            {'disabling_history': [ENTRY_4]},
        ),
        (
            {
                'to': '2020-09-22T07:10:12+00:00',
                'from': '2020-09-21T01:10:12+00:00',
            },
            {'disabling_history': [ENTRY_1, ENTRY_2]},
        ),
        ({'limit': 3}, {'disabling_history': [ENTRY_3, ENTRY_1]}),
        ({'id': 1}, {'disabling_history': [ENTRY_1]}),
    ],
)
@pytest.mark.config(
    VGW_API_DISABLING_HISTORY_SETTINGS={
        'db_requests': {
            'status_change': {
                'network_timeout_ms': 2000,
                'statement_timeout_ms': 1000,
            },
            'read_history': {
                'network_timeout_ms': 2000,
                'statement_timeout_ms': 1000,
            },
        },
        'history_enabled': True,
        'history_entries_limit': 2,
    },
)
async def test_get_disabling_history_filters(
        taxi_vgw_api, params, expected_response,
):
    response = await taxi_vgw_api.get('v1/disabling_history/', params=params)
    assert response.json() == expected_response
    assert response.status_code == 200
