# pylint: disable=too-many-lines
import copy

import pytest

from testsuite.utils import matching

CARGO_C2C_C2C_FEEDBACK_REASONS_CONFIG = [
    {
        'scores': [1, 2, 3, 4],
        'reason_id': 'too_long_delivery',
        'tanker_key': {
            'key': 'client_message.feedback_action.reasons.too_long_delivery',
            'keyset': 'cargo',
        },
    },
    {
        'scores': [1, 2, 3, 4],
        'allowed_for': [
            {
                'tariffs': ['courier'],
                'taxi_requirements': ['some_undefined_requirement'],
            },
        ],
        'reason_id': 'unable_to_contact',
        'tanker_key': {
            'key': 'client_message.feedback_action.reasons.unable_to_contact',
            'keyset': 'cargo',
        },
    },
    {
        'scores': [1],
        'reason_id': 'order_wasnt_delivered',
        'allowed_for': [
            {
                'tariffs': ['courier'],
                'taxi_requirements': ['door_to_door', 'cargo_loaders'],
            },
        ],
        'tanker_key': {
            'key': (
                'client_message.feedback_action.reasons.order_wasnt_delivered'
            ),
            'keyset': 'cargo',
        },
    },
    {
        'scores': [1, 2, 3, 4],
        'allowed_for': [{'has_comment': True}],
        'reason_id': 'comment',
        'tanker_key': {
            'key': 'client_message.feedback_action.reasons.comment',
            'keyset': 'cargo',
        },
    },
    {
        'scores': [5],
        'reason_id': 'perfect',
        'tanker_key': {
            'key': 'client_message.feedback_action.reasons.perfect',
            'keyset': 'cargo',
        },
        'icon': {
            'active': 'delivery_perfect_active_icon',
            'inactive': 'delivery_perfect_inactive_icon',
        },
    },
]

CARGO_C2C_FEEDBACK_SUBTITLES_CONFIG = [
    {
        'scores': [1, 2, 3],
        'tanker_key': {
            'key': (
                'client_message.feedback_action'
                '.subtitles.what_disappointed_you'
            ),
            'keyset': 'cargo',
        },
    },
    {
        'scores': [4],
        'tanker_key': {
            'key': (
                'client_message.feedback_action'
                '.subtitles.what_spoiled_the_impression'
            ),
            'keyset': 'cargo',
        },
    },
    {
        'scores': [5],
        'tanker_key': {
            'key': (
                'client_message.feedback_action.subtitles.what_did_you_like'
            ),
            'keyset': 'cargo',
        },
    },
]


@pytest.mark.config(
    CARGO_C2C_C2C_FEEDBACK_REASONS=CARGO_C2C_C2C_FEEDBACK_REASONS_CONFIG,
    CARGO_C2C_FEEDBACK_SUBTITLES=CARGO_C2C_FEEDBACK_SUBTITLES_CONFIG,
    CARGO_C2C_REQUIREMENT_IMAGE_TAGS={
        '__default__': 'delivery_requirement_default',
        'door_to_door': 'delivery_door_to_door',
    },
)
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.parametrize(
    'claim_comment,route_comment',
    [(None, None), ('some_somment', None), (None, 'some_comment')],
)
async def test_common_has_comment(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mock_claims_full,
        claim_comment,
        route_comment,
):
    mock_claims_full.tariff = 'courier'

    order_id = await create_cargo_c2c_orders(
        claim_comment=claim_comment, route_comment=route_comment,
    )
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'supported_content_item_types': [
                'list_item',
                'header',
                'separator',
                'postcard',
                'details',
            ],
        },
        headers=default_pa_headers('phone_pd_id_3'),
    )

    assert response.status_code == 200
    assert {
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
                'reason_id': 'order_wasnt_delivered',
                'title': 'Заказ не доставлен',
                'scores': [1],
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
    } in response.json()['state']['primary_actions']


@pytest.mark.config(
    CARGO_C2C_ENABLE_CARGO_CLAIMS_ETA=True,
    CARGO_TYPE_LIMITS={
        'lcv_l': {
            'carrying_capacity_max_kg': 6000,
            'carrying_capacity_min_kg': 1400,
            'height_max_cm': 250,
            'height_min_cm': 180,
            'length_max_cm': 601,
            'length_min_cm': 380,
            'width_max_cm': 250,
            'width_min_cm': 180,
            'requirement_value': 1,
        },
        'lcv_m': {
            'carrying_capacity_max_kg': 6000,
            'carrying_capacity_min_kg': 700,
            'height_max_cm': 230,
            'height_min_cm': 150,
            'length_max_cm': 520,
            'length_min_cm': 260,
            'width_max_cm': 230,
            'width_min_cm': 130,
            'requirement_value': 2,
        },
        'van': {
            'carrying_capacity_max_kg': 2001,
            'carrying_capacity_min_kg': 300,
            'height_max_cm': 201,
            'height_min_cm': 90,
            'length_max_cm': 290,
            'length_min_cm': 170,
            'width_max_cm': 201,
            'width_min_cm': 96,
            'requirement_value': 3,
        },
    },
    CARGO_C2C_C2C_FEEDBACK_REASONS=CARGO_C2C_C2C_FEEDBACK_REASONS_CONFIG,
    CARGO_C2C_FEEDBACK_SUBTITLES=CARGO_C2C_FEEDBACK_SUBTITLES_CONFIG,
    CARGO_C2C_REQUIREMENT_IMAGE_TAGS={
        '__default__': 'delivery_requirement_default',
        'door_to_door': 'delivery_door_to_door',
    },
)
@pytest.mark.experiments3(filename='experiment.json')
async def test_initiator(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mock_claims_full,
):
    mock_claims_full.tariff = 'courier'
    mock_claims_full.current_point = {
        'claim_point_id': 5,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': 'pending',
    }

    order_id = await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'supported_content_item_types': [
                'list_item',
                'header',
                'separator',
                'postcard',
                'details',
            ],
        },
        headers=default_pa_headers('phone_pd_id_3'),
    )

    details_object = {
        'type': 'details',
        'id': matching.uuid_string,
        'title': {
            'color': 'TextMain',
            'max_lines': 1,
            'text': 'Детали заказа',
            'typography': 'body2',
        },
        'subtitle': {
            'color': 'TextMinor',
            'max_lines': 1,
            'text': 'Курьер - 298.8 ₽ - оплачено',
            'typography': 'caption1',
        },
        'lead_icon': {'image_tag': 'delivery_info'},
        'sections': [
            {
                'items': [
                    {
                        'subtitle': 'Ср 23 Сентября 0:01',
                        'title': 'Тариф Курьер',
                        'type': 'subtitle',
                    },
                    {
                        'subtitle': 'Включено',
                        'title': 'Грузчики: 2',
                        'type': 'subtitle',
                    },
                    {
                        'subtitle': 'Размеры кузова',
                        'title': 'Средний кузов',
                        'type': 'subtitle',
                    },
                    {
                        'subtitle': 'Включено',
                        'title': 'От двери до двери',
                        'type': 'subtitle',
                    },
                    {
                        'subtitle': 'Стимость',
                        'title': '298.8 ₽',
                        'type': 'subtitle',
                    },
                    {
                        'subtitle': 'VISA ••••4444',
                        'title': 'Способ оплаты',
                        'type': 'subtitle',
                    },
                ],
            },
            {
                'title': 'Исполнитель',
                'items': [
                    {
                        'title': 'Petr',
                        'subtitle': 'голубой BMW, номер A001AA77',
                        'type': 'subtitle',
                    },
                    {'title': 'ООО ПАРК', 'type': 'subtitle'},
                    {
                        'title': 'Дополнительно о партнере',
                        'items': [
                            {'type': 'subtitle', 'title': 'legal_address'},
                            {'type': 'subtitle', 'title': 'ОГРН: 123'},
                            {
                                'type': 'subtitle',
                                'title': 'Часы работы: 9:00-18:00',
                            },
                        ],
                        'type': 'accordion',
                    },
                ],
            },
        ],
    }

    assert response.status_code == 200
    resp = response.json()
    resp.pop('etag')

    assert resp == {
        'state': {
            'context': {
                'is_performer_position_available': True,
                'display_targets': ['multiorder'],
            },
            'summary': 'Курьер в пути к точке отправления: 1 мин',
            'description': 'голубой BMW',
            'performer': {
                'name': 'Petr',
                'short_name': 'Иван',
                'rating': '4.7',
                'phone': '+7123',
                'photo_url': 'testavatar',
                'vehicle_model': 'BMW',
                'vehicle_number': 'A001AA77',
            },
            'primary_actions': [
                {
                    'type': 'feedback',
                    'title': 'Фидбэк',
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
                            'title': 'Слишком долгая доставка',
                            'scores': [1, 2, 3, 4],
                        },
                        {
                            'reason_id': 'order_wasnt_delivered',
                            'title': 'Заказ не доставлен',
                            'scores': [1],
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
                },
                {
                    'type': 'performer_call',
                    'title': 'Звонок курьеру',
                    'communication_method': {
                        'type': 'voice_forwarding_call',
                        'forwarding_id': 'performer',
                    },
                },
                {
                    'type': 'cancel',
                    'title': 'Отмена доставки',
                    'message': {
                        'body': (
                            'Курьер уже ждет посылку, '
                            'поэтому бесплатная отмена '
                            'недоступна'
                        ),
                        'close_button': {'title': 'Закрыть'},
                        'confirm_button': {
                            'cancel_type': 'paid',
                            'title': 'Отменить платно',
                        },
                        'title': 'Платная отмена',
                    },
                },
                {
                    'type': 'share',
                    'title': 'Поделиться',
                    'sharing_url': matching.AnyString(),
                },
                {
                    'type': 'tips',
                    'choices': [
                        {
                            'type': 'predefined',
                            'decimal_value': '0',
                            'title': 'Без чаевых',
                            'choice_id': matching.AnyString(),
                            'tips_type': 'flat',
                        },
                        {
                            'type': 'predefined',
                            'decimal_value': '20',
                            'title': '20 ₽',
                            'choice_id': matching.AnyString(),
                            'tips_type': 'flat',
                        },
                        {
                            'type': 'predefined',
                            'decimal_value': '30',
                            'title': '30 ₽',
                            'choice_id': matching.AnyString(),
                            'tips_type': 'flat',
                        },
                        {
                            'type': 'predefined',
                            'decimal_value': '50',
                            'title': '50 ₽',
                            'choice_id': matching.AnyString(),
                            'tips_type': 'flat',
                        },
                        {
                            'type': 'manual',
                            'title': 'Другая сумма',
                            'extra_subtitle': 'Сумма, ₽',
                            'min_tips_value': 9.0,
                            'max_tips_value': 400.0,
                            'choice_id': matching.AnyString(),
                            'tips_value_pattern': '%s ₽',
                        },
                    ],
                    'last_choice_id': matching.AnyString(),
                },
                {
                    'type': 'order_more',
                    'title': 'Заказать еще',
                    'vertical': 'delivery',
                    'vertical_trap': True,
                    'sheet_expansion': 'collapsed',
                },
            ],
            'secondary_actions': [],
            'sorted_route_points': [
                {
                    'visit_status': 'visited',
                    'type': 'source',
                    'uri': 'some uri',
                    'coordinates': [1, 1.1],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора 1',
                    'area_description': 'Москва, Россия',
                    'entrance': '4',
                    'comment': 'some comment',
                    'contact': {'phone': 'phone_pd_i'},
                },
                {
                    'visit_status': 'visited',
                    'type': 'destination',
                    'uri': 'some uri',
                    'coordinates': [2, 2.2],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора 2',
                    'area_description': 'Москва, Россия',
                    'entrance': '4',
                    'comment': 'some comment',
                    'contact': {'phone': 'phone_pd_i'},
                },
                {
                    'visit_status': 'pending',
                    'type': 'destination',
                    'uri': 'some uri',
                    'coordinates': [3, 3.3],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора 3',
                    'area_description': 'Москва, Россия',
                    'entrance': '4',
                    'comment': 'some comment',
                    'contact': {'phone': 'phone_pd_i'},
                },
                {
                    'visit_status': 'pending',
                    'type': 'destination',
                    'uri': 'some uri',
                    'coordinates': [4, 4.4],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора 4',
                    'area_description': 'Москва, Россия',
                    'entrance': '4',
                    'comment': 'some comment',
                    'contact': {'phone': 'phone_pd_i'},
                },
                {
                    'visit_status': 'pending',
                    'type': 'destination',
                    'uri': 'some uri',
                    'coordinates': [5, 5.5],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора 5',
                    'area_description': 'Москва, Россия',
                    'entrance': '4',
                    'comment': 'some comment',
                    'contact': {'phone': 'phone_pd_i'},
                },
            ],
            'active_route_points': [2],
            'performer_route': {
                'sorted_route_points': [{'coordinates': [3, 3.3]}],
            },
            'meta': {
                'order_provider_id': 'cargo-c2c',
                'order_status': 'performer_found',
                'roles': ['initiator'],
                'tariff_class': 'courier',
            },
            'content_sections': [
                {
                    'id': matching.uuid_string,
                    'items': [
                        {
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMain',
                                'max_lines': 1,
                                'text': 'Грузчики: 2',
                                'typography': 'body2',
                            },
                            'trail_text': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Включено',
                                'typography': 'caption1',
                            },
                            'type': 'list_item',
                            'lead_icon': {
                                'image_tag': 'delivery_requirement_default',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMain',
                                'max_lines': 1,
                                'text': 'Средний кузов',
                                'typography': 'body2',
                            },
                            'subtitle': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Размеры кузова',
                                'typography': 'caption1',
                            },
                            'trail_text': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Включено',
                                'typography': 'caption1',
                            },
                            'type': 'list_item',
                            'lead_icon': {
                                'image_tag': 'delivery_requirement_default',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMain',
                                'max_lines': 1,
                                'text': 'От двери до двери',
                                'typography': 'body2',
                            },
                            'trail_text': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Включено',
                                'typography': 'caption1',
                            },
                            'type': 'list_item',
                            'lead_icon': {
                                'image_tag': 'delivery_door_to_door',
                            },
                        },
                    ],
                },
                {
                    'id': matching.uuid_string,
                    'items': [
                        {
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMain',
                                'max_lines': 1,
                                'text': 'VISA ••••4444',
                                'typography': 'body2',
                            },
                            'subtitle': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Способ оплаты',
                                'typography': 'caption1',
                            },
                            'type': 'list_item',
                            'lead_icon': {
                                'image_tag': 'delivery_payment_default',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        details_object,
                        {
                            'type': 'header',
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Отправитель',
                                'typography': 'caption1',
                            },
                        },
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'subtitle': {
                                'text': 'phone_pd_i',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'lead_icon': {'image_tag': 'delivery_phone'},
                            'title': {
                                'text': 'Телефон для связи',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'БЦ Аврора 1',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'subtitle': {
                                'text': 'под. 4',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {'image_tag': 'delivery_point_red'},
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'Комментарий',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {
                                'image_tag': 'delivery_comment_outline',
                            },
                            'subtitle': {
                                'text': 'some comment',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                        },
                        {
                            'type': 'header',
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Получатель № 1',
                                'typography': 'caption1',
                            },
                        },
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'subtitle': {
                                'text': 'phone_pd_i',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'lead_icon': {'image_tag': 'delivery_phone'},
                            'title': {
                                'text': 'Телефон для связи',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'БЦ Аврора 2',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'subtitle': {
                                'text': 'под. 4',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {'image_tag': 'delivery_point'},
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'Комментарий',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {
                                'image_tag': 'delivery_comment_outline',
                            },
                            'subtitle': {
                                'text': 'some comment',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                        },
                        {
                            'type': 'header',
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Получатель № 2',
                                'typography': 'caption1',
                            },
                        },
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'subtitle': {
                                'text': 'phone_pd_i',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'lead_icon': {'image_tag': 'delivery_phone'},
                            'title': {
                                'text': 'Телефон для связи',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'БЦ Аврора 3',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'subtitle': {
                                'text': 'под. 4',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {'image_tag': 'delivery_point'},
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'Комментарий',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {
                                'image_tag': 'delivery_comment_outline',
                            },
                            'subtitle': {
                                'text': 'some comment',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                        },
                        {
                            'type': 'header',
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Получатель № 3',
                                'typography': 'caption1',
                            },
                        },
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'subtitle': {
                                'text': 'phone_pd_i',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'lead_icon': {'image_tag': 'delivery_phone'},
                            'title': {
                                'text': 'Телефон для связи',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'БЦ Аврора 4',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'subtitle': {
                                'text': 'под. 4',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {'image_tag': 'delivery_point'},
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'Комментарий',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {
                                'image_tag': 'delivery_comment_outline',
                            },
                            'subtitle': {
                                'text': 'some comment',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                        },
                        {
                            'type': 'header',
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Получатель № 4',
                                'typography': 'caption1',
                            },
                        },
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'subtitle': {
                                'text': 'phone_pd_i',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'lead_icon': {'image_tag': 'delivery_phone'},
                            'title': {
                                'text': 'Телефон для связи',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'БЦ Аврора 5',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'subtitle': {
                                'text': 'под. 4',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {'image_tag': 'delivery_point'},
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'Комментарий',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {
                                'image_tag': 'delivery_comment_outline',
                            },
                            'subtitle': {
                                'text': 'some comment',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                        },
                    ],
                },
            ],
            'details': {
                'sections': [
                    {
                        'items': [
                            {
                                'subtitle': 'Ср 23 Сентября 0:01',
                                'title': 'Тариф Курьер',
                                'type': 'subtitle',
                            },
                            {
                                'subtitle': 'Включено',
                                'title': 'Грузчики: 2',
                                'type': 'subtitle',
                            },
                            {
                                'subtitle': 'Размеры кузова',
                                'title': 'Средний кузов',
                                'type': 'subtitle',
                            },
                            {
                                'subtitle': 'Включено',
                                'title': 'От двери до двери',
                                'type': 'subtitle',
                            },
                            {
                                'subtitle': 'Стимость',
                                'title': '298.8 ₽',
                                'type': 'subtitle',
                            },
                            {
                                'subtitle': 'VISA ••••4444',
                                'title': 'Способ оплаты',
                                'type': 'subtitle',
                            },
                        ],
                    },
                    {
                        'title': 'Исполнитель',
                        'items': [
                            {
                                'title': 'Petr',
                                'subtitle': 'голубой BMW, номер A001AA77',
                                'type': 'subtitle',
                            },
                            {'title': 'ООО ПАРК', 'type': 'subtitle'},
                            {
                                'title': 'Дополнительно о партнере',
                                'items': [
                                    {
                                        'type': 'subtitle',
                                        'title': 'legal_address',
                                    },
                                    {'type': 'subtitle', 'title': 'ОГРН: 123'},
                                    {
                                        'type': 'subtitle',
                                        'title': 'Часы работы: 9:00-18:00',
                                    },
                                ],
                                'type': 'accordion',
                            },
                        ],
                    },
                ],
                'title': 'Детали заказа',
                'subtitle': 'Стоимость доставки 298.8 ₽',
            },
        },
    }


@pytest.mark.config(
    CARGO_C2C_ENABLE_CARGO_CLAIMS_ETA=True,
    CARGO_C2C_ESTIMATE_TIME_TO_FIND_PERFORMER={'courier': {'estimate': 120}},
    CARGO_C2C_PERFORMER_SEARCHING_DESCRIPTION={
        'courier': {
            'key': (
                'c2c.client_message.initiator.performer_not_ready_description'
            ),
        },
    },
)
@pytest.mark.now('2020-09-23T14:44:01.174824+00:00')
@pytest.mark.parametrize(
    'status, expected_description',
    [
        pytest.param(
            'accepted',
            'Курьера искать чуть дольше, чем такси. Пожалуйста, подождите.',
        ),
        pytest.param(
            'performer_lookup',
            'Курьера искать чуть дольше, чем такси. Пожалуйста, подождите.',
        ),
        pytest.param(
            'performer_draft',
            'Курьера искать чуть дольше, чем такси. Пожалуйста, подождите.',
        ),
    ],
)
@pytest.mark.experiments3(filename='experiment.json')
async def test_initiator_description(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mock_claims_full,
        status,
        expected_description,
):
    mock_claims_full.claim_status = status
    mock_claims_full.current_point_id = 1

    order_id = await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'supported_content_item_types': [
                'list_item',
                'header',
                'separator',
                'postcard',
                'details',
            ],
        },
        headers=default_pa_headers('phone_pd_id_3'),
    )
    assert response.status_code == 200
    assert (
        response.json()['state'].get('description', None)
        == expected_description
    )


@pytest.mark.config(
    CARGO_C2C_ENABLE_CARGO_CLAIMS_ETA=True,
    CARGO_C2C_ESTIMATE_TIME_TO_FIND_PERFORMER={'courier': {'estimate': 120}},
)
@pytest.mark.now('2020-09-23T14:44:01.174824+00:00')
@pytest.mark.parametrize(
    'status',
    [
        pytest.param('accepted'),
        pytest.param('performer_lookup'),
        pytest.param('performer_draft'),
    ],
)
@pytest.mark.experiments3(filename='experiment.json')
async def test_initiator_context(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mock_claims_full,
        status,
):
    mock_claims_full.claim_status = status
    mock_claims_full.current_point_id = 1

    order_id = await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'supported_content_item_types': [
                'list_item',
                'header',
                'separator',
                'postcard',
                'details',
            ],
        },
        headers=default_pa_headers('phone_pd_id_3'),
    )
    assert response.status_code == 200
    assert response.json()['state']['context']['performer_search'] == {
        'is_in_progress': True,
        'estimate': 120,
    }


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.parametrize(
    'status, current_point_id, point_visit_status, '
    'expected_summary, expected_description',
    [
        pytest.param(
            'accepted', 1, 'pending', 'Поиск исполнителя', 'голубой BMW',
        ),
        pytest.param(
            'performer_lookup',
            1,
            'pending',
            'Поиск исполнителя',
            'голубой BMW',
        ),
        pytest.param(
            'performer_draft',
            1,
            'pending',
            'Поиск исполнителя',
            'голубой BMW',
        ),
        pytest.param(
            'performer_found',
            1,
            'pending',
            'Курьер в пути к точке отправления',
            'голубой BMW',
        ),
        pytest.param(
            'performer_found',
            1,
            'pending',
            'Курьер в пути к точке отправления: 5 мин',
            'голубой BMW',
            marks=[
                pytest.mark.config(CARGO_C2C_ENABLE_CARGO_CLAIMS_ETA=True),
                pytest.mark.now('2020-09-23T17:44:01+03:00'),
            ],
        ),
        pytest.param(
            'pickup_arrived',
            1,
            'arrived',
            'Ожидание',
            'голубой BMW',
            marks=pytest.mark.now('2020-06-17T22:40:50+0300'),
        ),
        pytest.param(
            'pickup_arrived',
            1,
            'arrived',
            'Платное ожидание',
            'голубой BMW',
            marks=pytest.mark.now('2020-06-17T22:50:50+0300'),
        ),
        pytest.param(
            'ready_for_pickup_confirmation',
            1,
            'arrived',
            'Ожидание',
            'голубой BMW',
            marks=pytest.mark.now('2020-06-17T22:40:50+0300'),
        ),
        pytest.param(
            'ready_for_pickup_confirmation',
            1,
            'arrived',
            'Платное ожидание',
            'голубой BMW',
            marks=pytest.mark.now('2020-06-17T22:50:50+0300'),
        ),
        pytest.param(
            'pickuped',
            2,
            'pending',
            'Курьер в пути к точке получения',
            'голубой BMW',
        ),
        pytest.param(
            'pickuped',
            2,
            'pending',
            'Курьер в пути к точке получения: 5 мин',
            'голубой BMW',
            marks=[
                pytest.mark.config(CARGO_C2C_ENABLE_CARGO_CLAIMS_ETA=True),
                pytest.mark.now('2020-09-23T17:44:01+03:00'),
            ],
        ),
        pytest.param(
            'delivery_arrived',
            2,
            'arrived',
            'Ожидание',
            'голубой BMW',
            marks=pytest.mark.now('2020-06-17T22:40:50+0300'),
        ),
        pytest.param(
            'delivery_arrived',
            2,
            'arrived',
            'Платное ожидание',
            'голубой BMW',
            marks=pytest.mark.now('2020-06-17T22:50:50+0300'),
        ),
        pytest.param(
            'ready_for_delivery_confirmation',
            2,
            'arrived',
            'Ожидание',
            'голубой BMW',
            marks=pytest.mark.now('2020-06-17T22:40:50+0300'),
        ),
        pytest.param(
            'ready_for_delivery_confirmation',
            2,
            'arrived',
            'Платное ожидание',
            'голубой BMW',
            marks=pytest.mark.now('2020-06-17T22:50:50+0300'),
        ),
        pytest.param('delivered', 5, 'visited', 'Доставлено', 'голубой BMW'),
        pytest.param(
            'delivered_finish', 5, 'visited', 'Доставлено', 'голубой BMW',
        ),
        pytest.param(
            'returning',
            1,
            'pending',
            'Курьер возвращает посылку',
            'голубой BMW',
        ),
        pytest.param(
            'return_arrived',
            1,
            'pending',
            'Курьер возвращает посылку',
            'голубой BMW',
        ),
        pytest.param(
            'ready_for_return_confirmation',
            1,
            'arrived',
            'Курьер возвращает посылку',
            'голубой BMW',
        ),
        pytest.param(
            'returned',
            1,
            'visited',
            'Заказ отменен',
            'Заказ успешно возвращён отправителю',
        ),
        pytest.param(
            'returned_finish',
            1,
            'visited',
            'Заказ отменен',
            'Заказ успешно возвращён отправителю',
        ),
        pytest.param(
            'performer_not_found',
            1,
            'pending',
            'Заказ отменен',
            'Исполнитель не найден',
        ),
        pytest.param('failed', 1, 'pending', 'Заказ отменен', 'Ошибка'),
        pytest.param(
            'cancelled',
            1,
            'pending',
            'Заказ отменен',
            'Подскажите причину отмены',
        ),
        pytest.param(
            'cancelled_with_payment',
            1,
            'pending',
            'Заказ отменен',
            'Подскажите причину отмены',
        ),
        pytest.param(
            'cancelled_by_taxi',
            1,
            'pending',
            'Заказ отменен',
            'К сожалению, заказ отменён. '
            'Пожалуйста, закажите доставку ещё раз.',
        ),
        pytest.param(
            'cancelled_with_items_on_hands',
            1,
            'pending',
            'Заказ отменен',
            'К сожалению, заказ отменён. '
            'Пожалуйста, закажите доставку ещё раз.',
        ),
    ],
)
@pytest.mark.experiments3(filename='experiment.json')
async def test_initiator_texts(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mockserver,
        load_json,
        mock_claims_full,
        status,
        current_point_id,
        point_visit_status,
        expected_summary,
        expected_description,
):
    mock_claims_full.claim_status = status
    mock_claims_full.current_point_id = current_point_id
    mock_claims_full.current_point = {
        'claim_point_id': current_point_id,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': point_visit_status,
    }

    order_id = await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'supported_content_item_types': [
                'list_item',
                'header',
                'separator',
                'postcard',
                'details',
            ],
        },
        headers=default_pa_headers('phone_pd_id_3'),
    )
    assert response.status_code == 200
    assert response.json()['state']['summary'] == expected_summary
    assert (
        response.json()['state'].get('description', None)
        == expected_description
    )


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.parametrize('phone_pd_id', ['phone_pd_id_3', 'phone_pd_id_1'])
async def test_delivery_terminated(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mock_claims_full,
        phone_pd_id,
):
    mock_claims_full.claim_status = 'delivered_finish'

    order_id = await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'supported_content_item_types': [
                'list_item',
                'header',
                'separator',
                'postcard',
                'details',
            ],
        },
        headers=default_pa_headers(phone_pd_id),
    )
    assert response.status_code == 200
    assert response.json()['state']['context']['present_as_completed']


@pytest.mark.config(
    CARGO_C2C_ENABLE_CARGO_CLAIMS_ETA=True,
    CARGO_TYPE_LIMITS={
        'lcv_l': {
            'carrying_capacity_max_kg': 6000,
            'carrying_capacity_min_kg': 1400,
            'height_max_cm': 250,
            'height_min_cm': 180,
            'length_max_cm': 601,
            'length_min_cm': 380,
            'width_max_cm': 250,
            'width_min_cm': 180,
            'requirement_value': 1,
        },
        'lcv_m': {
            'carrying_capacity_max_kg': 6000,
            'carrying_capacity_min_kg': 700,
            'height_max_cm': 230,
            'height_min_cm': 150,
            'length_max_cm': 520,
            'length_min_cm': 260,
            'width_max_cm': 230,
            'width_min_cm': 130,
            'requirement_value': 2,
        },
        'van': {
            'carrying_capacity_max_kg': 2001,
            'carrying_capacity_min_kg': 300,
            'height_max_cm': 201,
            'height_min_cm': 90,
            'length_max_cm': 290,
            'length_min_cm': 170,
            'width_max_cm': 201,
            'width_min_cm': 96,
            'requirement_value': 3,
        },
    },
    CARGO_C2C_C2C_FEEDBACK_REASONS=CARGO_C2C_C2C_FEEDBACK_REASONS_CONFIG,
    CARGO_C2C_FEEDBACK_SUBTITLES=CARGO_C2C_FEEDBACK_SUBTITLES_CONFIG,
    CARGO_C2C_REQUIREMENT_IMAGE_TAGS={
        '__default__': 'delivery_requirement_default',
        'door_to_door': 'delivery_door_to_door',
    },
)
@pytest.mark.config(CARGO_C2C_ENABLE_CARGO_CLAIMS_ETA=True)
@pytest.mark.experiments3(filename='experiment.json')
async def test_sender(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mock_claims_full,
):
    mock_claims_full.current_point = {
        'claim_point_id': 5,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': 'pending',
    }

    order_id = await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'supported_content_item_types': [
                'list_item',
                'header',
                'separator',
                'postcard',
                'details',
            ],
        },
        headers=default_pa_headers('phone_pd_id_1'),
    )

    details_object = {
        'type': 'details',
        'id': matching.uuid_string,
        'title': {
            'color': 'TextMain',
            'max_lines': 1,
            'text': 'Детали заказа',
            'typography': 'body2',
        },
        'subtitle': {
            'color': 'TextMinor',
            'max_lines': 1,
            'text': 'Курьер - оплачено',
            'typography': 'caption1',
        },
        'lead_icon': {'image_tag': 'delivery_info'},
        'sections': [
            {
                'items': [
                    {
                        'subtitle': 'Ср 23 Сентября 0:01',
                        'title': 'Тариф Курьер',
                        'type': 'subtitle',
                    },
                    {
                        'subtitle': 'Включено',
                        'title': 'Грузчики: 2',
                        'type': 'subtitle',
                    },
                    {
                        'subtitle': 'Размеры кузова',
                        'title': 'Средний кузов',
                        'type': 'subtitle',
                    },
                    {
                        'subtitle': 'Включено',
                        'title': 'От двери до двери',
                        'type': 'subtitle',
                    },
                ],
            },
            {
                'title': 'Исполнитель',
                'items': [
                    {
                        'title': 'Petr',
                        'subtitle': 'голубой BMW, номер A001AA77',
                        'type': 'subtitle',
                    },
                    {'title': 'ООО ПАРК', 'type': 'subtitle'},
                    {
                        'title': 'Дополнительно о партнере',
                        'items': [
                            {'type': 'subtitle', 'title': 'legal_address'},
                            {'type': 'subtitle', 'title': 'ОГРН: 123'},
                            {
                                'type': 'subtitle',
                                'title': 'Часы работы: 9:00-18:00',
                            },
                        ],
                        'type': 'accordion',
                    },
                ],
            },
        ],
    }

    assert response.status_code == 200
    resp = response.json()
    resp.pop('etag')
    assert resp == {
        'state': {
            'context': {
                'is_performer_position_available': True,
                'display_targets': ['multiorder'],
            },
            'summary': 'Курьер в пути к точке отправления: ~1 мин',
            'description': 'голубой BMW',
            'performer': {
                'name': 'Petr',
                'short_name': 'Иван',
                'rating': '4.7',
                'phone': '+7123',
                'photo_url': 'testavatar',
                'vehicle_model': 'BMW',
                'vehicle_number': 'A001AA77',
            },
            'primary_actions': [
                {
                    'type': 'feedback',
                    'title': 'Фидбэк',
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
                            'title': 'Слишком долгая доставка',
                            'scores': [1, 2, 3, 4],
                        },
                        {
                            'reason_id': 'order_wasnt_delivered',
                            'title': 'Заказ не доставлен',
                            'scores': [1],
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
                },
                {
                    'type': 'performer_call',
                    'title': 'Звонок курьеру',
                    'communication_method': {
                        'type': 'voice_forwarding_call',
                        'forwarding_id': 'performer',
                    },
                },
                {
                    'type': 'share',
                    'title': 'Поделиться',
                    'sharing_url': matching.AnyString(),
                },
            ],
            'secondary_actions': [],
            'sorted_route_points': [
                {
                    'visit_status': 'visited',
                    'type': 'source',
                    'uri': 'some uri',
                    'coordinates': [1, 1.1],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора 1',
                    'area_description': 'Москва, Россия',
                    'entrance': '4',
                    'comment': 'some comment',
                    'contact': {'phone': 'phone_pd_i'},
                },
                {
                    'visit_status': 'visited',
                    'type': 'destination',
                    'uri': 'some uri',
                    'coordinates': [2, 2.2],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора 2',
                    'area_description': 'Москва, Россия',
                },
                {
                    'visit_status': 'pending',
                    'type': 'destination',
                    'uri': 'some uri',
                    'coordinates': [3, 3.3],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора 3',
                    'area_description': 'Москва, Россия',
                },
                {
                    'visit_status': 'pending',
                    'type': 'destination',
                    'uri': 'some uri',
                    'coordinates': [4, 4.4],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора 4',
                    'area_description': 'Москва, Россия',
                },
                {
                    'visit_status': 'pending',
                    'type': 'destination',
                    'uri': 'some uri',
                    'coordinates': [5, 5.5],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора 5',
                    'area_description': 'Москва, Россия',
                },
            ],
            'active_route_points': [2],
            'performer_route': {
                'sorted_route_points': [{'coordinates': [3, 3.3]}],
            },
            'meta': {
                'order_provider_id': 'cargo-c2c',
                'order_status': 'performer_found',
                'roles': ['sender'],
                'tariff_class': 'courier',
            },
            'content_sections': [
                {
                    'id': matching.uuid_string,
                    'items': [
                        {
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMain',
                                'max_lines': 1,
                                'text': 'Грузчики: 2',
                                'typography': 'body2',
                            },
                            'trail_text': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Включено',
                                'typography': 'caption1',
                            },
                            'type': 'list_item',
                            'lead_icon': {
                                'image_tag': 'delivery_requirement_default',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMain',
                                'max_lines': 1,
                                'text': 'Средний кузов',
                                'typography': 'body2',
                            },
                            'subtitle': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Размеры кузова',
                                'typography': 'caption1',
                            },
                            'trail_text': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Включено',
                                'typography': 'caption1',
                            },
                            'type': 'list_item',
                            'lead_icon': {
                                'image_tag': 'delivery_requirement_default',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMain',
                                'max_lines': 1,
                                'text': 'От двери до двери',
                                'typography': 'body2',
                            },
                            'trail_text': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Включено',
                                'typography': 'caption1',
                            },
                            'type': 'list_item',
                            'lead_icon': {
                                'image_tag': 'delivery_door_to_door',
                            },
                        },
                    ],
                },
                {
                    'id': matching.uuid_string,
                    'items': [
                        {
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMain',
                                'max_lines': 1,
                                'text': 'Уже оплачено',
                                'typography': 'body2',
                            },
                            'type': 'list_item',
                            'lead_icon': {
                                'image_tag': 'delivery_payment_default',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        details_object,
                        {
                            'type': 'header',
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Отправитель',
                                'typography': 'caption1',
                            },
                        },
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'subtitle': {
                                'text': 'phone_pd_i',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'lead_icon': {'image_tag': 'delivery_phone'},
                            'title': {
                                'text': 'Телефон для связи',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'БЦ Аврора 1',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'subtitle': {
                                'text': 'под. 4',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {'image_tag': 'delivery_point_red'},
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'Комментарий',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {
                                'image_tag': 'delivery_comment_outline',
                            },
                            'subtitle': {
                                'text': 'some comment',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                        },
                        {
                            'type': 'header',
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Первый получатель',
                                'typography': 'caption1',
                            },
                        },
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'subtitle': {
                                'text': 'phone_pd_i',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'lead_icon': {'image_tag': 'delivery_phone'},
                            'title': {
                                'text': 'Телефон для связи',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'БЦ Аврора 2',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'lead_icon': {'image_tag': 'delivery_point'},
                        },
                        {
                            'type': 'header',
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Второй получатель',
                                'typography': 'caption1',
                            },
                        },
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'subtitle': {
                                'text': 'phone_pd_i',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'lead_icon': {'image_tag': 'delivery_phone'},
                            'title': {
                                'text': 'Телефон для связи',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'БЦ Аврора 3',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'lead_icon': {'image_tag': 'delivery_point'},
                        },
                        {
                            'type': 'header',
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Третий получатель',
                                'typography': 'caption1',
                            },
                        },
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'subtitle': {
                                'text': 'phone_pd_i',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'lead_icon': {'image_tag': 'delivery_phone'},
                            'title': {
                                'text': 'Телефон для связи',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'БЦ Аврора 4',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'lead_icon': {'image_tag': 'delivery_point'},
                        },
                    ],
                },
            ],
            'details': {
                'sections': [
                    {
                        'items': [
                            {
                                'subtitle': 'Ср 23 Сентября 0:01',
                                'title': 'Тариф Курьер',
                                'type': 'subtitle',
                            },
                            {
                                'subtitle': 'Включено',
                                'title': 'Грузчики: 2',
                                'type': 'subtitle',
                            },
                            {
                                'subtitle': 'Размеры кузова',
                                'title': 'Средний кузов',
                                'type': 'subtitle',
                            },
                            {
                                'subtitle': 'Включено',
                                'title': 'От двери до двери',
                                'type': 'subtitle',
                            },
                        ],
                    },
                    {
                        'title': 'Исполнитель',
                        'items': [
                            {
                                'title': 'Petr',
                                'subtitle': 'голубой BMW, номер A001AA77',
                                'type': 'subtitle',
                            },
                            {'title': 'ООО ПАРК', 'type': 'subtitle'},
                            {
                                'title': 'Дополнительно о партнере',
                                'items': [
                                    {
                                        'type': 'subtitle',
                                        'title': 'legal_address',
                                    },
                                    {'type': 'subtitle', 'title': 'ОГРН: 123'},
                                    {
                                        'type': 'subtitle',
                                        'title': 'Часы работы: 9:00-18:00',
                                    },
                                ],
                                'type': 'accordion',
                            },
                        ],
                    },
                ],
                'title': 'Детали заказа',
            },
        },
    }


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.parametrize(
    'status, current_point_id, point_visit_status, '
    'expected_summary, expected_description',
    [
        pytest.param('accepted', 1, 'pending', 'Курьер где-то', 'голубой BMW'),
        pytest.param(
            'performer_lookup', 1, 'pending', 'Курьер где-то', 'голубой BMW',
        ),
        pytest.param(
            'performer_draft', 1, 'pending', 'Курьер где-то', 'голубой BMW',
        ),
        pytest.param(
            'performer_found',
            1,
            'pending',
            'Курьер в пути к точке отправления',
            'голубой BMW',
        ),
        pytest.param(
            'performer_found',
            1,
            'pending',
            'Курьер в пути к точке отправления: ~5 мин',
            'голубой BMW',
            marks=[
                pytest.mark.config(CARGO_C2C_ENABLE_CARGO_CLAIMS_ETA=True),
                pytest.mark.now('2020-09-23T17:44:01+03:00'),
            ],
        ),
        pytest.param(
            'pickup_arrived',
            1,
            'arrived',
            'Ожидание',
            'голубой BMW',
            marks=pytest.mark.now('2020-06-17T22:40:50+0300'),
        ),
        pytest.param(
            'pickup_arrived',
            1,
            'arrived',
            'Платное ожидание',
            'голубой BMW',
            marks=pytest.mark.now('2020-06-17T22:50:50+0300'),
        ),
        pytest.param(
            'ready_for_pickup_confirmation',
            1,
            'arrived',
            'Ожидание',
            'голубой BMW',
            marks=pytest.mark.now('2020-06-17T22:40:50+0300'),
        ),
        pytest.param(
            'ready_for_pickup_confirmation',
            1,
            'arrived',
            'Платное ожидание',
            'голубой BMW',
            marks=pytest.mark.now('2020-06-17T22:50:50+0300'),
        ),
        pytest.param(
            'pickuped',
            2,
            'pending',
            'Курьер в пути к точке получения',
            'голубой BMW',
        ),
        pytest.param(
            'pickuped',
            2,
            'pending',
            'Курьер в пути к точке получения: ~5 мин',
            'голубой BMW',
            marks=[
                pytest.mark.config(CARGO_C2C_ENABLE_CARGO_CLAIMS_ETA=True),
                pytest.mark.now('2020-09-23T17:44:01+03:00'),
            ],
        ),
        pytest.param(
            'delivery_arrived',
            2,
            'arrived',
            'Курьер приехал на точку получения',
            'голубой BMW',
        ),
        pytest.param(
            'ready_for_delivery_confirmation',
            2,
            'arrived',
            'Курьер приехал на точку получения',
            'голубой BMW',
        ),
        pytest.param('delivered', 5, 'visited', 'Доставлено', 'голубой BMW'),
        pytest.param(
            'delivered_finish', 5, 'visited', 'Доставлено', 'голубой BMW',
        ),
        pytest.param(
            'returning',
            1,
            'pending',
            'Курьер возвращает посылку',
            'голубой BMW',
        ),
        pytest.param(
            'return_arrived',
            1,
            'pending',
            'Курьер возвращает посылку',
            'голубой BMW',
        ),
        pytest.param(
            'ready_for_return_confirmation',
            1,
            'arrived',
            'Курьер возвращает посылку',
            'голубой BMW',
        ),
        pytest.param(
            'returned',
            1,
            'visited',
            'Заказ отменен',
            'Заказ успешно возвращён отправителю',
        ),
        pytest.param(
            'returned_finish',
            1,
            'visited',
            'Заказ отменен',
            'Заказ успешно возвращён отправителю',
        ),
        pytest.param(
            'performer_not_found',
            1,
            'pending',
            'Заказ отменен',
            'Исполнитель не найден',
        ),
        pytest.param('failed', 1, 'pending', 'Заказ отменен', 'Ошибка'),
        pytest.param(
            'cancelled',
            1,
            'pending',
            'Заказ отменен',
            'К сожалению, заказ отменён. '
            'Пожалуйста, закажите доставку ещё раз.',
        ),
        pytest.param(
            'cancelled_with_payment',
            1,
            'pending',
            'Заказ отменен',
            'К сожалению, заказ отменён. '
            'Пожалуйста, закажите доставку ещё раз.',
        ),
        pytest.param(
            'cancelled_by_taxi',
            1,
            'pending',
            'Заказ отменен',
            'К сожалению, заказ отменён. '
            'Пожалуйста, закажите доставку ещё раз.',
        ),
        pytest.param(
            'cancelled_with_items_on_hands',
            1,
            'pending',
            'Заказ отменен',
            'К сожалению, заказ отменён. '
            'Пожалуйста, закажите доставку ещё раз.',
        ),
    ],
)
async def test_sender_texts(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mockserver,
        load_json,
        mock_claims_full,
        status,
        current_point_id,
        point_visit_status,
        expected_summary,
        expected_description,
):
    mock_claims_full.claim_status = status
    mock_claims_full.current_point_id = current_point_id
    mock_claims_full.current_point = {
        'claim_point_id': current_point_id,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': point_visit_status,
    }

    order_id = await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'supported_content_item_types': [
                'list_item',
                'header',
                'separator',
                'postcard',
                'details',
            ],
        },
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert response.json()['state']['summary'] == expected_summary
    assert (
        response.json()['state'].get('description', None)
        == expected_description
    )


@pytest.mark.now('2020-08-23T14:49:01.174824+00:00')
@pytest.mark.parametrize(
    'status, expected_summary, expected_description',
    [
        pytest.param(
            'accepted', 'Доставка запланирована', 'Ср 23 Сентября 17:49',
        ),
        pytest.param(
            'performer_lookup',
            'Доставка запланирована',
            'Ср 23 Сентября 17:49',
        ),
        pytest.param(
            'performer_draft',
            'Доставка запланирована',
            'Ср 23 Сентября 17:49',
        ),
        pytest.param(
            'performer_found', 'Курьер в пути к точке отправления', None,
        ),
    ],
)
@pytest.mark.experiments3(filename='experiment.json')
async def test_delayed_order(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mockserver,
        load_json,
        mock_claims_full,
        status,
        expected_summary,
        expected_description,
):
    mock_claims_full.claim_status = status
    mock_claims_full.file_name = 'claim_full_response_with_due.json'

    order_id = await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'supported_content_item_types': [
                'list_item',
                'header',
                'separator',
                'postcard',
                'details',
            ],
        },
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp['state']['summary'] == expected_summary
    assert resp['state'].get('description', None) == expected_description

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'supported_content_item_types': [
                'list_item',
                'header',
                'separator',
                'postcard',
                'details',
            ],
        },
        headers=default_pa_headers('phone_pd_id_3'),
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp['state']['summary'] == expected_summary
    assert resp['state'].get('description', None) == expected_description


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.parametrize(
    'phone_pd_id', ['phone_pd_id_1', 'phone_pd_id_2', 'phone_pd_id_3'],
)
async def test_delivery_failed(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        get_default_order_id,
        default_pa_headers,
        mockserver,
        load_json,
        phone_pd_id,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        resp = load_json('claim_full_response.json')
        resp['status'] = 'failed'
        for point in resp['route_points']:
            point['visit_status'] = 'skipped'
        return mockserver.make_response(json=resp)

    @mockserver.json_handler('/cargo-claims/v2/claims/points-eta')
    def _claims_points_eta(request):
        full = load_json('claim_full_response.json')
        points_eta = {
            'id': full['id'],
            'route_points': [],
            'performer_position': [52.569089, 39.60258],
        }

        for point in full['route_points']:
            point.pop('contact', None)
            point.pop('skip_confirmation', None)
            point['visit_status'] = 'skipped'
            points_eta['route_points'].append(point)

        return mockserver.make_response(json=points_eta)

    order_id = await create_cargo_c2c_orders()

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'supported_content_item_types': [
                'list_item',
                'header',
                'separator',
                'postcard',
                'details',
            ],
        },
        headers=default_pa_headers(phone_pd_id),
    )
    assert response.status_code == 200
    resp = response.json()['state']
    assert resp['context']['present_as_completed']
    assert resp['primary_actions'] == []
    assert 'performer' not in resp


@pytest.mark.config(
    CARGO_C2C_ENABLE_CARGO_CLAIMS_ETA=True,
    CARGO_TYPE_LIMITS={
        'lcv_l': {
            'carrying_capacity_max_kg': 6000,
            'carrying_capacity_min_kg': 1400,
            'height_max_cm': 250,
            'height_min_cm': 180,
            'length_max_cm': 601,
            'length_min_cm': 380,
            'width_max_cm': 250,
            'width_min_cm': 180,
            'requirement_value': 1,
        },
        'lcv_m': {
            'carrying_capacity_max_kg': 6000,
            'carrying_capacity_min_kg': 700,
            'height_max_cm': 230,
            'height_min_cm': 150,
            'length_max_cm': 520,
            'length_min_cm': 260,
            'width_max_cm': 230,
            'width_min_cm': 130,
            'requirement_value': 2,
        },
        'van': {
            'carrying_capacity_max_kg': 2001,
            'carrying_capacity_min_kg': 300,
            'height_max_cm': 201,
            'height_min_cm': 90,
            'length_max_cm': 290,
            'length_min_cm': 170,
            'width_max_cm': 201,
            'width_min_cm': 96,
            'requirement_value': 3,
        },
    },
    CARGO_C2C_C2C_FEEDBACK_REASONS=CARGO_C2C_C2C_FEEDBACK_REASONS_CONFIG,
    CARGO_C2C_FEEDBACK_SUBTITLES=CARGO_C2C_FEEDBACK_SUBTITLES_CONFIG,
    CARGO_C2C_REQUIREMENT_IMAGE_TAGS={
        '__default__': 'delivery_requirement_default',
        'door_to_door': 'delivery_door_to_door',
    },
)
@pytest.mark.config(CARGO_C2C_ENABLE_CARGO_CLAIMS_ETA=True)
@pytest.mark.experiments3(filename='experiment.json')
async def test_recipient(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mockserver,
        load_json,
        mock_claims_full,
):
    mock_claims_full.current_point = {
        'claim_point_id': 5,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': 'pending',
    }

    order_id = await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'supported_content_item_types': [
                'list_item',
                'header',
                'separator',
                'postcard',
                'details',
            ],
        },
        headers=default_pa_headers('phone_pd_id_2'),
    )

    details_object = {
        'type': 'details',
        'id': matching.uuid_string,
        'title': {
            'color': 'TextMain',
            'max_lines': 1,
            'text': 'Детали заказа',
            'typography': 'body2',
        },
        'subtitle': {
            'color': 'TextMinor',
            'max_lines': 1,
            'text': 'Курьер - оплачено',
            'typography': 'caption1',
        },
        'lead_icon': {'image_tag': 'delivery_info'},
        'sections': [
            {
                'items': [
                    {
                        'subtitle': 'Ср 23 Сентября 0:01',
                        'title': 'Тариф Курьер',
                        'type': 'subtitle',
                    },
                    {
                        'subtitle': 'Включено',
                        'title': 'Грузчики: 2',
                        'type': 'subtitle',
                    },
                    {
                        'subtitle': 'Размеры кузова',
                        'title': 'Средний кузов',
                        'type': 'subtitle',
                    },
                    {
                        'subtitle': 'Включено',
                        'title': 'От двери до двери',
                        'type': 'subtitle',
                    },
                ],
            },
            {
                'title': 'Исполнитель',
                'items': [
                    {
                        'title': 'Petr',
                        'subtitle': 'голубой BMW, номер A001AA77',
                        'type': 'subtitle',
                    },
                    {'title': 'ООО ПАРК', 'type': 'subtitle'},
                    {
                        'title': 'Дополнительно о партнере',
                        'items': [
                            {'type': 'subtitle', 'title': 'legal_address'},
                            {'type': 'subtitle', 'title': 'ОГРН: 123'},
                            {
                                'type': 'subtitle',
                                'title': 'Часы работы: 9:00-18:00',
                            },
                        ],
                        'type': 'accordion',
                    },
                ],
            },
        ],
    }

    assert response.status_code == 200
    resp = response.json()
    resp.pop('etag')
    assert resp == {
        'state': {
            'content_sections': [
                {
                    'id': matching.uuid_string,
                    'items': [
                        {
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMain',
                                'max_lines': 1,
                                'text': 'Грузчики: 2',
                                'typography': 'body2',
                            },
                            'trail_text': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Включено',
                                'typography': 'caption1',
                            },
                            'type': 'list_item',
                            'lead_icon': {
                                'image_tag': 'delivery_requirement_default',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMain',
                                'max_lines': 1,
                                'text': 'Средний кузов',
                                'typography': 'body2',
                            },
                            'subtitle': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Размеры кузова',
                                'typography': 'caption1',
                            },
                            'trail_text': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Включено',
                                'typography': 'caption1',
                            },
                            'type': 'list_item',
                            'lead_icon': {
                                'image_tag': 'delivery_requirement_default',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMain',
                                'max_lines': 1,
                                'text': 'От двери до двери',
                                'typography': 'body2',
                            },
                            'trail_text': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Включено',
                                'typography': 'caption1',
                            },
                            'type': 'list_item',
                            'lead_icon': {
                                'image_tag': 'delivery_door_to_door',
                            },
                        },
                    ],
                },
                {
                    'id': matching.uuid_string,
                    'items': [
                        {
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMain',
                                'max_lines': 1,
                                'text': 'Уже оплачено',
                                'typography': 'body2',
                            },
                            'type': 'list_item',
                            'lead_icon': {
                                'image_tag': 'delivery_payment_default',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        details_object,
                        {
                            'type': 'header',
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Отправитель',
                                'typography': 'caption1',
                            },
                        },
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'subtitle': {
                                'text': 'phone_pd_i',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'lead_icon': {'image_tag': 'delivery_phone'},
                            'title': {
                                'text': 'Телефон для связи',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'БЦ Аврора 1',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'lead_icon': {'image_tag': 'delivery_point_red'},
                        },
                        {
                            'type': 'header',
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Получатель',
                                'typography': 'caption1',
                            },
                        },
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'subtitle': {
                                'text': 'phone_pd_i',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'lead_icon': {'image_tag': 'delivery_phone'},
                            'title': {
                                'text': 'Телефон для связи',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'БЦ Аврора 5',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'subtitle': {
                                'text': 'под. 4',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {'image_tag': 'delivery_point'},
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'Комментарий',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {
                                'image_tag': 'delivery_comment_outline',
                            },
                            'subtitle': {
                                'text': 'some comment',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                        },
                    ],
                },
            ],
            'details': {
                'sections': [
                    {
                        'items': [
                            {
                                'subtitle': 'Ср 23 Сентября 0:01',
                                'title': 'Тариф Курьер',
                                'type': 'subtitle',
                            },
                            {
                                'subtitle': 'Включено',
                                'title': 'Грузчики: 2',
                                'type': 'subtitle',
                            },
                            {
                                'subtitle': 'Размеры кузова',
                                'title': 'Средний кузов',
                                'type': 'subtitle',
                            },
                            {
                                'subtitle': 'Включено',
                                'title': 'От двери до двери',
                                'type': 'subtitle',
                            },
                        ],
                    },
                    {
                        'title': 'Исполнитель',
                        'items': [
                            {
                                'title': 'Petr',
                                'subtitle': 'голубой BMW, номер A001AA77',
                                'type': 'subtitle',
                            },
                            {'title': 'ООО ПАРК', 'type': 'subtitle'},
                            {
                                'title': 'Дополнительно о партнере',
                                'items': [
                                    {
                                        'type': 'subtitle',
                                        'title': 'legal_address',
                                    },
                                    {'type': 'subtitle', 'title': 'ОГРН: 123'},
                                    {
                                        'type': 'subtitle',
                                        'title': 'Часы работы: 9:00-18:00',
                                    },
                                ],
                                'type': 'accordion',
                            },
                        ],
                    },
                ],
                'title': 'Детали заказа',
            },
            'context': {
                'is_performer_position_available': True,
                'display_targets': ['multiorder'],
            },
            'summary': 'Курьер в пути к точке получения: ~1 мин',
            'description': 'голубой BMW',
            'performer': {
                'name': 'Petr',
                'short_name': 'Иван',
                'rating': '4.7',
                'phone': '+7123',
                'photo_url': 'testavatar',
                'vehicle_model': 'BMW',
                'vehicle_number': 'A001AA77',
            },
            'primary_actions': [
                {
                    'type': 'feedback',
                    'title': 'Фидбэк',
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
                            'title': 'Слишком долгая доставка',
                            'scores': [1, 2, 3, 4],
                        },
                        {
                            'reason_id': 'order_wasnt_delivered',
                            'title': 'Заказ не доставлен',
                            'scores': [1],
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
                },
                {
                    'type': 'performer_call',
                    'title': 'Звонок курьеру',
                    'communication_method': {
                        'type': 'voice_forwarding_call',
                        'forwarding_id': 'performer',
                    },
                },
                {
                    'type': 'share',
                    'title': 'Поделиться',
                    'sharing_url': matching.AnyString(),
                },
            ],
            'secondary_actions': [],
            'sorted_route_points': [
                {
                    'visit_status': 'visited',
                    'type': 'source',
                    'uri': 'some uri',
                    'coordinates': [1, 1.1],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора 1',
                    'area_description': 'Москва, Россия',
                },
                {
                    'visit_status': 'pending',
                    'type': 'destination',
                    'uri': 'some uri',
                    'coordinates': [5, 5.5],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора 5',
                    'area_description': 'Москва, Россия',
                    'entrance': '4',
                    'comment': 'some comment',
                    'contact': {'phone': 'phone_pd_i'},
                },
            ],
            'active_route_points': [1],
            'performer_route': {
                'sorted_route_points': [{'coordinates': [5, 5.5]}],
            },
            'meta': {
                'order_provider_id': 'cargo-c2c',
                'order_status': 'performer_found',
                'roles': ['recipient'],
                'tariff_class': 'courier',
            },
        },
    }


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.parametrize(
    'point_visit_status, resolved_till_point, '
    'expected_summary, expected_description',
    [
        pytest.param(
            'arrived', 4, 'Курьер приехал на точку получения', 'голубой BMW',
        ),
        pytest.param('visited', 6, 'Доставлено', 'голубой BMW'),
        pytest.param(
            'pending', 5, 'Курьер в пути к точке получения', 'голубой BMW',
        ),
        pytest.param(
            'pending',
            5,
            'Курьер в пути к точке получения: ~5 мин',
            'голубой BMW',
            marks=pytest.mark.config(CARGO_C2C_ENABLE_CARGO_CLAIMS_ETA=True),
        ),
        pytest.param(
            'pending', 4, 'Курьер в пути к точке отправления', 'голубой BMW',
        ),
        pytest.param(
            'pending',
            4,
            'Курьер будет у вас через ~5 мин',
            'голубой BMW',
            marks=pytest.mark.config(CARGO_C2C_ENABLE_CARGO_CLAIMS_ETA=True),
        ),
    ],
)
@pytest.mark.now('2020-09-23T14:44:01.174824+00:00')
async def test_recipient_texts(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mockserver,
        load_json,
        point_visit_status,
        resolved_till_point,
        expected_summary,
        expected_description,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        resp = load_json('claim_full_response.json')
        for point in resp['route_points']:
            if point['id'] == 5:
                point['visit_status'] = point_visit_status

        resp['on_the_way_state'] = {
            'current_point': {
                'claim_point_id': resolved_till_point,
                'last_status_change_ts': '2020-06-17T22:39:50+0300',
                'visit_status': 'pending',
            },
        }

        return mockserver.make_response(json=resp)

    @mockserver.json_handler('/cargo-claims/v2/claims/points-eta')
    def _claims_points_eta(request):
        full = load_json('claim_full_response.json')
        points_eta = {
            'id': full['id'],
            'route_points': [],
            'performer_position': [52.569089, 39.60258],
        }

        for point in full['route_points']:
            point.pop('contact', None)
            point.pop('skip_confirmation', None)
            if point['id'] == 5:
                point['visit_status'] = point_visit_status
            points_eta['route_points'].append(point)

        return mockserver.make_response(json=points_eta)

    order_id = await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'supported_content_item_types': [
                'list_item',
                'header',
                'separator',
                'postcard',
                'details',
            ],
        },
        headers=default_pa_headers('phone_pd_id_2'),
    )
    assert response.status_code == 200
    assert response.json()['state']['summary'] == expected_summary
    assert (
        response.json()['state'].get('description', None)
        == expected_description
    )


@pytest.mark.experiments3(filename='experiment.json')
async def test_recipient_delivery_terminated(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        get_default_order_id,
        default_pa_headers,
        mockserver,
        load_json,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        resp = load_json('claim_full_response.json')
        resp['status'] = 'pickuped'
        for point in resp['route_points']:
            if point['id'] == 5:
                point['visit_status'] = 'visited'
        return mockserver.make_response(json=resp)

    @mockserver.json_handler('/cargo-claims/v2/claims/points-eta')
    def _claims_points_eta(request):
        full = load_json('claim_full_response.json')
        points_eta = {
            'id': full['id'],
            'route_points': [],
            'performer_position': [52.569089, 39.60258],
        }

        for point in full['route_points']:
            point.pop('contact', None)
            point.pop('skip_confirmation', None)
            if point['id'] == 5:
                point['visit_status'] = 'visited'
            points_eta['route_points'].append(point)

        return mockserver.make_response(json=points_eta)

    order_id = await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'supported_content_item_types': [
                'list_item',
                'header',
                'separator',
                'postcard',
                'details',
            ],
        },
        headers=default_pa_headers('phone_pd_id_2'),
    )
    assert response.status_code == 200
    assert response.json()['state']['context']['present_as_completed']


@pytest.mark.config(CARGO_C2C_ENABLE_CARGO_CLAIMS_ETA=True)
@pytest.mark.experiments3(filename='experiment.json')
async def test_deliveries(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mockserver,
        load_json,
        mock_claims_full,
):
    mock_claims_full.current_point = {
        'claim_point_id': 5,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': 'pending',
    }

    order_id = await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/deliveries',
        json={'deliveries': []},
        headers=default_pa_headers('phone_pd_id_3'),
    )

    assert response.status_code == 200
    resp = response.json()
    resp['deliveries'][0].pop('etag')
    assert resp == {
        'deliveries': [
            {
                'delivery_id': 'cargo-c2c/' + order_id,
                'state': {
                    'context': {
                        'is_performer_position_available': True,
                        'auto_open_postcard': False,
                        'display_targets': ['multiorder'],
                    },
                    'summary': 'Курьер в пути к точке отправления: 1 мин',
                    'description': 'голубой BMW',
                    'performer': {
                        'name': 'Petr',
                        'short_name': 'Иван',
                        'rating': '4.7',
                        'phone': '+7123',
                        'photo_url': 'testavatar',
                        'vehicle_model': 'BMW',
                        'vehicle_number': 'A001AA77',
                    },
                    'sorted_route_points': [
                        {'coordinates': [3.0, 3.3], 'type': 'destination'},
                    ],
                    'active_route_points': [0],
                    'performer_route': {
                        'sorted_route_points': [{'coordinates': [3.0, 3.3]}],
                    },
                    'actions': [
                        {
                            'type': 'performer_call',
                            'title': 'Звонок курьеру',
                            'communication_method': {
                                'type': 'voice_forwarding_call',
                                'forwarding_id': 'performer',
                            },
                        },
                        {
                            'title': 'Детали',
                            'type': 'open_tracking_card',
                            'expansion': 'expanded',
                        },
                    ],
                    'meta': {
                        'order_provider_id': 'cargo-c2c',
                        'order_status': 'performer_found',
                        'roles': ['initiator'],
                        'tariff_class': 'courier',
                    },
                },
            },
        ],
        'shipments': [],
    }


@pytest.mark.config(CARGO_C2C_ENABLE_CARGO_CLAIMS_ETA=True)
@pytest.mark.experiments3(filename='experiment.json')
async def test_faulty_deliveries(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mockserver,
        load_json,
        mock_claims_full,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        return mockserver.make_response(
            json={'code': 'not_found', 'message': 'no such claim_id'},
            status=404,
        )

    @mockserver.json_handler('/cargo-claims/v2/claims/points-eta')
    def _claims_points_eta(request):
        full = load_json('claim_full_response.json')
        points_eta = {
            'id': full['id'],
            'route_points': [],
            'performer_position': [52.569089, 39.60258],
        }

        for point in full['route_points']:
            point.pop('contact', None)
            point.pop('skip_confirmation', None)
            points_eta['route_points'].append(point)

        return mockserver.make_response(json=points_eta)

    await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/deliveries',
        json={'deliveries': []},
        headers=default_pa_headers('phone_pd_id_3'),
    )

    assert response.status_code == 200
    assert response.json() == {'deliveries': [], 'shipments': []}


@pytest.mark.config(
    CARGO_C2C_ENABLE_CARGO_CLAIMS_ETA=True,
    CARGO_C2C_ESTIMATE_TIME_TO_FIND_PERFORMER={'courier': {'estimate': 120}},
)
@pytest.mark.experiments3(filename='experiment.json')
async def test_deliveries_post_context(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mockserver,
        load_json,
        mock_claims_full,
):
    mock_claims_full.claim_status = 'accepted'
    mock_claims_full.current_point_id = 1
    order_id = await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/deliveries',
        json={'deliveries': []},
        headers=default_pa_headers('phone_pd_id_3'),
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp['deliveries'][0]['state']['context']['performer_search'] == {
        'is_in_progress': True,
        'estimate': 120,
    }

    assert resp['deliveries'][0]['delivery_id'] == 'cargo-c2c/' + order_id


@pytest.mark.experiments3(filename='experiment.json')
async def test_deliveries_actions(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mockserver,
        load_json,
        mock_claims_full,
):
    mock_claims_full.claim_status = 'accepted'
    mock_claims_full.current_point_id = 1
    await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/deliveries',
        json={'deliveries': []},
        headers=default_pa_headers('phone_pd_id_3'),
    )
    assert response.status_code == 200
    resp = response.json()

    cancel_action = {
        'title': 'Отмена доставки',
        'message': {
            'title': 'Платная отмена',
            'body': (
                'Курьер уже ждет посылку, поэтому бесплатная отмена недоступна'
            ),
            'close_button': {'title': 'Закрыть'},
            'confirm_button': {
                'cancel_type': 'paid',
                'title': 'Отменить платно',
            },
        },
        'type': 'cancel',
    }

    assert cancel_action in resp['deliveries'][0]['state']['actions']


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(CARGO_C2C_ENABLE_ADDRESS_LOCALIZE=True)
async def test_address_localization(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mock_claims_full,
        yamaps,
        mockserver,
        load_json,
):
    order_id = await create_cargo_c2c_orders(
        expected_claims_request=load_json(
            'cargo_claims_create_expected_request_with_localization.json',
        ),
    )
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'supported_content_item_types': [
                'list_item',
                'header',
                'separator',
                'postcard',
                'details',
            ],
        },
        headers=default_pa_headers('phone_pd_id_3'),
    )
    assert response.status_code == 200
    assert response.json()['state']['sorted_route_points'] == [
        {
            'visit_status': 'visited',
            'type': 'source',
            'uri': 'ymapsbm1://geo?exit1',
            'coordinates': [1.0, 1.1],
            'full_text': 'Россия, Москва, Садовническая улица',
            'short_text': 'Садовническая улица',
            'area_description': 'Москва, Россия',
            'entrance': '4',
            'comment': 'some comment',
            'contact': {'phone': 'phone_pd_i'},
        },
        {
            'visit_status': 'visited',
            'type': 'destination',
            'uri': 'ymapsbm1://geo?exit1',
            'coordinates': [2.0, 2.2],
            'full_text': 'Россия, Москва, Садовническая улица',
            'short_text': 'Садовническая улица',
            'area_description': 'Москва, Россия',
            'entrance': '4',
            'comment': 'some comment',
            'contact': {'phone': 'phone_pd_i'},
        },
        {
            'visit_status': 'pending',
            'type': 'destination',
            'uri': 'ymapsbm1://geo?exit1',
            'coordinates': [3.0, 3.3],
            'full_text': 'Россия, Москва, Садовническая улица',
            'short_text': 'Садовническая улица',
            'area_description': 'Москва, Россия',
            'entrance': '4',
            'comment': 'some comment',
            'contact': {'phone': 'phone_pd_i'},
        },
        {
            'visit_status': 'pending',
            'type': 'destination',
            'uri': 'ymapsbm1://geo?exit1',
            'coordinates': [4.0, 4.4],
            'full_text': 'Россия, Москва, Садовническая улица',
            'short_text': 'Садовническая улица',
            'area_description': 'Москва, Россия',
            'entrance': '4',
            'comment': 'some comment',
            'contact': {'phone': 'phone_pd_i'},
        },
        {
            'visit_status': 'pending',
            'type': 'destination',
            'uri': 'ymapsbm1://geo?exit1',
            'coordinates': [5.0, 5.5],
            'full_text': 'Россия, Москва, Садовническая улица',
            'short_text': 'Садовническая улица',
            'area_description': 'Москва, Россия',
            'entrance': '4',
            'comment': 'some comment',
            'contact': {'phone': 'phone_pd_i'},
        },
    ]


@pytest.mark.config(
    CARGO_C2C_C2C_CANCEL_REASONS=[
        {
            'allowed_for': [{'cancel_type': 'paid', 'tariffs': ['cargo']}],
            'reason_id': 'went_in_wrong_direction',
            'tanker_key': {
                'key': 'cancel_reasons.went_in_wrong_direction',
                'keyset': 'cargo',
            },
        },
        {
            'allowed_for': [
                {'cancel_type': 'paid', 'tariffs': ['express', 'courier']},
            ],
            'reason_id': 'asked_to_cancel',
            'tanker_key': {
                'key': 'cancel_reasons.asked_to_cancel',
                'keyset': 'cargo',
            },
        },
        {
            'allowed_for': [{'cancel_type': 'free', 'tariffs': ['courier']}],
            'reason_id': 'too_long_to_wait',
            'tanker_key': {
                'key': 'cancel_reasons.too_long_to_wait',
                'keyset': 'cargo',
            },
        },
        {
            'reason_id': 'unable_to_contact',
            'tanker_key': {
                'key': 'cancel_reasons.unable_to_contact',
                'keyset': 'cargo',
            },
        },
    ],
)
@pytest.mark.parametrize(
    'tariff, reasons',
    [
        (
            'cargo',
            [
                {
                    'reason_id': 'went_in_wrong_direction',
                    'title': 'Курьер не двигался по маршруту',
                },
                {
                    'reason_id': 'unable_to_contact',
                    'title': 'Не удалось связаться с курьером',
                },
            ],
        ),
        (
            'courier',
            [
                {
                    'reason_id': 'asked_to_cancel',
                    'title': 'Курьер попросил отменить заказ',
                },
                {
                    'reason_id': 'unable_to_contact',
                    'title': 'Не удалось связаться с курьером',
                },
            ],
        ),
    ],
)
@pytest.mark.experiments3(filename='experiment.json')
async def test_cancel_feedback_action(
        taxi_cargo_c2c,
        default_pa_headers,
        create_cargo_c2c_orders,
        mock_claims_full,
        tariff,
        reasons,
):
    order_id = await create_cargo_c2c_orders()
    mock_claims_full.tariff = tariff
    mock_claims_full.claim_status = 'cancelled'

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'supported_content_item_types': [
                'list_item',
                'header',
                'separator',
                'postcard',
                'details',
            ],
        },
        headers=default_pa_headers('phone_pd_id_3'),
    )

    assert response.status_code == 200
    assert response.json()['state']['primary_actions'] == [
        {
            'type': 'cancel_feedback',
            'title': 'Фидбэк по отмене',
            'reasons': reasons,
        },
    ]


@pytest.mark.config(
    CARGO_C2C_C2C_FEEDBACK_REASONS=CARGO_C2C_C2C_FEEDBACK_REASONS_CONFIG,
    CARGO_C2C_FEEDBACK_SUBTITLES=CARGO_C2C_FEEDBACK_SUBTITLES_CONFIG,
    CARGO_C2C_REQUIREMENT_IMAGE_TAGS={
        '__default__': 'delivery_requirement_default',
        'door_to_door': 'delivery_door_to_door',
    },
)
@pytest.mark.experiments3(filename='experiment.json')
async def test_last_feedback(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mock_claims_full,
):
    order_id = await create_cargo_c2c_orders()

    response = await taxi_cargo_c2c.post(
        '/v1/actions/save-client-feedback',
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
            },
            'type': 'order_feedback',
            'score': 4,
            'reasons': [
                {'reason_id': 'too_long_delivery'},
                {'reason_id': 'unable_to_contact'},
            ],
        },
    )
    assert response.status_code == 200

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'supported_content_item_types': [
                'list_item',
                'header',
                'separator',
                'postcard',
                'details',
            ],
        },
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200

    assert response.json()['state']['primary_actions'] == [
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
                    'reason_id': 'order_wasnt_delivered',
                    'title': 'Заказ не доставлен',
                    'scores': [1],
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
            'last_feedback': {
                'score': 4,
                'reason_ids': ['too_long_delivery', 'unable_to_contact'],
            },
        },
        {
            'type': 'performer_call',
            'title': 'Звонок курьеру',
            'communication_method': {
                'type': 'voice_forwarding_call',
                'forwarding_id': 'performer',
            },
        },
        {
            'type': 'share',
            'title': 'Поделиться',
            'sharing_url': matching.AnyString(),
        },
    ]


@pytest.mark.experiments3(filename='experiment.json')
async def test_personal_service_unavalable(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mock_claims_full,
        mockserver,
):

    mock_claims_full.tariff = 'courier'

    order_id = await create_cargo_c2c_orders()

    @mockserver.json_handler(f'/personal/v1/phones/bulk_retrieve')
    async def _(request):
        return mockserver.make_response(status=500)

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={'delivery_id': 'cargo-c2c/' + order_id},
        headers=default_pa_headers('phone_pd_id_3'),
    )

    assert response.status_code == 200
    resp = response.json()
    resp.pop('etag')
    for point in resp['state']['sorted_route_points']:
        assert 'contact' not in point


@pytest.mark.parametrize(
    'price_on_timer, price_per_minute',
    [
        pytest.param(
            '30 ₽', '5', marks=[pytest.mark.now('2020-06-17T22:50:50+0300')],
        ),
        pytest.param(
            '7k ₽', '5', marks=[pytest.mark.now('2020-06-18T22:50:50+0300')],
        ),
        pytest.param(
            '0.3 ₽',
            '0.05',
            marks=[pytest.mark.now('2020-06-17T22:50:50+0300')],
        ),
        pytest.param(
            '3 ₽', '6', marks=[pytest.mark.now('2020-06-17T22:45:20+0300')],
        ),
    ],
)
@pytest.mark.experiments3(filename='experiment.json')
async def test_paid_waiting_info(
        taxi_cargo_c2c,
        default_pa_headers,
        create_cargo_c2c_orders,
        mock_claims_full,
        mockserver,
        load_json,
        default_calc_response_v2,
        price_on_timer,
        price_per_minute,
):
    current_point_id = 2

    @mockserver.json_handler('/cargo-pricing/v2/taxi/calc/retrieve')
    def _retrieve(request):
        resp = copy.deepcopy(default_calc_response_v2)
        resp['calculations'][0]['result']['prices'][
            'source_waiting_price_per_unit'
        ] = price_per_minute
        resp['calculations'][0]['result']['details']['waypoints'][0][
            'waiting'
        ] = (
            {
                'total_waiting': '400',
                'paid_waiting': '100',
                'free_waiting_time': '300',
                'was_limited': False,
                'paid_waiting_disabled': False,
            }
        )
        return resp

    mock_claims_full.current_point = {
        'claim_point_id': 5,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': 'arrived',
    }
    mock_claims_full.current_point_id = current_point_id
    mock_claims_full.claim_status = 'pickup_arrived'

    await create_cargo_c2c_orders()

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/deliveries',
        json={'deliveries': []},
        headers=default_pa_headers('phone_pd_id_3'),
    )

    assert response.status_code == 200
    assert response.json()['deliveries'][0]['state']['paid_waiting_info'] == {
        'free_waiting_until': 1592423090,
        'paid_waiting_title': 'Платное ожидание',
        'waiting_price': price_on_timer,
    }


@pytest.mark.now('2020-06-17T22:47:50.174824+03:00')
@pytest.mark.parametrize(
    'waiting_part, expected_summary',
    [
        (
            {
                'total_waiting': '400',
                'paid_waiting': '100',
                'was_limited': False,
                'paid_waiting_disabled': True,
            },
            'Курьер около вас. Будьте готовы отдать посылку',
        ),
        (
            {
                'total_waiting': '400',
                'paid_waiting': '100',
                'free_waiting_time': '300',
                'was_limited': False,
                'paid_waiting_disabled': False,
            },
            'Платное ожидание',
        ),
        (
            {
                'total_waiting': '400',
                'paid_waiting': '100',
                'free_waiting_time': '600',
                'was_limited': False,
                'paid_waiting_disabled': False,
            },
            'Ожидание',
        ),
    ],
)
@pytest.mark.experiments3(filename='experiment.json')
async def test_waiting_summary(
        taxi_cargo_c2c,
        default_pa_headers,
        create_cargo_c2c_orders,
        mock_claims_full,
        mockserver,
        load_json,
        default_calc_response_v2,
        waiting_part,
        expected_summary,
):
    current_point_id = 2

    @mockserver.json_handler('/cargo-pricing/v2/taxi/calc/retrieve')
    def _retrieve(request):
        resp = copy.deepcopy(default_calc_response_v2)
        resp['calculations'][0]['result']['details']['waypoints'][0][
            'waiting'
        ] = waiting_part
        return resp

    mock_claims_full.current_point = {
        'claim_point_id': 5,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': 'arrived',
    }
    mock_claims_full.current_point_id = current_point_id
    mock_claims_full.claim_status = 'pickup_arrived'

    await create_cargo_c2c_orders()

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/deliveries',
        json={'deliveries': []},
        headers=default_pa_headers('phone_pd_id_3'),
    )

    assert response.status_code == 200
    assert (
        response.json()['deliveries'][0]['state']['summary']
        == expected_summary
    )


@pytest.mark.experiments3(filename='experiment.json')
async def test_restore_preorder(
        taxi_cargo_c2c,
        default_pa_headers,
        create_cargo_c2c_orders,
        mock_claims_full,
        mockserver,
        load_json,
):
    mock_claims_full.claim_status = 'cancelled'

    await create_cargo_c2c_orders()

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/deliveries',
        json={'deliveries': []},
        headers=default_pa_headers('phone_pd_id_3'),
    )

    assert response.status_code == 200
    assert (
        response.json()['deliveries'][0]['state']['context'][
            'restore_preorder'
        ]
        is True
    )


@pytest.mark.config(
    CARGO_C2C_C2C_FEEDBACK_REASONS=CARGO_C2C_C2C_FEEDBACK_REASONS_CONFIG,
)
async def test_inconsistent_feedback(
        taxi_cargo_c2c, create_cargo_c2c_orders, default_pa_headers, pgsql,
):
    order_id = await create_cargo_c2c_orders()

    response = await taxi_cargo_c2c.post(
        '/v1/actions/save-client-feedback',
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
            },
            'type': 'order_feedback',
            'score': 4,
            'reasons': [
                {'reason_id': 'perfect'},
                {'reason_id': 'order_wasnt_delivered'},
                {'reason_id': 'too_long_delivery'},
            ],
        },
    )
    assert response.status_code == 200

    cursor = pgsql['cargo_c2c'].cursor()
    cursor.execute('SELECT * FROM cargo_c2c.clients_feedbacks')
    saved_feedback = list(cursor)

    assert len(saved_feedback) == 1
    assert saved_feedback[0][3] == 4
    assert saved_feedback[0][4] == ['too_long_delivery']


@pytest.mark.config(
    CARGO_C2C_ENABLE_CARGO_CLAIMS_ETA=True,
    CARGO_TYPE_LIMITS={
        'lcv_l': {
            'carrying_capacity_max_kg': 6000,
            'carrying_capacity_min_kg': 1400,
            'height_max_cm': 250,
            'height_min_cm': 180,
            'length_max_cm': 601,
            'length_min_cm': 380,
            'width_max_cm': 250,
            'width_min_cm': 180,
            'requirement_value': 1,
        },
        'lcv_m': {
            'carrying_capacity_max_kg': 6000,
            'carrying_capacity_min_kg': 700,
            'height_max_cm': 230,
            'height_min_cm': 150,
            'length_max_cm': 520,
            'length_min_cm': 260,
            'width_max_cm': 230,
            'width_min_cm': 130,
            'requirement_value': 2,
        },
        'van': {
            'carrying_capacity_max_kg': 2001,
            'carrying_capacity_min_kg': 300,
            'height_max_cm': 201,
            'height_min_cm': 90,
            'length_max_cm': 290,
            'length_min_cm': 170,
            'width_max_cm': 201,
            'width_min_cm': 96,
            'requirement_value': 3,
        },
    },
    CARGO_C2C_C2C_FEEDBACK_REASONS=CARGO_C2C_C2C_FEEDBACK_REASONS_CONFIG,
    CARGO_C2C_FEEDBACK_SUBTITLES=CARGO_C2C_FEEDBACK_SUBTITLES_CONFIG,
    CARGO_C2C_REQUIREMENT_IMAGE_TAGS={
        '__default__': 'delivery_requirement_default',
        'door_to_door': 'delivery_door_to_door',
    },
)
@pytest.mark.experiments3(filename='experiment.json')
async def test_initiator_cargocorp(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mock_claims_full,
        mock_payment_method,
):
    mock_claims_full.tariff = 'courier'
    mock_claims_full.file_name = 'claim_full_response_cargocorp.json'
    mock_claims_full.current_point = {
        'claim_point_id': 5,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': 'pending',
    }

    order_id = await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'supported_content_item_types': [
                'list_item',
                'header',
                'separator',
                'postcard',
                'details',
            ],
        },
        headers=default_pa_headers('phone_pd_id_3'),
    )

    details_object = {
        'type': 'details',
        'id': matching.uuid_string,
        'title': {
            'color': 'TextMain',
            'max_lines': 1,
            'text': 'Детали заказа',
            'typography': 'body2',
        },
        'subtitle': {
            'color': 'TextMinor',
            'max_lines': 1,
            'text': 'Курьер - 298.8 ₽ - оплачено',
            'typography': 'caption1',
        },
        'lead_icon': {'image_tag': 'delivery_info'},
        'sections': [
            {
                'items': [
                    {
                        'subtitle': 'Ср 23 Сентября 0:01',
                        'title': 'Тариф Курьер',
                        'type': 'subtitle',
                    },
                    {
                        'subtitle': 'Включено',
                        'title': 'Грузчики: 2',
                        'type': 'subtitle',
                    },
                    {
                        'subtitle': 'Размеры кузова',
                        'title': 'Средний кузов',
                        'type': 'subtitle',
                    },
                    {
                        'subtitle': 'Включено',
                        'title': 'От двери до двери',
                        'type': 'subtitle',
                    },
                    {
                        'subtitle': 'Стимость',
                        'title': '298.8 ₽',
                        'type': 'subtitle',
                    },
                    {
                        'subtitle': 'CRGCRP',
                        'title': 'Способ оплаты',
                        'type': 'subtitle',
                    },
                ],
            },
            {
                'title': 'Исполнитель',
                'items': [
                    {
                        'title': 'Petr',
                        'subtitle': 'голубой BMW, номер A001AA77',
                        'type': 'subtitle',
                    },
                    {'title': 'ООО ПАРК', 'type': 'subtitle'},
                    {
                        'title': 'Дополнительно о партнере',
                        'items': [
                            {'type': 'subtitle', 'title': 'legal_address'},
                            {'type': 'subtitle', 'title': 'ОГРН: 123'},
                            {
                                'type': 'subtitle',
                                'title': 'Часы работы: 9:00-18:00',
                            },
                        ],
                        'type': 'accordion',
                    },
                ],
            },
        ],
    }

    assert response.status_code == 200
    resp = response.json()
    resp.pop('etag')

    assert resp == {
        'state': {
            'context': {
                'is_performer_position_available': True,
                'display_targets': ['multiorder'],
            },
            'summary': 'Курьер в пути к точке отправления: 1 мин',
            'description': 'голубой BMW',
            'performer': {
                'name': 'Petr',
                'short_name': 'Иван',
                'rating': '4.7',
                'phone': '+7123',
                'photo_url': 'testavatar',
                'vehicle_model': 'BMW',
                'vehicle_number': 'A001AA77',
            },
            'primary_actions': [
                {
                    'type': 'feedback',
                    'title': 'Фидбэк',
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
                            'title': 'Слишком долгая доставка',
                            'scores': [1, 2, 3, 4],
                        },
                        {
                            'reason_id': 'order_wasnt_delivered',
                            'title': 'Заказ не доставлен',
                            'scores': [1],
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
                },
                {
                    'type': 'performer_call',
                    'title': 'Звонок курьеру',
                    'communication_method': {
                        'type': 'voice_forwarding_call',
                        'forwarding_id': 'performer',
                    },
                },
                {
                    'type': 'cancel',
                    'title': 'Отмена доставки',
                    'message': {
                        'body': (
                            'Курьер уже ждет посылку, '
                            'поэтому бесплатная отмена '
                            'недоступна'
                        ),
                        'close_button': {'title': 'Закрыть'},
                        'confirm_button': {
                            'cancel_type': 'paid',
                            'title': 'Отменить платно',
                        },
                        'title': 'Платная отмена',
                    },
                },
                {
                    'type': 'share',
                    'title': 'Поделиться',
                    'sharing_url': matching.AnyString(),
                },
                {
                    'type': 'order_more',
                    'title': 'Заказать еще',
                    'vertical': 'delivery',
                    'vertical_trap': True,
                    'sheet_expansion': 'collapsed',
                },
            ],
            'secondary_actions': [],
            'sorted_route_points': [
                {
                    'visit_status': 'visited',
                    'type': 'source',
                    'uri': 'some uri',
                    'coordinates': [1, 1.1],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора 1',
                    'area_description': 'Москва, Россия',
                    'entrance': '4',
                    'comment': 'some comment',
                    'contact': {'phone': 'phone_pd_i'},
                },
                {
                    'visit_status': 'visited',
                    'type': 'destination',
                    'uri': 'some uri',
                    'coordinates': [2, 2.2],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора 2',
                    'area_description': 'Москва, Россия',
                    'entrance': '4',
                    'comment': 'some comment',
                    'contact': {'phone': 'phone_pd_i'},
                },
                {
                    'visit_status': 'pending',
                    'type': 'destination',
                    'uri': 'some uri',
                    'coordinates': [3, 3.3],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора 3',
                    'area_description': 'Москва, Россия',
                    'entrance': '4',
                    'comment': 'some comment',
                    'contact': {'phone': 'phone_pd_i'},
                },
                {
                    'visit_status': 'pending',
                    'type': 'destination',
                    'uri': 'some uri',
                    'coordinates': [4, 4.4],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора 4',
                    'area_description': 'Москва, Россия',
                    'entrance': '4',
                    'comment': 'some comment',
                    'contact': {'phone': 'phone_pd_i'},
                },
                {
                    'visit_status': 'pending',
                    'type': 'destination',
                    'uri': 'some uri',
                    'coordinates': [5, 5.5],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора 5',
                    'area_description': 'Москва, Россия',
                    'entrance': '4',
                    'comment': 'some comment',
                    'contact': {'phone': 'phone_pd_i'},
                },
            ],
            'active_route_points': [2],
            'performer_route': {
                'sorted_route_points': [{'coordinates': [3, 3.3]}],
            },
            'meta': {
                'order_provider_id': 'cargo-c2c',
                'order_status': 'performer_found',
                'roles': ['initiator'],
                'tariff_class': 'courier',
            },
            'content_sections': [
                {
                    'id': matching.uuid_string,
                    'items': [
                        {
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMain',
                                'max_lines': 1,
                                'text': 'Грузчики: 2',
                                'typography': 'body2',
                            },
                            'trail_text': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Включено',
                                'typography': 'caption1',
                            },
                            'type': 'list_item',
                            'lead_icon': {
                                'image_tag': 'delivery_requirement_default',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMain',
                                'max_lines': 1,
                                'text': 'Средний кузов',
                                'typography': 'body2',
                            },
                            'subtitle': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Размеры кузова',
                                'typography': 'caption1',
                            },
                            'trail_text': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Включено',
                                'typography': 'caption1',
                            },
                            'type': 'list_item',
                            'lead_icon': {
                                'image_tag': 'delivery_requirement_default',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMain',
                                'max_lines': 1,
                                'text': 'От двери до двери',
                                'typography': 'body2',
                            },
                            'trail_text': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Включено',
                                'typography': 'caption1',
                            },
                            'type': 'list_item',
                            'lead_icon': {
                                'image_tag': 'delivery_door_to_door',
                            },
                        },
                    ],
                },
                {
                    'id': matching.uuid_string,
                    'items': [
                        {
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMain',
                                'max_lines': 1,
                                'text': 'CRGCRP',
                                'typography': 'body2',
                            },
                            'subtitle': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Способ оплаты',
                                'typography': 'caption1',
                            },
                            'type': 'list_item',
                            'lead_icon': {
                                'image_tag': 'delivery_payment_default',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        details_object,
                        {
                            'type': 'header',
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Отправитель',
                                'typography': 'caption1',
                            },
                        },
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'subtitle': {
                                'text': 'phone_pd_i',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'lead_icon': {'image_tag': 'delivery_phone'},
                            'title': {
                                'text': 'Телефон для связи',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'БЦ Аврора 1',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'subtitle': {
                                'text': 'под. 4',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {'image_tag': 'delivery_point_red'},
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'Комментарий',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {
                                'image_tag': 'delivery_comment_outline',
                            },
                            'subtitle': {
                                'text': 'some comment',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                        },
                        {
                            'type': 'header',
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Получатель № 1',
                                'typography': 'caption1',
                            },
                        },
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'subtitle': {
                                'text': 'phone_pd_i',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'lead_icon': {'image_tag': 'delivery_phone'},
                            'title': {
                                'text': 'Телефон для связи',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'БЦ Аврора 2',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'subtitle': {
                                'text': 'под. 4',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {'image_tag': 'delivery_point'},
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'Комментарий',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {
                                'image_tag': 'delivery_comment_outline',
                            },
                            'subtitle': {
                                'text': 'some comment',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                        },
                        {
                            'type': 'header',
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Получатель № 2',
                                'typography': 'caption1',
                            },
                        },
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'subtitle': {
                                'text': 'phone_pd_i',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'lead_icon': {'image_tag': 'delivery_phone'},
                            'title': {
                                'text': 'Телефон для связи',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'БЦ Аврора 3',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'subtitle': {
                                'text': 'под. 4',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {'image_tag': 'delivery_point'},
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'Комментарий',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {
                                'image_tag': 'delivery_comment_outline',
                            },
                            'subtitle': {
                                'text': 'some comment',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                        },
                        {
                            'type': 'header',
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Получатель № 3',
                                'typography': 'caption1',
                            },
                        },
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'subtitle': {
                                'text': 'phone_pd_i',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'lead_icon': {'image_tag': 'delivery_phone'},
                            'title': {
                                'text': 'Телефон для связи',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'БЦ Аврора 4',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'subtitle': {
                                'text': 'под. 4',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {'image_tag': 'delivery_point'},
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'Комментарий',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {
                                'image_tag': 'delivery_comment_outline',
                            },
                            'subtitle': {
                                'text': 'some comment',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                        },
                        {
                            'type': 'header',
                            'id': matching.uuid_string,
                            'title': {
                                'color': 'TextMinor',
                                'max_lines': 1,
                                'text': 'Получатель № 4',
                                'typography': 'caption1',
                            },
                        },
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'subtitle': {
                                'text': 'phone_pd_i',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'lead_icon': {'image_tag': 'delivery_phone'},
                            'title': {
                                'text': 'Телефон для связи',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'БЦ Аврора 5',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'subtitle': {
                                'text': 'под. 4',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {'image_tag': 'delivery_point'},
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'Комментарий',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {
                                'image_tag': 'delivery_comment_outline',
                            },
                            'subtitle': {
                                'text': 'some comment',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                        },
                    ],
                },
            ],
            'details': {
                'sections': [
                    {
                        'items': [
                            {
                                'subtitle': 'Ср 23 Сентября 0:01',
                                'title': 'Тариф Курьер',
                                'type': 'subtitle',
                            },
                            {
                                'subtitle': 'Включено',
                                'title': 'Грузчики: 2',
                                'type': 'subtitle',
                            },
                            {
                                'subtitle': 'Размеры кузова',
                                'title': 'Средний кузов',
                                'type': 'subtitle',
                            },
                            {
                                'subtitle': 'Включено',
                                'title': 'От двери до двери',
                                'type': 'subtitle',
                            },
                            {
                                'subtitle': 'Стимость',
                                'title': '298.8 ₽',
                                'type': 'subtitle',
                            },
                            {
                                'subtitle': 'CRGCRP',
                                'title': 'Способ оплаты',
                                'type': 'subtitle',
                            },
                        ],
                    },
                    {
                        'title': 'Исполнитель',
                        'items': [
                            {
                                'title': 'Petr',
                                'subtitle': 'голубой BMW, номер A001AA77',
                                'type': 'subtitle',
                            },
                            {'title': 'ООО ПАРК', 'type': 'subtitle'},
                            {
                                'title': 'Дополнительно о партнере',
                                'items': [
                                    {
                                        'type': 'subtitle',
                                        'title': 'legal_address',
                                    },
                                    {'type': 'subtitle', 'title': 'ОГРН: 123'},
                                    {
                                        'type': 'subtitle',
                                        'title': 'Часы работы: 9:00-18:00',
                                    },
                                ],
                                'type': 'accordion',
                            },
                        ],
                    },
                ],
                'title': 'Детали заказа',
                'subtitle': 'Стоимость доставки 298.8 ₽',
            },
        },
    }


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.parametrize(
    'selected_tips, selected_choice_num',
    [('50', 3), (None, 0), ('0', 0), ('25', 4)],
)
async def test_selected_tips(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        pgsql,
        mock_claims_full,
        selected_tips,
        selected_choice_num,
):
    order_id = await create_cargo_c2c_orders()

    if selected_tips is not None:
        cursor = pgsql['cargo_c2c'].cursor()
        cursor.execute(
            """
            INSERT INTO cargo_c2c.clients_feedbacks (
                phone_pd_id,
                order_id,
                order_provider_id,
                selected_tips,
                selected_tips_type
            ) VALUES ('phone_pd_id_3', '{}', 'cargo-c2c', '{}', 'flat')
            """.format(
                order_id, selected_tips,
            ),
        )

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={'delivery_id': 'cargo-c2c/' + order_id},
        headers=default_pa_headers('phone_pd_id_3'),
    )

    assert response.status_code == 200
    resp = response.json()
    resp.pop('etag')

    tips_actions_enabled = False
    for action in resp['state']['primary_actions']:
        if action['type'] == 'tips':
            tips_actions_enabled = True

            if selected_choice_num == len(action['choices']) - 1:
                assert selected_tips == action['choices'][-1]['decimal_value']

            assert (
                action['last_choice_id']
                == action['choices'][selected_choice_num]['choice_id']
            )

    assert tips_actions_enabled


@pytest.mark.experiments3(filename='experiment.json')
async def test_selected_tips_with_defaults(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        pgsql,
        mock_claims_full,
):
    order_id = await create_cargo_c2c_orders(add_user_default_tips=True)

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={'delivery_id': 'cargo-c2c/' + order_id},
        headers=default_pa_headers('phone_pd_id_3'),
    )

    assert response.status_code == 200
    resp = response.json()

    for action in resp['state']['primary_actions']:
        if action['type'] == 'tips':
            assert action == {
                'type': 'tips',
                'choices': [
                    {
                        'type': 'predefined',
                        'decimal_value': '0',
                        'title': 'Без чаевых',
                        'choice_id': 'predefined_0',
                        'tips_type': 'flat',
                    },
                    {
                        'type': 'predefined',
                        'decimal_value': '20',
                        'title': '20 ₽',
                        'choice_id': 'predefined_20',
                        'tips_type': 'flat',
                    },
                    {
                        'type': 'predefined',
                        'decimal_value': '30',
                        'title': '30 ₽',
                        'choice_id': 'predefined_30',
                        'tips_type': 'flat',
                    },
                    {
                        'type': 'predefined',
                        'decimal_value': '50',
                        'title': '50 ₽',
                        'choice_id': 'predefined_50',
                        'tips_type': 'flat',
                    },
                    {
                        'type': 'predefined',
                        'decimal_value': '10',
                        'title': '10%',
                        'choice_id': 'percent_10',
                        'tips_type': 'percent',
                    },
                    {
                        'type': 'manual',
                        'title': 'Другая сумма',
                        'extra_subtitle': 'Сумма, ₽',
                        'min_tips_value': 9.0,
                        'max_tips_value': 400.0,
                        'choice_id': matching.AnyString(),
                        'tips_value_pattern': '%s ₽',
                    },
                ],
                'last_choice_id': 'percent_10',
            }


@pytest.mark.experiments3(
    name='delivery_slow_courier_flow',
    consumers=['cargo-c2c/deliveries'],
    default_value={
        'enabled': True,
        'order_timings': {
            'order_complete_eta': 14400,
            'pickup_eta': 7200,
            'rounding_rule': 15,
        },
        'summary_overrides': {
            'performer_lookup': {
                'summary_keyset': 'cargo',
                'summary_tanker_key': 'performer_not_ready_summary_sdd',
                'description_keyset': 'cargo',
                'description_tanker_key': (
                    'performer_not_ready_description_sdd'
                ),
            },
        },
        'show_performer_search_timer': False,
    },
    is_config=True,
    clauses=[],
)
@pytest.mark.experiments3(
    name='cargo_c2c_deliveries_handler_control',
    consumers=['cargo-c2c/deliveries'],
    default_value={'enabled': True},
    is_config=True,
    clauses=[],
)
@pytest.mark.now('2020-09-23T14:44:01.174824+00:00')
async def test_slow_courier_flow(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mock_claims_full,
):
    mock_claims_full.claim_status = 'performer_lookup'

    await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/deliveries',
        json={'deliveries': []},
        headers=default_pa_headers('phone_pd_id_3'),
    )

    assert response.status_code == 200
    assert (
        'performer_search'
        not in response.json()['deliveries'][0]['state']['context'].keys()
    )
    assert (
        response.json()['deliveries'][0]['state']['description']
        == 'Сообщим, когда назначим курьера'
    )


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.parametrize(
    'status, role_by_phone, is_expected_order_more',
    [
        pytest.param('new', 'phone_pd_id_3', True),
        pytest.param('accepted', 'phone_pd_id_1', False),
        pytest.param('delivered', 'phone_pd_id_3', False),
    ],
)
async def test_initiator_order_more_action(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mock_claims_full,
        status,
        role_by_phone,
        is_expected_order_more,
):
    mock_claims_full.claim_status = status

    order_id = await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'supported_content_item_types': [
                'list_item',
                'header',
                'separator',
                'postcard',
                'details',
            ],
        },
        headers=default_pa_headers(role_by_phone),
    )

    assert response.status_code == 200

    ex_ordre_more = {
        'type': 'order_more',
        'title': 'Заказать еще',
        'vertical': 'delivery',
        'vertical_trap': True,
        'sheet_expansion': 'collapsed',
    }
    primary_actions_resp = response.json()['state']['primary_actions']
    assert (ex_ordre_more in primary_actions_resp) == is_expected_order_more


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.parametrize(
    'status,has_cost_details',
    [('performer_found', False), ('delivered_finish', True)],
)
async def test_cost_details(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mock_claims_full,
        status,
        has_cost_details,
):
    mock_claims_full.claim_status = status
    order_id = await create_cargo_c2c_orders()

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={'delivery_id': 'cargo-c2c/' + order_id},
        headers=default_pa_headers('phone_pd_id_3'),
    )

    assert response.status_code == 200

    if has_cost_details:
        assert response.json()['state']['cost_details'] == {
            'components': [
                {'title': 'Доставка', 'value': '100 ₽'},
                {'title': 'Платное ожидание, 15 мин.', 'value': '100.999 ₽'},
            ],
        }
    else:
        assert 'cost_details' not in response.json()['state']


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.parametrize(
    'claim_status, claim_warnings, expected_completed_state_buttons, expected_summary, expected_message',
    [
        pytest.param('accepted', [], None, 'Поиск исполнителя', None),
        pytest.param(
            'cancelled',
            [],
            {'primary': {'title': 'Готово', 'action': {'type': 'done'}}},
            'Заказ отменен',
            None,
        ),
        pytest.param(
            'cancelled_by_taxi',
            [
                {
                    'source': 'taxi_requirements',
                    'code': 'cancelled_by_early_hold',
                },
            ],
            {
                'primary': {
                    'title': 'Изменить способ оплаты',
                    'action': {
                        'type': 'go-to-summary',
                        'change_payment_method': True,
                    },
                },
                'secondary': {
                    'title': 'Вернуться к заказу',
                    'action': {'type': 'done'},
                },
            },
            'Заказ отменён: оплата не прошла',
            {
                'id': matching.uuid_string,
                'lead_icon': {'image_tag': 'some_icon'},
                'title': {
                    'color': 'TextMain',
                    'max_lines': 4,
                    'text': 'Мы не смогли списать 298.8 ₽ с вашей карты. Проверьте, что с ней все в порядке, или измените список оплаты',
                    'typography': 'body2',
                },
                'type': 'list_item',
            },
        ),
    ],
)
async def test_failed_early_hold_state(
        mock_claims_full,
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mockserver,
        claim_status,
        claim_warnings,
        expected_completed_state_buttons,
        expected_summary,
        expected_message,
):
    mock_claims_full.claim_status = claim_status
    mock_claims_full.warnings = claim_warnings

    order_id = await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'supported_content_item_types': [
                'list_item',
                'header',
                'separator',
                'postcard',
                'details',
            ],
        },
        headers=default_pa_headers('phone_pd_id_3'),
    )

    assert response.status_code == 200

    rest = response.json()
    assert expected_summary == rest['state']['summary']
    if expected_completed_state_buttons:
        completed_state_buttons = rest['state']['completed_state_buttons']
        assert completed_state_buttons == expected_completed_state_buttons
    if expected_message:
        assert (
            expected_message in rest['state']['content_sections'][1]['items']
        )


async def test_error_service(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mockserver,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _handle(request):
        return mockserver.make_response(status=500)

    order_id = await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'supported_content_item_types': [
                'list_item',
                'header',
                'separator',
                'postcard',
                'details',
            ],
        },
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 500


@pytest.mark.experiments3(filename='experiment.json')
async def test_drafted_deliveries(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mockserver,
        get_default_estimate_request,
        get_default_draft_request,
):
    @mockserver.json_handler('/uantifraud/v1/delivery/can_make_order')
    def _mock_can_make_order(request):
        return mockserver.make_response(json={'status': 'allow'})

    estimate_request = get_default_estimate_request()
    draft_request = get_default_draft_request()

    response = await taxi_cargo_c2c.post(
        '/v1/delivery/estimate',
        json=estimate_request,
        headers=default_pa_headers('phone_pd_id_3'),
    )
    assert response.status_code == 200

    draft_request['offer_id'] = response.json()['estimations'][0]['offer_id']
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/draft',
        json=draft_request,
        headers=default_pa_headers('phone_pd_id_3'),
    )
    assert response.status_code == 200

    order_id = response.json()['delivery_id'].split('/')[1]
    response = await taxi_cargo_c2c.post(
        '/v1/processing/delivery-order/commit',
        json={
            'id': {
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
                'phone_pd_id': 'phone_pd_id_3',
            },
        },
    )
    assert response.status_code == 200

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/deliveries',
        json={'deliveries': [], 'shipments': []},
        headers=default_pa_headers('phone_pd_id_3'),
    )
    assert response.status_code == 200
    assert response.json() == {
        'deliveries': [
            {
                'delivery_id': matching.AnyString(),
                'etag': matching.AnyString(),
                'state': {
                    'actions': [],
                    'active_route_points': [],
                    'context': {'display_targets': ['multiorder']},
                    'meta': {
                        'order_provider_id': 'cargo-c2c',
                        'order_status': 'accepted',
                        'roles': ['initiator'],
                        'tariff_class': '',
                    },
                    'sorted_route_points': [],
                    'summary': 'Заказ создан',
                },
            },
        ],
        'shipments': [],
    }

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'supported_content_item_types': [
                'list_item',
                'header',
                'separator',
                'postcard',
                'details',
            ],
        },
        headers=default_pa_headers('phone_pd_id_3'),
    )
    assert response.status_code == 200
    assert response.json() == {
        'etag': matching.AnyString(),
        'state': {
            'primary_actions': [],
            'secondary_actions': [],
            'active_route_points': [],
            'context': {'display_targets': ['multiorder']},
            'meta': {
                'order_provider_id': 'cargo-c2c',
                'order_status': 'accepted',
                'roles': ['initiator'],
                'tariff_class': '',
            },
            'sorted_route_points': [],
            'summary': 'Заказ создан',
        },
    }

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/deliveries',
        json={'deliveries': []},
        headers=default_pa_headers('phone_pd_id_4'),
    )
    assert response.status_code == 200
    assert response.json() == {'deliveries': [], 'shipments': []}

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'supported_content_item_types': [
                'list_item',
                'header',
                'separator',
                'postcard',
                'details',
            ],
        },
        headers=default_pa_headers('phone_pd_id_4'),
    )
    assert response.status_code == 404


@pytest.mark.experiments3(filename='experiment.json')
async def test_commited_deliveries_without_clients_orders(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mockserver,
        get_default_estimate_request,
        get_default_draft_request,
        default_calc_response,
        mock_cargo_pricing,
        mock_claims_full,
):
    @mockserver.json_handler('/cargo-pricing/v1/taxi/calc/retrieve')
    def _calc(request):
        response = default_calc_response.copy()
        response['request'] = mock_cargo_pricing.v2_calc_mock.next_call()[
            'request'
        ].json
        return response

    @mockserver.json_handler('/cargo-claims/v2/claims/c2c/create')
    def _create_claim(request):
        return {
            'id': 'some_cargo_ref_id',
            'items': [
                {
                    'pickup_point': 1,
                    'droppof_point': 2,
                    'title': 'item title 1',
                    'cost_value': '10.40',
                    'cost_currency': 'RUB',
                    'quantity': 1,
                },
            ],
            'comment': 'commit',
            'route_points': [
                {
                    'id': 1,
                    'visit_order': 1,
                    'address': {
                        'fullname': '1',
                        'coordinates': [37.8, 55.4],
                        'country': '1',
                        'city': '1',
                        'street': '1',
                        'building': '1',
                        'comment': 'commit',
                    },
                    'contact': {'phone': '+79999999991', 'name': 'string'},
                    'type': 'source',
                    'visit_status': 'pending',
                    'visited_at': {},
                },
                {
                    'id': 2,
                    'visit_order': 2,
                    'address': {
                        'fullname': '2',
                        'coordinates': [37.8, 55.4],
                        'country': '2',
                        'city': '2',
                        'street': '2',
                        'building': '2',
                        'comment': 'commit',
                    },
                    'contact': {'phone': '+79999999992', 'name': 'string'},
                    'type': 'destination',
                    'visit_status': 'pending',
                    'visited_at': {},
                },
            ],
            'status': 'accepted',
            'version': 1,
            'created_ts': '2020-09-23T14:44:03.154152+00:00',
            'updated_ts': '2020-09-23T14:44:03.154152+00:00',
            'revision': 1,
            'user_request_revision': '123',
        }

    @mockserver.json_handler('/uantifraud/v1/delivery/can_make_order')
    def _mock_can_make_order(request):
        return mockserver.make_response(json={'status': 'allow'})

    estimate_request = get_default_estimate_request()
    draft_request = get_default_draft_request()

    response = await taxi_cargo_c2c.post(
        '/v1/delivery/estimate',
        json=estimate_request,
        headers=default_pa_headers('phone_pd_id_3'),
    )
    assert response.status_code == 200

    draft_request['offer_id'] = response.json()['estimations'][0]['offer_id']
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/draft',
        json=draft_request,
        headers=default_pa_headers('phone_pd_id_3'),
    )
    assert response.status_code == 200

    order_id = response.json()['delivery_id'].split('/')[1]
    response = await taxi_cargo_c2c.post(
        '/v1/processing/delivery-order/commit',
        json={
            'id': {
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
                'phone_pd_id': 'phone_pd_id_3',
            },
        },
    )
    assert response.status_code == 200

    response = await taxi_cargo_c2c.post(
        '/v1/processing/delivery-order/create-c2c-order',
        json={
            'id': {
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
                'phone_pd_id': 'phone_pd_id_3',
            },
        },
    )
    assert response.status_code == 200

    response = await taxi_cargo_c2c.post(
        '/v1/clients-orders',
        json={'order_id': order_id, 'order_provider_id': 'cargo-c2c'},
    )
    assert response.status_code == 200
    assert response.json() == {'orders': []}

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'supported_content_item_types': [
                'list_item',
                'header',
                'separator',
                'postcard',
                'details',
            ],
        },
        headers=default_pa_headers('phone_pd_id_3'),
    )
    assert response.json()['state'] == {
        'active_route_points': [],
        'context': {'display_targets': ['multiorder']},
        'meta': {
            'order_provider_id': 'cargo-c2c',
            'order_status': 'accepted',
            'roles': ['initiator'],
            'tariff_class': '',
        },
        'primary_actions': [],
        'secondary_actions': [],
        'sorted_route_points': [],
        'summary': 'Заказ создан',
    }

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/deliveries',
        json={'deliveries': [], 'shipments': []},
        headers=default_pa_headers('phone_pd_id_2'),
    )
    assert response.status_code == 200
    assert response.json() == {'deliveries': [], 'shipments': []}

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-c2c/' + order_id,
            'supported_content_item_types': [
                'list_item',
                'header',
                'separator',
                'postcard',
                'details',
            ],
        },
        headers=default_pa_headers('phone_pd_id_2'),
    )
    assert response.status_code == 404
