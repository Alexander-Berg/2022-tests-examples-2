# pylint: disable=too-many-lines
import pytest

from testsuite.utils import matching


async def get_sharing_key(
        taxi_cargo_c2c, order_id, order_provider_id, phone_pd_id=None,
):
    response = await taxi_cargo_c2c.post(
        '/v1/clients-orders',
        json={'order_id': order_id, 'order_provider_id': order_provider_id},
    )
    assert response.status_code == 200

    orders = response.json()['orders']
    for order in orders:
        if order['id']['phone_pd_id'] == phone_pd_id:
            return order['sharing_key']

    return orders[0]['sharing_key']


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
    CARGO_C2C_REQUIREMENT_IMAGE_TAGS={
        '__default__': 'delivery_requirement_default',
        'door_to_door': 'delivery_door_to_door',
    },
)
@pytest.mark.experiments3(filename='experiment.json')
async def test_info(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        get_default_order_id,
        mock_claims_full,
):
    mock_claims_full.current_point = {
        'claim_point_id': 5,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': 'pending',
    }

    order_id = await create_cargo_c2c_orders()
    key = await get_sharing_key(
        taxi_cargo_c2c, order_id, 'cargo-c2c', 'phone_pd_id_3',
    )

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/shared-route/info',
        json={'key': key},
        headers={'Accept-Language': 'ru'},
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
            'text': 'Курьер - 298.8 ₽ - оплачено',
            'typography': 'caption1',
        },
        'lead_icon': {'image_tag': 'delivery_info'},
        'sections': [
            {
                'items': [
                    {'title': 'Тариф Курьер', 'type': 'subtitle'},
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
                        'title': '298.8\xa0₽',
                        'type': 'subtitle',
                        'subtitle': 'Стимость',
                    },
                    {
                        'subtitle': 'Оплата картой',
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
    assert resp == {
        'context': {'is_performer_position_available': True},
        'summary': 'Курьер в пути к точке отправления: 1 мин',
        'description': 'голубой BMW',
        'route_points': [
            {
                'visit_status': 'visited',
                'type': 'source',
                'uri': 'some uri',
                'coordinates': [1.0, 1.1],
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
                'coordinates': [2.0, 2.2],
                'full_text': 'Россия, Москва, Садовническая улица 82',
                'short_text': 'БЦ Аврора 2',
                'entrance': '4',
                'comment': 'some comment',
                'area_description': 'Москва, Россия',
                'contact': {'phone': 'phone_pd_i'},
            },
            {
                'visit_status': 'pending',
                'type': 'destination',
                'uri': 'some uri',
                'coordinates': [3.0, 3.3],
                'full_text': 'Россия, Москва, Садовническая улица 82',
                'short_text': 'БЦ Аврора 3',
                'entrance': '4',
                'comment': 'some comment',
                'area_description': 'Москва, Россия',
                'contact': {'phone': 'phone_pd_i'},
            },
            {
                'visit_status': 'pending',
                'type': 'destination',
                'uri': 'some uri',
                'coordinates': [4.0, 4.4],
                'full_text': 'Россия, Москва, Садовническая улица 82',
                'short_text': 'БЦ Аврора 4',
                'entrance': '4',
                'comment': 'some comment',
                'area_description': 'Москва, Россия',
                'contact': {'phone': 'phone_pd_i'},
            },
            {
                'visit_status': 'pending',
                'type': 'destination',
                'uri': 'some uri',
                'coordinates': [5.0, 5.5],
                'full_text': 'Россия, Москва, Садовническая улица 82',
                'short_text': 'БЦ Аврора 5',
                'entrance': '4',
                'comment': 'some comment',
                'area_description': 'Москва, Россия',
                'contact': {'phone': 'phone_pd_i'},
            },
        ],
        'performer_route': {
            'sorted_route_points': [{'coordinates': [3.0, 3.3]}],
        },
        'performer': {
            'name': 'Petr',
            'short_name': 'Иван',
            'vehicle_model': 'BMW',
            'vehicle_number': 'A001AA77',
            'photo_url': 'testavatar',
            'phone': '',
            'rating': '4.7',
        },
        'actions': [
            {'type': 'feedback', 'title': 'Фидбэк', 'subtitles': []},
            {
                'title': 'Звонок курьеру',
                'communication_method': {
                    'forwarding_id': 'performer',
                    'type': 'voice_forwarding_call',
                },
                'type': 'performer_call',
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
                'type': 'order_more',
                'title': 'Заказать еще',
                'vertical': 'delivery',
                'vertical_trap': True,
                'sheet_expansion': 'collapsed',
            },
        ],
        'details': {
            'sections': [
                {
                    'items': [
                        {'title': 'Тариф Курьер', 'type': 'subtitle'},
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
                            'title': '298.8\xa0₽',
                            'type': 'subtitle',
                            'subtitle': 'Стимость',
                        },
                        {
                            'subtitle': 'Оплата картой',
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
            'title': 'Детали заказа',
            'subtitle': 'Стоимость доставки 298.8\xa0₽',
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
                        'lead_icon': {'image_tag': 'delivery_door_to_door'},
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
                            'text': 'Оплата картой',
                            'typography': 'body2',
                        },
                        'subtitle': {
                            'color': 'TextMinor',
                            'max_lines': 1,
                            'text': 'Способ оплаты',
                            'typography': 'caption1',
                        },
                        'type': 'list_item',
                        'lead_icon': {'image_tag': 'delivery_payment_default'},
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
                            'color': 'TextMain',
                            'max_lines': 1,
                            'text': 'БЦ Аврора 1',
                            'typography': 'body2',
                        },
                        'subtitle': {
                            'color': 'TextMinor',
                            'max_lines': 1,
                            'text': 'под. 4',
                            'typography': 'caption1',
                        },
                        'lead_icon': {'image_tag': 'delivery_point_red'},
                    },
                    {'id': matching.uuid_string, 'type': 'separator'},
                    {
                        'id': matching.uuid_string,
                        'subtitle': {
                            'color': 'TextMain',
                            'max_lines': 1,
                            'text': 'some comment',
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
                    {
                        'id': matching.uuid_string,
                        'title': {
                            'color': 'TextMinor',
                            'max_lines': 1,
                            'text': 'Получатель № 1',
                            'typography': 'caption1',
                        },
                        'type': 'header',
                    },
                    {
                        'id': matching.uuid_string,
                        'subtitle': {
                            'color': 'TextMain',
                            'max_lines': 1,
                            'text': 'phone_pd_i',
                            'typography': 'body2',
                        },
                        'lead_icon': {'image_tag': 'delivery_phone'},
                        'title': {
                            'text': 'Телефон для связи',
                            'max_lines': 1,
                            'typography': 'caption1',
                            'color': 'TextMinor',
                        },
                        'type': 'list_item',
                    },
                    {'id': matching.uuid_string, 'type': 'separator'},
                    {
                        'id': matching.uuid_string,
                        'subtitle': {
                            'color': 'TextMinor',
                            'max_lines': 1,
                            'text': 'под. 4',
                            'typography': 'caption1',
                        },
                        'title': {
                            'color': 'TextMain',
                            'max_lines': 1,
                            'text': 'БЦ Аврора 2',
                            'typography': 'body2',
                        },
                        'lead_icon': {'image_tag': 'delivery_point'},
                        'type': 'list_item',
                    },
                    {'id': matching.uuid_string, 'type': 'separator'},
                    {
                        'id': matching.uuid_string,
                        'subtitle': {
                            'color': 'TextMain',
                            'max_lines': 1,
                            'text': 'some comment',
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
                            'color': 'TextMain',
                            'max_lines': 1,
                            'text': 'БЦ Аврора 3',
                            'typography': 'body2',
                        },
                        'subtitle': {
                            'color': 'TextMinor',
                            'max_lines': 1,
                            'text': 'под. 4',
                            'typography': 'caption1',
                        },
                        'lead_icon': {'image_tag': 'delivery_point'},
                    },
                    {'id': matching.uuid_string, 'type': 'separator'},
                    {
                        'id': matching.uuid_string,
                        'subtitle': {
                            'color': 'TextMain',
                            'max_lines': 1,
                            'text': 'some comment',
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
                    {'id': matching.uuid_string, 'type': 'separator'},
                    {
                        'id': matching.uuid_string,
                        'subtitle': {
                            'color': 'TextMinor',
                            'max_lines': 1,
                            'text': 'под. 4',
                            'typography': 'caption1',
                        },
                        'title': {
                            'color': 'TextMain',
                            'max_lines': 1,
                            'text': 'БЦ Аврора 4',
                            'typography': 'body2',
                        },
                        'lead_icon': {'image_tag': 'delivery_point'},
                        'type': 'list_item',
                    },
                    {'id': matching.uuid_string, 'type': 'separator'},
                    {
                        'id': matching.uuid_string,
                        'subtitle': {
                            'color': 'TextMain',
                            'max_lines': 1,
                            'text': 'some comment',
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
                    {
                        'id': matching.uuid_string,
                        'title': {
                            'color': 'TextMinor',
                            'max_lines': 1,
                            'text': 'Получатель № 4',
                            'typography': 'caption1',
                        },
                        'type': 'header',
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
                    {'id': matching.uuid_string, 'type': 'separator'},
                    {
                        'id': matching.uuid_string,
                        'subtitle': {
                            'color': 'TextMinor',
                            'max_lines': 1,
                            'text': 'под. 4',
                            'typography': 'caption1',
                        },
                        'title': {
                            'color': 'TextMain',
                            'max_lines': 1,
                            'text': 'БЦ Аврора 5',
                            'typography': 'body2',
                        },
                        'lead_icon': {'image_tag': 'delivery_point'},
                        'type': 'list_item',
                    },
                    {'id': matching.uuid_string, 'type': 'separator'},
                    {
                        'id': matching.uuid_string,
                        'subtitle': {
                            'color': 'TextMain',
                            'max_lines': 1,
                            'text': 'some comment',
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
        ],
    }

    assert response.headers['X-Refresh-After'] == '10000'


async def test_performer_position(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        get_default_order_id,
        default_pa_headers,
        mock_claims_full,
        mock_driver_trackstory,
):
    mock_claims_full.current_point = {
        'claim_point_id': 5,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': 'pending',
    }

    key = await get_sharing_key(
        taxi_cargo_c2c, get_default_order_id(), 'cargo-claims',
    )

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/shared-route/performer-position', json={'key': key},
    )
    assert response.status_code == 200
    assert response.json() == {
        'position': mock_driver_trackstory.position,
        'pin': {'type': 'default', 'pin_type': 'auto'},
    }

    assert response.headers['X-Refresh-After'] == '10000'


async def test_c2c_voiceforwarding(
        taxi_cargo_c2c, create_cargo_c2c_orders, mockserver, mock_claims_full,
):
    @mockserver.json_handler('/vgw-api/v1/forwardings')
    def _vgw_request(request):
        resp = {
            'phone': '+71234567890',
            'ext': '100',
            'expires_at': '2020-04-01T11:35:00+00:00',
        }
        return mockserver.make_response(json=resp)

    order_id = await create_cargo_c2c_orders()
    key = await get_sharing_key(taxi_cargo_c2c, order_id, 'cargo-c2c')

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/shared-route/voiceforwarding',
        json={'key': key, 'forwarding_id': 'performer'},
    )
    assert response.status_code == 200
    assert response.json() == {'phone': '+71234567890', 'ext': '100'}


@pytest.mark.parametrize(
    'status',
    [
        pytest.param('accepted'),
        pytest.param('performer_lookup'),
        pytest.param('performer_draft'),
    ],
)
async def test_performer_search_context(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mock_claims_full,
        status,
):
    mock_claims_full.claim_status = status
    mock_claims_full.current_point_id = 1

    order_id = await create_cargo_c2c_orders()
    key = await get_sharing_key(
        taxi_cargo_c2c, order_id, 'cargo-c2c', 'phone_pd_id_3',
    )

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/shared-route/info',
        json={'key': key},
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.json()['context']['performer_search']
    assert response.json()['performer']['photo_url'] == 'testavatar'


async def test_feedback_requested(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mock_claims_full,
        create_cargo_claims_orders,
        get_default_order_id,
        order_processing_feedback_requested,
):
    mock_claims_full.current_point = {
        'claim_point_id': 5,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': 'pending',
    }

    key = await get_sharing_key(
        taxi_cargo_c2c,
        get_default_order_id(),
        'cargo-claims',
        'phone_pd_id_1',
    )
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/shared-route/feedback',
        json={
            'key': key,
            'score': 3,
            'comment': 'comment',
            'reasons': [{'reason_id': 'a'}, {'reason_id': 'b'}],
        },
        headers={'X-Idempotency-Token': '123'},
    )

    assert response.status_code == 200
    assert response.json() == {'operation_id': '123'}

    assert order_processing_feedback_requested.next_call() == {
        'arg': {
            'data': {
                'order_id': 'b1fe01ddc30247279f806e6c5e210a9f',
                'order_provider_id': 'cargo-claims',
                'phone_pd_id': 'phone_pd_id_1',
                'type': 'order_feedback',
                'score': 3,
                'comment': 'comment',
                'reasons': [{'reason_id': 'a'}, {'reason_id': 'b'}],
            },
            'kind': 'feedback-requested',
        },
    }


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
    CARGO_C2C_REQUIREMENT_IMAGE_TAGS={
        '__default__': 'delivery_requirement_default',
        'door_to_door': 'delivery_door_to_door',
    },
)
@pytest.mark.config(CARGO_C2C_ENABLE_CARGO_CLAIMS_ETA=True)
@pytest.mark.experiments3(filename='experiment.json')
async def test_sender_shared_route(
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
    key = await get_sharing_key(
        taxi_cargo_c2c, order_id, 'cargo-c2c', 'phone_pd_id_1',
    )

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/shared-route/info',
        json={'key': key},
        headers={'Accept-Language': 'ru'},
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
                    {'title': 'Тариф Курьер', 'type': 'subtitle'},
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
    assert resp == {
        'context': {'is_performer_position_available': True},
        'summary': 'Курьер в пути к точке отправления: ~1 мин',
        'description': 'голубой BMW',
        'performer': {
            'name': 'Petr',
            'short_name': 'Иван',
            'rating': '4.7',
            'phone': '',
            'photo_url': 'testavatar',
            'vehicle_model': 'BMW',
            'vehicle_number': 'A001AA77',
        },
        'performer_route': {
            'sorted_route_points': [{'coordinates': [3, 3.3]}],
        },
        'actions': [
            {'type': 'feedback', 'title': 'Фидбэк', 'subtitles': []},
            {
                'type': 'performer_call',
                'title': 'Звонок курьеру',
                'communication_method': {
                    'type': 'voice_forwarding_call',
                    'forwarding_id': 'performer',
                },
            },
        ],
        'route_points': [
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
        'details': {
            'sections': [
                {
                    'items': [
                        {'title': 'Тариф Курьер', 'type': 'subtitle'},
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
            'title': 'Детали заказа',
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
                        'lead_icon': {'image_tag': 'delivery_door_to_door'},
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
                        'lead_icon': {'image_tag': 'delivery_payment_default'},
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
                        'subtitle': {
                            'text': 'some comment',
                            'max_lines': 1,
                            'typography': 'body2',
                            'color': 'TextMain',
                        },
                        'lead_icon': {'image_tag': 'delivery_comment_outline'},
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
    }


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
    CARGO_C2C_REQUIREMENT_IMAGE_TAGS={
        '__default__': 'delivery_requirement_default',
        'door_to_door': 'delivery_door_to_door',
    },
)
@pytest.mark.config(CARGO_C2C_ENABLE_CARGO_CLAIMS_ETA=True)
@pytest.mark.experiments3(filename='experiment.json')
async def test_recipient_shared_route(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mock_claims_full,
        mockserver,
        load_json,
):
    mock_claims_full.current_point = {
        'claim_point_id': 5,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': 'pending',
    }

    order_id = await create_cargo_c2c_orders()
    key = await get_sharing_key(
        taxi_cargo_c2c, order_id, 'cargo-c2c', 'phone_pd_id_2',
    )

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/shared-route/info',
        json={'key': key},
        headers={'Accept-Language': 'ru'},
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
        'lead_icon': {'image_tag': 'delivery_info'},
        'subtitle': {
            'color': 'TextMinor',
            'max_lines': 1,
            'text': 'Курьер - оплачено',
            'typography': 'caption1',
        },
        'sections': [
            {
                'items': [
                    {'title': 'Тариф Курьер', 'type': 'subtitle'},
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
    assert resp == {
        # would be included
        # if we didn't ignore the rest of recipient's route points
        'context': {},  # 'is_performer_position_available': True},
        'summary': 'Курьер в пути к точке получения: ~1 мин',
        'description': 'голубой BMW',
        'performer': {
            'name': 'Petr',
            'short_name': 'Иван',
            'rating': '4.7',
            'phone': '',
            'photo_url': 'testavatar',
            'vehicle_model': 'BMW',
            'vehicle_number': 'A001AA77',
        },
        'performer_route': {
            'sorted_route_points': [{'coordinates': [5, 5.5]}],
        },
        'actions': [
            {'type': 'feedback', 'title': 'Фидбэк', 'subtitles': []},
            {
                'type': 'performer_call',
                'title': 'Звонок курьеру',
                'communication_method': {
                    'type': 'voice_forwarding_call',
                    'forwarding_id': 'performer',
                },
            },
        ],
        'route_points': [
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
                'coordinates': [5, 5.5],
                'full_text': 'Россия, Москва, Садовническая улица 82',
                'short_text': 'БЦ Аврора 5',
                'area_description': 'Москва, Россия',
                'entrance': '4',
                'comment': 'some comment',
                'contact': {'phone': 'phone_pd_i'},
            },
        ],
        'details': {
            'sections': [
                {
                    'items': [
                        {'title': 'Тариф Курьер', 'type': 'subtitle'},
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
            'title': 'Детали заказа',
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
                        'lead_icon': {'image_tag': 'delivery_door_to_door'},
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
                        'lead_icon': {'image_tag': 'delivery_payment_default'},
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
                            'color': 'TextMain',
                            'max_lines': 1,
                            'text': 'БЦ Аврора 2',
                            'typography': 'body2',
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
                        'subtitle': {
                            'text': 'some comment',
                            'max_lines': 1,
                            'typography': 'body2',
                            'color': 'TextMain',
                        },
                        'lead_icon': {'image_tag': 'delivery_comment_outline'},
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
                            'color': 'TextMain',
                            'max_lines': 1,
                            'text': 'БЦ Аврора 5',
                            'typography': 'body2',
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
                        'subtitle': {
                            'text': 'some comment',
                            'max_lines': 1,
                            'typography': 'body2',
                            'color': 'TextMain',
                        },
                        'lead_icon': {'image_tag': 'delivery_comment_outline'},
                    },
                ],
            },
        ],
    }


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
)
@pytest.mark.config(CARGO_C2C_ENABLE_CARGO_CLAIMS_ETA=True)
@pytest.mark.experiments3(filename='experiment.json')
async def test_recipient_shared_route_b2c(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        get_default_order_id,
        default_pa_headers,
        mock_claims_full,
        mockserver,
        load_json,
):
    mock_claims_full.current_point = {
        'claim_point_id': 5,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': 'pending',
    }

    key = await get_sharing_key(
        taxi_cargo_c2c,
        get_default_order_id(),
        'cargo-claims',
        'phone_pd_id_2',
    )
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/shared-route/info',
        json={'key': key},
        headers={'Accept-Language': 'ru'},
    )

    assert response.status_code == 200


@pytest.mark.experiments3(filename='experiment.json')
async def test_ndd_with_support(
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

    key = await get_sharing_key(
        taxi_cargo_c2c,
        get_default_order_id(),
        'logistic-platform',
        'phone_pd_id_1',
    )

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/shared-route/info',
        json={'key': key},
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp['actions'] == [
        {
            'ndd_data': {
                'operator_id': 'taxi-external',
                'external_order_id': '32779352',
                'lp_order_id': 'b1fe01ddc30247279f806e6c5e210a9f',
            },
            'title': 'Помощь',
            'type': 'show_support_web',
        },
    ]
