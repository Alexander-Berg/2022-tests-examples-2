# pylint: disable=import-only-modules

import pytest

from tests_eats_report_storage.widgets.utils import consts
from tests_eats_report_storage.widgets.utils import helpers


@pytest.mark.now('2022-02-22T03:00')
@pytest.mark.parametrize(
    'widget_slug, preset_period_type, charts_len, points_len',
    [
        ('plus_orders_count', 'week', 2, 4),
        ('plus_orders_count', 'month', 2, 1),
        ('plus_orders_count', 'year', 2, 1),
        ('plus_gmv_lcy', 'week', 2, 4),
        ('plus_gmv_lcy', 'month', 2, 1),
        ('plus_gmv_lcy', 'year', 2, 1),
        ('plus_gmv_lcy_line_with_delta', 'week', 1, 4),
        ('plus_gmv_lcy_line_with_delta', 'month', 1, 1),
        ('plus_gmv_lcy_line_with_delta', 'year', 1, 1),
        ('plus_frequency_val', 'year', 2, 1),
    ],
)
@pytest.mark.pgsql(
    'eats_report_storage', files=('eats_report_storage_metrics_data.sql',),
)
async def test_return_metrics_for_preset_period_type(
        taxi_eats_report_storage,
        mock_authorizer_200,
        mock_core_places_info_request,
        pgsql,
        widget_slug,
        preset_period_type,
        charts_len,
        points_len,
):
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
        json={
            'widget_slug': widget_slug,
            'places': [1],
            'preset_period_type': preset_period_type,
        },
    )

    helpers.check_data_count(
        response.json()['payload'], charts_len, points_len,
    )


@pytest.mark.now('2021-11-11T03:00:00Z+03')
@pytest.mark.parametrize(
    'widget_slug, charts_len, status, metrics_total_value, '
    'metrics_delta_value, metrics_values, html, total_value,'
    'restapp_link, extra_content',
    [
        (
            'plus_orders_count',
            2,
            ['active', 'partly_active', 'inactive'],
            ['6 000', '6 600'],
            ['2 000', '2 200'],
            [[1000, 1100], [2000, 2200], [3000, 3300]],
            None,
            None,
            None,
            None,
        ),
        pytest.param(
            'plus_gmv_lcy',
            2,
            ['active', 'partly_active', 'inactive'],
            ['601.33 ¥', '661.01 ₽'],
            ['200.56 ¥', '221 ₽'],
            [[100.11, 110], [200.56, 220.01], [300.67, 331]],
            '<h1>За выбранный период оборот от клиентов с Плюсом составил 601.33&nbsp;¥</h1>\nНачислено баллов: 7\nСписано баллов: 6&nbsp;000',  # noqa: E501
            '601.33 ¥',
            {'text': 'Перейти в раздел Плюса', 'slug': 'place_plus_manage'},
            {
                'main_text': 'За выбранный период оборот от клиентов с Плюсом составил 601.33 ¥',  # noqa: E501
                'extra_text': (
                    'Начислено баллов: 7\n' 'Списано баллов: 6 000'
                ),
                'links': [
                    {
                        'text': 'Перейти в раздел Плюса',
                        'slug': 'place_plus_manage',
                    },
                ],
                'button': {
                    'text': 'Статистика по баллам',
                    'slug': 'place_plus_stats',
                },
            },
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_PLUS_WIDGETS={
                        'widgets': [
                            {
                                'chart_type': 'bar_stacked',
                                'description': (
                                    'Сумма всех чеков за период по заказам'
                                ),
                                'extra_content': {
                                    'button': {
                                        'slug': 'place_plus_stats',
                                        'text': 'Статистика по баллам',
                                    },
                                    'extra_text': 'Начислено баллов: {cashback_by_place_lcy_total}\nСписано баллов: {cashback_spent_by_user_lcy_total}',  # noqa: E501
                                    'links': [
                                        {
                                            'slug': 'place_plus_manage',
                                            'text': 'Перейти в раздел Плюса',
                                        },
                                    ],
                                    'main_text': 'За выбранный период оборот от клиентов с Плюсом составил {plus_user_w_plus_gmv_lcy_total}',  # noqa: E501
                                },
                                'html': '<h1>За выбранный период оборот от клиентов с Плюсом составил {plus_user_w_plus_gmv_lcy_total}</h1>\nНачислено баллов: {cashback_by_place_lcy_total}\nСписано баллов: {cashback_spent_by_user_lcy_total}',  # noqa: E501
                                'metric_id_for_total_value': (
                                    'plus_user_w_plus_gmv_lcy'
                                ),
                                'metrics': [
                                    'plus_user_w_plus_gmv_lcy',
                                    'plus_user_wo_plus_gmv_lcy',
                                ],
                                'restapp_link': {
                                    'slug': 'place_plus_manage',
                                    'text': 'Перейти в раздел Плюса',
                                },
                                'stretch_to_full_width': True,
                                'title': 'Выручка',
                                'widget_id': 'plus_gmv_lcy',
                                'widget_type': 'widget_basic_chart',
                            },
                        ],
                    },
                ),
            ],
            id='extra_content_without',
        ),
        pytest.param(
            'plus_gmv_lcy',
            2,
            ['active', 'partly_active', 'inactive'],
            ['601.33 ¥', '661.01 ₽'],
            ['200.56 ¥', '221 ₽'],
            [[100.11, 110], [200.56, 220.01], [300.67, 331]],
            '<h1>За выбранный период оборот от клиентов с Плюсом составил 601.33&nbsp;¥</h1>\nНачислено баллов: 7\nСписано баллов: 6&nbsp;000',  # noqa: E501
            '601.33 ¥',
            {'text': 'Перейти в раздел Плюса', 'slug': 'place_plus_manage'},
            {
                'main_text': 'За выбранный период оборот от клиентов с Плюсом составил 601.33 ¥',  # noqa: E501
                'extra_text': (
                    'Начислено баллов: 7\n' 'Списано баллов: 6 000'
                ),
                'links': [
                    {
                        'text': 'Перейти в раздел Плюса',
                        'slug': 'place_plus_manage',
                    },
                ],
                'button': {
                    'text': 'Статистика по баллам',
                    'slug': 'place_plus_stats',
                },
            },
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_PLUS_WIDGETS={
                        'widgets': [
                            {
                                'chart_type': 'bar_stacked',
                                'description': (
                                    'Сумма всех чеков за период по заказам'
                                ),
                                'extra_content': {
                                    'button': {
                                        'slug': 'place_plus_stats',
                                        'text': 'Статистика по баллам',
                                    },
                                    'extra_text': (
                                        'template:plus_gmv_lcy_extra_text'
                                    ),
                                    'links': [
                                        {
                                            'slug': 'place_plus_manage',
                                            'text': 'Перейти в раздел Плюса',
                                        },
                                    ],
                                    'main_text': (
                                        'template:plus_gmv_lcy_main_text'
                                    ),
                                },
                                'html': '<h1>За выбранный период оборот от клиентов с Плюсом составил {plus_user_w_plus_gmv_lcy_total}</h1>\nНачислено баллов: {cashback_by_place_lcy_total}\nСписано баллов: {cashback_spent_by_user_lcy_total}',  # noqa: E501
                                'metric_id_for_total_value': (
                                    'plus_user_w_plus_gmv_lcy'
                                ),
                                'metrics': [
                                    'plus_user_w_plus_gmv_lcy',
                                    'plus_user_wo_plus_gmv_lcy',
                                ],
                                'restapp_link': {
                                    'slug': 'place_plus_manage',
                                    'text': 'Перейти в раздел Плюса',
                                },
                                'stretch_to_full_width': True,
                                'title': 'Выручка',
                                'widget_id': 'plus_gmv_lcy',
                                'widget_type': 'widget_basic_chart',
                            },
                        ],
                    },
                ),
            ],
            id='extra_content_with_templater',
        ),
        (
            'plus_gmv_lcy_line_with_delta',
            1,
            ['active', 'partly_active', 'inactive'],
            ['601.33 ¥'],
            ['200.56 ¥'],
            [[100.11], [200.56], [300.67]],
            None,
            None,
            None,
            None,
        ),
        (
            'plus_frequency_val',
            2,
            ['active', 'partly_active', 'inactive'],
            ['30 000', '33 000'],
            ['20 000', '22 000'],
            [[10000, 11000], [20000, 22000], [30000, 33000]],
            None,
            None,
            None,
            None,
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_report_storage', files=('eats_report_storage_metrics_data.sql',),
)
async def test_return_metrics_for_custom_period(
        taxi_eats_report_storage,
        mock_authorizer_200,
        mock_core_places_info_request,
        pgsql,
        widget_slug,
        charts_len,
        status,
        metrics_total_value,
        metrics_delta_value,
        metrics_values,
        html,
        total_value,
        restapp_link,
        extra_content,
):
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
        json={
            'widget_slug': widget_slug,
            'places': [1],
            'preset_period_type': 'custom',
            'period_begin': '2015-06-10T00:00:00+00:00',
            'period_end': '2015-08-20T00:00:00+00:00',
        },
    )

    helpers.check_data_count(response.json()['payload'], charts_len, 3)
    helpers.check_data(
        response.json()['payload'],
        status,
        metrics_total_value,
        metrics_delta_value,
        metrics_values,
        html,
        total_value,
        restapp_link,
        extra_content,
    )
