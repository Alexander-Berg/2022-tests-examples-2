import pytest


EXPECTED_CONFIGS = [
    {
        'algorithm_name': 'kt2',
        'description': 'тут описание для вывода на фронт',
        'metric_name': 'название метрики: экстра трипы, отобранные офферы',
        'second_metric_name': 'название второй метрики',
        'max_absolute_value': 300.0,
        'min_value': 0.05,
        'max_value': 0.5,
        'is_price_strikethrough': True,
        'classes': ['econom', 'uberx', 'business'],
        'discount_duration': 365,
        'disable_by_surge': 1.2,
        'payment_types': ['card', 'applepay'],
        'segment_stats_path': 'kt2_segment_stats_hist2',
        'segment_stats_hist_path': 'kt2_segment_stats',
        'user_segment_path': 'kt2_user_segments',
        'yql_tagging_path': 'kt2_tagging_test2',
        'yql_tagging_hist_path': 'kt2_tagging_test_hist2',
        'is_tagging_active': True,
        'algorithm_type': 'katusha',
        'push_segment_stats_path': 'kt2_segment_stats_push',
        'control_hashing_salt': '',
        'random_hashing_salt': '2021-07-19-random_users-kt2',
        'control_share': 20,
        'random_share': 10,
    },
]


@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=['fill_pg_algorithms_configs.sql'],
)
async def test_delete_algorithm_config(web_app_client):
    response_add = await web_app_client.delete(
        '/v1/algorithms/configs/delete', params={'algorithm_name': 'testing'},
    )
    assert response_add.status == 200

    response_get = await web_app_client.get('/v1/algorithms/configs')
    assert response_get.status == 200

    content = await response_get.json()

    assert (
        sorted(content, key=lambda x: x['algorithm_name']) == EXPECTED_CONFIGS
    )


@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=['fill_pg_algorithms_configs.sql'],
)
async def test_delete_non_existent_algorithm_config(web_app_client):
    response = await web_app_client.delete(
        '/v1/algorithms/configs/delete',
        params={'algorithm_name': 'non_existent'},
    )
    assert response.status == 400

    content = await response.json()
    assert content['code'] == 'BadRequest::ConfigNotFound'
