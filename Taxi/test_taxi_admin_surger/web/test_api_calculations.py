import pytest


@pytest.mark.parametrize(
    'params, expected_len, expected_cursor',
    [
        ({'calculation_id': 'cc_id_0'}, 1, '-1636638384480832649'),
        ({'geopoint_id': 'gg_wp_1'}, 1, '-1636638377259540330'),
        ({'pipeline_id': 'pipeline_0'}, 2, '-1636638377259540330'),
        (
            {'pipeline_id': 'pipeline_0', 'geopoint_id': 'gg_wp_1'},
            1,
            '-1636638377259540330',
        ),
        ({}, 3, '-1636637996488415715'),
        ({'cursor': '-1636638384480832649'}, 2, '-1636637996488415715'),
        (
            {'cursor': '-1636638384480832649', 'max_records': 1},
            1,
            '-1636638377259540330',
        ),
        ({'cursor': '-1636637996488415715'}, 0, None),
    ],
)
@pytest.mark.yt(dyn_table_data=['yt_calculations_log.yaml'])
@pytest.mark.config(
    SURGE_YT_LOGS_PATH='//home/taxi/testsuite/surge-calculations-log',
)
async def test_calculations_log(
        web_app_client, yt_apply, params, expected_len, expected_cursor,
):
    response = await web_app_client.get(
        'admin/v1/calculations-log', params=params,
    )
    assert response.status == 200

    data = await response.json()
    assert data.get('cursor') == expected_cursor
    assert 'entities' in data
    entities = data['entities']
    assert len(entities) == expected_len
    for row in entities:
        if 'calculation_id' in params:
            assert params['calculation_id'] == row['calculation_id']
