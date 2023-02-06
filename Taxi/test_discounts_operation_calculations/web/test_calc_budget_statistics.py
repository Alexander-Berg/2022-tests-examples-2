import pytest

CONTROL_SHARE = 10
TEST_SHARE = (100 - CONTROL_SHARE) / 100
URL = '/v2/statistics/calc_budget_statistics'


@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=[
        'fill_pg_segment_stats_all.sql',
        'fill_pg_suggests_v2.sql',
        'fill_pg_calc_segment_stats_tasks.sql',
    ],
)
@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_ALGORITHMS_CONFIGS={
        'kt': {
            'name': 'algorithm1',
            'metric_name': 'Отобранные поездки',
            'second_metric_name': 'Цена дополнительного оффера',
            'algorithm_type': 'katusha',
            'control_share': CONTROL_SHARE,
        },
    },
)
async def test_retrieve_statistics_v2(web_app_client):
    response = await web_app_client.post(
        URL,
        json={
            'suggest_id': 1,
            'all_fixed_discounts': [
                {
                    'algorithm_id': 'kt',
                    'fixed_discounts': [
                        {'discount_value': 0, 'segment': 'control'},
                        {'discount_value': 12, 'segment': 'random'},
                    ],
                },
            ],
        },
    )
    assert response.status == 200
    content = await response.json()
    assert len(content['charts']) == 3


@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=[
        'fill_pg_segment_stats_all.sql',
        'fill_pg_suggests_v2.sql',
        'fill_pg_calc_segment_stats_tasks.sql',
    ],
)
@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_ALGORITHMS_CONFIGS={
        'kt': {
            'name': 'algorithm1',
            'metric_name': 'Отобранные поездки',
            'second_metric_name': 'Цена дополнительного оффера',
            'algorithm_type': 'katusha',
            'control_share': CONTROL_SHARE,
        },
    },
)
async def test_retrieve_statistics_v2_missed_bucket(web_app_client, pgsql):
    cursor = pgsql['discounts_operation_calculations'].cursor()
    # Delete data with price_from < 100 for metrika_notactive_Mconv segment
    # In old code this caused exception (response.status == 500)
    query = """DELETE FROM discounts_operation_calculations.segment_stats_all
    WHERE segment = 'metrika_notactive_Mconv' AND price_from < 100"""
    cursor.execute(query)
    cursor.close()

    response = await web_app_client.post(
        URL,
        json={
            'suggest_id': 1,
            'all_fixed_discounts': [
                {
                    'algorithm_id': 'kt',
                    'fixed_discounts': [
                        {'discount_value': 0, 'segment': 'control'},
                        {'discount_value': 12, 'segment': 'random'},
                    ],
                },
            ],
        },
    )
    assert response.status == 200
    content = await response.json()
    assert len(content['charts']) == 3


@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=[
        'fill_pg_segment_stats_all.sql',
        'fill_pg_suggests_v2.sql',
        'fill_pg_calc_segment_stats_tasks.sql',
    ],
)
@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_ALGORITHMS_CONFIGS={
        'kt': {
            'name': 'algorithm1',
            'metric_name': 'Отобранные поездки',
            'second_metric_name': 'Цена дополнительного оффера',
            'algorithm_type': 'katusha',
            'control_share': CONTROL_SHARE,
        },
    },
)
async def test_retrieve_statistics_v2_nonzero_min_disc(web_app_client, pgsql):
    cursor = pgsql['discounts_operation_calculations'].cursor()
    # change suggest_id for segment_stats
    query = """UPDATE discounts_operation_calculations.segment_stats_all
    SET suggest_id = 2"""
    cursor.execute(query)
    cursor.close()
    response = await web_app_client.post(
        URL,
        json={
            'suggest_id': 2,
            'all_fixed_discounts': [
                {
                    'algorithm_id': 'kt',
                    'fixed_discounts': [
                        {'discount_value': 0, 'segment': 'control'},
                        {'discount_value': 12, 'segment': 'random'},
                    ],
                },
            ],
        },
    )
    assert response.status == 200
    content = await response.json()
    assert len(content['charts']) == 3
