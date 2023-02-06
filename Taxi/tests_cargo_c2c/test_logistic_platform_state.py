# pylint: disable=C0302
import pytest

from testsuite.utils import matching


DEFAULT_CONTENT_SECTION = [
    {
        'id': matching.uuid_string,
        'items': [
            {
                'id': matching.uuid_string,
                'subtitle': {
                    'color': 'TextMinor',
                    'max_lines': 1,
                    'text': '№32779352',
                    'typography': 'caption1',
                },
                'title': {
                    'color': 'TextMain',
                    'max_lines': 1,
                    'text': 'Заказ из R&G',
                    'typography': 'body2',
                },
                'lead_icon': {'image_tag': 'delivery_shopping_cart'},
                'trail_subtitle': {
                    'color': 'TextMinor',
                    'max_lines': 1,
                    'text': 'К оплате',
                    'typography': 'caption1',
                },
                'trail_text': {
                    'color': 'TextMain',
                    'max_lines': 1,
                    'text': '990 ₽',
                    'typography': 'body2',
                },
                'type': 'list_item',
            },
            {'id': matching.uuid_string, 'type': 'separator'},
            {
                'id': matching.uuid_string,
                'title': {
                    'color': 'TextMain',
                    'max_lines': 1,
                    'text': 'Доставка до двери',
                    'typography': 'body2',
                },
                'type': 'list_item',
                'lead_icon': {'image_tag': 'delivery_door_to_door'},
                'trail_text': {
                    'color': 'TextMain',
                    'max_lines': 1,
                    'text': 'Бесплатно',
                    'typography': 'body2',
                },
            },
            {
                'id': matching.uuid_string,
                'title': {
                    'color': 'TextMinor',
                    'max_lines': 1,
                    'text': 'Получатель',
                    'typography': 'caption1',
                },
                'type': 'header',
            },
            {
                'id': matching.uuid_string,
                'subtitle': {
                    'color': 'TextMinor',
                    'max_lines': 1,
                    'text': 'кв. 12, под. 12, этаж 12',
                    'typography': 'caption1',
                },
                'title': {
                    'color': 'TextMain',
                    'max_lines': 1,
                    'text': 'Садовническая улица',
                    'typography': 'body2',
                },
                'type': 'list_item',
                'lead_icon': {'image_tag': 'delivery_point'},
            },
            {'id': matching.uuid_string, 'type': 'separator'},
            {
                'id': matching.uuid_string,
                'subtitle': {
                    'color': 'TextMain',
                    'max_lines': 1,
                    'text': 'some_comment',
                    'typography': 'body2',
                },
                'title': {
                    'color': 'TextMinor',
                    'max_lines': 1,
                    'text': 'Комментарий',
                    'typography': 'caption1',
                },
                'type': 'list_item',
                'lead_icon': {'image_tag': 'delivery_comment_outline'},
            },
        ],
    },
]

CONTENT_SECTION_WITH_PERFORMER = [
    {
        'id': matching.uuid_string,
        'items': [
            {
                'id': matching.uuid_string,
                'subtitle': {
                    'color': 'TextMinor',
                    'max_lines': 1,
                    'text': '№32779352',
                    'typography': 'caption1',
                },
                'title': {
                    'color': 'TextMain',
                    'max_lines': 1,
                    'text': 'Заказ из R&G',
                    'typography': 'body2',
                },
                'type': 'list_item',
                'lead_icon': {'image_tag': 'delivery_shopping_cart'},
                'trail_subtitle': {
                    'color': 'TextMinor',
                    'max_lines': 1,
                    'text': 'К ' 'оплате',
                    'typography': 'caption1',
                },
                'trail_text': {
                    'color': 'TextMain',
                    'max_lines': 1,
                    'text': '990 ₽',
                    'typography': 'body2',
                },
            },
            {'id': matching.uuid_string, 'type': 'separator'},
            {
                'id': matching.uuid_string,
                'title': {
                    'color': 'TextMain',
                    'max_lines': 1,
                    'text': 'Доставка до двери',
                    'typography': 'body2',
                },
                'type': 'list_item',
                'lead_icon': {'image_tag': 'delivery_door_to_door'},
                'trail_text': {
                    'color': 'TextMain',
                    'max_lines': 1,
                    'text': 'Бесплатно',
                    'typography': 'body2',
                },
            },
            {
                'id': matching.uuid_string,
                'title': {
                    'color': 'TextMinor',
                    'max_lines': 1,
                    'text': 'Исполнитель',
                    'typography': 'caption1',
                },
                'type': 'header',
            },
            {
                'id': matching.uuid_string,
                'title': {
                    'color': 'TextMain',
                    'max_lines': 1,
                    'text': 'Petr',
                    'typography': 'body2',
                },
                'type': 'list_item',
            },
            {'id': matching.uuid_string, 'type': 'separator'},
            {
                'id': matching.uuid_string,
                'subtitle': {
                    'color': 'TextMain',
                    'max_lines': 1,
                    'text': 'BMW, A001AA77',
                    'typography': 'body2',
                },
                'title': {
                    'color': 'TextMinor',
                    'max_lines': 1,
                    'text': 'Авто',
                    'typography': 'caption1',
                },
                'type': 'list_item',
            },
            {
                'id': matching.uuid_string,
                'title': {
                    'color': 'TextMinor',
                    'max_lines': 1,
                    'text': 'Получатель',
                    'typography': 'caption1',
                },
                'type': 'header',
            },
            {
                'id': matching.uuid_string,
                'subtitle': {
                    'color': 'TextMinor',
                    'max_lines': 1,
                    'text': 'кв. 12, под. 12, этаж 12',
                    'typography': 'caption1',
                },
                'title': {
                    'color': 'TextMain',
                    'max_lines': 1,
                    'text': 'Садовническая улица',
                    'typography': 'body2',
                },
                'type': 'list_item',
                'lead_icon': {'image_tag': 'delivery_point'},
            },
            {'id': matching.uuid_string, 'type': 'separator'},
            {
                'id': matching.uuid_string,
                'subtitle': {
                    'color': 'TextMain',
                    'max_lines': 1,
                    'text': 'some_comment',
                    'typography': 'body2',
                },
                'title': {
                    'color': 'TextMinor',
                    'max_lines': 1,
                    'text': 'Комментарий',
                    'typography': 'caption1',
                },
                'type': 'list_item',
                'lead_icon': {'image_tag': 'delivery_comment_outline'},
            },
        ],
    },
]


@pytest.mark.experiments3(filename='experiment.json')
async def test_order_created(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        default_pa_headers,
        mock_logistic_platform,
        mock_order_statuses_history,
        mock_claims_full,
):
    await create_logistic_platform_orders()
    mock_logistic_platform.file_name = 'order_created.json'
    mock_order_statuses_history.file_name = 'order_created.json'
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={'delivery_id': 'logistic-platform/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert response.json() == {
        'etag': matching.AnyString(),
        'state': {
            'active_route_points': [0, 1],
            'context': {
                'is_performer_position_available': False,
                'original_order_id': '32779352',
                'display_targets': ['multiorder'],
            },
            'meta': {
                'order_provider_id': 'logistic-platform',
                'order_status': 'CREATED_IN_PLATFORM',
                'roles': ['initiator'],
                'tariff_class': '',
            },
            'icon_strategy': {
                'image_tag': 'delivery_market_icon_for_delivery_state',
                'type': 'remote_image',
            },
            'primary_actions': [
                {
                    'open_pdf': False,
                    'title': 'Состав заказа',
                    'type': 'show_content_order_history',
                    'url': 'some_url32779352',
                },
                {
                    'message': {
                        'body': 'Точно отменить?',
                        'close_button': {'title': 'Закрыть'},
                        'confirm_button': {
                            'cancel_type': 'free',
                            'title': 'Отменить',
                        },
                        'title': 'Отмена',
                    },
                    'title': 'Отмена доставки',
                    'type': 'cancel',
                },
            ],
            'secondary_actions': [
                {
                    'title': 'Помощь',
                    'type': 'show_support_web',
                    'url': 'some_enurl_template?32779352',
                },
            ],
            'sorted_route_points': [
                {
                    'area_description': '',
                    'coordinates': [37.632745, 55.774532],
                    'full_text': '',
                    'short_text': '',
                    'type': 'source',
                    'uri': 'ymapsbm1://geo?ll=55.774532%2C37.632745',
                    'visit_status': 'pending',
                },
                {
                    'area_description': '',
                    'coordinates': [37.652874, 55.737148],
                    'full_text': '',
                    'short_text': '',
                    'type': 'destination',
                    'uri': 'ymapsbm1://geo?ll=55.737148%2C37.652874',
                    'visit_status': 'pending',
                },
            ],
            'summary': 'Заказ собирают',
            'description': 'Сообщим, когда передадут курьеру',
            'content_sections': DEFAULT_CONTENT_SECTION,
        },
    }


@pytest.mark.experiments3(filename='experiment.json')
async def test_in_middle_node(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        default_pa_headers,
        mock_logistic_platform,
        mock_order_statuses_history,
        mock_claims_full,
):
    await create_logistic_platform_orders()
    mock_logistic_platform.file_name = 'in_middle_node.json'
    mock_order_statuses_history.file_name = 'in_middle_node.json'
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={'delivery_id': 'logistic-platform/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert response.json() == {
        'etag': matching.AnyString(),
        'state': {
            'active_route_points': [0, 1],
            'context': {
                'is_performer_position_available': False,
                'original_order_id': '32779352',
                'display_targets': ['multiorder'],
            },
            'meta': {
                'order_provider_id': 'logistic-platform',
                'order_status': 'VALIDATING',
                'roles': ['initiator'],
                'tariff_class': '',
            },
            'icon_strategy': {
                'image_tag': 'delivery_market_icon_for_delivery_state',
                'type': 'remote_image',
            },
            'primary_actions': [
                {
                    'open_pdf': False,
                    'title': 'Состав заказа',
                    'type': 'show_content_order_history',
                    'url': 'some_url32779352',
                },
                {
                    'message': {
                        'body': 'Точно отменить?',
                        'close_button': {'title': 'Закрыть'},
                        'confirm_button': {
                            'cancel_type': 'free',
                            'title': 'Отменить',
                        },
                        'title': 'Отмена',
                    },
                    'title': 'Отмена доставки',
                    'type': 'cancel',
                },
            ],
            'secondary_actions': [
                {
                    'title': 'Помощь',
                    'type': 'show_support_web',
                    'url': 'some_enurl_template?32779352',
                },
            ],
            'sorted_route_points': [
                {
                    'area_description': '',
                    'coordinates': [37.632745, 55.774532],
                    'full_text': '',
                    'short_text': '',
                    'type': 'source',
                    'uri': 'ymapsbm1://geo?ll=55.774532%2C37.632745',
                    'visit_status': 'pending',
                },
                {
                    'area_description': '',
                    'coordinates': [37.652874, 55.737148],
                    'full_text': '',
                    'short_text': '',
                    'type': 'destination',
                    'uri': 'ymapsbm1://geo?ll=55.737148%2C37.652874',
                    'visit_status': 'pending',
                },
            ],
            'summary': 'Заказ собирают',
            'description': 'Сообщим, когда передадут курьеру',
            'content_sections': DEFAULT_CONTENT_SECTION,
        },
    }


@pytest.mark.experiments3(filename='experiment.json')
async def test_delivering(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        default_pa_headers,
        mock_logistic_platform,
        mock_order_statuses_history,
        mock_claims_full,
):
    await create_logistic_platform_orders()
    mock_logistic_platform.file_name = 'delivering.json'
    mock_order_statuses_history.file_name = 'delivering.json'
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={'delivery_id': 'logistic-platform/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert response.json() == {
        'etag': matching.AnyString(),
        'state': {
            'active_route_points': [0],
            'context': {
                'is_performer_position_available': True,
                'original_order_id': '32779352',
                'display_targets': ['multiorder'],
            },
            'meta': {
                'order_provider_id': 'logistic-platform',
                'order_status': 'PICKUPED',
                'roles': ['initiator'],
                'tariff_class': '',
            },
            'icon_strategy': {
                'image_tag': 'delivery_market_icon_for_delivery_state',
                'type': 'remote_image',
            },
            'primary_actions': [
                {
                    'communication_method': {
                        'forwarding_id': 'performer',
                        'type': 'voice_forwarding_call',
                    },
                    'title': 'Звонок курьеру',
                    'type': 'performer_call',
                },
                {
                    'open_pdf': False,
                    'title': 'Состав заказа',
                    'type': 'show_content_order_history',
                    'url': 'some_url32779352',
                },
                {
                    'type': 'share',
                    'title': 'Поделиться',
                    'sharing_url': matching.AnyString(),
                },
            ],
            'secondary_actions': [
                {
                    'title': 'Помощь',
                    'type': 'show_support_web',
                    'url': 'some_enurl_template?32779352',
                },
            ],
            'sorted_route_points': [
                {
                    'area_description': '',
                    'coordinates': [37.652874, 55.737148],
                    'full_text': '',
                    'short_text': '',
                    'type': 'destination',
                    'uri': 'ymapsbm1://geo?ll=55.737148%2C37.652874',
                    'visit_status': 'pending',
                },
            ],
            'performer': {
                'name': 'Petr',
                'short_name': 'Иван',
                'rating': '4.7',
                'phone': '+7123',
                'photo_url': 'testavatar',
                'vehicle_model': 'BMW',
                'vehicle_number': 'A001AA77',
            },
            'performer_route': {
                'sorted_route_points': [
                    {'coordinates': [37.652874, 55.737148]},
                ],
            },
            'summary': 'Заказ в пути: ещё 1 мин',
            'content_sections': CONTENT_SECTION_WITH_PERFORMER,
        },
    }


@pytest.mark.experiments3(filename='experiment.json')
async def test_delivered(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        default_pa_headers,
        mock_claims_full,
        mock_logistic_platform,
        mock_order_statuses_history,
):
    await create_logistic_platform_orders()
    mock_logistic_platform.file_name = 'delivered.json'
    mock_order_statuses_history.file_name = 'delivered.json'
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={'delivery_id': 'logistic-platform/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert response.json() == {
        'etag': matching.AnyString(),
        'state': {
            'active_route_points': [0],
            'context': {
                'is_performer_position_available': False,
                'original_order_id': '32779352',
                'present_as_completed': True,
                'display_targets': ['multiorder'],
            },
            'meta': {
                'order_provider_id': 'logistic-platform',
                'order_status': 'DELIVERED_FINISH',
                'roles': ['initiator'],
                'tariff_class': '',
            },
            'icon_strategy': {
                'image_tag': 'delivery_market_icon_for_delivery_state',
                'type': 'remote_image',
            },
            'primary_actions': [
                {
                    'communication_method': {
                        'forwarding_id': 'performer',
                        'type': 'voice_forwarding_call',
                    },
                    'title': 'Звонок курьеру',
                    'type': 'performer_call',
                },
                {
                    'open_pdf': False,
                    'title': 'Состав заказа',
                    'type': 'show_content_order_history',
                    'url': 'some_url32779352',
                },
                {
                    'title': 'Фидбэк',
                    'type': 'feedback',
                    'subtitles': [
                        {
                            'scores': [1, 2, 3],
                            'title': 'Что вас разочаровало?',
                        },
                        {'scores': [4], 'title': 'Что испортило впечатление?'},
                        {
                            'scores': [5],
                            'title': 'Что вам особенно понравилось?',
                        },
                    ],
                    'reasons': [
                        {
                            'reason_id': 'too_long_delivery',
                            'scores': [1, 2, 3, 4],
                            'title': 'Слишком долгая доставка',
                        },
                        {
                            'reason_id': 'comment',
                            'scores': [1, 2, 3, 4],
                            'title': 'Курьер не учёл комментарий',
                        },
                        {
                            'icon': {
                                'active': 'delivery_perfect_active_icon',
                                'inactive': 'delivery_perfect_inactive_icon',
                            },
                            'reason_id': 'perfect',
                            'scores': [5],
                            'title': 'Всё как надо',
                        },
                    ],
                },
            ],
            'secondary_actions': [
                {
                    'title': 'Помощь',
                    'type': 'show_support_web',
                    'url': 'some_enurl_template?32779352',
                },
            ],
            'sorted_route_points': [
                {
                    'area_description': '',
                    'coordinates': [37.652874, 55.737148],
                    'full_text': '',
                    'short_text': '',
                    'type': 'destination',
                    'uri': 'ymapsbm1://geo?ll=55.737148%2C37.652874',
                    'visit_status': 'pending',
                },
            ],
            'summary': 'Заказ доставлен',
            'description': 'Оцените сервис со стороны курьера',
            'performer': {
                'name': 'Petr',
                'short_name': 'Иван',
                'rating': '4.7',
                'phone': '+7123',
                'photo_url': 'testavatar',
                'vehicle_model': 'BMW',
                'vehicle_number': 'A001AA77',
            },
            'completed_state_buttons': {
                'primary': {'title': 'Готово', 'action': {'type': 'done'}},
            },
            'content_sections': CONTENT_SECTION_WITH_PERFORMER,
        },
    }


@pytest.mark.experiments3(filename='experiment.json')
async def test_cancelled(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        default_pa_headers,
        mock_logistic_platform,
        mock_order_statuses_history,
        mock_claims_full,
):
    await create_logistic_platform_orders()
    mock_logistic_platform.file_name = 'cancelled.json'
    mock_order_statuses_history.file_name = 'cancelled.json'
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={'delivery_id': 'logistic-platform/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert response.json() == {
        'etag': matching.AnyString(),
        'state': {
            'active_route_points': [0],
            'context': {
                'is_performer_position_available': False,
                'present_as_completed': True,
                'original_order_id': '32779352',
                'display_targets': ['multiorder'],
            },
            'meta': {
                'order_provider_id': 'logistic-platform',
                'order_status': 'CANCELLED',
                'roles': ['initiator'],
                'tariff_class': '',
            },
            'icon_strategy': {
                'image_tag': 'delivery_market_icon_for_delivery_state',
                'type': 'remote_image',
            },
            'primary_actions': [],
            'secondary_actions': [],
            'sorted_route_points': [
                {
                    'area_description': '',
                    'coordinates': [37.652874, 55.737148],
                    'full_text': '',
                    'short_text': '',
                    'type': 'destination',
                    'uri': 'ymapsbm1://geo?ll=55.737148%2C37.652874',
                    'visit_status': 'pending',
                },
            ],
            'summary': 'Заказ отменён',
            'completed_state_buttons': {
                'primary': {'title': 'Готово', 'action': {'type': 'done'}},
            },
            'content_sections': DEFAULT_CONTENT_SECTION,
        },
    }


@pytest.mark.experiments3(filename='experiment.json')
async def test_returning(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        default_pa_headers,
        mock_logistic_platform,
        mock_order_statuses_history,
        mock_claims_full,
):
    await create_logistic_platform_orders()
    mock_logistic_platform.file_name = 'returning.json'
    mock_order_statuses_history.file_name = 'returning.json'
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={'delivery_id': 'logistic-platform/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert response.json()['state'] == {
        'active_route_points': [0],
        'context': {
            'is_performer_position_available': False,
            'present_as_completed': True,
            'original_order_id': '32779352',
            'display_targets': ['multiorder'],
        },
        'meta': {
            'order_provider_id': 'logistic-platform',
            'order_status': 'RETURNED_FINISH',
            'roles': ['initiator'],
            'tariff_class': '',
        },
        'icon_strategy': {
            'image_tag': 'delivery_market_icon_for_delivery_state',
            'type': 'remote_image',
        },
        'primary_actions': [],
        'secondary_actions': [],
        'sorted_route_points': [
            {
                'area_description': '',
                'coordinates': [37.652874, 55.737148],
                'full_text': '',
                'short_text': '',
                'type': 'destination',
                'uri': 'ymapsbm1://geo?ll=55.737148%2C37.652874',
                'visit_status': 'pending',
            },
        ],
        'summary': 'Заказ отменён',
        'completed_state_buttons': {
            'primary': {'title': 'Готово', 'action': {'type': 'done'}},
        },
        'content_sections': DEFAULT_CONTENT_SECTION,
    }


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.parametrize(
    'file_name',
    [
        'order_created.json',
        'in_middle_node.json',
        'delivering.json',
        'delivered.json',
        'cancelled.json',
    ],
)
async def test_deliveries(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        default_pa_headers,
        mock_logistic_platform,
        mock_order_statuses_history,
        mock_claims_full,
        file_name,
):
    await create_logistic_platform_orders()
    mock_logistic_platform.file_name = file_name
    mock_order_statuses_history.file_name = file_name
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/deliveries',
        json={'deliveries': []},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    resp = response.json()
    if file_name in ['delivered.json', 'delivering.json']:
        for delivery in resp['deliveries']:
            assert delivery['state']['actions'] == [
                {
                    'communication_method': {
                        'forwarding_id': 'performer',
                        'type': 'voice_forwarding_call',
                    },
                    'title': 'Звонок курьеру',
                    'type': 'performer_call',
                },
                {
                    'open_pdf': False,
                    'title': 'Состав заказа',
                    'type': 'show_content_order_history',
                    'url': 'some_url32779352',
                },
                {
                    'title': 'Детали',
                    'type': 'open_tracking_card',
                    'expansion': 'expanded',
                },
            ]
    else:
        for delivery in resp['deliveries']:
            assert delivery['state']['actions'] == []


@pytest.mark.experiments3(filename='experiment.json')
async def test_feedback_action(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        default_pa_headers,
        mock_logistic_platform,
        mock_order_statuses_history,
        mock_claims_full,
):
    await create_logistic_platform_orders()
    mock_logistic_platform.file_name = 'delivered.json'
    mock_order_statuses_history.file_name = 'delivered.json'

    response = await taxi_cargo_c2c.post(
        '/v1/actions/save-client-feedback',
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': get_default_order_id(),
                'order_provider_id': 'logistic-platform',
            },
            'type': 'order_feedback',
            'score': 4,
            'reasons': [{'reason_id': 'too_long_delivery'}],
        },
    )
    assert response.status_code == 200

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={'delivery_id': 'logistic-platform/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200

    assert response.json()['state']['primary_actions'] == [
        {
            'type': 'performer_call',
            'title': 'Звонок курьеру',
            'communication_method': {
                'type': 'voice_forwarding_call',
                'forwarding_id': 'performer',
            },
        },
        {
            'open_pdf': False,
            'title': 'Состав заказа',
            'type': 'show_content_order_history',
            'url': 'some_url32779352',
        },
        {
            'type': 'feedback',
            'title': 'Фидбэк',
            'subtitles': [
                {'scores': [1, 2, 3], 'title': 'Что вас разочаровало?'},
                {'scores': [4], 'title': 'Что испортило впечатление?'},
                {'scores': [5], 'title': 'Что вам особенно понравилось?'},
            ],
            'reasons': [
                {
                    'reason_id': 'too_long_delivery',
                    'title': 'Слишком долгая доставка',
                    'scores': [1, 2, 3, 4],
                },
                {
                    'reason_id': 'comment',
                    'title': 'Курьер не учёл комментарий',
                    'scores': [1, 2, 3, 4],
                },
                {
                    'reason_id': 'perfect',
                    'title': 'Всё как надо',
                    'scores': [5],
                    'icon': {
                        'active': 'delivery_perfect_active_icon',
                        'inactive': 'delivery_perfect_inactive_icon',
                    },
                },
            ],
            'last_feedback': {'score': 4, 'reason_ids': ['too_long_delivery']},
        },
    ]


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.parametrize(
    'do_not_show_in_go, expected_deliveries_count', [(False, 1), (True, 0)],
)
async def test_do_not_show_in_go(
        taxi_cargo_c2c,
        get_default_order_id,
        default_pa_headers,
        mock_logistic_platform,
        mock_order_statuses_history,
        mock_claims_full,
        do_not_show_in_go,
        expected_deliveries_count,
):
    mock_logistic_platform.file_name = 'delivered.json'
    mock_order_statuses_history.file_name = 'delivered.json'

    await taxi_cargo_c2c.post(
        '/v1/actions/save-clients-orders',
        json={
            'orders': [
                {
                    'id': {
                        'phone_pd_id': 'phone_pd_id_2',
                        'order_id': get_default_order_id(),
                        'order_provider_id': 'logistic-platform',
                    },
                    'roles': ['recipient'],
                    'do_not_show_in_go': do_not_show_in_go,
                },
            ],
        },
    )

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/deliveries',
        json={'deliveries': []},
        headers=default_pa_headers('phone_pd_id_2'),
    )
    assert len(response.json()['deliveries']) == expected_deliveries_count


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_c2c_lp_order_tanker_keys',
    consumers=['cargo-c2c/lp_order'],
    clauses=[],
    default_value={
        'tanker_keys_by_args': [
            {
                'required_args': [
                    'delivery_interval_numeric_date_upper',
                    'delivery_interval_time_from',
                    'delivery_interval_time_to',
                ],
                'texts': {
                    'summary': {
                        'key': 'market_express.delivery_interval.summary',
                        'keyset': 'cargo_client_messages',
                    },
                },
            },
            {
                'required_args': [],
                'texts': {
                    'summary': {
                        'key': 'delivery.summary',
                        'keyset': 'cargo_client_messages',
                    },
                },
            },
        ],
    },
    is_config=True,
)
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.now('2021-02-25T10:00:00')
@pytest.mark.parametrize(
    'from_ts, to_ts, expected_summary, expected_content_item',
    [
        (
            1614322800,
            1614330000,
            'Курьер завтра с 10:00 до 12:00',
            '26 февраля, 10:00–12:00',
        ),
        (
            1614243600,
            1614265200,
            'Курьер сегодня с 12:00 до 18:00',
            '25 февраля, 12:00–18:00',
        ),
        (
            1614492000,
            1614499200,
            'Курьер 28.02 с 09:00 до 11:00',
            '28 февраля, 09:00–11:00',
        ),
        (
            1614153600,
            1614168000,
            'Курьер 24.02 с 11:00 до 15:00',
            '24 февраля, 11:00–15:00',
        ),
        (
            1614225600,
            1614229200,
            'Курьер сегодня с 07:00 до 08:00',
            '25 февраля, 07:00–08:00',
        ),
    ],
)
async def test_delivery_interval(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        default_pa_headers,
        load_json,
        mockserver,
        mock_claims_full,
        mock_order_statuses_history,
        from_ts,
        to_ts,
        expected_summary,
        expected_content_item,
):
    @mockserver.json_handler(
        '/logistic-platform-admin/api/admin/request/trace',
    )
    def _mock_trace(request):
        resp = load_json('logistic-platform/trace/in_middle_node.json')
        resp['model']['delivery_interval'] = {
            'Timezone': 'Europe/Moscow',
            'from': from_ts,
            'to': to_ts,
        }
        return resp

    await create_logistic_platform_orders()
    mock_order_statuses_history.file_name = 'in_middle_node.json'
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={'delivery_id': 'logistic-platform/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert response.json()['state']['summary'] == expected_summary
    assert response.json()['state']['content_sections'][0]['items'][-1] == {
        'id': matching.uuid_string,
        'subtitle': {
            'color': 'TextMain',
            'max_lines': 1,
            'text': expected_content_item,
            'typography': 'body2',
        },
        'title': {
            'color': 'TextMinor',
            'max_lines': 1,
            'text': 'Выбранное время',
            'typography': 'caption1',
        },
        'type': 'list_item',
        'lead_icon': {'image_tag': 'delivery_clock'},
    }


@pytest.mark.config(
    CARGO_C2C_ACTUAL_INFO_REQUEST_SETTINGS=[
        'yd',
        'yd_new',
        'self_pickup',
        'strizh',
    ],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_c2c_lp_order_tanker_keys',
    consumers=['cargo-c2c/lp_order'],
    clauses=[],
    default_value={
        'tanker_keys_by_args': [
            {
                'required_args': [
                    'delivery_interval_numeric_date_upper',
                    'delivery_interval_time_from',
                    'delivery_interval_time_to',
                ],
                'texts': {
                    'summary': {
                        'key': 'market_express.delivery_interval.summary',
                        'keyset': 'cargo_client_messages',
                    },
                },
            },
            {
                'required_args': ['delivery_interval_numeric_date_lowwer'],
                'texts': {
                    'summary': {
                        'key': (
                            'ndd.delivery_interval_numeric_date_lowwer.summary'
                        ),
                        'keyset': 'cargo_client_messages',
                    },
                },
            },
            {
                'required_args': [],
                'texts': {
                    'summary': {
                        'key': 'delivery.summary',
                        'keyset': 'cargo_client_messages',
                    },
                },
            },
        ],
    },
    is_config=True,
)
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.now('2021-02-25T10:00:00')
@pytest.mark.parametrize(
    'actual_delivery_interval, expected_summary',
    [
        pytest.param(
            {},
            'Курьер завтра с 10:00 до 12:00',
            marks=pytest.mark.config(
                CARGO_C2C_ENABLE_LP_ACTUAL_INFO_REQUEST=False,
            ),
        ),
        (
            {
                'delivery_date': '2021-02-25',
                'delivery_interval': {
                    'from': '15:00+03:00',
                    'to': '17:00+03:00',
                },
            },
            'Курьер сегодня с 15:00 до 17:00',
        ),
        (
            {
                'delivery_date': '2021-02-26',
                'delivery_interval': {
                    'from': '13:00+03:00',
                    'to': '15:00+03:00',
                },
            },
            'Курьер завтра с 13:00 до 15:00',
        ),
        (
            {
                'delivery_date': '2021-02-27',
                'delivery_interval': {
                    'from': '12:00+03:00',
                    'to': '14:00+03:00',
                },
            },
            'Курьер 27.02 с 12:00 до 14:00',
        ),
        (
            {'delivery_date': '2021-02-25', 'delivery_interval': ''},
            'Доставим сегодня',
        ),
        ({'delivery_date': '2021-02-26'}, 'Доставим завтра'),
        ({'delivery_date': '2021-02-27'}, 'Доставим 27.02'),
    ],
)
async def test_actual_info_request(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        default_pa_headers,
        load_json,
        mockserver,
        mock_claims_full,
        mock_order_statuses_history,
        actual_delivery_interval,
        expected_summary,
):
    @mockserver.json_handler(
        '/logistic-platform-admin/api/admin/request/trace',
    )
    def _mock_trace(request):
        resp = load_json('logistic-platform/trace/ndd_order_created.json')
        resp['model']['delivery_interval'] = {
            'Timezone': 'Europe/Moscow',
            'from': 1614322800,
            'to': 1614330000,
        }
        return resp

    @mockserver.json_handler(
        '/logistic-platform-admin/api/admin/request/actual_info',
    )
    def _actual_info(request):
        actual_info_response = {
            'driver_fio': 'Мизин Александр Александрович',
            'driver_phone_number': '+79131234567',
            'car_number': 'а123бв',
        }
        actual_info_response.update(actual_delivery_interval.items())
        return actual_info_response

    await create_logistic_platform_orders()
    mock_order_statuses_history.file_name = 'in_middle_node.json'
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={'delivery_id': 'logistic-platform/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert response.json()['state']['summary'] == expected_summary


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.experiments3(
    name='cargo_c2c_lp_timeline_settings',
    consumers=['cargo-c2c/lp_order'],
    default_value={
        'enabled': True,
        'items': [
            {
                'id': 'accepted',
                'image_tag': 'delivery_timeline_delivery_accepted',
                'image_tag_dark': 'delivery_timeline_delivery_accepted',
                'conditions': [{'status': 'CREATED_IN_PLATFORM'}],
            },
            {
                'id': 'in_stock',
                'image_tag': 'delivery_timeline_delivery_in_stock',
                'image_tag_dark': 'delivery_timeline_delivery_in_stock',
                'conditions': [{'is_reservation_in_first_node': True}],
            },
            {
                'id': 'accepted',
                'image_tag': 'delivery_timeline_delivery_delivering',
                'image_tag_dark': 'delivery_timeline_delivery_delivering',
                'conditions': [{'is_transfer_from_first_node': True}],
            },
            {
                'id': 'accepted',
                'image_tag': 'delivery_timeline_delivery_finished',
                'image_tag_dark': 'delivery_timeline_delivery_finished',
                'conditions': [{'status': 'DELIVERED_FINISH'}],
            },
        ],
    },
    is_config=True,
    clauses=[],
)
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.parametrize(
    'trace_filename, expected_timeline_statuses',
    [
        ('order_created.json', ['passed', 'pending', 'pending', 'pending']),
        ('in_middle_node.json', ['passed', 'passed', 'pending', 'pending']),
        ('delivering.json', ['passed', 'passed', 'passed', 'pending']),
        ('delivered.json', ['passed', 'passed', 'passed', 'passed']),
        ('cancelled.json', []),
        ('returning.json', []),
    ],
)
async def test_timeline(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        default_pa_headers,
        load_json,
        mockserver,
        mock_claims_full,
        mock_logistic_platform,
        mock_order_statuses_history,
        trace_filename,
        expected_timeline_statuses,
):
    await create_logistic_platform_orders()
    mock_logistic_platform.file_name = trace_filename
    mock_order_statuses_history.file_name = trace_filename

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={'delivery_id': 'logistic-platform/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200

    timeline_statuses = []
    if 'timeline' in response.json()['state']:
        for status in response.json()['state']['timeline']['horizontal']:
            timeline_statuses.append(status['status'])

    assert timeline_statuses == expected_timeline_statuses

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/deliveries',
        json={
            'deliveries': [
                {
                    'delivery_id': (
                        'logistic-platform/' + get_default_order_id()
                    ),
                    'etag': '9e9b21bbc7ba416b8bce63707c3caca3',
                },
            ],
        },
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200

    timeline_statuses = []
    if 'timeline' in response.json()['deliveries'][0]['state']:
        for status in response.json()['deliveries'][0]['state']['timeline'][
                'horizontal'
        ]:
            timeline_statuses.append(status['status'])

    assert timeline_statuses == expected_timeline_statuses


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.experiments3(
    name='cargo_c2c_lp_timeline_settings',
    consumers=['cargo-c2c/lp_order'],
    default_value={
        'enabled': True,
        'reverse_filling': True,
        'items': [
            {
                'id': 'accepted',
                'image_tag': 'delivery_timeline_delivery_finished',
                'image_tag_dark': 'delivery_timeline_delivery_finished',
                'conditions': [{'status': 'DELIVERED_FINISH'}],
            },
            {
                'id': 'accepted',
                'image_tag': 'delivery_timeline_delivery_delivering',
                'image_tag_dark': 'delivery_timeline_delivery_delivering',
                'conditions': [{'is_transfer_from_first_node': True}],
            },
            {
                'id': 'in_stock',
                'image_tag': 'delivery_timeline_delivery_in_stock',
                'image_tag_dark': 'delivery_timeline_delivery_in_stock',
                'conditions': [{'is_reservation_in_first_node': True}],
            },
            {
                'id': 'accepted',
                'image_tag': 'delivery_timeline_delivery_accepted',
                'image_tag_dark': 'delivery_timeline_delivery_accepted',
                'conditions': [{'status': 'CREATED_IN_PLATFORM'}],
            },
        ],
    },
    is_config=True,
    clauses=[],
)
async def test_reverse_timeline(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        default_pa_headers,
        load_json,
        mockserver,
        mock_claims_full,
        mock_logistic_platform,
        mock_order_statuses_history,
):
    await create_logistic_platform_orders()
    mock_logistic_platform.file_name = 'in_middle_node.json'
    mock_order_statuses_history.file_name = 'in_middle_node.json'

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={'delivery_id': 'logistic-platform/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200

    timeline_statuses = []
    if 'timeline' in response.json()['state']:
        for status in response.json()['state']['timeline']['horizontal']:
            timeline_statuses.append(status['status'])

    assert timeline_statuses == ['pending', 'pending', 'passed', 'passed']


@pytest.mark.now('2022-04-13T01:00:00')
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.parametrize(
    'restrictions, timetable',
    [
        (
            [
                {'day': 31, 'time_from': 1000, 'time_to': 2000},
                {'day': 96, 'time_from': 1000, 'time_to': 1800},
            ],
            'Пн.-Пт.: 10:00-20:00\nСб.-Вс.: 10:00-18:00',
        ),
        (
            [{'day': 127, 'time_from': 700, 'time_to': 2000}],
            'Ежедневно: 7:00-20:00',
        ),
        (
            [
                {'day': 1, 'time_from': 700, 'time_to': 2000},
                {'day': 2, 'time_from': 700, 'time_to': 2000},
                {'day': 32, 'time_from': 700, 'time_to': 2000},
            ],
            'Пн.: 7:00-20:00\nВт.: 7:00-20:00\nСр.: выходной\n'
            'Чт.: выходной\nПт.: выходной\nСб.: 7:00-20:00\nВс.: выходной',
        ),
    ],
)
async def test_self_pickup(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        default_pa_headers,
        load_json,
        mockserver,
        mock_claims_full,
        mock_order_statuses_history,
        restrictions,
        timetable,
):
    @mockserver.json_handler(
        '/logistic-platform-admin/api/admin/request/trace',
    )
    def _mock_trace(request):
        response = load_json(
            'logistic-platform/trace/self_pickup_order_created.json',
        )
        response['model']['stations'][0]['timetable_input'][
            'restrictions'
        ] = restrictions
        response['model']['stations'][0]['timetable_output'][
            'restrictions'
        ] = restrictions
        return response

    await create_logistic_platform_orders()
    mock_order_statuses_history.file_name = 'in_middle_node.json'
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={'delivery_id': 'logistic-platform/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert response.json() == {
        'etag': matching.AnyString(),
        'state': {
            'active_route_points': [0],
            'context': {
                'is_performer_position_available': False,
                'original_order_id': '9bcf92d9-72d9-42b4-92e7-eb5ae485e36a',
                'display_targets': ['multiorder'],
            },
            'description': 'Заказ принят',
            'meta': {
                'order_provider_id': 'logistic-platform',
                'order_status': 'VALIDATING',
                'roles': ['initiator'],
                'tariff_class': '',
            },
            'icon_strategy': {
                'image_tag': 'delivery_market_icon_for_delivery_state',
                'type': 'remote_image',
            },
            'primary_actions': [],
            'secondary_actions': [],
            'sorted_route_points': [
                {
                    'area_description': '',
                    'coordinates': [37.605683, 55.608427],
                    'full_text': '',
                    'short_text': '',
                    'type': 'destination',
                    'uri': 'ymapsbm1://geo?ll=55.608427%2C37.605683',
                    'visit_status': 'pending',
                },
            ],
            'summary': 'сегодня в пункте выдачи',
            'content_sections': [
                {
                    'id': matching.AnyString(),
                    'items': [
                        {
                            'id': matching.AnyString(),
                            'lead_icon': {
                                'image_tag': 'delivery_shopping_cart',
                            },
                            'title': {
                                'color': 'TextMain',
                                'max_lines': 1,
                                'text': 'Заказ из TestAPI&Co',
                                'typography': 'body2',
                            },
                            'trail_subtitle': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'К оплате',
                                'typography': 'caption1',
                            },
                            'trail_text': {
                                'color': 'TextMain',
                                'max_lines': 1,
                                'text': '990 ₽',
                                'typography': 'body2',
                            },
                            'type': 'list_item',
                        },
                        {'id': matching.AnyString(), 'type': 'separator'},
                        {
                            'id': matching.AnyString(),
                            'lead_icon': {'image_tag': 'delivery_clock'},
                            'subtitle': {
                                'color': 'TextMain',
                                'max_lines': 1,
                                'text': 'Хранится до 19 Апреля 20:00',
                                'typography': 'body2',
                            },
                            'title': {
                                'color': '',
                                'max_lines': 0,
                                'text': '',
                                'typography': '',
                            },
                            'type': 'list_item',
                        },
                        {
                            'id': matching.AnyString(),
                            'title': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Пункт выдачи',
                                'typography': 'caption1',
                            },
                            'type': 'header',
                        },
                        {
                            'id': matching.AnyString(),
                            'lead_icon': {'image_tag': 'delivery_point'},
                            'subtitle': {
                                'color': 'TextMain',
                                'max_lines': 1,
                                'text': 'Садовническая улица',
                                'typography': 'body2',
                            },
                            'title': {
                                'color': '',
                                'max_lines': 0,
                                'text': '',
                                'typography': '',
                            },
                            'trail_payload': {
                                'buffer': 'Садовническая улица',
                                'in_app_notification_text': 'Адрес скопирован',
                                'type': 'copy-payload',
                            },
                            'type': 'list_item',
                        },
                        {'id': matching.AnyString(), 'type': 'separator'},
                        {
                            'id': matching.AnyString(),
                            'lead_icon': {
                                'image_tag': 'delivery_comment_outline',
                            },
                            'subtitle': {
                                'color': 'TextMain',
                                'max_lines': 4,
                                'text': 'Вход со стороны улицы Кооперативная.',
                                'typography': 'body2',
                            },
                            'title': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Как добраться',
                                'typography': 'caption1',
                            },
                            'type': 'list_item',
                        },
                        {'id': matching.AnyString(), 'type': 'separator'},
                        {
                            'id': matching.AnyString(),
                            'lead_icon': {'image_tag': 'delivery_timetable'},
                            'subtitle': {
                                'color': 'TextMain',
                                'max_lines': 7,
                                'text': timetable,
                                'typography': 'body2',
                            },
                            'title': {
                                'color': '',
                                'max_lines': 0,
                                'text': '',
                                'typography': '',
                            },
                            'type': 'list_item',
                        },
                        {
                            'id': matching.AnyString(),
                            'title': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Получатель',
                                'typography': 'caption1',
                            },
                            'type': 'header',
                        },
                        {
                            'id': matching.AnyString(),
                            'lead_icon': {'image_tag': 'delivery_person'},
                            'subtitle': {
                                'color': 'TextMain',
                                'max_lines': 1,
                                'text': 'Галина ',
                                'typography': 'body2',
                            },
                            'title': {
                                'color': '',
                                'max_lines': 0,
                                'text': '',
                                'typography': '',
                            },
                            'type': 'list_item',
                        },
                        {'id': matching.AnyString(), 'type': 'separator'},
                        {
                            'id': matching.AnyString(),
                            'lead_icon': {'image_tag': 'delivery_phone'},
                            'subtitle': {
                                'color': 'TextMain',
                                'max_lines': 1,
                                'text': '+71111111111',
                                'typography': 'body2',
                            },
                            'title': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Телефон для связи',
                                'typography': 'caption1',
                            },
                            'type': 'list_item',
                        },
                    ],
                },
            ],
        },
    }


@pytest.mark.now('2022-04-13T01:00:00')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_c2c_lp_content_sections',
    consumers=['cargo-c2c/lp_order'],
    clauses=[],
    default_value={
        'content_sections': [
            {
                'id': 'main',
                'items_blocks': [
                    {'name': 'self_pickup_sender'},
                    {'name': 'self_pickup_recipient'},
                    {'name': 'self_pickup_recipient_station'},
                    {'name': 'self_pickup_sender_station'},
                    {'name': 'delivery_payment'},
                    {'name': 'c2c_package'},
                    {'name': 'c2c_details'},
                    {'name': 'c2c_dropoff_code'},
                ],
            },
        ],
        'enabled': True,
    },
    is_config=True,
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_c2c_lp_actions_control',
    consumers=['cargo-c2c/lp_order'],
    clauses=[],
    default_value={
        'deliveries_actions': [],
        'shared_route_actions': [],
        'state_primary_actions': [
            'source_station_call',
            'destination_station_call',
        ],
        'state_secondary_actions': ['support'],
    },
    is_config=True,
)
@pytest.mark.experiments3(filename='experiment.json')
async def test_logistic_platform_c2c(
        taxi_cargo_c2c,
        create_logistic_platform_c2c_orders,
        get_default_order_id,
        default_pa_headers,
        load_json,
        mockserver,
        mock_claims_full,
        mock_logistic_platform,
        mock_order_statuses_history,
):
    order_id = await create_logistic_platform_c2c_orders()
    mock_logistic_platform.file_name = 'self_pickup_order_created.json'
    mock_order_statuses_history.file_name = 'in_middle_node.json'
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={'delivery_id': 'logistic-platform-c2c/' + order_id},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert response.json()['state']['content_sections'] == [
        {
            'id': matching.AnyString(),
            'items': [
                {
                    'id': matching.AnyString(),
                    'title': {
                        'color': 'TextMinor',
                        'max_lines': 1,
                        'text': 'Отправитель',
                        'typography': 'caption1',
                    },
                    'type': 'header',
                },
                {
                    'id': matching.AnyString(),
                    'lead_icon': {'image_tag': 'delivery_person'},
                    'subtitle': {
                        'color': 'TextMain',
                        'max_lines': 1,
                        'text': 'Иван ',
                        'typography': 'body2',
                    },
                    'title': {
                        'color': '',
                        'max_lines': 0,
                        'text': '',
                        'typography': '',
                    },
                    'type': 'list_item',
                },
                {'id': matching.AnyString(), 'type': 'separator'},
                {
                    'id': matching.AnyString(),
                    'lead_icon': {'image_tag': 'delivery_phone'},
                    'subtitle': {
                        'color': 'TextMain',
                        'max_lines': 1,
                        'text': '+70000000002',
                        'typography': 'body2',
                    },
                    'title': {
                        'color': 'TextMinor',
                        'max_lines': 1,
                        'text': 'Телефон для связи',
                        'typography': 'caption1',
                    },
                    'type': 'list_item',
                },
                {
                    'id': matching.AnyString(),
                    'title': {
                        'color': 'TextMinor',
                        'max_lines': 1,
                        'text': 'Получатель',
                        'typography': 'caption1',
                    },
                    'type': 'header',
                },
                {
                    'id': matching.AnyString(),
                    'lead_icon': {'image_tag': 'delivery_person'},
                    'subtitle': {
                        'color': 'TextMain',
                        'max_lines': 1,
                        'text': 'Галина ',
                        'typography': 'body2',
                    },
                    'title': {
                        'color': '',
                        'max_lines': 0,
                        'text': '',
                        'typography': '',
                    },
                    'type': 'list_item',
                },
                {'id': matching.AnyString(), 'type': 'separator'},
                {
                    'id': matching.AnyString(),
                    'lead_icon': {'image_tag': 'delivery_phone'},
                    'subtitle': {
                        'color': 'TextMain',
                        'max_lines': 1,
                        'text': '+71111111111',
                        'typography': 'body2',
                    },
                    'title': {
                        'color': 'TextMinor',
                        'max_lines': 1,
                        'text': 'Телефон для связи',
                        'typography': 'caption1',
                    },
                    'type': 'list_item',
                },
                {
                    'id': matching.AnyString(),
                    'title': {
                        'color': 'TextMinor',
                        'max_lines': 1,
                        'text': 'Пункт выдачи',
                        'typography': 'caption1',
                    },
                    'type': 'header',
                },
                {
                    'id': matching.AnyString(),
                    'lead_icon': {'image_tag': 'delivery_point'},
                    'subtitle': {
                        'color': 'TextMain',
                        'max_lines': 1,
                        'text': 'Садовническая улица',
                        'typography': 'body2',
                    },
                    'title': {
                        'color': '',
                        'max_lines': 0,
                        'text': '',
                        'typography': '',
                    },
                    'trail_payload': {
                        'buffer': 'Садовническая улица',
                        'in_app_notification_text': 'Адрес скопирован',
                        'type': 'copy-payload',
                    },
                    'type': 'list_item',
                },
                {'id': matching.AnyString(), 'type': 'separator'},
                {
                    'id': matching.AnyString(),
                    'lead_icon': {'image_tag': 'delivery_comment_outline'},
                    'subtitle': {
                        'color': 'TextMain',
                        'max_lines': 4,
                        'text': 'Вход со стороны улицы Кооперативная.',
                        'typography': 'body2',
                    },
                    'title': {
                        'color': 'TextMinor',
                        'max_lines': 1,
                        'text': 'Как добраться',
                        'typography': 'caption1',
                    },
                    'type': 'list_item',
                },
                {'id': matching.AnyString(), 'type': 'separator'},
                {
                    'id': matching.AnyString(),
                    'lead_icon': {'image_tag': 'delivery_timetable'},
                    'subtitle': {
                        'color': 'TextMain',
                        'max_lines': 7,
                        'text': 'Пн.-Пт.: 10:00-20:00\nСб.-Вс.: 10:00-18:00',
                        'typography': 'body2',
                    },
                    'title': {
                        'color': '',
                        'max_lines': 0,
                        'text': '',
                        'typography': '',
                    },
                    'type': 'list_item',
                },
                {
                    'id': matching.AnyString(),
                    'title': {
                        'color': 'TextMinor',
                        'max_lines': 1,
                        'text': 'Пункт приема',
                        'typography': 'caption1',
                    },
                    'type': 'header',
                },
                {
                    'id': matching.AnyString(),
                    'lead_icon': {'image_tag': 'delivery_point'},
                    'subtitle': {
                        'color': 'TextMain',
                        'max_lines': 1,
                        'text': 'Садовническая улица',
                        'typography': 'body2',
                    },
                    'title': {
                        'color': '',
                        'max_lines': 0,
                        'text': '',
                        'typography': '',
                    },
                    'trail_payload': {
                        'buffer': 'Садовническая улица',
                        'in_app_notification_text': 'Адрес скопирован',
                        'type': 'copy-payload',
                    },
                    'type': 'list_item',
                },
                {'id': matching.AnyString(), 'type': 'separator'},
                {
                    'id': matching.AnyString(),
                    'lead_icon': {'image_tag': 'delivery_timetable'},
                    'subtitle': {
                        'color': 'TextMain',
                        'max_lines': 7,
                        'text': 'Ежедневно: 6:00-23:00',
                        'typography': 'body2',
                    },
                    'title': {
                        'color': '',
                        'max_lines': 0,
                        'text': '',
                        'typography': '',
                    },
                    'type': 'list_item',
                },
                {
                    'id': matching.AnyString(),
                    'lead_icon': {'image_tag': 'delivery_payment_default'},
                    'title': {
                        'color': 'TextMain',
                        'max_lines': 1,
                        'text': 'Доставка',
                        'typography': 'body2',
                    },
                    'trail_text': {
                        'color': 'TextMain',
                        'max_lines': 1,
                        'text': 'Бесплатно',
                        'typography': 'body2',
                    },
                    'type': 'list_item',
                },
                {
                    'id': matching.AnyString(),
                    'lead_icon': {'image_tag': 'delivery_package'},
                    'subtitle': {
                        'color': 'TextMinor',
                        'max_lines': 1,
                        'text': '10 х 10 х 10 см',
                        'typography': 'caption1',
                    },
                    'title': {
                        'color': 'TextMain',
                        'max_lines': 1,
                        'text': 'Посылка',
                        'typography': 'body2',
                    },
                    'type': 'list_item',
                },
                {
                    'id': matching.AnyString(),
                    'lead_icon': {'image_tag': 'delivery_info'},
                    'sections': [
                        {
                            'items': [
                                {'title': 'ООО ПАРК', 'type': 'subtitle'},
                                {'title': 'legal_address', 'type': 'subtitle'},
                                {'title': 'ОГРН: 123', 'type': 'subtitle'},
                                {
                                    'title': 'Часы работы: 9:00-18:00',
                                    'type': 'subtitle',
                                },
                            ],
                        },
                    ],
                    'title': {
                        'color': 'TextMain',
                        'max_lines': 1,
                        'text': 'Детали заказа',
                        'typography': 'body2',
                    },
                    'type': 'details',
                },
                {
                    'id': matching.AnyString(),
                    'lead_icon': {'image_tag': 'delivery_lock'},
                    'subtitle': {
                        'color': 'TextMinor',
                        'max_lines': 1,
                        'text': 'Сообщите сотруднику пункта',
                        'typography': 'caption1',
                    },
                    'title': {
                        'color': 'TextMain',
                        'max_lines': 1,
                        'text': 'Код приема',
                        'typography': 'body2',
                    },
                    'trail_text': {
                        'color': 'TextMain',
                        'max_lines': 1,
                        'text': 'LO-external_order_id_3',
                        'typography': 'body2',
                    },
                    'type': 'list_item',
                },
            ],
        },
    ]
    assert response.json()['state']['primary_actions'] == [
        {
            'communication_method': {
                'phone_number': 'phone_3',
                'type': 'direct_phone_call',
            },
            'title': 'Позвонить в пункт',
            'type': 'performer_call',
        },
        {
            'communication_method': {
                'phone_number': 'phone_1',
                'type': 'direct_phone_call',
            },
            'title': 'Позвонить в пункт',
            'type': 'performer_call',
        },
    ]
    assert response.json()['state']['details']


@pytest.mark.parametrize(
    'unavailable_handle',
    [
        '/logistic-platform-admin/api/admin/request/trace',
        '/logistic-platform-uservices/api/internal/platform/request/info',
        '/logistic-platform-admin/api/internal/platform/request/history',
    ],
)
async def test_error_service(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        default_pa_headers,
        unavailable_handle,
        mockserver,
):
    await create_logistic_platform_orders()

    @mockserver.json_handler(unavailable_handle)
    def _handle(request):
        return mockserver.make_response(status=500)

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={'delivery_id': 'logistic-platform/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 500


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_c2c_lp_order_tanker_keys',
    consumers=['cargo-c2c/lp_order'],
    clauses=[
        {
            'predicate': {
                'init': {
                    'arg_name': 'has_active_cancellation_request',
                    'arg_type': 'bool',
                    'value': True,
                },
                'type': 'eq',
            },
            'title': '',
            'value': {
                'tanker_keys_by_args': [
                    {
                        'required_args': [],
                        'texts': {
                            'summary': {
                                'key': 'delivery.canceling',
                                'keyset': 'cargo_client_messages',
                            },
                        },
                    },
                ],
            },
        },
    ],
    default_value={
        'tanker_keys_by_args': [
            {
                'required_args': [],
                'texts': {
                    'summary': {
                        'key': 'delivery.summary',
                        'keyset': 'cargo_client_messages',
                    },
                },
            },
        ],
    },
    is_config=True,
)
@pytest.mark.experiments3(filename='experiment.json')
async def test_cancel_requested(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        default_pa_headers,
        mockserver,
):
    @mockserver.json_handler('/processing/v1/delivery/order/events')
    def _events(request):
        return {
            'events': [
                {
                    'event_id': '2',
                    'created': '2020-02-25T06:00:00+03:00',
                    'handled': True,
                    'payload': {'kind': 'order-cancel-succeeded'},
                },
            ],
        }

    await create_logistic_platform_orders()
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={'delivery_id': 'logistic-platform/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    response.json()['state']['summary'] == 'Заказ отменяется'
