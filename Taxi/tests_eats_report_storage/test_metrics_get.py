# flake8: noqa
# pylint: disable=redefined-outer-name, import-only-modules, too-many-lines

import pytest
from .conftest import exp3_config_metrics, exp3_config_switch_flag

PARTNER_ID = 1

PLACE_IDS = [1, 2]

CONFIG_METRIC_GMV_LCY = {
    'metric_id': 'plus_user_w_plus_gmv_lcy',
    'granularity': ['day', 'week', 'month'],
    'periods': ['week', 'month', 'year', 'custom', 'all_time'],
    'permissions': ['permission.stats.plus', 'other_permission'],
    'name': 'template:users_with_plus',
    'data_key': 'plus_user_w_plus_gmv_lcy',
    'value_unit_sign': '₽',
    'simbols_after_comma': 1,
    'reference_value': {
        'bad_template': 'плохое значение без шаблона',
        'good_template': 'хорошее значение без шаблона',
        'value': 31.5,
    },
}

CONFIG_METRIC_ORDER_CNT = {
    'metric_id': 'plus_user_wo_plus_order_cnt',
    'granularity': ['day', 'week', 'month'],
    'periods': ['week', 'month', 'year', 'custom', 'all_time'],
    'permissions': ['permission.stats.plus', 'other_permission'],
    'name': 'Пользователи без Плюса',
    'data_key': 'plus_user_wo_plus_order_cnt',
    'inverse': True,
    'reference_value': {
        'bad_template': 'template:metric_reference_bad',
        'good_template': 'template:metric_reference_good',
        'value': 35000,
    },
}

CONFIG_METRICS = {'metrics': [CONFIG_METRIC_GMV_LCY, CONFIG_METRIC_ORDER_CNT]}

CONFIG_TEMPLATER = {
    'templates': [
        {'slug': 'users_with_plus', 'template': 'Пользователи с Плюсом'},
        {
            'slug': 'metric_reference_bad',
            'template': 'плохое значение с шаблоном',
        },
        {
            'slug': 'metric_reference_good',
            'template': 'хорошее значение с шаблоном',
        },
    ],
}

EXPECT_RESPONSE = [
    {
        'place_id': 1,
        'metrics': [
            {
                'data_key': 'plus_user_w_plus_gmv_lcy',
                'name': 'Пользователи с Плюсом',
                'value_unit_sign': '₽',
                'total_value': {'title': '29.7 ₽', 'value': 29.7},
                'delta_value': {'title': '5.5 ₽', 'value': 5.5},
                'inverse': False,
                'reference_value': {
                    'title': 'плохое значение без шаблона',
                    'value': 31.5,
                },
                'points_data': [
                    {
                        'status': 'active',
                        'value': 2.2,
                        'title': '2.2',
                        'dt_from': '2021-09-10T00:00:00+00:00',
                        'dt_to': '2021-09-10T00:00:00+00:00',
                        'xlabel': '10.09',
                    },
                    {
                        'status': 'active',
                        'value': 3.3,
                        'title': '3.3',
                        'dt_from': '2021-09-11T00:00:00+00:00',
                        'dt_to': '2021-09-11T00:00:00+00:00',
                        'xlabel': '11.09',
                    },
                    {
                        'status': 'active',
                        'value': 4.4,
                        'title': '4.4',
                        'dt_from': '2021-09-12T00:00:00+00:00',
                        'dt_to': '2021-09-12T00:00:00+00:00',
                        'xlabel': '12.09',
                    },
                    {
                        'status': 'active',
                        'value': 5.5,
                        'title': '5.5',
                        'dt_from': '2021-09-13T00:00:00+00:00',
                        'dt_to': '2021-09-13T00:00:00+00:00',
                        'xlabel': '13.09',
                    },
                    {
                        'status': 'active',
                        'value': 6.6,
                        'title': '6.6',
                        'dt_from': '2021-09-14T00:00:00+00:00',
                        'dt_to': '2021-09-14T00:00:00+00:00',
                        'xlabel': '14.09',
                    },
                    {
                        'status': 'active',
                        'value': 7.7,
                        'title': '7.7',
                        'dt_from': '2021-09-15T00:00:00+00:00',
                        'dt_to': '2021-09-15T00:00:00+00:00',
                        'xlabel': '15.09',
                    },
                ],
            },
            {
                'data_key': 'plus_user_wo_plus_order_cnt',
                'name': 'Пользователи без Плюса',
                'total_value': {'title': '27 000', 'value': 27000.0},
                'delta_value': {'title': '5 000', 'value': 5000.0},
                'inverse': True,
                'reference_value': {
                    'title': 'хорошее значение с шаблоном',
                    'value': 35000.0,
                },
                'points_data': [
                    {
                        'status': 'active',
                        'value': 2000.0,
                        'title': '2 000',
                        'dt_from': '2021-09-10T00:00:00+00:00',
                        'dt_to': '2021-09-10T00:00:00+00:00',
                        'xlabel': '10.09',
                    },
                    {
                        'status': 'active',
                        'value': 3000.0,
                        'title': '3 000',
                        'dt_from': '2021-09-11T00:00:00+00:00',
                        'dt_to': '2021-09-11T00:00:00+00:00',
                        'xlabel': '11.09',
                    },
                    {
                        'status': 'active',
                        'value': 4000.0,
                        'title': '4 000',
                        'dt_from': '2021-09-12T00:00:00+00:00',
                        'dt_to': '2021-09-12T00:00:00+00:00',
                        'xlabel': '12.09',
                    },
                    {
                        'status': 'active',
                        'value': 5000.0,
                        'title': '5 000',
                        'dt_from': '2021-09-13T00:00:00+00:00',
                        'dt_to': '2021-09-13T00:00:00+00:00',
                        'xlabel': '13.09',
                    },
                    {
                        'status': 'active',
                        'value': 6000.0,
                        'title': '6 000',
                        'dt_from': '2021-09-14T00:00:00+00:00',
                        'dt_to': '2021-09-14T00:00:00+00:00',
                        'xlabel': '14.09',
                    },
                    {
                        'status': 'active',
                        'value': 7000.0,
                        'title': '7 000',
                        'dt_from': '2021-09-15T00:00:00+00:00',
                        'dt_to': '2021-09-15T00:00:00+00:00',
                        'xlabel': '15.09',
                    },
                ],
            },
        ],
    },
    {
        'place_id': 2,
        'metrics': [
            {
                'data_key': 'plus_user_w_plus_gmv_lcy',
                'name': 'Пользователи с Плюсом',
                'value_unit_sign': '₽',
                'total_value': {'title': '46.5 ₽', 'value': 46.5},
                'delta_value': {'title': '3 ₽', 'value': 3.0},
                'inverse': False,
                'points_data': [
                    {
                        'status': 'active',
                        'value': 10.1,
                        'title': '10.1',
                        'dt_from': '2021-09-01T00:00:00+00:00',
                        'dt_to': '2021-09-01T00:00:00+00:00',
                        'xlabel': '01.09',
                    },
                    {
                        'status': 'active',
                        'value': 11.1,
                        'title': '11.1',
                        'dt_from': '2021-09-02T00:00:00+00:00',
                        'dt_to': '2021-09-02T00:00:00+00:00',
                        'xlabel': '02.09',
                    },
                    {
                        'status': 'active',
                        'value': 12.1,
                        'title': '12.1',
                        'dt_from': '2021-09-03T00:00:00+00:00',
                        'dt_to': '2021-09-03T00:00:00+00:00',
                        'xlabel': '03.09',
                    },
                    {
                        'status': 'active',
                        'value': 13.1,
                        'title': '13.1',
                        'dt_from': '2021-09-04T00:00:00+00:00',
                        'dt_to': '2021-09-04T00:00:00+00:00',
                        'xlabel': '04.09',
                    },
                ],
                'reference_value': {
                    'title': 'хорошее значение без шаблона',
                    'value': 31.5,
                },
            },
            {
                'data_key': 'plus_user_wo_plus_order_cnt',
                'name': 'Пользователи без Плюса',
                'total_value': {'title': '46 000', 'value': 46000.0},
                'delta_value': {'title': '3 000', 'value': 3000.0},
                'inverse': True,
                'points_data': [
                    {
                        'status': 'active',
                        'value': 10000.0,
                        'title': '10 000',
                        'dt_from': '2021-09-01T00:00:00+00:00',
                        'dt_to': '2021-09-01T00:00:00+00:00',
                        'xlabel': '01.09',
                    },
                    {
                        'status': 'active',
                        'value': 11000.0,
                        'title': '11 000',
                        'dt_from': '2021-09-02T00:00:00+00:00',
                        'dt_to': '2021-09-02T00:00:00+00:00',
                        'xlabel': '02.09',
                    },
                    {
                        'status': 'active',
                        'value': 12000.0,
                        'title': '12 000',
                        'dt_from': '2021-09-03T00:00:00+00:00',
                        'dt_to': '2021-09-03T00:00:00+00:00',
                        'xlabel': '03.09',
                    },
                    {
                        'status': 'active',
                        'value': 13000.0,
                        'title': '13 000',
                        'dt_from': '2021-09-04T00:00:00+00:00',
                        'dt_to': '2021-09-04T00:00:00+00:00',
                        'xlabel': '04.09',
                    },
                ],
                'reference_value': {
                    'title': 'плохое значение с шаблоном',
                    'value': 35000.0,
                },
            },
        ],
    },
]


@pytest.mark.config(
    EATS_REPORT_STORAGE_PLUS_METRICS=CONFIG_METRICS,
    EATS_REPORT_STORAGE_TEXT_TEMPLATER=CONFIG_TEMPLATER,
)
@pytest.mark.pgsql(
    'eats_report_storage', files=('eats_report_storage_metrics_data.sql',),
)
async def test_service_return_metrics_data(taxi_eats_report_storage):
    response = await taxi_eats_report_storage.post(
        '/internal/place-metrics/metrics/get',
        json={
            'metrics': [
                'plus_user_w_plus_gmv_lcy',
                'plus_user_wo_plus_order_cnt',
            ],
            'places': [
                {
                    'place_id': 1,
                    'period_begin': '2021-09-10T03:00:00+03:00',
                    'period_end': '2021-09-15T03:00:00+03:00',
                },
                {
                    'place_id': 2,
                    'period_begin': '2021-09-01T03:00:00+03:00',
                    'period_end': '2021-09-04T03:00:00+03:00',
                },
            ],
        },
    )

    assert response.json()['payload'] == EXPECT_RESPONSE


@pytest.mark.config(EATS_REPORT_STORAGE_PLUS_METRICS=CONFIG_METRICS)
async def test_service_return_404_for_unknown_metric(taxi_eats_report_storage):
    response = await taxi_eats_report_storage.post(
        '/internal/place-metrics/metrics/get',
        json={
            'metrics': [
                'plus_user_w_plus_gmv_lcy',
                'plus_user_wo_plus_order_cnt',
                'unknown_metric',
            ],
            'places': [
                {
                    'place_id': 1,
                    'period_begin': '2021-09-10T03:00:00+03:00',
                    'period_end': '2021-09-15T03:00:00+03:00',
                },
                {
                    'place_id': 2,
                    'period_begin': '2021-09-01T03:00:00+03:00',
                    'period_end': '2021-09-04T03:00:00+03:00',
                },
            ],
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Unexpected metric \'unknown_metric\'',
    }


@pytest.mark.config(EATS_REPORT_STORAGE_TEXT_TEMPLATER=CONFIG_TEMPLATER)
@pytest.mark.pgsql(
    'eats_report_storage', files=('eats_report_storage_metrics_data.sql',),
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_PLUS_METRICS=CONFIG_METRICS,
                ),
                exp3_config_switch_flag('old'),
            ],
            id='metrics_only_old_config_old',
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_PLUS_METRICS=CONFIG_METRICS,
                ),
                exp3_config_switch_flag('merge'),
            ],
            id='metrics_only_old_config_merge',
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_PLUS_METRICS=CONFIG_METRICS,
                ),
                exp3_config_metrics(
                    [
                        ('plus_user_w_plus_gmv_lcy', CONFIG_METRIC_GMV_LCY),
                        (
                            'plus_user_wo_plus_order_cnt',
                            CONFIG_METRIC_ORDER_CNT,
                        ),
                    ],
                ),
                exp3_config_switch_flag('merge'),
            ],
            id='metrics_everywhere_in_configs_merge',
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_PLUS_METRICS=CONFIG_METRICS,
                ),
                exp3_config_metrics(
                    [
                        ('plus_user_w_plus_gmv_lcy', CONFIG_METRIC_GMV_LCY),
                        (
                            'plus_user_wo_plus_order_cnt',
                            CONFIG_METRIC_ORDER_CNT,
                        ),
                    ],
                ),
                exp3_config_switch_flag('old'),
            ],
            id='metrics_everywhere_in_configs_old',
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_PLUS_METRICS=CONFIG_METRICS,
                ),
                exp3_config_metrics(
                    [
                        ('plus_user_w_plus_gmv_lcy', CONFIG_METRIC_GMV_LCY),
                        (
                            'plus_user_wo_plus_order_cnt',
                            CONFIG_METRIC_ORDER_CNT,
                        ),
                    ],
                ),
                exp3_config_switch_flag('new'),
            ],
            id='metrics_everywhere_in_configs_new',
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_PLUS_METRICS={
                        'metrics': [CONFIG_METRIC_GMV_LCY],
                    },
                ),
                exp3_config_metrics(
                    [('plus_user_wo_plus_order_cnt', CONFIG_METRIC_ORDER_CNT)],
                ),
                exp3_config_switch_flag('merge'),
            ],
            id='metrics_merge_configs',
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_PLUS_METRICS={
                        'metrics': [CONFIG_METRIC_ORDER_CNT],
                    },
                ),
                exp3_config_metrics(
                    [('plus_user_w_plus_gmv_lcy', CONFIG_METRIC_GMV_LCY)],
                ),
                exp3_config_switch_flag('merge'),
            ],
            id='metrics_merge_configs_2',
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_PLUS_METRICS={'metrics': []},
                ),
                exp3_config_metrics(
                    [
                        ('plus_user_w_plus_gmv_lcy', CONFIG_METRIC_GMV_LCY),
                        (
                            'plus_user_wo_plus_order_cnt',
                            CONFIG_METRIC_ORDER_CNT,
                        ),
                    ],
                ),
                exp3_config_switch_flag('merge'),
            ],
            id='metrics_only_config30_merge',
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_PLUS_METRICS={'metrics': []},
                ),
                exp3_config_metrics(
                    [
                        ('plus_user_w_plus_gmv_lcy', CONFIG_METRIC_GMV_LCY),
                        (
                            'plus_user_wo_plus_order_cnt',
                            CONFIG_METRIC_ORDER_CNT,
                        ),
                    ],
                ),
                exp3_config_switch_flag('new'),
            ],
            id='metrics_only_config30_new',
        ),
    ],
)
async def test_get_metrics_with_conf3(taxi_eats_report_storage):
    response = await taxi_eats_report_storage.post(
        '/internal/place-metrics/metrics/get',
        json={
            'metrics': [
                'plus_user_w_plus_gmv_lcy',
                'plus_user_wo_plus_order_cnt',
            ],
            'places': [
                {
                    'place_id': 1,
                    'period_begin': '2021-09-10T03:00:00+03:00',
                    'period_end': '2021-09-15T03:00:00+03:00',
                },
                {
                    'place_id': 2,
                    'period_begin': '2021-09-01T03:00:00+03:00',
                    'period_end': '2021-09-04T03:00:00+03:00',
                },
            ],
        },
    )

    assert response.json()['payload'] == EXPECT_RESPONSE
