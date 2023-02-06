# flake8: noqa E501
import pandas as pd
import pytest

from taxi.stq import async_worker_ng

from discounts_operation_calculations.internals import enums
from discounts_operation_calculations.internals import helpers
from discounts_operation_calculations.internals import (
    segment_stats_loader_v2 as seg_loader,
)
from discounts_operation_calculations.stq import calc_segment_stats
from test_discounts_operation_calculations import conftest


@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_ELASTICITIES=conftest.ELASTICITIES_DICT,
)
@pytest.mark.parametrize(
    'stats_type, stats_columns, replace_columns, expected_results, '
    'expected_results_control, expected_results_random, '
    'control_share, random_share',
    (
        pytest.param(
            enums.StatsType.DEFAULT,
            [
                'city',
                'price_bucket',
                'segment',
                'discount',
                'currency_rate',
                'currency_code',
                'trips',
                'gmv',
                'gmv_low_surge',
                'active_users',
            ],
            {},
            [
                [
                    'test_city',
                    '2',
                    50,
                    100,
                    pytest.approx(488.53749999999997),
                    pytest.approx(44356.825),
                    pytest.approx(46280.242824999994),
                    3,
                    pytest.approx(24.9154125),
                    pytest.approx(24.9154125),
                    pytest.approx(1189.12478475),
                    1.0,
                    'RUB',
                    enums.StatsType.DEFAULT.value,
                    pytest.approx(477.275),
                ],
            ],
            [
                [
                    'test_city',
                    'control',
                    50,
                    100,
                    pytest.approx(118.95),
                    pytest.approx(10829.050000000001),
                    pytest.approx(11049.401199999998),
                    3,
                    pytest.approx(2.8548),
                    pytest.approx(2.8548),
                    pytest.approx(282.04953600000005),
                    1.0,
                    'RUB',
                    'default',
                    pytest.approx(116.95),
                ],
            ],
            [
                [
                    'test_city',
                    'random',
                    50,
                    100,
                    pytest.approx(89.21249999999999),
                    pytest.approx(8121.787499999999),
                    pytest.approx(8287.050899999998),
                    3,
                    pytest.approx(2.1411),
                    pytest.approx(2.1411),
                    pytest.approx(211.537152),
                    1.0,
                    'RUB',
                    'default',
                    pytest.approx(87.71249999999999),
                ],
            ],
            20 / 100,
            15 / 100,
        ),
        pytest.param(
            enums.StatsType.FLAT,
            [
                'city',
                'price_bucket',
                'segment',
                'discount',
                'currency_rate',
                'currency_code',
                'high_surge_trips',
                'gmv',
                'gmv_high_surge',
                'active_users',
            ],
            {'gmv_high_surge': 'gmv_low_surge', 'high_surge_trips': 'trips'},
            [
                [
                    'test_city',
                    '2',
                    50,
                    100,
                    pytest.approx(79.5625),
                    pytest.approx(49575.274999999994),
                    pytest.approx(49864.82074999999),
                    3,
                    pytest.approx(3.1029375000000003),
                    pytest.approx(3.1029375000000003),
                    pytest.approx(231.4138725),
                    1.0,
                    'RUB',
                    enums.StatsType.FLAT.value,
                    pytest.approx(533.425),
                ],
            ],
            [
                [
                    'test_city',
                    'control',
                    50,
                    100,
                    pytest.approx(8.825000000000001),
                    pytest.approx(5414.525000000001),
                    pytest.approx(5434.298000000001),
                    3,
                    pytest.approx(0.21180000000000004),
                    pytest.approx(0.21180000000000004),
                    pytest.approx(25.30944),
                    1.0,
                    'RUB',
                    'flat',
                    pytest.approx(58.475),
                ],
            ],
            [
                [
                    'test_city',
                    'random',
                    50,
                    100,
                    pytest.approx(4.4125000000000005),
                    pytest.approx(2707.2625000000003),
                    pytest.approx(2717.1490000000003),
                    3,
                    pytest.approx(0.10590000000000002),
                    pytest.approx(0.10590000000000002),
                    pytest.approx(12.65472),
                    1.0,
                    'RUB',
                    'flat',
                    pytest.approx(29.2375),
                ],
            ],
            10 / 100,
            5 / 100,
        ),
        pytest.param(
            enums.StatsType.PUSH,
            [
                'city',
                'price_bucket',
                'segment',
                'discount',
                'currency_rate',
                'currency_code',
                'trips',
                'gmv',
                'gmv_low_surge',
                'active_users',
            ],
            {},
            [
                [
                    'test_city',
                    '2',
                    50,
                    100,
                    pytest.approx(574.75),
                    pytest.approx(52184.5),
                    pytest.approx(53914.9105),
                    3,
                    pytest.approx(22.41525),
                    pytest.approx(22.41525),
                    pytest.approx(1382.9973149999998),
                    1.0,
                    'RUB',
                    enums.StatsType.PUSH.value,
                    pytest.approx(561.5),
                ],
            ],
            [
                [
                    'test_city',
                    'control',
                    50,
                    100,
                    0.0,
                    0.0,
                    0.0,
                    3,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    'RUB',
                    'push',
                    0.0,
                ],
            ],
            [
                [
                    'test_city',
                    'random',
                    50,
                    100,
                    0.0,
                    0.0,
                    0.0,
                    3,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    'RUB',
                    'push',
                    0.0,
                ],
            ],
            0,
            0,
        ),
    ),
)
async def test_get_segment_stats(
        stq3_context,
        load_json,
        stats_type,
        stats_columns,
        replace_columns,
        expected_results,
        expected_results_random,
        expected_results_control,
        control_share,
        random_share,
):
    elasticities = calc_segment_stats.get_elasticities(
        stq3_context, 'test_city', 'kt',
    )
    default_elasticity = elasticities[enums.StatsType.DEFAULT.value]
    push_elasticity = elasticities[enums.StatsType.PUSH.value]
    flat_elasticity = elasticities.get(
        enums.StatsType.FLAT.value, push_elasticity,
    )
    el_dict = {
        enums.StatsType.DEFAULT: default_elasticity,
        enums.StatsType.FLAT: flat_elasticity,
        enums.StatsType.PUSH: push_elasticity,
    }

    raw_segment_stats = pd.DataFrame(load_json('raw_stats.json'))
    segment_stats = raw_segment_stats[stats_columns]
    if replace_columns:
        segment_stats.rename(columns=replace_columns, inplace=True)
    loader = seg_loader.SegmentStatsGetter(stq3_context)
    elasticity = loader.get_elasticity(
        city='test_city',
        min_disc=0,
        max_disc=12,
        disc_step=3,
        elasticity_dict=el_dict[stats_type],
    )
    result = loader.get_segment_stats(
        segment_stats, elasticity, control_share, random_share, stats_type,
    )
    # drop doc column because it is unused column and can have rounding flaps
    result = result.drop('doc', axis=1)

    assert result.values.tolist()[1:2] == expected_results

    control_result = result[result.segment == 'control']
    assert control_result.values.tolist()[1:2] == expected_results_control

    random_result = result[result.segment == 'random']
    assert random_result.values.tolist()[1:2] == expected_results_random


@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_ELASTICITIES=conftest.ELASTICITIES_DICT,
    DISCOUNTS_OPERATION_CALCULATIONS_DISCOUNTS_RANGE={
        'default': {'max_disc': 30, 'min_disc': 0},
        'test_city': {'max_disc': 27, 'min_disc': 0},
    },
)
async def test_get_all_segment_stats(stq3_context, load_json):
    elasticities = calc_segment_stats.get_elasticities(
        stq3_context, 'test_city', 'kt',
    )
    default_elasticity = elasticities[enums.StatsType.DEFAULT.value]
    push_elasticity = elasticities[enums.StatsType.PUSH.value]
    flat_elasticity = elasticities.get(
        enums.StatsType.FLAT.value, push_elasticity,
    )
    job_config = helpers.JobConfig(
        fct_order_path='a',
        ma_users_raw_path='b',
        city_tz_mapping_path='c',
        discounts_city_mapping_path='d',
        result_path='e',
        currency_rate_path='f',
        geo_hierarchy_path='g',
        user_segments_path='h',
        selected_city='test_city',
        min_disc=0,
        max_disc=40,
        surge_limit=1.8,
        tariffs=['uberx', 'econom'],
        payment_types=['card', 'bitkoin', 'cash'],
        companies=['company1', 'company2'],
        total_executor_cores=80,
        disc_step=3,
        control_share=0.2,
        random_share=0.1,
        elasticity_dict=default_elasticity,
        push_elasticity_dict=push_elasticity,
        flat_elasticity_dict=flat_elasticity,
    )
    raw_segment_stats = pd.DataFrame(load_json('raw_stats.json'))
    loader = seg_loader.SegmentStatsGetter(stq3_context)
    result = await loader.get_all_segment_stats(raw_segment_stats, job_config)

    assert len(result) == 72
    assert result[:2] == [
        {
            'active_users': 505.35,
            'city': 'test_city',
            'currency_code': 'RUB',
            'currency_rate': 1.0,
            'discount': 0,
            'doc': (
                '{"active_users": 505.35, '
                '"gmv_low_surge": 39932.55, "new_gmv": '
                '46966.05, "extra_trips": 0.0}'
            ),
            'extra_trips': 0.0,
            'gmv': 46966.05,
            'metric': 0.0,
            'new_gmv': 46966.05,
            'price_from': 50,
            'price_to': 100,
            'segment': '2',
            'stats_type': 'default',
            'trips': 517.275,
            'weekly_budget': 0.0,
        },
        {
            'active_users': 505.35,
            'city': 'test_city',
            'currency_code': 'RUB',
            'currency_rate': 1.0,
            'discount': 3,
            'doc': (
                '{"active_users": 505.35, '
                '"gmv_low_surge": 39932.55, "new_gmv": '
                '49002.61005, "extra_trips": 26.381025}'
            ),
            'extra_trips': 26.381025,
            'gmv': 46966.05,
            'metric': 26.381025,
            'new_gmv': 49002.61005,
            'price_from': 50,
            'price_to': 100,
            'segment': '2',
            'stats_type': 'default',
            'trips': 517.275,
            'weekly_budget': 1259.0733015,
        },
    ]


@pytest.mark.now('2020-08-14 10:00:00')
@pytest.mark.pgsql(
    'discounts_operation_calculations',
    files=['fill_pg_suggests.sql', 'fill_pg_calc_segment_stats_tasks.sql'],
)
@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_DISCOUNTS_RANGE={
        'default': {'max_disc': 30, 'min_disc': 0},
        'test_city': {'max_disc': 27, 'min_disc': 0},
    },
    DISCOUNTS_OPERATION_CALCULATIONS_ALGORITHMS_CONFIGS={
        'kt': {
            'name': 'kt',
            'metric_name': 'test_metric_name',
            'algorithm_type': 'katusha',
            'max_absolute_value': 300,
            'max_value': 0.5,
            'min_value': 0.05,
            'discount_duration': 5,
            'classes': ['econom', 'uberx'],
            'disable_by_surge': 1.2,
            'payment_types': ['card'],
            'random_share': 10,
            'control_share': 20,
            'user_segment_path': '1',
            'second_metric_name': 'Цена дополнительного оффера',
        },
    },
    DISCOUNTS_OPERATION_CALCULATIONS_ELASTICITIES=conftest.ELASTICITIES_DICT,
    DISCOUNTS_OPERATION_CALCULATIONS_COMMON_CONFIG={
        'ma_users_path': 'a',
        'city_tz_mapping_path': 'b',
        'discounts_city_mapping_path': 'c',
    },
)
async def test_postprocess_segment_stats_stq(
        pgsql, submission_id, patch, mock_yt_client, stq3_context, load_json,
):
    @patch('discounts_operation_calculations.utils.spark_submit._spark_submit')
    async def _spark_submit(*args, **kwargs):
        return submission_id

    @patch('discounts_operation_calculations.utils.spark_submit.poll')
    async def _poll(*args, **kwargs):
        return 'FINISHED'

    @patch(
        'discounts_operation_calculations.internals.segment_stats_loader_v2.'
        'SegmentStatsLoader._load_from_yt',
    )
    async def _load_from_yt(*args, **kwargs):
        return load_json('raw_stats.json')

    task_id = 'a8d1e267b27949558980b157ac8e8d76'

    # Run calc_segment_stats stq task
    await calc_segment_stats.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id=task_id, exec_tries=0, reschedule_counter=0, queue='',
        ),
    )

    cursor = pgsql['discounts_operation_calculations'].cursor()
    cursor.execute(
        'SELECT '
        'suggest_id, algorithm_id, stats_type, trips, extra_trips, '
        'price_from, price_to, gmv, new_gmv, discount, city, segment, metric, '
        'weekly_budget, currency_code, currency_rate, active_users '
        'FROM discounts_operation_calculations.segment_stats_all '
        'ORDER BY segment, price_from desc, discount desc, stats_type',
    )

    res = list(cursor)
    assert len(res) == 72

    control_res = [row for row in res if row[-6] == 'control']
    assert len(control_res) == 18
    assert control_res[:2] == [
        (
            1,
            'kt',
            'default',
            112.75,
            5.412,
            100,
            150,
            33203.6,
            33864.428,
            6.0,
            'test_city',
            'control',
            5.412,
            865.68468,
            'RUB',
            1.0,
            223.4,
        ),
        (
            1,
            'kt',
            'flat',
            151.45,
            7.2696,
            100,
            150,
            33203.6,
            34136.5448,
            6.0,
            'test_city',
            'control',
            7.2696,
            1222.157688,
            'RUB',
            1.0,
            223.4,
        ),
    ]

    random_res = [row for row in res if row[-6] == 'random']
    assert len(random_res) == 18
    assert random_res[:2] == [
        (
            1,
            'kt',
            'default',
            56.375,
            2.706,
            100,
            150,
            16601.8,
            16932.214,
            6.0,
            'test_city',
            'random',
            2.706,
            432.84234,
            'RUB',
            1.0,
            111.7,
        ),
        (
            1,
            'kt',
            'flat',
            75.725,
            3.6348,
            100,
            150,
            16601.8,
            17068.2724,
            6.0,
            'test_city',
            'random',
            3.6348,
            611.078844,
            'RUB',
            1.0,
            111.7,
        ),
    ]
