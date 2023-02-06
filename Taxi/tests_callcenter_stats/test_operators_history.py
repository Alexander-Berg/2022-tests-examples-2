import pytest

OPERATORS_HISTORY_URL = '/v1/operators/history'


@pytest.mark.pgsql(
    'callcenter_stats', files=['callcenter_operators_history.sql'],
)
@pytest.mark.parametrize(
    ['request_body', 'expected_status', 'expected_data'],
    [
        pytest.param('body_1.json', 200, 'expected_data_1.json', id='limit=5'),
        pytest.param(
            'body_2.json',
            200,
            'expected_data_2.json',
            id='limit=100,cursor=7, test skip',
        ),
        pytest.param(
            'body_3.json', 200, 'empty_expected_data.json', id='limit=0',
        ),
        pytest.param('body_4.json', 200, 'expected_data_4.json', id='limit=1'),
        pytest.param(
            'body_5.json', 200, 'expected_data_5.json', id='limit=1,cursor=1',
        ),
        pytest.param(
            'body_6.json',
            200,
            'expected_data_6.json',
            id='limit=100,cursor=10',
        ),
        pytest.param('empty_body.json', 400, None, id='{}'),
        pytest.param('negative_limit_body.json', 400, None, id='limit=-1'),
        pytest.param(
            'body_7.json', 200, 'expected_data_7.json', id='check meta',
        ),
    ],
)
async def test_operators_history(
        taxi_callcenter_stats,
        request_body,
        load_json,
        mock_personal,
        expected_status,
        expected_data,
):
    response = await taxi_callcenter_stats.post(
        OPERATORS_HISTORY_URL, json=load_json(request_body),
    )
    assert response.status_code == expected_status
    if expected_data:
        assert response.json() == load_json(expected_data)
