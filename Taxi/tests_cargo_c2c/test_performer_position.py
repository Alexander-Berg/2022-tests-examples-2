import pytest


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
                    'porchnumber': '4',
                    'extra_data': {},
                },
                'destinations': [
                    {
                        'uris': ['some uri'],
                        'geopoint': [37.642859, 55.735316],
                        'fullname': 'Россия, Москва, Садовническая улица 82',
                        'short_text': 'БЦ Аврора',
                        'description': 'Москва, Россия',
                        'porchnumber': '4',
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
                'car_number': 'СОURIЕR A123BC799',
            },
        ],
        'performer': {'candidate_index': 0},
    }


@pytest.mark.parametrize('provider_id', ['cargo-claims', 'cargo-c2c'])
async def test_cargo(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        create_cargo_c2c_orders,
        get_default_order_id,
        default_pa_headers,
        mock_claims_full,
        mock_driver_trackstory,
        provider_id,
):
    mock_claims_full.current_point = {
        'claim_point_id': 5,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': 'pending',
    }

    if provider_id == 'cargo-c2c':
        order_id = await create_cargo_c2c_orders()
    else:
        order_id = get_default_order_id()

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/performer-position',
        json={'delivery_id': provider_id + '/' + order_id},
        headers=default_pa_headers('phone_pd_id_1'),
    )

    assert response.status_code == 200
    resp = response.json()

    assert resp == {
        'position': mock_driver_trackstory.position,
        'pin': {'type': 'default', 'pin_type': 'pedestrian'},
    }

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/performer-position',
        json={'delivery_id': provider_id + '/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_3'),
    )
    assert response.status_code == 404
    assert response.headers['X-Refresh-After'] == '10'


@pytest.mark.parametrize(
    'provider_id, unavailable_handle',
    [
        ('cargo-claims', '/cargo-claims/v2/claims/full'),
        ('cargo-claims', '/driver-trackstory/position'),
        ('cargo-c2c', '/cargo-claims/v2/claims/full'),
        ('cargo-c2c', '/driver-trackstory/position'),
    ],
)
async def test_cargo_error_service(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        create_cargo_c2c_orders,
        get_default_order_id,
        default_pa_headers,
        mock_claims_full,
        provider_id,
        unavailable_handle,
        mockserver,
):
    mock_claims_full.current_point = {
        'claim_point_id': 5,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': 'pending',
    }

    @mockserver.json_handler(unavailable_handle)
    def _handle(request):
        return mockserver.make_response(status=500)

    if provider_id == 'cargo-c2c':
        order_id = await create_cargo_c2c_orders()
    else:
        order_id = get_default_order_id()

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/performer-position',
        json={'delivery_id': provider_id + '/' + order_id},
        headers=default_pa_headers('phone_pd_id_1'),
    )

    assert response.status_code == 500


@pytest.mark.parametrize('provider_id', ['cargo-claims', 'cargo-c2c'])
@pytest.mark.config(
    CARGO_C2C_CORP_CLIENT_ID_TO_SHOW_PIN_ON_MAP_LOADABLE={
        '__default__cargo_c2c__foot__': {
            'image_tag': 'some-foot-tag',
            'rotatable': True,
            'anchor': {'x': 0.5, 'y': 0.5},
        },
        '__default__cargo_c2c__car__': {
            'image_tag': 'some-car-tag',
            'rotatable': True,
            'anchor': {'x': 0.5, 'y': 0.5},
        },
    },
)
async def test_loadable_pins_for_c2c(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        create_cargo_c2c_orders,
        get_default_order_id,
        default_pa_headers,
        mock_claims_full,
        mock_driver_trackstory,
        provider_id,
):
    mock_claims_full.current_point = {
        'claim_point_id': 5,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': 'pending',
    }

    if provider_id == 'cargo-c2c':
        order_id = await create_cargo_c2c_orders()
    else:
        order_id = get_default_order_id()

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/performer-position',
        json={'delivery_id': provider_id + '/' + order_id},
        headers=default_pa_headers('phone_pd_id_1'),
    )

    assert response.status_code == 200
    resp = response.json()

    assert resp == {
        'position': mock_driver_trackstory.position,
        'pin': {
            'type': 'loadable',
            'image_tag': 'some-foot-tag',
            'rotatable': True,
            'anchor': {'x': 0.5, 'y': 0.5},
        },
    }

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/performer-position',
        json={'delivery_id': provider_id + '/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_3'),
    )
    assert response.status_code == 404
    assert response.headers['X-Refresh-After'] == '10'


async def test_cargo_claims_recipient(
        taxi_cargo_c2c,
        get_default_order_id,
        default_pa_headers,
        load_json,
        mockserver,
        mock_claims_full,
):
    mock_claims_full.current_point_id = 1

    response = await taxi_cargo_c2c.post(
        '/v1/actions/save-clients-orders',
        json={
            'orders': [
                {
                    'id': {
                        'phone_pd_id': 'phone_pd_id_1',
                        'order_id': get_default_order_id(),
                        'order_provider_id': 'cargo-claims',
                    },
                    'roles': ['recipient'],
                },
            ],
        },
    )
    assert response.status_code == 200

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/performer-position',
        json={'delivery_id': 'cargo-claims/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 404
    assert response.headers['X-Refresh-After'] == '10'


@pytest.mark.parametrize(
    'status,taxi_status',
    [
        ('assigned', 'driving'),
        ('assigned', 'waiting'),
        ('assigned', 'transporting'),
    ],
)
async def test_taxi_order(
        taxi_cargo_c2c,
        create_taxi_orders,
        get_default_order_id,
        default_pa_headers,
        order_archive_mock,
        status,
        taxi_status,
        mock_driver_trackstory,
):
    order_archive_mock.set_order_proc(
        get_proc(get_default_order_id(), status, taxi_status),
    )

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/performer-position',
        json={'delivery_id': 'taxi/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_2'),
    )

    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp == {
        'position': mock_driver_trackstory.position,
        'pin': {'type': 'default', 'pin_type': 'pedestrian'},
    }


async def test_taxi_no_performer(
        taxi_cargo_c2c,
        create_taxi_orders,
        get_default_order_id,
        default_pa_headers,
        order_archive_mock,
):
    proc = get_proc(get_default_order_id(), 'pending', None)
    proc['candidates'] = []
    proc.pop('performer')
    order_archive_mock.set_order_proc(proc)

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/performer-position',
        json={'delivery_id': 'taxi/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_2'),
    )
    assert response.status_code == 404
    assert response.headers['X-Refresh-After'] == '10'


@pytest.mark.parametrize(
    'unavailable_handle',
    ['/order-archive/v1/order_proc/retrieve', '/driver-trackstory/position'],
)
async def test_taxi_error_service(
        taxi_cargo_c2c,
        create_taxi_orders,
        get_default_order_id,
        default_pa_headers,
        order_archive_mock,
        mockserver,
        unavailable_handle,
):
    order_archive_mock.set_order_proc(
        get_proc(get_default_order_id(), 'assigned', 'driving'),
    )

    @mockserver.json_handler(unavailable_handle)
    def _handle(request):
        return mockserver.make_response(status=500)

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/performer-position',
        json={'delivery_id': 'taxi/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_2'),
    )
    assert response.status_code == 500


async def test_taxi_order_terminated(
        taxi_cargo_c2c,
        create_taxi_orders,
        get_default_order_id,
        default_pa_headers,
        order_archive_mock,
):
    order_archive_mock.set_order_proc(
        get_proc(get_default_order_id(), 'finished', 'complete'),
    )

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
        '/4.0/cargo-c2c/v1/delivery/performer-position',
        json={'delivery_id': 'taxi/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_2'),
    )
    assert response.status_code == 404
    assert response.headers['X-Refresh-After'] == '10'


async def test_taxi_corp(
        taxi_cargo_c2c,
        create_taxi_orders,
        get_default_order_id,
        default_pa_headers,
        order_archive_mock,
        mock_driver_trackstory,
):
    order_archive_mock.set_order_proc(
        get_proc(get_default_order_id(), 'assigned', 'transporting'),
    )

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/performer-position',
        json={'delivery_id': 'taxi/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_2'),
    )
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp == {
        'position': mock_driver_trackstory.position,
        'pin': {'type': 'default', 'pin_type': 'pedestrian'},
    }

    proc = get_proc(get_default_order_id(), 'assigned', 'driving')
    proc['order']['request'].update(
        {'corp': {'client_id': '5e36732e2bc54e088b1466e08e31c486'}},
    )
    order_archive_mock.set_order_proc(proc)
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/performer-position',
        json={'delivery_id': 'taxi/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_2'),
    )
    assert response.status_code == 404
    assert response.headers['X-Refresh-After'] == '10'


MARKET_CORP_CLIENT_ID = '70a499f9eec844e9a758f4bc33e667c0'


@pytest.mark.parametrize(
    'expected_pin_type, expected_type, expected_image_tag',
    [
        pytest.param('pedestrian', 'default', None),
        pytest.param(
            None,
            'loadable',
            'some_pedestrian_tag',
            marks=pytest.mark.config(
                CARGO_C2C_CORP_CLIENT_ID_TO_SHOW_PIN_ON_MAP_LOADABLE={
                    MARKET_CORP_CLIENT_ID: {
                        'image_tag': 'abacaba',
                        'pedestrian_tag': 'some_pedestrian_tag',
                        'car_tag': 'some_car_tag',
                        'rotatable': True,
                        'anchor': {'x': 0.5, 'y': 0.3},
                    },
                },
            ),
        ),
    ],
)
async def test_cargo_claims_corp_pin_to_show(
        taxi_cargo_c2c,
        create_cargo_claims_orders,
        get_default_order_id,
        default_pa_headers,
        mock_claims_full,
        mock_driver_trackstory,
        expected_pin_type,
        expected_type,
        expected_image_tag,
):
    mock_claims_full.corp_client_id = MARKET_CORP_CLIENT_ID
    mock_claims_full.claim_status = 'accepted'
    mock_claims_full.current_point_id = 1
    mock_claims_full.current_point = {
        'claim_point_id': 5,
        'last_status_change_ts': '2020-06-17T22:39:50+0300',
        'visit_status': 'pending',
    }

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/performer-position',
        json={'delivery_id': 'cargo-claims/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    resp = response.json()['pin']

    assert resp.get('type', None) == expected_type
    assert resp.get('pin_type', None) == expected_pin_type
    assert resp.get('image_tag', None) == expected_image_tag


@pytest.mark.experiments3(filename='experiment.json')
async def test_logistic_platform(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        default_pa_headers,
        mock_claims_full,
        mock_driver_trackstory,
        mock_logistic_platform,
        mock_order_statuses_history,
):
    await create_logistic_platform_orders()
    mock_logistic_platform.file_name = 'delivering.json'
    mock_order_statuses_history.file_name = 'delivering.json'
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/performer-position',
        json={'delivery_id': 'logistic-platform/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    assert response.json() == {
        'pin': {
            'anchor': {'x': 0.5, 'y': 0.3},
            'image_tag': 'abacaba',
            'rotatable': True,
            'type': 'loadable',
        },
        'position': {
            'direction': 0,
            'lat': 37.5,
            'lon': 55.7,
            'speed': 0.0,
            'timestamp': 100,
        },
    }


@pytest.mark.parametrize(
    'file_name',
    [
        'delivered.json',
        'in_middle_node.json',
        'order_created.json',
        'cancelled.json',
    ],
)
async def test_logistic_platform_no_position(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        default_pa_headers,
        mock_driver_trackstory,
        mock_logistic_platform,
        mock_order_statuses_history,
        file_name,
):
    await create_logistic_platform_orders()
    mock_logistic_platform.file_name = file_name
    mock_order_statuses_history.file_name = file_name
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/performer-position',
        json={'delivery_id': 'logistic-platform/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'unavailable_handle',
    [
        '/logistic-platform-admin/api/admin/request/trace',
        '/logistic-platform-uservices/api/internal/platform/request/info',
        '/logistic-platform-admin/api/internal/platform/request/history',
        '/cargo-claims/v2/claims/full',
        '/driver-trackstory/position',
    ],
)
@pytest.mark.experiments3(filename='experiment.json')
async def test_logistic_platform_error_service(
        taxi_cargo_c2c,
        create_logistic_platform_orders,
        get_default_order_id,
        default_pa_headers,
        mock_claims_full,
        mock_logistic_platform,
        mock_order_statuses_history,
        unavailable_handle,
        mockserver,
):
    await create_logistic_platform_orders()
    mock_logistic_platform.file_name = 'delivering.json'
    mock_order_statuses_history.file_name = 'delivering.json'

    @mockserver.json_handler(unavailable_handle)
    def _handle(request):
        return mockserver.make_response(status=500)

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/performer-position',
        json={'delivery_id': 'logistic-platform/' + get_default_order_id()},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 500
