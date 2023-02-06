# pylint: disable=import-only-modules

import pytest

from tests_eats_report_storage.conftest import exp3_config_sections
from tests_eats_report_storage.conftest import exp3_config_switch_flag
from tests_eats_report_storage.widgets.utils import consts


MOCKS_CONFIG = {'widgets_list_mock': False, 'widget_get_mock': False}

CONFIG_PERIODS = {
    'periods': [
        {'period_type': 'week', 'available_granularity': ['day']},
        {'period_type': 'month', 'available_granularity': ['day', 'week']},
        {'period_type': 'year', 'available_granularity': ['month']},
    ],
}

CONFIG_SECTIONS = {
    'sections': [
        {'name': 'plus', 'widgets': ['plus_orders_count', 'plus_ltv_lcy']},
        {'name': 'advert', 'widgets': ['plus_gmv_lcy', 'plus_new_user']},
    ],
}

CONFIG_METRICS = {
    'metrics': [
        {
            'metric_id': 'metric1',
            'granularity': ['day', 'week', 'month'],
            'periods': ['week', 'month', 'year', 'custom'],
            'permissions': ['permission1'],
            'name': 'Name1',
            'data_key': 'metric1',
        },
        {
            'metric_id': 'metric2',
            'granularity': ['day', 'week', 'month'],
            'periods': ['week', 'month', 'year', 'custom'],
            'permissions': ['permission1', 'other_permission'],
            'name': 'Name2',
            'data_key': 'metric2',
        },
        {
            'metric_id': 'metric3',
            'granularity': ['day', 'week', 'month'],
            'periods': ['week', 'month', 'year', 'custom'],
            'permissions': ['other_permission'],
            'name': 'Name3',
            'data_key': 'metric3',
        },
    ],
}

CONFIG_WIDGETS = {
    'widgets': [
        {
            'widget_id': 'plus_orders_count',
            'metrics': ['metric1', 'metric2'],
            'title': 'Заказы',
            'description': 'Все заказы за период',
            'stretch_to_full_width': False,
            'chart_type': 'bar_stacked',
            'widget_type': 'widget_basic_chart',
        },
        {
            'widget_id': 'plus_gmv_lcy',
            'metrics': ['metric1'],
            'title': 'Выручка',
            'description': 'Сумма всех чеков за период по заказам',
            'stretch_to_full_width': True,
            'chart_type': 'bar_stacked',
            'widget_type': 'widget_basic_chart',
            'restapp_link': {
                'text': 'Перейти в раздел Плюса',
                'slug': 'place_plus_manage',
            },
        },
        {
            'widget_id': 'plus_ltv_lcy',
            'metrics': ['metric2', 'metric3'],
            'title': 'Пожизненная стоимость',
            'description': (
                'Выручка на одного пользователя, '
                'которую он принесёт за всё время '
                'заказов в этом ресторане'
            ),
            'stretch_to_full_width': False,
            'chart_type': 'line',
            'widget_type': 'widget_basic_chart',
        },
        {
            'widget_id': 'plus_new_user',
            'metrics': [],
            'title': 'Рекурсивный виджет',
            'description': 'Проверяем вложенные виджеты в ручке списка',
            'stretch_to_full_width': False,
            'chart_type': 'no_data',
            'widget_type': 'recursive',
            'layout': {
                'desktop': [['plus_gmv_lcy', 'plus_ltv_lcy']],
                'mobile': [['plus_gmv_lcy'], ['plus_ltv_lcy']],
            },
        },
    ],
}

CONFIG_PROMO_SECTIONS = {
    'sections': [
        {
            'name': 'promo',
            'widgets': [
                'promo_orders_number_value',
                'promo_mean_receipt_value',
                'promo_proceeds_value',
                'promo_new_users_value',
                'promo_proceeds',
                'promo_orders_number',
                'promo_mean_receipts',
                'promo_new_users',
                'promo_conversion',
            ],
        },
    ],
}

CONFIG_PROMO_METRICS = {
    'metrics': [
        {
            'data_key': 'promo_orders_number',
            'granularity': ['day', 'week', 'month'],
            'metric_id': 'promo_orders_number',
            'name': 'Количество заказов',
            'periods': ['week', 'month', 'year', 'custom'],
            'permissions': ['permission.promo.status'],
        },
        {
            'data_key': 'promo_mean_receipts',
            'granularity': ['day', 'week', 'month'],
            'metric_id': 'promo_mean_receipts',
            'name': 'Средний чек',
            'periods': ['week', 'month', 'year', 'custom'],
            'permissions': ['permission.promo.status'],
            'value_unit_sign': '₽',
        },
        {
            'data_key': 'promo_proceeds',
            'granularity': ['day', 'week', 'month'],
            'metric_id': 'promo_proceeds',
            'name': 'Выручка',
            'periods': ['week', 'month', 'year', 'custom'],
            'permissions': ['permission.promo.status'],
            'value_unit_sign': '₽',
        },
        {
            'data_key': 'promo_new_users',
            'granularity': ['day', 'week', 'month'],
            'metric_id': 'promo_new_users',
            'name': 'Новые пользователи',
            'periods': ['week', 'month', 'year', 'custom'],
            'permissions': ['permission.promo.status'],
        },
        {
            'data_key': 'promo_conversion',
            'granularity': ['day', 'week', 'month'],
            'metric_id': 'promo_conversion',
            'name': 'Конверсия',
            'periods': ['week', 'month', 'year', 'custom'],
            'permissions': ['permission.promo.status'],
        },
        {
            'data_key': 'orders_number',
            'granularity': ['day', 'week', 'month'],
            'metric_id': 'orders_number',
            'name': 'Количество заказов',
            'periods': ['week', 'month', 'year', 'custom'],
            'permissions': ['permission.promo.status'],
        },
        {
            'data_key': 'mean_receipts',
            'granularity': ['day', 'week', 'month'],
            'metric_id': 'mean_receipts',
            'name': 'Средний чек',
            'periods': ['week', 'month', 'year', 'custom'],
            'permissions': ['permission.promo.status'],
            'value_unit_sign': '₽',
        },
        {
            'data_key': 'proceeds',
            'granularity': ['day', 'week', 'month'],
            'metric_id': 'proceeds',
            'name': 'Выручка',
            'periods': ['week', 'month', 'year', 'custom'],
            'permissions': ['permission.promo.status'],
            'value_unit_sign': '₽',
        },
        {
            'data_key': 'new_users',
            'granularity': ['day', 'week', 'month'],
            'metric_id': 'new_users',
            'name': 'Новые пользователи',
            'periods': ['week', 'month', 'year', 'custom'],
            'permissions': ['permission.promo.status'],
        },
        {
            'data_key': 'conversion',
            'granularity': ['day', 'week', 'month'],
            'metric_id': 'conversion',
            'name': 'Конверсия',
            'periods': ['week', 'month', 'year', 'custom'],
            'permissions': ['permission.promo.status'],
        },
    ],
}

CONFIG_PROMO_WIDGETS = {
    'widgets': [
        {
            'chart_type': 'sum_value',
            'description': 'Заказы за период',
            'metrics': ['promo_orders_number'],
            'title': 'Количество заказов',
            'widget_id': 'promo_orders_number_value',
        },
        {
            'chart_type': 'sum_value',
            'description': 'Сумма всех чеков за период по заказам',
            'metrics': ['promo_proceeds'],
            'title': 'Выручка',
            'widget_id': 'promo_proceeds_value',
        },
        {
            'chart_type': 'sum_value',
            'description': 'Средний чек',
            'metrics': ['promo_mean_receipts'],
            'title': 'Средний чек',
            'widget_id': 'promo_mean_receipt_value',
        },
        {
            'chart_type': 'sum_value',
            'description': 'Всего новых пользователей сделавших заказ во время проведения акции',  # noqa: E501
            'metrics': ['promo_new_users'],
            'title': 'Новые пользователи',
            'widget_id': 'promo_new_users_value',
        },
        {
            'chart_type': 'bar_stacked',
            'description': 'Выручка за период',
            'metrics': ['promo_proceeds', 'proceeds'],
            'title': 'Выручка',
            'widget_id': 'promo_proceeds',
        },
        {
            'chart_type': 'line',
            'description': 'Количество заказов за период',
            'metrics': ['promo_orders_number', 'orders_number'],
            'title': 'Количество заказов',
            'widget_id': 'promo_orders_number',
        },
        {
            'chart_type': 'line',
            'description': 'Средний чек за период',
            'metrics': ['promo_mean_receipts', 'mean_receipts'],
            'title': 'Средний чек',
            'widget_id': 'promo_mean_receipts',
        },
        {
            'chart_type': 'bar_stacked',
            'description': 'Новые пользователи за период',
            'metrics': ['promo_new_users', 'new_users'],
            'title': 'Новые пользователи',
            'widget_id': 'promo_new_users',
        },
        {
            'chart_type': 'line',
            'description': 'Конверсия новых пользователй',
            'metrics': ['promo_conversion', 'conversion'],
            'title': 'Конверсия',
            'widget_id': 'promo_conversion',
        },
    ],
}


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_PERIODS=CONFIG_PERIODS,
                    EATS_REPORT_STORAGE_SECTIONS=CONFIG_SECTIONS,
                    EATS_REPORT_STORAGE_PLUS_WIDGETS=CONFIG_WIDGETS,
                    EATS_REPORT_STORAGE_PLUS_METRICS=CONFIG_METRICS,
                ),
            ],
            id='standart',
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_PERIODS=CONFIG_PERIODS,
                    EATS_REPORT_STORAGE_SECTIONS=CONFIG_SECTIONS,
                    EATS_REPORT_STORAGE_PLUS_WIDGETS=CONFIG_WIDGETS,
                    EATS_REPORT_STORAGE_PLUS_METRICS=CONFIG_METRICS,
                ),
                exp3_config_switch_flag('old'),
            ],
            id='conf_on_switch_old',
        ),
        pytest.param(
            marks=[
                exp3_config_sections(CONFIG_SECTIONS),
                pytest.mark.config(
                    EATS_REPORT_STORAGE_PERIODS=CONFIG_PERIODS,
                    EATS_REPORT_STORAGE_SECTIONS={'sections': []},
                    EATS_REPORT_STORAGE_PLUS_WIDGETS=CONFIG_WIDGETS,
                    EATS_REPORT_STORAGE_PLUS_METRICS=CONFIG_METRICS,
                ),
                exp3_config_switch_flag('merge'),
            ],
            id='conf_on_switch_merge',
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_PERIODS=CONFIG_PERIODS,
                    EATS_REPORT_STORAGE_SECTIONS=CONFIG_SECTIONS,
                    EATS_REPORT_STORAGE_PLUS_WIDGETS=CONFIG_WIDGETS,
                    EATS_REPORT_STORAGE_PLUS_METRICS=CONFIG_METRICS,
                ),
                exp3_config_sections(CONFIG_SECTIONS),
                exp3_config_switch_flag('merge'),
            ],
            id='conf_on_switch_merge_all',
        ),
        pytest.param(
            marks=[
                pytest.mark.config(
                    EATS_REPORT_STORAGE_PERIODS=CONFIG_PERIODS,
                    EATS_REPORT_STORAGE_SECTIONS=CONFIG_SECTIONS,
                    EATS_REPORT_STORAGE_PLUS_WIDGETS=CONFIG_WIDGETS,
                    EATS_REPORT_STORAGE_PLUS_METRICS=CONFIG_METRICS,
                ),
                exp3_config_sections(CONFIG_SECTIONS),
                exp3_config_switch_flag('old'),
            ],
            id='conf_on_switch_on_old',
        ),
    ],
)
async def test_service_return_all_widgets_if_authorizer_response_ok(
        taxi_eats_report_storage, mock_authorizer_200,
):
    response = await taxi_eats_report_storage.get(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/list',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
    )
    expected_response = {
        'payload': [
            {
                'section': 'advert',
                'widgets': [
                    {
                        'chart_type': 'bar_stacked',
                        'description': 'Сумма всех чеков за период по заказам',
                        'stretch_to_full_width': True,
                        'title': 'Выручка',
                        'widget_slug': 'plus_gmv_lcy',
                        'widget_type': 'widget_basic_chart',
                        'restapp_link': {
                            'text': 'Перейти в раздел Плюса',
                            'slug': 'place_plus_manage',
                        },
                    },
                    {
                        'chart_type': 'no_data',
                        'description': (
                            'Проверяем вложенные виджеты в ручке списка'
                        ),
                        'stretch_to_full_width': False,
                        'title': 'Рекурсивный виджет',
                        'widget_slug': 'plus_new_user',
                        'widget_type': 'recursive',
                        'layout': {
                            'desktop': [['plus_gmv_lcy', 'plus_ltv_lcy']],
                            'mobile': [['plus_gmv_lcy'], ['plus_ltv_lcy']],
                        },
                        'subwidgets': [
                            {
                                'chart_type': 'line',
                                'description': (
                                    'Выручка на одного пользователя, '
                                    'которую он принесёт за всё время '
                                    'заказов в этом ресторане'
                                ),
                                'stretch_to_full_width': False,
                                'title': 'Пожизненная стоимость',
                                'widget_slug': 'plus_ltv_lcy',
                                'widget_type': 'widget_basic_chart',
                            },
                            {
                                'chart_type': 'bar_stacked',
                                'description': (
                                    'Сумма всех чеков за период по заказам'
                                ),
                                'stretch_to_full_width': True,
                                'title': 'Выручка',
                                'widget_slug': 'plus_gmv_lcy',
                                'widget_type': 'widget_basic_chart',
                                'restapp_link': {
                                    'text': 'Перейти в раздел Плюса',
                                    'slug': 'place_plus_manage',
                                },
                            },
                        ],
                    },
                ],
            },
            {
                'section': 'plus',
                'widgets': [
                    {
                        'chart_type': 'bar_stacked',
                        'description': 'Все заказы за период',
                        'stretch_to_full_width': False,
                        'title': 'Заказы',
                        'widget_slug': 'plus_orders_count',
                        'widget_type': 'widget_basic_chart',
                    },
                    {
                        'chart_type': 'line',
                        'description': (
                            'Выручка на одного пользователя, '
                            'которую он принесёт за всё время '
                            'заказов в этом ресторане'
                        ),
                        'stretch_to_full_width': False,
                        'title': 'Пожизненная стоимость',
                        'widget_slug': 'plus_ltv_lcy',
                        'widget_type': 'widget_basic_chart',
                    },
                ],
            },
        ],
    }

    sort_expected_response = dict(expected_response)

    for item in list(sort_expected_response['payload']):
        for widget in item['widgets']:
            if 'subwidgets' in widget:
                widget['subwidgets'] = sorted(
                    widget['subwidgets'], key=lambda x: x['widget_slug'],
                )

    sort_response = response.json()
    for item in list(sort_response['payload']):
        for data in item['widgets']:
            if 'subwidgets' in data:
                data['subwidgets'] = sorted(
                    data['subwidgets'], key=lambda x: x['widget_slug'],
                )

    assert sort_expected_response == sort_response


@pytest.mark.config(
    EATS_REPORT_STORAGE_PERIODS=CONFIG_PERIODS,
    EATS_REPORT_STORAGE_SECTIONS=CONFIG_SECTIONS,
    EATS_REPORT_STORAGE_PLUS_WIDGETS=CONFIG_WIDGETS,
    EATS_REPORT_STORAGE_PLUS_METRICS=CONFIG_METRICS,
)
async def test_service_return_only_widgets_that_has_metrics_allowed_by_permissions(  # noqa: E501
        taxi_eats_report_storage, mock_authorizer_w_details_403,
):
    response = await taxi_eats_report_storage.get(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/list',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
    )
    expected_response = {
        'payload': [
            {
                'section': 'advert',
                'widgets': [
                    {
                        'chart_type': 'bar_stacked',
                        'description': 'Сумма всех чеков за период по заказам',
                        'stretch_to_full_width': True,
                        'title': 'Выручка',
                        'widget_slug': 'plus_gmv_lcy',
                        'widget_type': 'widget_basic_chart',
                        'restapp_link': {
                            'text': 'Перейти в раздел Плюса',
                            'slug': 'place_plus_manage',
                        },
                    },
                ],
            },
            {
                'section': 'plus',
                'widgets': [
                    {
                        'chart_type': 'bar_stacked',
                        'description': 'Все заказы за период',
                        'stretch_to_full_width': False,
                        'title': 'Заказы',
                        'widget_slug': 'plus_orders_count',
                        'widget_type': 'widget_basic_chart',
                    },
                ],
            },
        ],
    }

    assert expected_response == response.json()
    assert sorted(expected_response.items()) == sorted(response.json().items())


@pytest.mark.config(
    EATS_REPORT_STORAGE_PERIODS=CONFIG_PERIODS,
    EATS_REPORT_STORAGE_SECTIONS=CONFIG_SECTIONS,
    EATS_REPORT_STORAGE_PLUS_WIDGETS=CONFIG_WIDGETS,
    EATS_REPORT_STORAGE_PLUS_METRICS=CONFIG_METRICS,
)
async def test_service_respond_500_if_authorizer_responded_400(
        taxi_eats_report_storage, mock_authorizer_400,
):
    response = await taxi_eats_report_storage.get(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/list',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
    )

    assert response.status_code == 500
    assert response.json() == {
        'code': '500',
        'message': 'Internal Server Error',
    }


@pytest.mark.config(
    EATS_REPORT_STORAGE_PERIODS=CONFIG_PERIODS,
    EATS_REPORT_STORAGE_SECTIONS=CONFIG_SECTIONS,
    EATS_REPORT_STORAGE_PLUS_WIDGETS=CONFIG_WIDGETS,
    EATS_REPORT_STORAGE_PLUS_METRICS=CONFIG_METRICS,
)
async def test_service_respond_500_if_authorizer_responded_403_without_details(
        taxi_eats_report_storage, mock_authorizer_wo_details_403,
):
    response = await taxi_eats_report_storage.get(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/list',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
    )

    assert response.status_code == 500
    assert response.json() == {
        'code': '500',
        'message': 'Internal Server Error',
    }


@pytest.mark.config(
    EATS_REPORT_STORAGE_PERIODS=CONFIG_PERIODS,
    EATS_REPORT_STORAGE_SECTIONS=CONFIG_SECTIONS,
    EATS_REPORT_STORAGE_PLUS_WIDGETS=CONFIG_WIDGETS,
    EATS_REPORT_STORAGE_PLUS_METRICS=CONFIG_METRICS,
)
async def test_service_respond_500_if_authorizer_responded_500(
        taxi_eats_report_storage, mock_authorizer_500,
):
    response = await taxi_eats_report_storage.get(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/list',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
    )

    assert response.status_code == 500
    assert response.json() == {
        'code': '500',
        'message': 'Internal Server Error',
    }


@pytest.mark.config(
    EATS_REPORT_STORAGE_PERIODS=CONFIG_PERIODS,
    EATS_REPORT_STORAGE_SECTIONS=CONFIG_SECTIONS,
    EATS_REPORT_STORAGE_PLUS_WIDGETS=CONFIG_WIDGETS,
    EATS_REPORT_STORAGE_PLUS_METRICS=CONFIG_METRICS,
)
@pytest.mark.parametrize(
    'section, expected_count', [('plus', 2), ('unknown', 0)],
)
async def test_service_return_only_one_section_with_section_param(
        taxi_eats_report_storage, mock_authorizer_200, section, expected_count,
):
    response = await taxi_eats_report_storage.get(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/list?section={}'.format(  # noqa: E501
            section,
        ),
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
    )

    assert response.status_code == 200
    assert len(response.json()['payload']) == 1
    assert response.json()['payload'][0]['section'] == section
    assert len(response.json()['payload'][0]['widgets']) == expected_count


@pytest.mark.disable_config_check
@pytest.mark.config(
    EATS_REPORT_STORAGE_PERIODS=CONFIG_PERIODS,
    EATS_REPORT_STORAGE_SECTIONS=CONFIG_PROMO_SECTIONS,
    EATS_REPORT_STORAGE_PROMO_WIDGETS_CFG=CONFIG_PROMO_WIDGETS,
    EATS_REPORT_STORAGE_PROMO_METRICS_CFG=CONFIG_PROMO_METRICS,
    EATS_REPORT_STORAGE_SWITCH_TO_MOCKS=MOCKS_CONFIG,
)
async def test_promo(taxi_eats_report_storage, mock_authorizer_200):
    response = await taxi_eats_report_storage.get(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/list?section={}'.format(  # noqa: E501
            'promo',
        ),
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
    )

    assert response.status_code == 200
    assert len(response.json()['payload']) == 1
    assert response.json()['payload'][0]['section'] == 'promo'
    assert len(response.json()['payload'][0]['widgets']) == 9
