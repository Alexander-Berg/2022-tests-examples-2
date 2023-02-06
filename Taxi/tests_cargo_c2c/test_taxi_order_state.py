# pylint: disable=too-many-lines
import pytest

from testsuite.utils import matching


@pytest.fixture(autouse=True)
def mock_driver_route_responder(mockserver, load_json):
    @mockserver.json_handler('/driver-route-responder/timeleft')
    def _timeleft(request):
        return mockserver.make_response(status=404)


def get_proc(order_id, status, taxi_status):
    return {
        '_id': order_id,
        'order': {
            'status': status,
            'taxi_status': taxi_status,
            'request': {
                'class': ['courier'],
                'source': {
                    'uris': ['some uri'],
                    'geopoint': [37.642859, 55.735316],
                    'fullname': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора',
                    'description': 'Москва, Россия',
                    'porchnumber': '10',
                    'extra_data': {
                        'floor': '1',
                        'apartment': '2',
                        'doorphone_number': '3',
                        'comment': '4',
                    },
                },
                'destinations': [
                    {
                        'uris': ['some uri'],
                        'geopoint': [38.642859, 56.735316],
                        'fullname': 'Россия, Москва, Садовническая улица 82',
                        'short_text': 'БЦ Аврора',
                        'description': 'Москва, Россия',
                        'porchnumber': '5',
                        'extra_data': {
                            'floor': '6',
                            'apartment': '7',
                            'doorphone_number': '8',
                            'comment': '9',
                        },
                    },
                ],
            },
            'nz': 'moscow',
        },
        'candidates': [
            {
                'first_name': 'Иван',
                'name': 'Petr',
                'phone_personal_id': '+7123_id',
                'driver_id': 'clid_driverid1',
                'db_id': 'parkid1',
                'car_model': 'BMW',
                'car_number': 'A001AA77',
                'car_color_code': 'some_code',
            },
        ],
        'performer': {'candidate_index': 0},
    }


@pytest.mark.experiments3(filename='experiment.json')
async def test_create(
        taxi_cargo_c2c,
        create_taxi_orders,
        get_default_order_id,
        default_pa_headers,
        order_archive_mock,
):
    order_archive_mock.set_order_proc(
        get_proc(get_default_order_id(), 'pending', None),
    )

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'taxi/' + get_default_order_id(),
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
    resp.pop('etag')
    assert resp == {
        'state': {
            'context': {
                'is_performer_position_available': True,
                'display_targets': ['multiorder'],
            },
            'summary': 'Курьер где-то',
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
            'secondary_actions': [],
            'sorted_route_points': [
                {
                    'visit_status': 'pending',
                    'type': 'source',
                    'uri': 'some uri',
                    'coordinates': [37.642859, 55.735316],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора',
                    'area_description': 'Москва, Россия',
                    'entrance': '10',
                    'floor': '1',
                    'room': '2',
                    'code': '3',
                },
                {
                    'visit_status': 'pending',
                    'type': 'destination',
                    'uri': 'some uri',
                    'coordinates': [38.642859, 56.735316],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора',
                    'area_description': 'Москва, Россия',
                    'entrance': '5',
                    'floor': '6',
                    'room': '7',
                    'code': '8',
                },
            ],
            'active_route_points': [0, 1],
            'performer_route': {
                'sorted_route_points': [
                    {'coordinates': [37.642859, 55.735316]},
                ],
            },
            'meta': {
                'order_provider_id': 'taxi',
                'order_status': 'pending',
                'roles': ['recipient'],
                'tariff_class': 'courier',
            },
            'content_sections': [
                {
                    'id': matching.uuid_string,
                    'items': [
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
                            'title': {
                                'text': 'БЦ Аврора',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'subtitle': {
                                'text': 'кв. 2, под. 10, этаж 1, домофон 3',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {'image_tag': 'delivery_point_red'},
                        },
                        {'id': matching.uuid_string, 'type': 'separator'},
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
                                'text': '4',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'lead_icon': {
                                'image_tag': 'delivery_comment_outline',
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
                            'title': {
                                'text': 'БЦ Аврора',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'subtitle': {
                                'text': 'кв. 7, под. 5, этаж 6, домофон 8',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {'image_tag': 'delivery_point'},
                        },
                        {'id': matching.uuid_string, 'type': 'separator'},
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
                                'text': '9',
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
        },
    }


@pytest.mark.config(
    ORDER_ROUTE_SHARING_SUPPORTED_CORPS={
        '5e36732e2bc54e088b1466e08e31c486': {
            'en': 'R&G',
            'ru': 'Рога и Копыта',
        },
    },
)
async def test_create_corp(
        taxi_cargo_c2c,
        create_taxi_orders,
        get_default_order_id,
        default_pa_headers,
        order_archive_mock,
):
    proc = get_proc(get_default_order_id(), 'pending', None)
    proc['order']['request'].update(
        {'corp': {'client_id': '5e36732e2bc54e088b1466e08e31c486'}},
    )
    order_archive_mock.set_order_proc(proc)

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'taxi/' + get_default_order_id(),
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
    assert resp['state']['description'] == 'R&G'
    assert resp['state']['summary'] == 'Заказ собирают'


@pytest.mark.experiments3(filename='experiment.json')
async def test_driving(
        taxi_cargo_c2c,
        create_taxi_orders,
        get_default_order_id,
        default_pa_headers,
        order_archive_mock,
):
    order_archive_mock.set_order_proc(
        get_proc(get_default_order_id(), 'assigned', 'driving'),
    )

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'taxi/' + get_default_order_id(),
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
    resp.pop('etag')
    assert resp == {
        'state': {
            'context': {
                'is_performer_position_available': True,
                'display_targets': ['multiorder'],
            },
            'summary': 'Курьер в пути к точке отправления',
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
            'secondary_actions': [],
            'sorted_route_points': [
                {
                    'visit_status': 'pending',
                    'type': 'source',
                    'uri': 'some uri',
                    'coordinates': [37.642859, 55.735316],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора',
                    'area_description': 'Москва, Россия',
                    'entrance': '10',
                    'floor': '1',
                    'room': '2',
                    'code': '3',
                },
                {
                    'visit_status': 'pending',
                    'type': 'destination',
                    'uri': 'some uri',
                    'coordinates': [38.642859, 56.735316],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора',
                    'area_description': 'Москва, Россия',
                    'entrance': '5',
                    'floor': '6',
                    'room': '7',
                    'code': '8',
                },
            ],
            'active_route_points': [0, 1],
            'performer_route': {
                'sorted_route_points': [
                    {'coordinates': [37.642859, 55.735316]},
                ],
            },
            'meta': {
                'order_provider_id': 'taxi',
                'order_status': 'assigned',
                'roles': ['recipient'],
                'tariff_class': 'courier',
            },
            'content_sections': [
                {
                    'id': matching.uuid_string,
                    'items': [
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
                            'title': {
                                'text': 'БЦ Аврора',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'subtitle': {
                                'text': 'кв. 2, под. 10, этаж 1, домофон 3',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {'image_tag': 'delivery_point_red'},
                        },
                        {'id': matching.uuid_string, 'type': 'separator'},
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
                                'text': '4',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'lead_icon': {
                                'image_tag': 'delivery_comment_outline',
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
                            'title': {
                                'text': 'БЦ Аврора',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'subtitle': {
                                'text': 'кв. 7, под. 5, этаж 6, домофон 8',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {'image_tag': 'delivery_point'},
                        },
                        {'id': matching.uuid_string, 'type': 'separator'},
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
                                'text': '9',
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
        },
    }


@pytest.mark.config(
    ORDER_ROUTE_SHARING_SUPPORTED_CORPS={
        '5e36732e2bc54e088b1466e08e31c486': {
            'en': 'R&G',
            'ru': 'Рога и Копыта',
        },
    },
)
async def test_driving_corp(
        taxi_cargo_c2c,
        create_taxi_orders,
        get_default_order_id,
        default_pa_headers,
        order_archive_mock,
):
    proc = get_proc(get_default_order_id(), 'assigned', 'driving')
    proc['order']['request'].update(
        {'corp': {'client_id': '5e36732e2bc54e088b1466e08e31c486'}},
    )
    order_archive_mock.set_order_proc(proc)

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'taxi/' + get_default_order_id(),
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
    assert resp['state']['description'] == 'R&G'
    assert resp['state']['summary'] == 'Заказ собирают'


@pytest.mark.experiments3(filename='experiment.json')
async def test_waiting(
        taxi_cargo_c2c,
        create_taxi_orders,
        get_default_order_id,
        default_pa_headers,
        order_archive_mock,
):
    order_archive_mock.set_order_proc(
        get_proc(get_default_order_id(), 'assigned', 'waiting'),
    )

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'taxi/' + get_default_order_id(),
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
    resp.pop('etag')
    assert resp == {
        'state': {
            'context': {
                'is_performer_position_available': True,
                'display_targets': ['multiorder'],
            },
            'summary': 'Курьер приехал',
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
            'secondary_actions': [],
            'sorted_route_points': [
                {
                    'visit_status': 'arrived',
                    'type': 'source',
                    'uri': 'some uri',
                    'coordinates': [37.642859, 55.735316],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора',
                    'area_description': 'Москва, Россия',
                    'entrance': '10',
                    'floor': '1',
                    'room': '2',
                    'code': '3',
                },
                {
                    'visit_status': 'pending',
                    'type': 'destination',
                    'uri': 'some uri',
                    'coordinates': [38.642859, 56.735316],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора',
                    'area_description': 'Москва, Россия',
                    'entrance': '5',
                    'floor': '6',
                    'room': '7',
                    'code': '8',
                },
            ],
            'active_route_points': [0, 1],
            'meta': {
                'order_provider_id': 'taxi',
                'order_status': 'assigned',
                'roles': ['recipient'],
                'tariff_class': 'courier',
            },
            'content_sections': [
                {
                    'id': matching.uuid_string,
                    'items': [
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
                            'title': {
                                'text': 'БЦ Аврора',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'subtitle': {
                                'text': 'кв. 2, под. 10, этаж 1, домофон 3',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {'image_tag': 'delivery_point_red'},
                        },
                        {'id': matching.uuid_string, 'type': 'separator'},
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
                                'text': '4',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'lead_icon': {
                                'image_tag': 'delivery_comment_outline',
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
                            'title': {
                                'text': 'БЦ Аврора',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'subtitle': {
                                'text': 'кв. 7, под. 5, этаж 6, домофон 8',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {'image_tag': 'delivery_point'},
                        },
                        {'id': matching.uuid_string, 'type': 'separator'},
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
                                'text': '9',
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
        },
    }


@pytest.mark.config(
    ORDER_ROUTE_SHARING_SUPPORTED_CORPS={
        '5e36732e2bc54e088b1466e08e31c486': {
            'en': 'R&G',
            'ru': 'Рога и Копыта',
        },
    },
)
async def test_waiting_corp(
        taxi_cargo_c2c,
        create_taxi_orders,
        get_default_order_id,
        default_pa_headers,
        order_archive_mock,
):
    proc = get_proc(get_default_order_id(), 'assigned', 'waiting')
    proc['order']['request'].update(
        {'corp': {'client_id': '5e36732e2bc54e088b1466e08e31c486'}},
    )
    order_archive_mock.set_order_proc(proc)

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'taxi/' + get_default_order_id(),
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
    assert resp['state']['description'] == 'R&G'
    assert resp['state']['summary'] == 'Заказ собирают'


@pytest.mark.experiments3(filename='experiment.json')
async def test_transporting(
        taxi_cargo_c2c,
        create_taxi_orders,
        get_default_order_id,
        default_pa_headers,
        order_archive_mock,
):
    order_archive_mock.set_order_proc(
        get_proc(get_default_order_id(), 'assigned', 'transporting'),
    )

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'taxi/' + get_default_order_id(),
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
    resp.pop('etag')
    assert resp == {
        'state': {
            'context': {
                'is_performer_position_available': True,
                'display_targets': ['multiorder'],
            },
            'summary': 'Курьер в пути к точке получения',
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
            'secondary_actions': [],
            'sorted_route_points': [
                {
                    'visit_status': 'visited',
                    'type': 'source',
                    'uri': 'some uri',
                    'coordinates': [37.642859, 55.735316],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора',
                    'area_description': 'Москва, Россия',
                    'entrance': '10',
                    'floor': '1',
                    'room': '2',
                    'code': '3',
                },
                {
                    'visit_status': 'pending',
                    'type': 'destination',
                    'uri': 'some uri',
                    'coordinates': [38.642859, 56.735316],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора',
                    'area_description': 'Москва, Россия',
                    'entrance': '5',
                    'floor': '6',
                    'room': '7',
                    'code': '8',
                },
            ],
            'active_route_points': [0, 1],
            'performer_route': {
                'sorted_route_points': [
                    {'coordinates': [38.642859, 56.735316]},
                ],
            },
            'meta': {
                'order_provider_id': 'taxi',
                'order_status': 'assigned',
                'roles': ['recipient'],
                'tariff_class': 'courier',
            },
            'content_sections': [
                {
                    'id': matching.uuid_string,
                    'items': [
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
                            'title': {
                                'text': 'БЦ Аврора',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'subtitle': {
                                'text': 'кв. 2, под. 10, этаж 1, домофон 3',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {'image_tag': 'delivery_point_red'},
                        },
                        {'id': matching.uuid_string, 'type': 'separator'},
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
                                'text': '4',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'lead_icon': {
                                'image_tag': 'delivery_comment_outline',
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
                            'title': {
                                'text': 'БЦ Аврора',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'subtitle': {
                                'text': 'кв. 7, под. 5, этаж 6, домофон 8',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {'image_tag': 'delivery_point'},
                        },
                        {'id': matching.uuid_string, 'type': 'separator'},
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
                                'text': '9',
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
        },
    }


@pytest.mark.config(
    ORDER_ROUTE_SHARING_SUPPORTED_CORPS={
        '5e36732e2bc54e088b1466e08e31c486': {
            'en': 'R&G',
            'ru': 'Рога и Копыта',
        },
    },
)
async def test_transporting_corp(
        taxi_cargo_c2c,
        create_taxi_orders,
        get_default_order_id,
        default_pa_headers,
        order_archive_mock,
):
    proc = get_proc(get_default_order_id(), 'assigned', 'transporting')
    proc['order']['request'].update(
        {'corp': {'client_id': '5e36732e2bc54e088b1466e08e31c486'}},
    )
    order_archive_mock.set_order_proc(proc)

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'taxi/' + get_default_order_id(),
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
    assert resp['state']['description'] == 'R&G'
    assert resp['state']['summary'] == 'Заказ в пути к точке получения'


@pytest.mark.experiments3(filename='experiment.json')
async def test_complete(
        taxi_cargo_c2c,
        create_taxi_orders,
        get_default_order_id,
        default_pa_headers,
        order_archive_mock,
        mockserver,
):
    @mockserver.json_handler('/driver-route-responder/timeleft')
    def _timeleft(request):
        return mockserver.make_response(json={}, status=200)

    order_archive_mock.set_order_proc(
        get_proc(get_default_order_id(), 'finished', 'complete'),
    )

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'taxi/' + get_default_order_id(),
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
    assert not _timeleft.times_called
    resp = response.json()
    resp.pop('etag')
    assert resp == {
        'state': {
            'context': {
                'present_as_completed': True,
                'display_targets': ['multiorder'],
            },
            'summary': 'Доставлено',
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
            'secondary_actions': [],
            'sorted_route_points': [
                {
                    'visit_status': 'visited',
                    'type': 'source',
                    'uri': 'some uri',
                    'coordinates': [37.642859, 55.735316],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора',
                    'area_description': 'Москва, Россия',
                    'entrance': '10',
                    'floor': '1',
                    'room': '2',
                    'code': '3',
                },
                {
                    'visit_status': 'visited',
                    'type': 'destination',
                    'uri': 'some uri',
                    'coordinates': [38.642859, 56.735316],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора',
                    'area_description': 'Москва, Россия',
                    'entrance': '5',
                    'floor': '6',
                    'room': '7',
                    'code': '8',
                },
            ],
            'active_route_points': [0, 1],
            'meta': {
                'order_provider_id': 'taxi',
                'order_status': 'finished',
                'roles': ['recipient'],
                'tariff_class': 'courier',
            },
            'content_sections': [
                {
                    'id': matching.uuid_string,
                    'items': [
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
                            'title': {
                                'text': 'БЦ Аврора',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'subtitle': {
                                'text': 'кв. 2, под. 10, этаж 1, домофон 3',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {'image_tag': 'delivery_point_red'},
                        },
                        {'id': matching.uuid_string, 'type': 'separator'},
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
                                'text': '4',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'lead_icon': {
                                'image_tag': 'delivery_comment_outline',
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
                            'title': {
                                'text': 'БЦ Аврора',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'subtitle': {
                                'text': 'кв. 7, под. 5, этаж 6, домофон 8',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {'image_tag': 'delivery_point'},
                        },
                        {'id': matching.uuid_string, 'type': 'separator'},
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
                                'text': '9',
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
            'completed_state_buttons': {
                'primary': {'action': {'type': 'done'}, 'title': 'Готово'},
            },
        },
    }

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/deliveries',
        json={'deliveries': []},
        headers=default_pa_headers('phone_pd_id_2'),
    )
    assert response.status_code == 200
    assert response.json()['deliveries'][0]['state']['context'] == {
        'auto_open_postcard': False,
        'is_completed': True,
        'display_targets': ['multiorder'],
    }


@pytest.mark.experiments3(filename='experiment.json')
async def test_empty_candidate(
        taxi_cargo_c2c,
        create_taxi_orders,
        get_default_order_id,
        default_pa_headers,
        order_archive_mock,
):
    proc = get_proc(get_default_order_id(), 'pending', None)
    proc['performer']['candidate_index'] = None
    order_archive_mock.set_order_proc(proc)

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'taxi/' + get_default_order_id(),
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
    resp.pop('etag')
    assert resp == {
        'state': {
            'context': {'display_targets': ['multiorder']},
            'summary': 'Курьер где-то',
            'primary_actions': [],
            'secondary_actions': [],
            'sorted_route_points': [
                {
                    'visit_status': 'pending',
                    'type': 'source',
                    'uri': 'some uri',
                    'coordinates': [37.642859, 55.735316],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора',
                    'area_description': 'Москва, Россия',
                    'entrance': '10',
                    'floor': '1',
                    'room': '2',
                    'code': '3',
                },
                {
                    'visit_status': 'pending',
                    'type': 'destination',
                    'uri': 'some uri',
                    'coordinates': [38.642859, 56.735316],
                    'full_text': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора',
                    'area_description': 'Москва, Россия',
                    'entrance': '5',
                    'floor': '6',
                    'room': '7',
                    'code': '8',
                },
            ],
            'active_route_points': [0, 1],
            'meta': {
                'order_provider_id': 'taxi',
                'order_status': 'pending',
                'roles': ['recipient'],
                'tariff_class': 'courier',
            },
            'content_sections': [
                {
                    'id': matching.uuid_string,
                    'items': [
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
                            'title': {
                                'text': 'БЦ Аврора',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'subtitle': {
                                'text': 'кв. 2, под. 10, этаж 1, домофон 3',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {'image_tag': 'delivery_point_red'},
                        },
                        {'id': matching.uuid_string, 'type': 'separator'},
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
                                'text': '4',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'lead_icon': {
                                'image_tag': 'delivery_comment_outline',
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
                            'title': {
                                'text': 'БЦ Аврора',
                                'max_lines': 1,
                                'typography': 'body2',
                                'color': 'TextMain',
                            },
                            'subtitle': {
                                'text': 'кв. 7, под. 5, этаж 6, домофон 8',
                                'max_lines': 1,
                                'typography': 'caption1',
                                'color': 'TextMinor',
                            },
                            'lead_icon': {'image_tag': 'delivery_point'},
                        },
                        {'id': matching.uuid_string, 'type': 'separator'},
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
                                'text': '9',
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
        },
    }


@pytest.mark.parametrize(
    'status, taxi_status, expected_summary, expected_description',
    [
        pytest.param('pending', None, 'Курьер где-то', 'голубой BMW'),
        pytest.param(
            'assigned',
            'driving',
            'Курьер в пути к точке отправления',
            'голубой BMW',
        ),
        pytest.param('assigned', 'waiting', 'Курьер приехал', 'голубой BMW'),
        pytest.param(
            'assigned',
            'transporting',
            'Курьер в пути к точке получения',
            'голубой BMW',
        ),
        pytest.param('finished', 'complete', 'Доставлено', 'голубой BMW'),
        pytest.param(
            'finished',
            'cancelled',
            'Заказ отменен',
            'К сожалению, заказ отменён. '
            'Пожалуйста, закажите доставку ещё раз.',
        ),
        pytest.param(
            'pending',
            'cancelled',
            'Заказ отменен',
            'К сожалению, заказ отменён. '
            'Пожалуйста, закажите доставку ещё раз.',
        ),
        pytest.param(
            'cancelled',
            'driving',
            'Заказ отменен',
            'К сожалению, заказ отменён. '
            'Пожалуйста, закажите доставку ещё раз.',
        ),
        pytest.param(
            'finished', 'expired', 'Заказ отменен', 'Исполнитель не найден',
        ),
        pytest.param(
            'finished', 'expired', 'Заказ отменен', 'Исполнитель не найден',
        ),
        pytest.param('finished', 'failed', 'Заказ отменен', 'Ошибка'),
    ],
)
async def test_texts(
        taxi_cargo_c2c,
        create_taxi_orders,
        get_default_order_id,
        default_pa_headers,
        order_archive_mock,
        status,
        taxi_status,
        expected_summary,
        expected_description,
):
    proc = get_proc(get_default_order_id(), status, taxi_status)
    order_archive_mock.set_order_proc(proc)

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'taxi/' + get_default_order_id(),
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
    assert response.json()['state']['description'] == expected_description


async def test_performer_eta(
        taxi_cargo_c2c,
        create_taxi_orders,
        get_default_order_id,
        default_pa_headers,
        order_archive_mock,
        mockserver,
):
    @mockserver.json_handler('/driver-route-responder/timeleft')
    def _timeleft(request):
        return mockserver.make_response(
            json={
                'position': [37.642859, 55.735316],
                'destination': [37.642859, 55.735316],
                'time_left': 160.12,
                'distance_left': 231.1,
                'tracking_type': 'route_tracking',
                'service_id': 'cargo-c2c',
                'etas': [],
            },
            status=200,
        )

    order_archive_mock.set_order_proc(
        get_proc(get_default_order_id(), 'assigned', 'transporting'),
    )

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'taxi/' + get_default_order_id(),
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
    assert (
        response.json()['state']['summary']
        == 'Курьер в пути к точке получения: ~2 мин'
    )


@pytest.mark.now('2222-07-20T11:00:00.00')
async def test_old_terminated_delivery(
        taxi_cargo_c2c,
        create_taxi_orders,
        get_default_order_id,
        default_pa_headers,
):
    response = await taxi_cargo_c2c.post(
        '/v1/processing/delivery-order/mark-order-terminated',
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_2',
                'order_id': get_default_order_id(),
                'order_provider_id': 'taxi',
            },
            'resolution': 'succeed',
        },
    )
    assert response.status_code == 200
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'taxi/' + get_default_order_id(),
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
    assert response.headers['X-Refresh-After'] == '10'


@pytest.mark.experiments3(filename='experiment.json')
async def test_failed_delivery(
        taxi_cargo_c2c,
        create_taxi_orders,
        get_default_order_id,
        default_pa_headers,
        order_archive_mock,
):
    order_archive_mock.set_order_proc(
        get_proc(get_default_order_id(), 'finished', 'failed'),
    )

    response = await taxi_cargo_c2c.post(
        '/v1/processing/delivery-order/mark-order-terminated',
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_2',
                'order_id': get_default_order_id(),
                'order_provider_id': 'taxi',
            },
            'resolution': 'failed',
        },
    )
    assert response.status_code == 200

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'taxi/' + get_default_order_id(),
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
    assert response.headers['X-Refresh-After'] == '10'
    assert response.json()['state'] == {
        'context': {
            'present_as_completed': True,
            'display_targets': ['multiorder'],
        },
        'summary': 'Заказ отменен',
        'description': 'Ошибка',
        'sorted_route_points': [
            {
                'visit_status': 'pending',
                'type': 'source',
                'uri': 'some uri',
                'coordinates': [37.642859, 55.735316],
                'full_text': 'Россия, Москва, Садовническая улица 82',
                'short_text': 'БЦ Аврора',
                'area_description': 'Москва, Россия',
                'entrance': '10',
                'floor': '1',
                'room': '2',
                'code': '3',
            },
            {
                'visit_status': 'pending',
                'type': 'destination',
                'uri': 'some uri',
                'coordinates': [38.642859, 56.735316],
                'full_text': 'Россия, Москва, Садовническая улица 82',
                'short_text': 'БЦ Аврора',
                'area_description': 'Москва, Россия',
                'entrance': '5',
                'floor': '6',
                'room': '7',
                'code': '8',
            },
        ],
        'active_route_points': [0, 1],
        'primary_actions': [],
        'secondary_actions': [],
        'meta': {
            'tariff_class': 'courier',
            'order_provider_id': 'taxi',
            'roles': ['recipient'],
            'order_status': 'finished',
        },
        'completed_state_buttons': {
            'primary': {'title': 'Готово', 'action': {'type': 'done'}},
        },
        'content_sections': [
            {
                'id': matching.uuid_string,
                'items': [
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
                        'title': {
                            'text': 'БЦ Аврора',
                            'max_lines': 1,
                            'typography': 'body2',
                            'color': 'TextMain',
                        },
                        'subtitle': {
                            'text': 'кв. 2, под. 10, этаж 1, домофон 3',
                            'max_lines': 1,
                            'typography': 'caption1',
                            'color': 'TextMinor',
                        },
                        'lead_icon': {'image_tag': 'delivery_point_red'},
                    },
                    {'id': matching.uuid_string, 'type': 'separator'},
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
                            'text': '4',
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
                            'text': 'Получатель',
                            'typography': 'caption1',
                        },
                    },
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
                            'text': 'кв. 7, под. 5, этаж 6, домофон 8',
                            'max_lines': 1,
                            'typography': 'caption1',
                            'color': 'TextMinor',
                        },
                        'lead_icon': {'image_tag': 'delivery_point'},
                    },
                    {'id': matching.uuid_string, 'type': 'separator'},
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
                            'text': '9',
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


async def test_courier_performer(
        taxi_cargo_c2c,
        create_taxi_orders,
        get_default_order_id,
        default_pa_headers,
        order_archive_mock,
):
    proc = get_proc(get_default_order_id(), 'pending', None)
    proc['candidates'][0]['car_number'] = 'СОURIЕR12345'
    order_archive_mock.set_order_proc(proc)

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'taxi/' + get_default_order_id(),
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
    assert not response.json()['state']['performer'].get(
        'vehicle_number', None,
    )


async def test_error_service(
        taxi_cargo_c2c,
        create_taxi_orders,
        get_default_order_id,
        default_pa_headers,
        mockserver,
):
    @mockserver.json_handler('/order-archive/v1/order_proc/retrieve')
    def _handle(request):
        return mockserver.make_response(status=500)

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={
            'delivery_id': 'taxi/' + get_default_order_id(),
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
    assert response.status_code == 500
