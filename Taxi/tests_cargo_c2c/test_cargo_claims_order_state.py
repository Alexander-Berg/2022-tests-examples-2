# pylint: disable=too-many-lines
import pytest

from testsuite.utils import matching


@pytest.mark.config(CARGO_C2C_ENABLE_CARGO_CLAIMS_ETA=True)
@pytest.mark.experiments3(filename='experiment.json')
async def test_sender(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        get_default_order_id,
        default_pa_headers,
        mock_claims_full,
):
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-claims/' + get_default_order_id(),
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
            'text': 'Рога и Копыта',
            'typography': 'caption1',
        },
        'lead_icon': {'image_tag': 'delivery_info'},
        'sections': [
            {
                'items': [
                    {
                        'subtitle': 'Ср 23 Сентября 17:44',
                        'title': 'Тариф Курьер',
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
                                'text': 'Доставка',
                                'typography': 'body2',
                            },
                            'trail_text': {
                                'color': 'TextMain',
                                'max_lines': 1,
                                'text': 'Оплачено',
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
                                'text': 'Исполнитель',
                                'typography': 'caption1',
                            },
                        },
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'Petr',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'Авто',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'subtitle': {
                                'text': 'голубой BMW, A001AA77',
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
                                'text': 'БЦ Аврора',
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
                                'text': 'БЦ Аврора',
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
                                'text': 'БЦ Аврора',
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
                                'subtitle': 'Ср 23 Сентября 17:44',
                                'title': 'Тариф Курьер',
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
            'description': 'Рога и Копыта',
            'summary': 'Заказ в пути к точке получения: 1 мин',
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
                    'short_text': 'БЦ Аврора',
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
                    'short_text': 'БЦ Аврора',
                    'area_description': 'Москва, Россия',
                },
                {
                    'visit_status': 'pending',
                    'type': 'destination',
                    'uri': 'some uri',
                    'coordinates': [3, 3.3],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора',
                    'area_description': 'Москва, Россия',
                },
                {
                    'visit_status': 'pending',
                    'type': 'destination',
                    'uri': 'some uri',
                    'coordinates': [4, 4.4],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора',
                    'area_description': 'Москва, Россия',
                },
                {
                    'visit_status': 'pending',
                    'type': 'destination',
                    'uri': 'some uri',
                    'coordinates': [5, 5.5],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора',
                    'area_description': 'Москва, Россия',
                },
            ],
            'active_route_points': [2],
            'performer_route': {
                'sorted_route_points': [{'coordinates': [3, 3.3]}],
            },
            'meta': {
                'order_provider_id': 'cargo-claims',
                'order_status': 'pickuped',
                'roles': ['sender'],
                'tariff_class': 'courier',
            },
        },
    }


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.parametrize(
    'status, current_point_id, point_visit_status, '
    'expected_summary, expected_description',
    [
        pytest.param(
            'accepted', 1, 'pending', 'Заказ собирают', 'Рога и Копыта',
        ),
        pytest.param(
            'accepted',
            1,
            'pending',
            'Заказ собирают',
            'голубой BMW',
            marks=pytest.mark.config(ORDER_ROUTE_SHARING_SUPPORTED_CORPS={}),
        ),
        pytest.param(
            'performer_lookup',
            1,
            'pending',
            'Заказ собирают',
            'Рога и Копыта',
        ),
        pytest.param(
            'performer_draft', 1, 'pending', 'Заказ собирают', 'Рога и Копыта',
        ),
        pytest.param(
            'performer_found',
            1,
            'pending',
            'Курьер направляется за посылкой',
            'Рога и Копыта',
        ),
        pytest.param(
            'performer_found',
            1,
            'pending',
            'Курьер направляется за посылкой',
            'голубой BMW',
            marks=pytest.mark.config(ORDER_ROUTE_SHARING_SUPPORTED_CORPS={}),
        ),
        pytest.param(
            'performer_found',
            1,
            'pending',
            'Курьер направляется за посылкой: 5 мин',
            'Рога и Копыта',
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
            'Рога и Копыта',
            marks=pytest.mark.now('2020-06-17T22:40:50+0300'),
        ),
        pytest.param(
            'pickup_arrived',
            1,
            'arrived',
            'Платное ожидание',
            'Рога и Копыта',
            marks=pytest.mark.now('2020-06-17T22:50:50+0300'),
        ),
        pytest.param(
            'ready_for_pickup_confirmation',
            1,
            'arrived',
            'Ожидание',
            'Рога и Копыта',
            marks=pytest.mark.now('2020-06-17T22:40:50+0300'),
        ),
        pytest.param(
            'ready_for_pickup_confirmation',
            1,
            'arrived',
            'Платное ожидание',
            'Рога и Копыта',
            marks=pytest.mark.now('2020-06-17T22:50:50+0300'),
        ),
        pytest.param(
            'pickuped',
            2,
            'pending',
            'Заказ в пути к точке получения',
            'Рога и Копыта',
        ),
        pytest.param(
            'pickuped',
            2,
            'pending',
            'Заказ в пути к точке получения: 5 мин',
            'Рога и Копыта',
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
            'Рога и Копыта',
        ),
        pytest.param(
            'ready_for_delivery_confirmation',
            2,
            'arrived',
            'Курьер приехал на точку получения',
            'Рога и Копыта',
        ),
        pytest.param('delivered', 5, 'visited', 'Доставлено', 'Рога и Копыта'),
        pytest.param(
            'delivered_finish', 5, 'visited', 'Доставлено', 'Рога и Копыта',
        ),
        pytest.param(
            'returning',
            1,
            'pending',
            'Курьер возвращает посылку',
            'Рога и Копыта',
        ),
        pytest.param(
            'return_arrived',
            1,
            'pending',
            'Курьер возвращает посылку',
            'Рога и Копыта',
        ),
        pytest.param(
            'ready_for_return_confirmation',
            1,
            'pending',
            'Курьер возвращает посылку',
            'Рога и Копыта',
        ),
        pytest.param(
            'returned', 1, 'pending', 'Заказ отменен', 'Рога и Копыта',
        ),
        pytest.param(
            'returned_finish', 1, 'pending', 'Заказ отменен', 'Рога и Копыта',
        ),
        pytest.param(
            'performer_not_found',
            1,
            'pending',
            'Заказ отменен',
            'Рога и Копыта',
        ),
        pytest.param('failed', 1, 'pending', 'Заказ отменен', 'Рога и Копыта'),
        pytest.param(
            'cancelled', 1, 'pending', 'Заказ отменен', 'Рога и Копыта',
        ),
        pytest.param(
            'cancelled_with_payment',
            1,
            'pending',
            'Заказ отменен',
            'Рога и Копыта',
        ),
        pytest.param(
            'cancelled_by_taxi',
            1,
            'pending',
            'Заказ отменен',
            'Рога и Копыта',
        ),
        pytest.param(
            'cancelled_with_items_on_hands',
            1,
            'pending',
            'Заказ отменен',
            'Рога и Копыта',
        ),
    ],
)
async def test_sender_texts(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        get_default_order_id,
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

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-claims/' + get_default_order_id(),
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


@pytest.mark.experiments3(filename='experiment.json')
async def test_sender_delivery_terminated(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        get_default_order_id,
        default_pa_headers,
        mock_claims_full,
):
    mock_claims_full.claim_status = 'delivered_finish'

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-claims/' + get_default_order_id(),
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
    assert response.json()['state']['context']['present_as_completed']


@pytest.mark.config(CARGO_C2C_ENABLE_CARGO_CLAIMS_ETA=True)
@pytest.mark.experiments3(filename='experiment.json')
async def test_recipient(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        get_default_order_id,
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

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-claims/' + get_default_order_id(),
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
            'text': 'Рога и Копыта',
            'typography': 'caption1',
        },
        'lead_icon': {'image_tag': 'delivery_info'},
        'sections': [
            {
                'items': [
                    {
                        'subtitle': 'Ср 23 Сентября 17:44',
                        'title': 'Тариф Курьер',
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
                                'text': 'Доставка',
                                'typography': 'body2',
                            },
                            'trail_text': {
                                'color': 'TextMain',
                                'max_lines': 1,
                                'text': 'Оплачено',
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
                                'text': 'Исполнитель',
                                'typography': 'caption1',
                            },
                        },
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'Petr',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                        },
                        {'type': 'separator', 'id': matching.uuid_string},
                        {
                            'type': 'list_item',
                            'id': matching.uuid_string,
                            'title': {
                                'text': 'Авто',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'subtitle': {
                                'text': 'голубой BMW, A001AA77',
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
                                'text': 'БЦ Аврора',
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
                            'subtitle': {
                                'text': 'some comment',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'lead_icon': {
                                'image_tag': 'delivery_comment_outline',
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
                                'subtitle': 'Ср 23 Сентября 17:44',
                                'title': 'Тариф Курьер',
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
            'description': 'Рога и Копыта',
            'summary': 'Заказ в пути к точке получения: 1 мин',
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
                    'visit_status': 'pending',
                    'type': 'destination',
                    'uri': 'some uri',
                    'coordinates': [5, 5.5],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора',
                    'area_description': 'Москва, Россия',
                    'entrance': '4',
                    'comment': 'some comment',
                    'contact': {'phone': 'phone_pd_i'},
                },
            ],
            'active_route_points': [0],
            'performer_route': {
                'sorted_route_points': [{'coordinates': [5, 5.5]}],
            },
            'meta': {
                'order_provider_id': 'cargo-claims',
                'order_status': 'pickuped',
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
            'arrived',
            4,
            'Курьер около вас. Будьте готовы принять посылку',
            'Рога и Копыта',
        ),
        pytest.param(
            'arrived',
            4,
            'Курьер около вас. Будьте готовы принять посылку',
            'голубой BMW',
            marks=pytest.mark.config(ORDER_ROUTE_SHARING_SUPPORTED_CORPS={}),
        ),
        pytest.param('visited', 6, 'Доставлено', 'Рога и Копыта'),
        pytest.param(
            'pending', 5, 'Заказ в пути к точке получения', 'Рога и Копыта',
        ),
        pytest.param(
            'pending',
            5,
            'Заказ в пути к точке получения: 5 мин',
            'Рога и Копыта',
            marks=pytest.mark.config(CARGO_C2C_ENABLE_CARGO_CLAIMS_ETA=True),
        ),
        pytest.param(
            'pending', 4, 'Курьер направляется за посылкой', 'Рога и Копыта',
        ),
        pytest.param(
            'pending',
            4,
            'Курьер будет у вас через ~5 мин',
            'Рога и Копыта',
            marks=pytest.mark.config(CARGO_C2C_ENABLE_CARGO_CLAIMS_ETA=True),
        ),
    ],
)
@pytest.mark.now('2020-09-23T14:44:01.174824+00:00')
async def test_recipient_texts(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        get_default_order_id,
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

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-claims/' + get_default_order_id(),
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
        create_cargo_claims_orders,
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

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-claims/' + get_default_order_id(),
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
        create_cargo_claims_orders,
        get_default_order_id,
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

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/deliveries',
        json={'deliveries': []},
        headers=default_pa_headers('phone_pd_id_2'),
    )

    assert response.status_code == 200
    resp = response.json()
    resp['deliveries'][0].pop('etag')
    assert resp == {
        'deliveries': [
            {
                'delivery_id': 'cargo-claims/' + get_default_order_id(),
                'state': {
                    'context': {
                        'auto_open_postcard': False,
                        'is_performer_position_available': True,
                        'display_targets': ['multiorder'],
                    },
                    'description': 'Рога и Копыта',
                    'summary': 'Заказ в пути к точке получения: 1 мин',
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
                        {'coordinates': [5.0, 5.5], 'type': 'destination'},
                    ],
                    'active_route_points': [0],
                    'performer_route': {
                        'sorted_route_points': [{'coordinates': [5.0, 5.5]}],
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
                        'order_provider_id': 'cargo-claims',
                        'order_status': 'pickuped',
                        'roles': ['recipient'],
                        'tariff_class': 'courier',
                    },
                },
            },
        ],
        'shipments': [],
    }


MARKET_CORP_CLIENT_ID = 'market_corp_client_id____size_32'


@pytest.mark.config(
    CARGO_C2C_CLAIMS_FEEDBACK_REASONS=[
        {
            'scores': [1, 2, 3, 4],
            'reason_id': 'too_long_delivery',
            'tanker_key': {
                'key': (
                    'client_message.feedback_action.reasons.too_long_delivery'
                ),
                'keyset': 'cargo',
            },
        },
        {
            'scores': [1, 2, 3, 4],
            'allowed_for': [
                {
                    'corp_client_ids': ['5e36732e2bc54e088b1466e08e31c486'],
                    'taxi_requirements': ['door_to_door'],
                },
            ],
            'reason_id': 'unable_to_contact',
            'tanker_key': {
                'key': (
                    'client_message.feedback_action.reasons.unable_to_contact'
                ),
                'keyset': 'cargo',
            },
        },
        {
            'scores': [1],
            'reason_id': 'order_wasnt_delivered',
            'allowed_for': [
                {
                    'corp_client_ids': [
                        '5e36732e2bc54e088b1466e08e31c486',
                        'market_corp_client_id____size_32',
                    ],
                },
            ],
            'tanker_key': {
                'key': (
                    'client_message.feedback_action'
                    '.reasons.order_wasnt_delivered'
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
    ],
    CARGO_C2C_FEEDBACK_SUBTITLES=[
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
                    'client_message.feedback_action'
                    '.subtitles.what_did_you_like'
                ),
                'keyset': 'cargo',
            },
        },
    ],
)
@pytest.mark.experiments3(filename='experiment.json')
async def test_feedback_action(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        get_default_order_id,
        default_pa_headers,
        mock_claims_full,
):
    mock_claims_full.corp_client_id = 'market_corp_client_id____size_32'
    mock_claims_full.claim_status = 'delivered'

    response = await taxi_cargo_c2c.post(
        '/v1/actions/save-client-feedback',
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': get_default_order_id(),
                'order_provider_id': 'cargo-claims',
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
            'delivery_id': 'cargo-claims/' + get_default_order_id(),
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
    ]


@pytest.mark.experiments3(filename='experiment.json')
async def test_fallback_address(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        get_default_order_id,
        default_pa_headers,
        mockserver,
        load_json,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        resp = load_json('claim_full_response.json')
        for point in resp['route_points']:
            point['address'].pop('uri')
            point['address'].pop('shortname')
            point['address'].pop('description')

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
            point['address'].pop('uri')
            point['address'].pop('shortname')
            point['address'].pop('description')
            points_eta['route_points'].append(point)

        return mockserver.make_response(json=points_eta)

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-claims/' + get_default_order_id(),
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
    assert response.json()['state']['sorted_route_points'] == [
        {
            'visit_status': 'pending',
            'type': 'destination',
            'uri': 'ymapsbm1://geo?ll=5.5%2C5',
            'coordinates': [5, 5.5],
            'full_text': 'Россия, Москва, Садовническая улица 82',
            'short_text': 'Россия, Москва, Садовническая улица 82',
            'area_description': 'Москва',
            'entrance': '4',
            'comment': 'some comment',
            'contact': {'phone': 'phone_pd_i'},
        },
    ]


MARKET_CORP_CLIENT_ID = '70a499f9eec844e9a758f4bc33e667c0'


@pytest.mark.config(
    CARGO_C2C_ENABLE_CARGO_CLAIMS_ETA=True,
    CARGO_C2C_SHOW_MARKET_CANCEL_ACTION=True,
    CARGO_C2C_CORP_CLIENT_ID_TO_SHOW_SUPPORT_SERVICE={
        MARKET_CORP_CLIENT_ID: {
            'title_key': 'client_message.support_from_service_action.title',
            'title_keyset': 'cargo',
            'url_template': 'some_{locale}url_template?{order_id}',
        },
    },
)
@pytest.mark.experiments3(filename='experiment.json')
async def test_corp_service_content_to_show_on(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        get_default_order_id,
        default_pa_headers,
        mock_claims_full,
):
    mock_claims_full.claim_status = 'performer_lookup'
    mock_claims_full.current_point_id = 1
    mock_claims_full.corp_client_id = MARKET_CORP_CLIENT_ID
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-claims/' + get_default_order_id(),
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
    resp = response.json()
    assert resp['state']['primary_actions'] == [
        {
            'communication_method': {
                'forwarding_id': 'performer',
                'type': 'voice_forwarding_call',
            },
            'title': 'Звонок курьеру',
            'type': 'performer_call',
        },
        {
            'title': 'Помощь',
            'type': 'show_support_web',
            'url': 'some_enurl_template?b1fe01ddc30247279f806e6c5e210a9f',
        },
        {
            'sharing_url': matching.AnyString(),
            'title': 'Поделиться',
            'type': 'share',
        },
    ]


TEST_MARKET_URL = (
    'https://taxi-frontend.taxi.tst.yandex.ru/'
    + 'webview/history/item/market/'
)


@pytest.mark.config(
    CARGO_C2C_ENABLE_CARGO_CLAIMS_ETA=True,
    CARGO_C2C_CORP_CLIENT_ID_TO_SHOW_CONTENT_ORDER_HISTORY={
        MARKET_CORP_CLIENT_ID: {
            'title_key': (
                'client_message.delivery_from_service_content_action.title'
            ),
            'url': TEST_MARKET_URL + '{order_id}',
            'open_pdf': False,
        },
    },
    CARGO_C2C_SHOW_MARKET_CANCEL_ACTION=False,
)
@pytest.mark.experiments3(filename='experiment.json')
async def test_corp_service_content_to_show_off(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        get_default_order_id,
        default_pa_headers,
        mock_claims_full,
):
    mock_claims_full.claim_status = 'performer_lookup'
    mock_claims_full.current_point_id = 1
    mock_claims_full.corp_client_id = MARKET_CORP_CLIENT_ID
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-claims/' + get_default_order_id(),
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
    resp = response.json()
    assert resp['state']['primary_actions'] == [
        {
            'communication_method': {
                'forwarding_id': 'performer',
                'type': 'voice_forwarding_call',
            },
            'title': 'Звонок курьеру',
            'type': 'performer_call',
        },
        {
            'url': TEST_MARKET_URL + 'b1fe01ddc30247279f806e6c5e210a9f',
            'open_pdf': False,
            'title': 'Состав заказа',
            'type': 'show_content_order_history',
        },
        {
            'sharing_url': matching.AnyString(),
            'title': 'Поделиться',
            'type': 'share',
        },
    ]


@pytest.mark.config(
    CARGO_C2C_ENABLE_CARGO_CLAIMS_ETA=True,
    CARGO_C2C_CORP_CLIENT_ID_IMAGE_TAG_TO_SHOW={
        MARKET_CORP_CLIENT_ID: {
            'image_tag': 'delivery_market_icon_for_delivery_state',
        },
    },
)
@pytest.mark.experiments3(filename='experiment.json')
async def test_initiator_corp_icon_tag_to_show_delivery(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        get_default_order_id,
        default_pa_headers,
        mock_claims_full,
):
    mock_claims_full.corp_client_id = MARKET_CORP_CLIENT_ID
    mock_claims_full.claim_status = 'accepted'
    mock_claims_full.current_point_id = 1

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-claims/' + get_default_order_id(),
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
    resp = response.json()
    assert response.status_code == 200
    assert resp['state']['icon_strategy'] == {
        'image_tag': 'delivery_market_icon_for_delivery_state',
        'type': 'remote_image',
    }

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/deliveries',
        json={'deliveries': []},
        headers=default_pa_headers('phone_pd_id_2'),
    )
    assert response.status_code == 200
    resp = response.json()['deliveries'][0]
    assert resp['state']['icon_strategy'] == {
        'image_tag': 'delivery_market_icon_for_delivery_state',
        'type': 'remote_image',
    }


async def test_error_service(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        get_default_order_id,
        default_pa_headers,
        mockserver,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _handle(request):
        return mockserver.make_response(status=500)

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'cargo-claims/' + get_default_order_id(),
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
