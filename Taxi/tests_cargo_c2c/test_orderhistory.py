# pylint: disable=too-many-lines
import pytest


def get_proc(order_id):
    return {
        '_id': order_id,
        'order': {
            'status': 'finished',
            'taxi_status': 'complete',
            'request': {
                'class': ['courier'],
                'source': {
                    'uris': ['some uri'],
                    'geopoint': [37.642859, 55.735316],
                    'fullname': 'Россия, Москва, Садовническая улица 82',
                    'short_text': 'БЦ Аврора1',
                    'description': 'Москва, Россия',
                    'porchnumber': '4',
                    'extra_data': {},
                },
                'destinations': [
                    {
                        'uris': ['some uri2'],
                        'geopoint': [37.642859, 55.735316],
                        'fullname': 'Россия, Чебоксары, Крутая улица 83',
                        'short_text': 'БЦ Аврора2',
                        'description': 'Чебоксары, Россия',
                        'porchnumber': '5',
                        'extra_data': {},
                    },
                    {
                        'uris': ['some uri3'],
                        'geopoint': [37.642859, 55.725218],
                        'fullname': 'Россия, Таганрог, Большая улица 18',
                        'short_text': 'БЦ Мармелад',
                        'description': 'Таганрог, Россия',
                        'porchnumber': '6',
                        'extra_data': {},
                    },
                ],
            },
        },
        'candidates': [
            {
                'first_name': 'Иван',
                'name': 'Petr',
                'phone_personal_id': '+7123_id',
                'driver_id': 'clid_driverid1',
                'db_id': 'parkid1',
            },
        ],
        'performer': {'candidate_index': 0},
    }


@pytest.mark.config(
    CARGO_C2C_ORDERHISTORY_ALLOWED_DELIVERIES=[
        'cargo-c2c',
        'cargo-claims',
        'logistic-platform',
        'taxi',
    ],
)
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.parametrize(
    'app_brand, not_empty_yt',
    [
        ('yataxi', True),
        ('uber', False),
        pytest.param(
            'uber',
            True,
            marks=pytest.mark.config(
                APPLICATION_BRAND_RELATED_BRANDS={
                    '__default__': [],
                    'uber': ['yataxi'],
                },
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'yt_enabled',
    [
        pytest.param(
            False,
            marks=pytest.mark.config(
                CARGO_C2C_ORDERHISTORY_ENABLE_YT_DELIVERY=False,
            ),
        ),
        pytest.param(
            True,
            marks=[
                pytest.mark.now('2021-02-25T13:47:03.979057'),
                pytest.mark.config(
                    CARGO_C2C_ORDERHISTORY_ENABLE_YT_DELIVERY=True,
                ),
                pytest.mark.yt(dyn_table_data=['yt_raw_denorm.yaml']),
            ],
        ),
    ],
)
async def test_list(
        taxi_cargo_c2c,
        create_taxi_orders,
        create_cargo_claims_orders,
        default_pa_headers,
        yt_apply,
        yt_enabled,
        get_default_order_id,
        order_archive_mock,
        app_brand,
        not_empty_yt,
        mock_claims_full,
):
    order_archive_mock.set_order_proc(get_proc(get_default_order_id()))

    response = await taxi_cargo_c2c.post(
        '/orderhistory/v1/list',
        json={'range': {}},
        headers=default_pa_headers('phone_pd_id_2', app_brand),
    )
    assert response.status_code == 200

    deliveries = response.json()['deliveries']
    for delivery in deliveries:
        delivery.pop('created_at')
    expected_deliveries = [
        {
            'delivery_id': 'cargo-claims/' + get_default_order_id(),
            'is_active': True,
            'taxi_order_id': '123',
            'image_tag': 'class_courier_icon_5',
            'route_points': [
                {
                    'short_text': 'БЦ Аврора',
                    'type': 'source',
                    'point': [37.642859, 55.735316],
                },
                {
                    'short_text': 'БЦ Аврора2',
                    'type': 'destination',
                    'point': [37.642859, 55.735316],
                },
            ],
            'performer': {'name': 'Petr', 'phone': '+7123'},
            'map_image': (
                'https://tc.mobile.yandex.net/get-map/1.x/?'
                'l=map&size=800,400&cr=0&lg=0&scale=1.4&lang=en&'
                'pt=37.642859,55.735316,comma_solid_red~'
                '37.642859,55.735316,comma_solid_blue&'
                'bbox=37.642859,55.735316~37.642859,55.735316'
            ),
            'status': 'in_progress',
        },
        {
            'delivery_id': 'taxi/' + get_default_order_id(),
            'is_active': True,
            'taxi_order_id': get_default_order_id(),
            'image_tag': 'class_courier_icon_5',
            'route_points': [
                {
                    'short_text': 'БЦ Аврора1',
                    'type': 'source',
                    'point': [37.642859, 55.735316],
                },
                {
                    'short_text': 'БЦ Аврора2',
                    'type': 'destination',
                    'point': [37.642859, 55.735316],
                },
                {
                    'short_text': 'БЦ Мармелад',
                    'type': 'destination',
                    'point': [37.642859, 55.725218],
                },
            ],
            'performer': {'name': 'Petr', 'phone': '+7123'},
            'map_image': (
                'https://tc.mobile.yandex.net/get-map/1.x/?'
                'l=map&size=800,400&cr=0&lg=0&scale=1.4&lang=en&'
                'pt=37.642859,55.735316,comma_solid_red~'
                '37.642859,55.735316,trackpoint~'
                '37.642859,55.725218,comma_solid_blue&'
                'bbox=37.642859,55.724814~37.642859,55.737336'
            ),
            'status': 'in_progress',
        },
    ]
    expected_last_order_id = 'taxi/' + get_default_order_id()
    if yt_enabled and not_empty_yt:
        yt_order = {
            'delivery_id': 'cargo-c2c/' + get_default_order_id(),
            'image_tag': 'class_courier_icon_5',
            'is_active': False,
            'map_image': (
                'https://tc.mobile.yandex.net/get-map/1.x/?l=map&'
                'size=800,400&cr=0&lg=0&scale=1.4&lang=en&'
                'pt=37.642859,55.735316,comma_solid_red'
                '~37.642859,55.735316,comma_solid_blue&'
                'bbox=37.642859,55.735316~37.642859,55.735316'
            ),
            'performer': {'name': 'Petr'},
            'route_points': [
                {
                    'point': [37.642859, 55.735316],
                    'short_text': 'БЦ Аврора',
                    'type': 'source',
                },
                {
                    'point': [37.642859, 55.735316],
                    'short_text': 'БЦ Аврора2',
                    'type': 'destination',
                },
            ],
            'taxi_order_id': '123',
            'status': 'cancelled',
        }
        expected_deliveries.append(yt_order)
        expected_last_order_id = 'logistic-platform/' + get_default_order_id()
        yt_lp_order = {
            'delivery_id': (
                'logistic-platform/b1fe01ddc30247279f806e6c5e210a9f'
            ),
            'image_tag': 'delivery_box_icon',
            'is_active': False,
            'map_image': (
                'https://tc.mobile.yandex.net/get-map/1.x/'
                '?l=map&size=800,400&cr=0&lg=0&scale=1.4&'
                'lang=en&pt=37.632233,55.768157,comma_solid_red'
            ),
            'route_points': [
                {
                    'point': [37.63223287, 55.76815715],
                    'short_text': 'Сретенка, 14',
                    'type': 'destination',
                },
            ],
            'status': 'cancelled',
            'support_url': (
                'https://m.taxi.yandex.ru/help/ridetech/yandex/pa'
                '/en_int/delivery/logistic_platform?from_order'
                '=true&order_id=b1fe01ddc30247279f806e6c5e210a9f'
            ),
            'taxi_order_id': '',
        }
        expected_deliveries.append(yt_lp_order)

    assert deliveries == expected_deliveries
    assert response.json()['cursor']['delivery_id'] == expected_last_order_id
    service_metadata = response.json()['service_metadata']
    service_metadata.pop('last_order_created_at')
    assert service_metadata == {
        'service': 'taxi',
        'name': 'my_taxi',
        'last_order_id': 'cargo-claims/' + get_default_order_id(),
        'flavor': 'delivery',
    }

    cursor = response.json()['cursor']
    response = await taxi_cargo_c2c.post(
        '/orderhistory/v1/list',
        json={'range': {'older_than': cursor}},
        headers=default_pa_headers('phone_pd_id_2', app_brand),
    )
    assert response.status_code == 200
    assert response.json()['deliveries'] == []


@pytest.mark.config(
    CARGO_C2C_ORDERHISTORY_ALLOWED_DELIVERIES=[
        'cargo-c2c',
        'cargo-claims',
        'taxi',
    ],
)
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.parametrize(
    'yt_enabled',
    [
        pytest.param(
            False,
            marks=pytest.mark.config(
                CARGO_C2C_ORDERHISTORY_ENABLE_YT_DELIVERY=False,
            ),
        ),
        pytest.param(
            True,
            marks=[
                pytest.mark.now('2021-02-25T13:47:03.979057'),
                pytest.mark.config(
                    CARGO_C2C_ORDERHISTORY_ENABLE_YT_DELIVERY=True,
                ),
                pytest.mark.yt(dyn_table_data=['yt_raw_denorm.yaml']),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'app_brand',
    [
        'yataxi',
        'uber',
        pytest.param(
            'uber',
            marks=pytest.mark.config(
                APPLICATION_BRAND_RELATED_BRANDS={
                    '__default__': [],
                    'yataxi': ['uber'],
                },
            ),
        ),
    ],
)
async def test_list_with_faulty_claims(
        taxi_cargo_c2c,
        create_taxi_orders,
        create_cargo_claims_orders,
        default_pa_headers,
        yt_apply,
        yt_enabled,
        get_default_order_id,
        order_archive_mock,
        app_brand,
        mock_claims_full,
        mockserver,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _faulty_claims_full(request):
        return mockserver.make_response(
            json={'code': 'not_found', 'message': 'no such claim_id'},
            status=404,
        )

    order_archive_mock.set_order_proc(get_proc(get_default_order_id()))

    response = await taxi_cargo_c2c.post(
        '/orderhistory/v1/list',
        json={'range': {}},
        headers=default_pa_headers('phone_pd_id_2', app_brand),
    )
    assert response.status_code == 200

    deliveries = response.json()['deliveries']
    for delivery in deliveries:
        delivery.pop('created_at')

    expected_deliveries = [
        {
            'delivery_id': 'taxi/' + get_default_order_id(),
            'is_active': True,
            'taxi_order_id': get_default_order_id(),
            'image_tag': 'class_courier_icon_5',
            'route_points': [
                {
                    'short_text': 'БЦ Аврора1',
                    'type': 'source',
                    'point': [37.642859, 55.735316],
                },
                {
                    'short_text': 'БЦ Аврора2',
                    'type': 'destination',
                    'point': [37.642859, 55.735316],
                },
                {
                    'short_text': 'БЦ Мармелад',
                    'type': 'destination',
                    'point': [37.642859, 55.725218],
                },
            ],
            'performer': {'name': 'Petr', 'phone': '+7123'},
            'map_image': (
                'https://tc.mobile.yandex.net/get-map/1.x/?'
                'l=map&size=800,400&cr=0&lg=0&scale=1.4&lang=en&'
                'pt=37.642859,55.735316,comma_solid_red~'
                '37.642859,55.735316,trackpoint~'
                '37.642859,55.725218,comma_solid_blue&'
                'bbox=37.642859,55.724814~37.642859,55.737336'
            ),
            'status': 'in_progress',
        },
    ]

    assert deliveries == expected_deliveries


@pytest.mark.config(
    CARGO_C2C_ORDERHISTORY_ALLOWED_DELIVERIES=[
        'cargo-c2c',
        'cargo-claims',
        'logistic-platform',
        'taxi',
    ],
)
@pytest.mark.experiments3(filename='experiment.json')
async def test_no_taxi_order_id(
        taxi_cargo_c2c,
        create_taxi_orders,
        create_cargo_claims_orders,
        default_pa_headers,
        get_default_order_id,
        order_archive_mock,
        load_json,
        mockserver,
        mock_claims_full,
):
    mock_claims_full.file_name = 'claim_full_response_without_taxi_order.json'
    order_archive_mock.set_order_proc(get_proc(get_default_order_id()))

    response = await taxi_cargo_c2c.post(
        '/orderhistory/v1/list',
        json={'range': {}},
        headers=default_pa_headers('phone_pd_id_2'),
    )
    assert response.status_code == 200
    deliveries = response.json()['deliveries']
    cursor = response.json()['cursor']
    for delivery in deliveries:
        delivery.pop('created_at')
    assert deliveries == [
        {
            'delivery_id': 'taxi/' + get_default_order_id(),
            'is_active': True,
            'taxi_order_id': get_default_order_id(),
            'image_tag': 'class_courier_icon_5',
            'route_points': [
                {
                    'short_text': 'БЦ Аврора1',
                    'type': 'source',
                    'point': [37.642859, 55.735316],
                },
                {
                    'short_text': 'БЦ Аврора2',
                    'type': 'destination',
                    'point': [37.642859, 55.735316],
                },
                {
                    'short_text': 'БЦ Мармелад',
                    'type': 'destination',
                    'point': [37.642859, 55.725218],
                },
            ],
            'performer': {'name': 'Petr', 'phone': '+7123'},
            'map_image': (
                'https://tc.mobile.yandex.net/get-map/1.x/?'
                'l=map&size=800,400&cr=0&lg=0&scale=1.4&lang=en&'
                'pt=37.642859,55.735316,comma_solid_red~'
                '37.642859,55.735316,trackpoint~'
                '37.642859,55.725218,comma_solid_blue&'
                'bbox=37.642859,55.724814~37.642859,55.737336'
            ),
            'status': 'in_progress',
        },
    ]
    assert cursor['delivery_id'] == 'taxi/' + get_default_order_id()


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.parametrize(
    'app_brand, expected_response_code',
    [
        ('yataxi', 200),
        ('uber', 200),
        pytest.param(
            'uber',
            200,
            marks=pytest.mark.config(
                APPLICATION_BRAND_RELATED_BRANDS={
                    '__default__': [],
                    'yataxi': ['uber'],
                },
            ),
        ),
    ],
)
async def test_taxi_item(
        taxi_cargo_c2c,
        create_taxi_orders,
        get_default_order_id,
        default_pa_headers,
        order_archive_mock,
        app_brand,
        expected_response_code,
        mock_claims_full,
):
    order_archive_mock.set_order_proc(get_proc(get_default_order_id()))

    response = await taxi_cargo_c2c.post(
        '/orderhistory/v1/item',
        json={'delivery_id': 'taxi/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_2', app_brand),
    )

    assert response.status_code == expected_response_code
    if expected_response_code != 200:
        return

    resp = response.json()
    assert resp.pop('created_at')
    assert resp == {
        'delivery_id': 'taxi/' + get_default_order_id(),
        'taxi_order_id': get_default_order_id(),
        'is_active': True,
        'performer': {'name': 'Petr', 'phone': '+7123'},
        'image_tag': 'class_courier_icon_5',
        'map_image': (
            'https://tc.mobile.yandex.net/get-map/1.x/?'
            'l=map&size=800,400&cr=0&lg=0&scale=1.4&lang=en&'
            'pt=37.642859,55.735316,comma_solid_red~'
            '37.642859,55.735316,trackpoint~'
            '37.642859,55.725218,comma_solid_blue&'
            'bbox=37.642859,55.724814~37.642859,55.737336'
        ),
        'route_points': [
            {
                'point': [37.642859, 55.735316],
                'short_text': 'БЦ Аврора1',
                'type': 'source',
            },
            {
                'point': [37.642859, 55.735316],
                'short_text': 'БЦ Аврора2',
                'type': 'destination',
            },
            {
                'point': [37.642859, 55.725218],
                'short_text': 'БЦ Мармелад',
                'type': 'destination',
            },
        ],
        'status': 'in_progress',
    }


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    CARGO_C2C_FILTERING_ORDERHISTORY_BY_STATUSES=[
        {
            'order_provider_id': 'taxi',
            'role': 'recipient',
            'allowed_statuses': ['abracadabra'],
        },
    ],
)
async def test_taxi_item_filtering_orderhistory_not_show(
        taxi_cargo_c2c,
        get_default_order_id,
        default_pa_headers,
        order_archive_mock,
        create_taxi_orders,
):
    order_archive_mock.set_order_proc(get_proc(get_default_order_id()))
    response = await taxi_cargo_c2c.post(
        '/orderhistory/v1/item',
        json={'delivery_id': 'taxi/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_2', 'yataxi'),
    )
    assert response.status_code == 404


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    CARGO_C2C_FILTERING_ORDERHISTORY_BY_STATUSES=[
        {
            'order_provider_id': 'taxi',
            'role': 'recipient',
            'allowed_statuses': ['finished'],
        },
    ],
)
async def test_taxi_item_filtering_orderhistory_show(
        create_taxi_orders,
        taxi_cargo_c2c,
        get_default_order_id,
        default_pa_headers,
        order_archive_mock,
):
    order_archive_mock.set_order_proc(get_proc(get_default_order_id()))
    response = await taxi_cargo_c2c.post(
        '/orderhistory/v1/item',
        json={'delivery_id': 'taxi/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_2', 'yataxi'),
    )
    assert response.status_code == 200


@pytest.mark.config(
    CARGO_C2C_ORDERHISTORY_ALLOWED_DELIVERIES=[
        'cargo-c2c',
        'cargo-claims',
        'logistic-platform',
        'taxi',
    ],
)
@pytest.mark.config(
    CARGO_C2C_FILTERING_ORDERHISTORY_BY_STATUSES=[
        {
            'order_provider_id': 'taxi',
            'role': 'sender',
            'allowed_statuses': [
                'finished',
                'complete',
                'failed',
                'processing',
                'pickuped',
            ],
        },
        {
            'order_provider_id': 'taxi',
            'role': 'recipient',
            'allowed_statuses': [
                'finished',
                'complete',
                'failed',
                'processing',
                'pickuped',
            ],
        },
        {
            'order_provider_id': 'taxi',
            'role': 'initiator',
            'allowed_statuses': [
                'finished',
                'complete',
                'failed',
                'processing',
                'pickuped',
            ],
        },
        {
            'order_provider_id': 'cargo-c2c',
            'role': 'sender',
            'allowed_statuses': [
                'finished',
                'complete',
                'failed',
                'processing',
                'pickuped',
            ],
        },
        {
            'order_provider_id': 'cargo-c2c',
            'role': 'recipient',
            'allowed_statuses': [
                'finished',
                'complete',
                'failed',
                'processing',
                'pickuped',
            ],
        },
        {
            'order_provider_id': 'cargo-c2c',
            'role': 'initiator',
            'allowed_statuses': [
                'finished',
                'complete',
                'failed',
                'processing',
                'pickuped',
            ],
        },
        {
            'order_provider_id': 'cargo-claims',
            'role': 'sender',
            'allowed_statuses': [
                'finished',
                'complete',
                'failed',
                'processing',
                'pickuped',
            ],
        },
        {
            'order_provider_id': 'cargo-claims',
            'role': 'recipient',
            'allowed_statuses': [
                'finished',
                'complete',
                'failed',
                'processing',
                'pickuped',
            ],
        },
        {
            'order_provider_id': 'cargo-claims',
            'role': 'initiator',
            'allowed_statuses': [
                'finished',
                'complete',
                'failed',
                'processing',
                'pickuped',
            ],
        },
    ],
)
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(CARGO_C2C_ORDERHISTORY_ENABLE_YT_DELIVERY=False)
async def test_list_filtering_orderhistory_show(
        taxi_cargo_c2c,
        create_taxi_orders,
        create_cargo_claims_orders,
        default_pa_headers,
        yt_apply,
        get_default_order_id,
        order_archive_mock,
        mock_claims_full,
):
    order_archive_mock.set_order_proc(get_proc(get_default_order_id()))
    response = await taxi_cargo_c2c.post(
        '/orderhistory/v1/list',
        json={'range': {}},
        headers=default_pa_headers('phone_pd_id_2', 'yataxi'),
    )
    assert response.status_code == 200
    deliveries = response.json()['deliveries']
    deliveries_order_id = []
    for delivery in deliveries:
        deliveries_order_id.append(delivery['delivery_id'])
    expected_deliveries = [
        'cargo-claims/' + get_default_order_id(),
        'taxi/' + get_default_order_id(),
    ]
    assert deliveries_order_id == expected_deliveries


@pytest.mark.yt(dyn_table_data=['yt_raw_denorm.yaml'])
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.parametrize(
    'app_brand, expected_response_code', [('yataxi', 200)],
)
@pytest.mark.parametrize(
    'use_db_adapter_pg_yt',
    [
        pytest.param(
            None,
            marks=pytest.mark.config(
                CARGO_C2C_ORDERHISTORY_DELIVERY_USE_DB_ADAPTER=False,
            ),
        ),
        pytest.param(
            None,
            marks=pytest.mark.config(
                CARGO_C2C_ORDERHISTORY_DELIVERY_USE_DB_ADAPTER=True,
            ),
        ),
    ],
)
@pytest.mark.config(CARGO_C2C_ORDERHISTORY_ENABLE_YT_DELIVERY=True)
@pytest.mark.skip('for validation of fbs pack-unpack functions only')
async def test_taxi_item_archive(
        taxi_cargo_c2c,
        get_default_order_id,
        default_pa_headers,
        order_archive_mock,
        app_brand,
        expected_response_code,
        use_db_adapter_pg_yt,
        yt_apply,
        mock_claims_full,
):
    order_archive_mock.set_order_proc(get_proc(get_default_order_id()))

    response = await taxi_cargo_c2c.post(
        '/orderhistory/v1/item',
        json={'delivery_id': 'cargo-c2c/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_2', app_brand),
    )

    assert response.status_code == expected_response_code
    if expected_response_code != 200:
        return

    resp = response.json()
    assert resp == {
        'created_at': '2021-01-24T13:47:03.979057+00:00',
        'delivery_id': 'cargo-c2c/' + get_default_order_id(),
        'image_tag': 'class_courier_icon_5',
        'is_active': False,
        'map_image': (
            'https://tc.mobile.yandex.net/get-map/1.x/'
            '?l=map&size=800,400&cr=0&lg=0&scale=1.4&lang=en&'
            'pt=37.642859,55.735316,comma_solid_red'
            '~37.642859,55.735316,comma_solid_blue&'
            'bbox=37.642859,55.735316~37.642859,55.735316'
        ),
        'performer': {'name': 'Petr'},
        'route_points': [
            {
                'point': [37.642859, 55.735316],
                'short_text': 'БЦ Аврора',
                'type': 'source',
            },
            {
                'point': [37.642859, 55.735316],
                'short_text': 'БЦ Аврора2',
                'type': 'destination',
            },
        ],
        'taxi_order_id': '123',
        'status': 'in_progress',
    }


@pytest.mark.experiments3(filename='experiment.json')
async def test_multipoint_map(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        default_pa_headers,
        get_default_order_id,
        order_archive_mock,
        mock_claims_full,
):
    response = await taxi_cargo_c2c.post(
        '/orderhistory/v1/item',
        json={'delivery_id': 'cargo-claims/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert (
        response.json()['map_image']
        == 'https://tc.mobile.yandex.net/get-map/1.x/?'
        'l=map&size=800,400&cr=0&lg=0&scale=1.4&lang=en&'
        'pt=37.642859,55.735316,comma_solid_red~'
        '37.642859,55.735316,trackpoint~'
        '37.642859,55.735316,trackpoint~'
        '37.642859,55.735316,trackpoint~'
        '37.642859,55.735316,comma_solid_blue&'
        'bbox=37.642859,55.735316~37.642859,55.735316'
    )


@pytest.mark.experiments3(filename='experiment.json')
async def test_cargo_c2c_order(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        get_default_order_id,
        mockserver,
        mock_claims_full,
):
    @mockserver.json_handler('/ridehistory/cargo/v2/item')
    def _mock_ridehistory(request):
        return {
            'legal_entities': [
                {
                    'type': 'a',
                    'title': 'a1',
                    'additional_properties': [
                        {'type': 'a2', 'value': 'a3'},
                        {'type': 'a4', 'value': 'a5'},
                    ],
                },
                {'type': 'b', 'title': 'b1'},
            ],
            'receipt': {'url_with_embedded_pdf': 'url_with_embedded_pdf'},
        }

    order_id = await create_cargo_c2c_orders()

    response = await taxi_cargo_c2c.post(
        '/orderhistory/v1/item',
        json={'delivery_id': 'cargo-c2c/' + order_id},
        headers=default_pa_headers('phone_pd_id_3'),
    )
    assert response.status_code == 200

    resp = response.json()
    assert resp.pop('created_at')
    assert resp == {
        'delivery_id': 'cargo-c2c/' + order_id,
        'is_active': True,
        'route_points': [
            {
                'short_text': 'БЦ Аврора',
                'type': 'source',
                'point': [37.642859, 55.735316],
            },
            {
                'short_text': 'БЦ Аврора',
                'type': 'destination',
                'point': [37.642859, 55.735316],
            },
            {
                'short_text': 'БЦ Аврора',
                'type': 'destination',
                'point': [37.642859, 55.735316],
            },
            {
                'short_text': 'БЦ Аврора',
                'type': 'destination',
                'point': [37.642859, 55.735316],
            },
            {
                'short_text': 'БЦ Аврора2',
                'type': 'destination',
                'point': [37.642859, 55.735316],
            },
        ],
        'performer': {'name': 'Petr', 'phone': '+7123'},
        'image_tag': 'class_courier_icon_5',
        'map_image': (
            'https://tc.mobile.yandex.net/get-map/1.x/?l=map&size=800,400&cr=0'
            '&lg=0&scale=1.4&lang=en&pt=37.642859,55.735316,comma_solid_red~'
            '37.642859,55.735316,trackpoint~37.642859,55.735316,trackpoint~'
            '37.642859,55.735316,trackpoint~'
            '37.642859,55.735316,comma_solid_blue&'
            'bbox=37.642859,55.735316~37.642859,55.735316'
        ),
        'taxi_order_id': '123',
        'status': 'in_progress',
        'payment': {
            'cost': '298.8 $SIGN$$CURRENCY$',
            'currency_code': 'RUB',
            'ride_cost': '298.8 $SIGN$$CURRENCY$',
            'payment_method': {
                'title': 'VISA ••••4444',
                'type': 'card',
                'system': 'VISA',
            },
        },
        'legal_entities': [
            {
                'type': 'a',
                'title': 'a1',
                'additional_properties': [
                    {'type': 'a2', 'value': 'a3'},
                    {'type': 'a4', 'value': 'a5'},
                ],
            },
            {'type': 'b', 'title': 'b1'},
        ],
        'receipt': {'url_with_embedded_pdf': 'url_with_embedded_pdf'},
    }


SCENARIO_TO_PAYMENT_METHOD = {
    'card': {'title': 'VISA ••••4444', 'type': 'card', 'system': 'VISA'},
    'cargocorp': {'title': 'CRGCRP', 'type': 'cargocorp'},
    'old_cargocorp': {'title': 'Корпоративный счёт', 'type': 'cargocorp'},
}


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.parametrize('scenario', ['card', 'cargocorp', 'old_cargocorp'])
async def test_cargo_c2c_order_cargocorp(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        get_default_order_id,
        mockserver,
        mock_claims_full,
        scenario,
):
    @mockserver.json_handler('/ridehistory/cargo/v2/item')
    def _mock_ridehistory(request):
        return {
            'legal_entities': [
                {
                    'type': 'a',
                    'title': 'a1',
                    'additional_properties': [
                        {'type': 'a2', 'value': 'a3'},
                        {'type': 'a4', 'value': 'a5'},
                    ],
                },
                {'type': 'b', 'title': 'b1'},
            ],
            'receipt': {'url_with_embedded_pdf': 'url_with_embedded_pdf'},
        }

    if scenario == 'cargocorp':
        mock_claims_full.file_name = 'claim_full_response_cargocorp.json'
    elif scenario == 'old_cargocorp':
        mock_claims_full.file_name = 'claim_full_response_old_cargocorp.json'

    order_id = await create_cargo_c2c_orders()

    response = await taxi_cargo_c2c.post(
        '/orderhistory/v1/item',
        json={'delivery_id': 'cargo-c2c/' + order_id},
        headers=default_pa_headers('phone_pd_id_3'),
    )
    assert response.status_code == 200

    resp = response.json()
    assert resp.pop('created_at')
    assert resp == {
        'delivery_id': 'cargo-c2c/' + order_id,
        'is_active': True,
        'route_points': [
            {
                'short_text': 'БЦ Аврора',
                'type': 'source',
                'point': [37.642859, 55.735316],
            },
            {
                'short_text': 'БЦ Аврора',
                'type': 'destination',
                'point': [37.642859, 55.735316],
            },
            {
                'short_text': 'БЦ Аврора',
                'type': 'destination',
                'point': [37.642859, 55.735316],
            },
            {
                'short_text': 'БЦ Аврора',
                'type': 'destination',
                'point': [37.642859, 55.735316],
            },
            {
                'short_text': 'БЦ Аврора2',
                'type': 'destination',
                'point': [37.642859, 55.735316],
            },
        ],
        'performer': {'name': 'Petr', 'phone': '+7123'},
        'image_tag': 'class_courier_icon_5',
        'map_image': (
            'https://tc.mobile.yandex.net/get-map/1.x/?l=map&size=800,400&cr=0'
            '&lg=0&scale=1.4&lang=en&pt=37.642859,55.735316,comma_solid_red~'
            '37.642859,55.735316,trackpoint~37.642859,55.735316,trackpoint~'
            '37.642859,55.735316,trackpoint~'
            '37.642859,55.735316,comma_solid_blue&'
            'bbox=37.642859,55.735316~37.642859,55.735316'
        ),
        'taxi_order_id': '123',
        'status': 'in_progress',
        'payment': {
            'cost': '298.8 $SIGN$$CURRENCY$',
            'currency_code': 'RUB',
            'ride_cost': '298.8 $SIGN$$CURRENCY$',
            'payment_method': SCENARIO_TO_PAYMENT_METHOD[scenario],
        },
        'legal_entities': [
            {
                'type': 'a',
                'title': 'a1',
                'additional_properties': [
                    {'type': 'a2', 'value': 'a3'},
                    {'type': 'a4', 'value': 'a5'},
                ],
            },
            {'type': 'b', 'title': 'b1'},
        ],
        'receipt': {'url_with_embedded_pdf': 'url_with_embedded_pdf'},
    }


async def test_delete_handler(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        default_pa_headers,
        get_default_order_id,
        pgsql,
):
    response = await taxi_cargo_c2c.delete(
        '/orderhistory/v1/remove',
        params={'delivery_id': 'cargo-claims/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_2'),
    )
    assert response.status_code == 200

    response = await taxi_cargo_c2c.delete(
        '/orderhistory/v1/remove',
        params={'delivery_id': 'cargo-claims/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_2'),
    )
    assert response.status_code == 200

    cursor = pgsql['cargo_c2c'].cursor()
    cursor.execute(
        'SELECT count(*) FROM cargo_c2c.orderhistory_deleted_clients_orders',
    )
    assert list(cursor) == [(1,)]


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(CARGO_C2C_ORDERHISTORY_ENABLE_YT_DELIVERY=True)
@pytest.mark.yt(dyn_table_data=['yt_raw_denorm_delete.yaml'])
async def test_list_with_delete(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        create_taxi_orders,
        default_pa_headers,
        get_default_order_id,
        order_archive_mock,
        yt_apply,
        mock_claims_full,
):
    order_archive_mock.set_order_proc(get_proc(get_default_order_id()))

    response = await taxi_cargo_c2c.delete(
        '/orderhistory/v1/remove',
        params={'delivery_id': 'taxi/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_2'),
    )
    assert response.status_code == 200
    response = await taxi_cargo_c2c.delete(
        '/orderhistory/v1/remove',
        params={'delivery_id': 'cargo-claims/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_2'),
    )
    assert response.status_code == 200

    response = await taxi_cargo_c2c.post(
        '/orderhistory/v1/list',
        json={'range': {}},
        headers=default_pa_headers('phone_pd_id_2'),
    )
    assert response.status_code == 200
    assert not response.json()['deliveries']


MARKET_CORP_CLIENT_ID = 'market_corp_client_id____size_32'


@pytest.mark.config(
    CARGO_C2C_ORDERHISTORY_ALLOWED_DELIVERIES=[
        'cargo-c2c',
        'cargo-claims',
        'logistic-platform',
        'taxi',
    ],
)
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    MARKET_CORP_CLIENT_ID_FOR_EXPRESS_ORDERS=MARKET_CORP_CLIENT_ID,
)
@pytest.mark.parametrize(
    'corp_client_id, save_history_length',
    [(MARKET_CORP_CLIENT_ID, 1), ('another__________________size_32', 2)],
)
async def test_market_history(
        taxi_cargo_c2c,
        create_taxi_orders,
        create_cargo_claims_orders,
        default_pa_headers,
        get_default_order_id,
        order_archive_mock,
        load_json,
        mockserver,
        mock_claims_full,
        corp_client_id,
        save_history_length,
):
    mock_claims_full.corp_client_id = corp_client_id
    order_archive_mock.set_order_proc(get_proc(get_default_order_id()))

    response = await taxi_cargo_c2c.post(
        '/orderhistory/v1/list',
        json={'range': {}},
        headers=default_pa_headers('phone_pd_id_2'),
    )

    assert response.status_code == 200
    deliveries = response.json()['deliveries']
    # first case - don't show market in history - hence size 1
    # seconds case - show non-market corp in history - hence size 2
    assert len(deliveries) == save_history_length


@pytest.mark.config(
    CARGO_C2C_ORDERHISTORY_ALLOWED_DELIVERIES=[
        'cargo-c2c',
        'cargo-claims',
        'logistic-platform',
        'taxi',
    ],
)
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    APPLICATION_BRAND_RELATED_BRANDS={
        '__default__': [],
        'yataxi': ['turboapp'],
        'turboapp': ['yataxi', 'asdasd!'],
    },
)
@pytest.mark.parametrize(
    'app_brand, is_empty_response',
    [('yataxi', False), ('turboapp', False), ('uber', True)],
)
async def test_related_brands(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        get_default_order_id,
        mockserver,
        mock_claims_full,
        pgsql,
        app_brand,
        is_empty_response,
):
    @mockserver.json_handler('/ridehistory/cargo/v2/item')
    def _mock_ridehistory(request):
        return {
            'legal_entities': [
                {
                    'type': 'a',
                    'title': 'a1',
                    'additional_properties': [
                        {'type': 'a2', 'value': 'a3'},
                        {'type': 'a4', 'value': 'a5'},
                    ],
                },
                {'type': 'b', 'title': 'b1'},
            ],
            'receipt': {'url_with_embedded_pdf': 'url_with_embedded_pdf'},
        }

    order_id = await create_cargo_c2c_orders()

    response = await taxi_cargo_c2c.post(
        '/orderhistory/v1/list',
        json={'range': {}},
        headers=default_pa_headers('phone_pd_id_3', app_brand),
    )

    assert response.status_code == 200

    if not is_empty_response:
        deliveries = response.json()['deliveries']

        assert len(deliveries) == 1
        assert deliveries[0]['delivery_id'] == 'cargo-c2c/' + order_id
    else:
        assert response.json() == {'deliveries': []}


@pytest.mark.config(
    CARGO_C2C_ORDERHISTORY_ALLOWED_DELIVERIES=[
        'cargo-c2c',
        'cargo-claims',
        'logistic-platform',
        'taxi',
    ],
)
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    APPLICATION_BRAND_RELATED_BRANDS={
        '__default__': [],
        'yataxi': ['turboapp'],
        'turboapp': ['yataxi'],
    },
)
@pytest.mark.parametrize(
    'app_brand, is_empty_response',
    [('yataxi', False), ('turboapp', False), ('uber', True)],
)
async def test_null_brand(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        get_default_order_id,
        mockserver,
        mock_claims_full,
        pgsql,
        app_brand,
        is_empty_response,
):
    @mockserver.json_handler('/ridehistory/cargo/v2/item')
    def _mock_ridehistory(request):
        return {
            'legal_entities': [
                {
                    'type': 'a',
                    'title': 'a1',
                    'additional_properties': [
                        {'type': 'a2', 'value': 'a3'},
                        {'type': 'a4', 'value': 'a5'},
                    ],
                },
                {'type': 'b', 'title': 'b1'},
            ],
            'receipt': {'url_with_embedded_pdf': 'url_with_embedded_pdf'},
        }

    order_id = await create_cargo_c2c_orders()

    cursor = pgsql['cargo_c2c'].cursor()
    cursor.execute('UPDATE cargo_c2c.orders SET brand = NULL')

    response = await taxi_cargo_c2c.post(
        '/orderhistory/v1/list',
        json={'range': {}},
        headers=default_pa_headers('phone_pd_id_3', app_brand),
    )

    assert response.status_code == 200

    if not is_empty_response:
        deliveries = response.json()['deliveries']

        assert len(deliveries) == 1
        assert deliveries[0]['delivery_id'] == 'cargo-c2c/' + order_id
    else:
        assert response.json() == {'deliveries': []}


@pytest.mark.now('2017-09-09T00:00:00+0300')
async def test_receipts(
        taxi_cargo_c2c,
        load_json,
        mockserver,
        order_archive_mock,
        get_default_order_id,
        default_pa_headers,
        create_cargo_c2c_orders,
        mock_claims_full,
):
    @mockserver.json_handler('/ridehistory/cargo/v2/item')
    def _mock_ridehistory(request):
        return {
            'legal_entities': [
                {
                    'type': 'a',
                    'title': 'a1',
                    'additional_properties': [
                        {'type': 'a2', 'value': 'a3'},
                        {'type': 'a4', 'value': 'a5'},
                    ],
                },
                {'type': 'b', 'title': 'b1'},
            ],
            'receipt': {'url_with_embedded_pdf': 'url_with_embedded_pdf'},
            'trust_order_id': 'trust_order_id++',
        }

    @mockserver.json_handler(
        '/cargo-fiscal/internal'
        '/cargo-fiscal/receipts/delivery/orders/result',
    )
    def _mock_cargo_fiscal(request):
        return {
            'receipts': [
                {
                    'transaction_id': '6220b6e4910d391fc611b690',
                    'is_ready': True,
                    'url': 'www.mnogochekoff.ru/474747',
                },
                {
                    'transaction_id': '6220b6e4911fc611b690',
                    'is_ready': True,
                    'url': 'www.mnogochekoff.ru/474749',
                    'context': {
                        'transaction_id': '6220b6e4911fc611b690',
                        'is_refund': True,
                        'price_details': {'total': '15.00'},
                    },
                },
                {
                    'transaction_id': '6220b6e4910d391fc611b691',
                    'is_ready': False,
                    'url': 'www.mnogochekoff.ru/474748',
                },
            ],
        }

    order_id = await create_cargo_c2c_orders()
    order_archive_mock.set_order_proc(get_proc(order_id))

    response = await taxi_cargo_c2c.post(
        '/orderhistory/v1/receipts',
        json={'delivery_id': 'cargo-c2c/' + order_id},
        headers=default_pa_headers('phone_pd_id_2', 'yataxi'),
    )

    assert response.status_code == 200
    assert response.json() == {
        'hide_receipt': False,
        'receipts': [
            {
                'receipt_url': 'www.mnogochekoff.ru/474747',
                'sum': '-',
                'title': 'Чек на оплату',
                'type': 'income',
            },
            {
                'receipt_url': 'www.mnogochekoff.ru/474749',
                'sum': '15.00',
                'title': 'Чек на возврат',
                'type': 'return_income',
            },
        ],
    }
