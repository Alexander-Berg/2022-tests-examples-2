import pytest

from tests_eats_report_storage.widgets.utils import consts


EMPTY_GMV_LCY_WIDGET = {
    'title': 'Выручка',
    'description': 'Сумма всех чеков за период по заказам',
    'widget_type': 'widget_basic_chart',
    'widget_slug': 'plus_gmv_lcy',
    'stretch_to_full_width': True,
    'chart_type': 'bar_stacked',
    'points_chunking': 'month',
    'charts': [
        {
            'data_key': 'plus_user_w_plus_gmv_lcy',
            'name': 'Пользователи с Плюсом',
            'target_value': {'title': 'нужно не меньше 99 ₽', 'value': 99.0},
            'value_unit_sign': '¥',
            'inverse': False,
            'points_data': [],
        },
        {
            'data_key': 'plus_user_wo_plus_gmv_lcy',
            'name': 'Пользователи без Плюса',
            'target_value': {'title': 'нужно не меньше 199 ₽', 'value': 199.0},
            'value_unit_sign': '₽',
            'inverse': False,
            'points_data': [],
        },
    ],
    'restapp_link': {
        'text': 'Перейти в раздел Плюса',
        'slug': 'place_plus_manage',
    },
}

UNAVAILABLE_TEMPLATER_CONFIG = {
    'templates': [
        {
            'slug': 'widget_unavailable_exception',
            'template': '{exception}',
            'params': [
                {
                    'arg': 'exception',
                    'type': 'map',
                    'map': [
                        {
                            'key': 'error_period',
                            'value': 'График построится за период от 1 месяца (шаблон)',  # noqa: E501
                        },
                        {
                            'key': 'custom_error',
                            'value': 'какая-то кастомная ошибка',
                        },
                        {
                            'key': 'error_widget_multi_places',
                            'value': 'Запрещено больше одного ресторана',
                        },
                    ],
                },
            ],
        },
    ],
}

PLUS_WIDGETS_CONFIG = {
    'widgets': [
        {
            'chart_type': 'line',
            'description': 'Среднее количество заказов',
            'metrics': [
                'plus_user_w_plus_frequency_val',
                'plus_user_wo_plus_frequency_val',
            ],
            'stretch_to_full_width': False,
            'title': 'Частота заказов',
            'unvailable_widget_text': 'template:widget_unavailable_exception',
            'widget_id': 'plus_frequency_val',
            'widget_type': 'widget_basic_chart',
            'multi_places_enabled': False,
        },
    ],
}


@pytest.mark.parametrize(
    'text,place_ids',
    [
        pytest.param(
            'График построится за период от 1 месяца (задайте более 31 дня)',
            [1],
            id='text_as_text',
        ),
        pytest.param(
            'График построится за период от 1 месяца (шаблон)',
            [1],
            marks=pytest.mark.config(
                EATS_REPORT_STORAGE_TEXT_TEMPLATER=UNAVAILABLE_TEMPLATER_CONFIG,  # noqa: E501
                EATS_REPORT_STORAGE_PLUS_WIDGETS=PLUS_WIDGETS_CONFIG,
            ),
            id='text_error_from_templater',
        ),
        pytest.param(
            'Запрещено больше одного ресторана',
            [1, 2],
            marks=pytest.mark.config(
                EATS_REPORT_STORAGE_TEXT_TEMPLATER=UNAVAILABLE_TEMPLATER_CONFIG,  # noqa: E501
                EATS_REPORT_STORAGE_PLUS_WIDGETS=PLUS_WIDGETS_CONFIG,
            ),
            id='multi_places_error',
        ),
    ],
)
async def test_service_return_error_message_for_metrics_with_unvailable_group_by(  # noqa: E501
        taxi_eats_report_storage,
        mock_authorizer_200,
        mock_core_places_info_request,
        text,
        place_ids,
):
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
        json={
            'widget_slug': 'plus_frequency_val',
            'places': place_ids,
            'preset_period_type': 'month',
        },
    )

    assert response.json()['payload']['charts'] == text


async def test_service_return_error_message_for_metrics_with_unvailable_period(
        taxi_eats_report_storage,
        mock_authorizer_200,
        mock_core_places_info_request,
):
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
        json={
            'widget_slug': 'plus_frequency_val',
            'preset_period_type': 'custom',
            'places': [1],
            'period_begin': '2015-06-10T00:00:00+00:00',
            'period_end': '2015-06-16T00:00:00+00:00',
        },
    )

    assert (
        response.json()['payload']['charts']
        == 'График построится за период от 1 месяца (задайте более 31 дня)'
    )


@pytest.mark.parametrize(
    'widget_slug, places, preset_period_type, period_group_by,'
    + 'period_begin, period_end',
    [
        ('plus_orders_count', [1], None, None, None, None),
        (
            'plus_orders_count',
            [1],
            None,
            'day',
            '2015-06-10T00:00:00+00:00',
            '2015-08-20T00:00:00+00:00',
        ),
    ],
)
async def test_service_return_error_for_invalid_params(
        taxi_eats_report_storage,
        mock_authorizer_200,
        mock_core_places_info_request,
        widget_slug,
        places,
        preset_period_type,
        period_group_by,
        period_begin,
        period_end,
):
    body = dict()
    body['widget_slug'] = widget_slug
    body['places'] = places
    body['preset_period_type'] = preset_period_type
    body['period_group_by'] = period_group_by
    body['period_begin'] = period_begin
    body['period_end'] = period_end
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
        json=body,
    )

    assert response.status_code == 400
    assert response.json()['code'] == '400'


async def test_service_respond_500_if_authorizer_responded_400(
        taxi_eats_report_storage,
        mock_authorizer_400,
        mock_core_places_info_request,
):
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
        json={
            'widget_slug': 'plus_gmv_lcy',
            'places': [1],
            'preset_period_type': 'month',
        },
    )

    assert response.status_code == 500
    assert response.json() == {
        'code': '500',
        'message': 'Internal Server Error',
    }


async def test_service_respond_500_if_authorizer_responded_403_with_details(
        taxi_eats_report_storage,
        mock_authorizer_w_details_403,
        mock_core_places_info_request,
):
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
        json={
            'widget_slug': 'plus_gmv_lcy',
            'places': [1],
            'preset_period_type': 'month',
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'No access to the places or no permissions',
    }


async def test_service_respond_500_if_authorizer_responded_403_without_details(
        taxi_eats_report_storage,
        mock_authorizer_wo_details_403,
        mock_core_places_info_request,
):
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
        json={
            'widget_slug': 'plus_gmv_lcy',
            'places': [1],
            'preset_period_type': 'month',
        },
    )

    assert response.status_code == 500
    assert response.json() == {
        'code': '500',
        'message': 'Internal Server Error',
    }


async def test_service_return_empty_metrics_if_there_is_no_data(
        taxi_eats_report_storage,
        mock_authorizer_200,
        mock_core_places_info_request,
        pgsql,
):
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
        json={
            'widget_slug': 'plus_gmv_lcy',
            'places': [1],
            'preset_period_type': 'custom',
            'period_begin': '2015-06-10T00:00:00+00:00',
            'period_end': '2015-08-20T00:00:00+00:00',
        },
    )

    assert response.json()['payload'] == EMPTY_GMV_LCY_WIDGET
