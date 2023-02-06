# pylint: disable=import-only-modules

import pytest

from tests_eats_report_storage.conftest import exp3_config_promo_types
from tests_eats_report_storage.conftest import make_rating_response
from tests_eats_report_storage.widgets.utils import consts
from tests_eats_report_storage.widgets.utils import helpers


CONFIG_PERIODS = {
    'periods': [
        {'period_type': 'week', 'available_granularity': ['day']},
        {'period_type': 'month', 'available_granularity': ['day', 'week']},
        {'period_type': 'year', 'available_granularity': ['month']},
    ],
}

CONFIG_SECTIONS = {
    'sections': [{'name': 'promo', 'widgets': ['promo_orders_number_value']}],
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
    ],
}

CONFIG_PROMO_WIDGETS_WITH_TOPIC = {
    'widgets': [
        {
            'chart_type': 'sum_value',
            'description': 'Заказы за период',
            'metrics': ['promo_orders_number'],
            'title': 'Количество заказов',
            'topic': 'top',
            'widget_id': 'promo_orders_number_value',
        },
    ],
}

HTML_WIDGET_RESPONSE = {
    'title': '',
    'description': '',
    'widget_type': 'html',
    'widget_slug': 'advert_newcommer_html',
    'stretch_to_full_width': True,
    'chart_type': 'no_data',
    'points_chunking': 'day',
    'charts': [],
    'html_content': '<h1>Новые пользователи</h1>',
    'extra_content': {'main_text': 'Новые пользователи'},
}

EXTRA_PLUS_WIDGET_RESPONSE = {
    'chart_type': 'bar_stacked',
    'charts': [
        {
            'data_key': 'plus_user_w_plus_gmv_lcy',
            'inverse': False,
            'name': 'Пользователи с Плюсом',
            'points_data': [],
            'target_value': {'title': 'нужно не меньше 99 ₽', 'value': 99.0},
            'value_unit_sign': '¥',
        },
        {
            'data_key': 'plus_user_wo_plus_gmv_lcy',
            'inverse': False,
            'name': 'Пользователи без Плюса',
            'points_data': [],
            'target_value': {'title': 'нужно не меньше 199 ₽', 'value': 199.0},
            'value_unit_sign': '₽',
        },
    ],
    'description': 'Сумма всех чеков за период по заказам',
    'points_chunking': 'day',
    'restapp_link': {
        'slug': 'place_plus_manage',
        'text': 'Перейти в раздел Плюса',
    },
    'stretch_to_full_width': True,
    'title': 'Выручка',
    'widget_slug': 'plus_gmv_lcy',
    'widget_type': 'widget_basic_chart',
}


@pytest.mark.pgsql(
    'eats_report_storage', files=('eats_report_storage_advert_stats.sql',),
)
async def test_check_total_value(
        taxi_eats_report_storage,
        pgsql,
        mock_authorizer_200,
        mock_core_places_info_request,
):
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
        json={
            'widget_slug': 'advert_conversion',
            'places': [1],
            'preset_period_type': 'custom',
            'period_begin': '2021-09-19T00:00:00+00:00',
            'period_end': '2021-09-21T00:00:00+00:00',
        },
    )

    assert (
        response.json()['payload']['charts'][0]['total_value']['value'] == 50.0
    )


@pytest.mark.pgsql(
    'eats_report_storage', files=('eats_report_storage_advert_stats.sql',),
)
async def test_service_return_recursive_widget(
        taxi_eats_report_storage,
        mock_authorizer_200,
        mock_eats_place_rating,
        mock_core_places_info_request,
        rating_response,
        pgsql,
):
    rating_response.set_data(make_rating_response(show_rating=True))
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
        json={
            'widget_slug': 'advert_gmv',
            'places': [1],
            'preset_period_type': 'custom',
            'period_begin': '2021-09-19T00:00:00+00:00',
            'period_end': '2021-09-21T00:00:00+00:00',
        },
    )
    assert response.status_code == 200
    widget = response.json()['payload']
    assert not widget['charts']
    assert widget['widget_type'] == 'recursive'
    assert widget['chart_type'] == 'no_data'
    assert len(widget['subwidgets']) == 3
    for subwidget in widget['subwidgets']:
        if subwidget['widget_slug'] in [
                'advert_gmv_line_with_delta',
                'advert_first_gmv_line_with_delta',
        ]:
            helpers.check_data_count(subwidget, 1, 3)
            helpers.check_data(
                subwidget,
                None,
                ['6.60 ₽'],
                ['2.20 ₽'],
                [[3.3], [2.2], [1.1]],
                None,
                None,
                None,
                None,
            )
        elif (
            subwidget['widget_slug'] == 'quality_place_raiting_sum_with_delta'
        ):
            helpers.check_data_count(subwidget, 1, 0)
            helpers.check_data(
                subwidget, None, ['4.1'], ['1.6'], [], None, None, None, None,
            )
    assert widget['layout']['desktop'] == [
        [
            'advert_gmv_line_with_delta',
            'advert_first_gmv_line_with_delta',
            'quality_place_raiting_sum_with_delta',
        ],
    ]
    assert widget['layout']['mobile'] == [
        ['advert_gmv_line_with_delta'],
        [
            'advert_first_gmv_line_with_delta',
            'quality_place_raiting_sum_with_delta',
        ],
    ]


@pytest.mark.pgsql(
    'eats_report_storage', files=('eats_report_storage_metrics_data.sql',),
)
@exp3_config_promo_types()
async def test_service_ignore_localized_currency_if_explicitly_set(
        taxi_eats_report_storage,
        mock_authorizer_200,
        mock_core_places_info_request,
        pgsql,
):
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
        json={
            'widget_slug': 'promo_mean_receipt_value',
            'places': [1],
            'preset_period_type': 'month',
            'additional_filters': {'promo_type': 'gift'},
        },
    )
    assert response.json()['payload']['charts'][0]['value_unit_sign'] == '₽'
    assert mock_core_places_info_request.times_called == 1


@pytest.mark.now('2022-02-22T06:00:00')
@pytest.mark.parametrize(
    'widget_slug, values, statuses, total_value',
    [
        (
            'plus_orders_count',
            [3, 6, 4],
            ['partly_active', 'active', 'partly_active'],
            13,
        ),
        (
            'plus_frequency_val',
            [1.5, 2, 2],
            ['partly_active', 'active', 'partly_active'],
            3,
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_report_storage',
    files=('eats_report_storage_multiple_place_ids.sql',),
)
async def test_return_metrics_for_multiple_place_ids(
        taxi_eats_report_storage,
        pgsql,
        mock_authorizer_200,
        mock_core_places_info_request,
        widget_slug,
        values,
        statuses,
        total_value,
):
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
        json={
            'widget_slug': widget_slug,
            'places': [1, 2, 3],
            'preset_period_type': 'custom',
            'period_begin': '2021-05-01T00:00:00+00:00',
            'period_end': '2021-08-01T00:00:00+00:00',
        },
    )

    data = response.json()['payload']['charts'][0]['points_data']
    for value_idx in range(
            len(response.json()['payload']['charts'][0]['points_data']),
    ):
        assert data[value_idx]['value'] == values[value_idx]
        assert data[value_idx]['status'] == statuses[value_idx]
    assert (
        response.json()['payload']['charts'][0]['total_value']['value']
        == total_value
    )
    assert response.status_code == 200


@pytest.mark.pgsql(
    'eats_report_storage', files=('eats_report_storage_metrics_data.sql',),
)
async def test_service_return_widget_for_metrics_with_stack(
        taxi_eats_report_storage,
        mock_authorizer_200,
        mock_core_places_info_request,
        pgsql,
):
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
        json={
            'widget_slug': 'plus_new_user',
            'places': [1],
            'preset_period_type': 'week',
        },
    )

    assert 'stack_id' not in response.json()['payload']['charts'][0]
    assert response.json()['payload']['charts'][1]['stack_id'] == 0
    assert response.json()['payload']['charts'][2]['stack_id'] == 1
    assert response.json()['payload']['charts'][3]['stack_id'] == 1


@pytest.mark.parametrize(
    'widget_slug, response_json',
    [
        pytest.param('advert_newcommer_html', HTML_WIDGET_RESPONSE),
        pytest.param('plus_gmv_lcy', EXTRA_PLUS_WIDGET_RESPONSE),
    ],
)
async def test_check_widgets_does_not_return_html(
        taxi_eats_report_storage,
        pgsql,
        mock_authorizer_200,
        mock_core_places_info_request,
        widget_slug,
        response_json,
):
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
        json={
            'widget_slug': widget_slug,
            'places': [1],
            'preset_period_type': 'custom',
            'period_begin': '2021-09-19T00:00:00+00:00',
            'period_end': '2021-09-21T00:00:00+00:00',
        },
    )

    assert response.json()['payload'] == response_json


@pytest.mark.config(
    EATS_REPORT_STORAGE_PLUS_METRICS={'metrics': []},
    EATS_REPORT_STORAGE_PLUS_WIDGETS={'widgets': []},
    EATS_REPORT_STORAGE_PERIODS=CONFIG_PERIODS,
    EATS_REPORT_STORAGE_SECTIONS=CONFIG_SECTIONS,
    EATS_REPORT_STORAGE_PROMO_METRICS_CFG=CONFIG_PROMO_METRICS,
    EATS_REPORT_STORAGE_PROMO_WIDGETS_CFG=CONFIG_PROMO_WIDGETS_WITH_TOPIC,
)
async def test_service_return_widget_list_with_topic(
        taxi_eats_report_storage, mock_authorizer_200,
):
    await taxi_eats_report_storage.invalidate_caches()
    response = await taxi_eats_report_storage.get(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/list?section=promo',  # noqa: E501
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
    )
    await taxi_eats_report_storage.invalidate_caches()
    assert response.status_code == 200
    assert len(response.json()['payload']) == 1
    assert response.json()['payload'][0]['section'] == 'promo'
    assert len(response.json()['payload'][0]['widgets']) == 1
    assert response.json()['payload'][0]['widgets'][0]['topic'] == 'top'


@pytest.mark.config(
    EATS_REPORT_STORAGE_PLUS_METRICS={'metrics': []},
    EATS_REPORT_STORAGE_PLUS_WIDGETS={'widgets': []},
    EATS_REPORT_STORAGE_PERIODS=CONFIG_PERIODS,
    EATS_REPORT_STORAGE_SECTIONS=CONFIG_SECTIONS,
    EATS_REPORT_STORAGE_PROMO_METRICS_CFG=CONFIG_PROMO_METRICS,
    EATS_REPORT_STORAGE_PROMO_WIDGETS_CFG=CONFIG_PROMO_WIDGETS_WITH_TOPIC,
)
@exp3_config_promo_types()
async def test_service_return_widget_get_with_topic(
        taxi_eats_report_storage, mock_authorizer_200, pgsql,
):
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
        json={
            'widget_slug': 'promo_orders_number_value',
            'places': [1],
            'preset_period_type': 'month',
            'additional_filters': {'promo_type': 'gift'},
        },
    )
    assert response.json()['payload']['topic'] == 'top'
