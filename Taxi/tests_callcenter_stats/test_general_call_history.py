import pytest

GENERAL_CALL_HISTORY_URL = '/cc/v1/callcenter-stats/v1/general-call-history'
GENERAL_CALL_LEG_HISTORY_URL = (
    '/cc/v1/callcenter-stats/v1/general-call-history/legs'
)
GENERAL_CALL_EVENT_HISTORY_URL = (
    '/cc/v1/callcenter-stats/v1/general-call-history/events'
)


@pytest.mark.pgsql(
    'callcenter_stats', files=['callcenter_general_call_history.sql'],
)
@pytest.mark.parametrize(
    ['request_body', 'expected_status', 'expected_data'],
    [
        pytest.param(
            'body_1.json', 200, 'expected_data_1.json', id='call_guid',
        ),
        pytest.param(
            'body_2.json', 200, 'expected_data_2.json', id='initiator_type',
        ),
        pytest.param(
            'body_3.json',
            200,
            'expected_data_3.json',
            id='initiator_type,initiator_id',
        ),
        pytest.param(
            'body_4.json', 200, 'empty_expected_data.json', id='limit=0',
        ),
        pytest.param('body_5.json', 200, 'expected_data_5.json', id='{}'),
        pytest.param('body_6.json', 200, 'expected_data_6.json', id='limit=1'),
        pytest.param(
            'body_7.json', 200, 'expected_data_7.json', id='limit=1,cursor=3',
        ),
        pytest.param(
            'body_8.json', 200, 'expected_data_8.json', id='controller_id',
        ),
        pytest.param('negative_limit_body.json', 400, None, id='limit=-1'),
    ],
)
async def test_general_call_history(
        taxi_callcenter_stats,
        request_body,
        load_json,
        mock_personal,
        expected_status,
        expected_data,
):
    response = await taxi_callcenter_stats.post(
        GENERAL_CALL_HISTORY_URL, json=load_json(request_body),
    )
    assert response.status_code == expected_status
    if expected_data:
        assert response.json() == load_json(expected_data)


@pytest.mark.pgsql(
    'callcenter_stats', files=['callcenter_general_call_history.sql'],
)
@pytest.mark.parametrize(
    ['request_body', 'expected_status', 'expected_data'],
    [
        pytest.param(
            'body_10.json', 200, 'expected_data_10.json', id='call_guid',
        ),
        pytest.param('body_5.json', 400, None, id='{}'),
    ],
)
async def test_call_leg_history(
        taxi_callcenter_stats,
        request_body,
        load_json,
        mock_personal,
        expected_status,
        expected_data,
):
    response = await taxi_callcenter_stats.post(
        GENERAL_CALL_LEG_HISTORY_URL, json=load_json(request_body),
    )
    assert response.status_code == expected_status
    if expected_data:
        assert response.json() == load_json(expected_data)


@pytest.mark.pgsql(
    'callcenter_stats', files=['callcenter_general_call_history.sql'],
)
@pytest.mark.parametrize(
    ['request_body', 'expected_status', 'expected_data'],
    [
        pytest.param(
            'body_20.json', 200, 'expected_data_20.json', id='call_guid',
        ),
        pytest.param('body_5.json', 400, None, id='{}'),
    ],
)
async def test_call_event_history(
        taxi_callcenter_stats,
        request_body,
        load_json,
        mock_personal,
        expected_status,
        expected_data,
):
    response = await taxi_callcenter_stats.post(
        GENERAL_CALL_EVENT_HISTORY_URL, json=load_json(request_body),
    )
    assert response.status_code == expected_status
    if expected_data:
        assert response.json() == load_json(expected_data)
