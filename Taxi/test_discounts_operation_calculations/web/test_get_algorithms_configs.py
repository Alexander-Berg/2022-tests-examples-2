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
    {
        'algorithm_name': 'testing',
        'description': 'Тестовый алгоритм',
        'metric_name': 'первая метрика',
        'second_metric_name': 'вторая метрика ',
        'max_absolute_value': 200.0,
        'min_value': 0.0,
        'max_value': 0.5,
        'is_price_strikethrough': True,
        'classes': ['econom', 'uberx', 'business'],
        'discount_duration': 7,
        'disable_by_surge': 1.2,
        'payment_types': ['card', 'applepay'],
        'segment_stats_path': 'testing_segment_stats_hist2',
        'segment_stats_hist_path': 'testing_segment_stats',
        'user_segment_path': 'testing_user_segments',
        'yql_tagging_path': 'testing_tagging_test2',
        'yql_tagging_hist_path': 'testing_tagging_test_hist2',
        'is_tagging_active': True,
        'control_hashing_salt': '10_2020_kt',
        'random_hashing_salt': '2021-07-19-random_users-kt2',
        'control_share': 30,
        'random_share': 10,
    },
]


@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=['fill_pg_algorithms_configs.sql'],
)
async def test_get_algorithms_configs(web_app_client):
    response = await web_app_client.get('/v1/algorithms/configs')

    assert response.status == 200
    content = await response.json()

    assert (
        sorted(content, key=lambda x: x['algorithm_name']) == EXPECTED_CONFIGS
    )
