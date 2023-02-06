import uuid

from testsuite.utils import matching


def get_processing_order_events(matching_datetime=False):
    return {
        'events': [
            {
                'event_id': '1',
                'created': (
                    matching.datetime_string
                    if matching_datetime
                    else '2020-02-25T06:00:00+03:00'
                ),
                'payload': {
                    'kind': 'order-cancel-failed',
                    'data': {
                        'code': 'inappropriate_status',
                        'message': 'some message',
                        'cancel_type': 'free',
                        'request_id': '123',
                    },
                },
                'handled': True,
            },
        ],
    }


def get_processing_cargo_claims_events(matching_datetime=False):
    return {
        'events': [
            {
                'event_id': '0f580f7654b646dea0cac9755d19eca1',
                'created': (
                    matching.datetime_string
                    if matching_datetime
                    else '2022-07-04T16:46:17.126109+00:00'
                ),
                'handled': True,
                'payload': {
                    'data': {
                        'called_from': 'processing',
                        'current_point_id': 1320448,
                        'status': 'performer_found',
                        'claim_id': 'e1888485e26a4268aecad12df0082608',
                    },
                    'kind': 'claims-order-status-changed',
                },
            },
        ],
    }


def get_processing_cargo_c2c_events(matching_datetime=False):
    return {
        'events': [
            {
                'event_id': '"3108210da7c443148a6f7e035dd3194c',
                'created': (
                    matching.datetime_string
                    if matching_datetime
                    else '2022-07-04T12:28:27.870972+00:00'
                ),
                'handled': True,
                'payload': {
                    'data': {
                        'called_from': 'processing',
                        'current_point_id': 1319647,
                        'status': 'performer_found',
                        'claim_id': 'ecda53254fee414f980fe45ee6cc4a3a',
                    },
                    'kind': 'c2c-order-status-changed',
                },
            },
        ],
    }


def get_admin_info_response(order_id, provider_processing_events=None):
    result = {
        'cargo_ref_id': 'some_cargo_ref_id',
        'created_ts': matching.datetime_string,
        'order_id': order_id,
        'order_provider_id': 'cargo-c2c',
        'phone_pd_id': 'phone_pd_id_1',
        'raw': {
            'client_order': {
                'created_ts': matching.datetime_string,
                'etag': matching.uuid_string,
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
                'phone_pd_id': 'phone_pd_id_1',
                'resolution': None,
                'roles': ['sender'],
                'terminated_at': None,
                'sharing_key': matching.AnyString(),
                'updated_ts': matching.datetime_string,
                'user_id': 'user_id_1_2',
                'do_not_show_in_go': None,
            },
            'offer': {
                'calc_id': 'cargo-pricing/v1/01234567890123456789012345678912',
                'created_ts': matching.datetime_string,
                'expectations': {
                    'meters_to_arrive': 7067,
                    'seconds_to_arrive': 778,
                },
                'delivery_description': {
                    'due': matching.datetime_string,
                    'payment_info': {'id': 'card-123', 'type': 'card'},
                    'route_points': [
                        {'coordinates': [55.0, 55.0], 'type': 'source'},
                        {'coordinates': [56.0, 56.0], 'type': 'destination'},
                    ],
                    'zone_name': 'moscow',
                },
                'estimate_response': {
                    'currency': 'RUB',
                    'offer_id': matching.uuid_string,
                    'price': '200.999',
                    'taxi_tariff': 'express',
                    'type': '',
                    'decision': 'order_allowed',
                },
                'offer_id': matching.uuid_string,
                'pa_auth_context': {
                    'application': 'iphone',
                    'locale': 'en',
                    'phone_pd_id': 'phone_pd_id_3',
                    'user_id': 'some_user_id',
                    'yandex_uid': 'yandex_uid',
                    'remote_ip': '1.1.1.1',
                },
                'taxi_tariff': {
                    'taxi_requirements': {'a': '123', 'b': 123},
                    'taxi_tariff': 'express',
                },
                'updated_ts': matching.datetime_string,
                'driver_eta_request_link_id': matching.uuid_string,
            },
            'order': {
                'additional_delivery_description': {
                    'comment': 'some_comment',
                    'payment_info': {'id': 'card-123', 'type': 'card'},
                    'route_points': [
                        {
                            'area_description': 'some ' 'area_description',
                            'comment': 'comment',
                            'contact': {
                                'name': 'some_name',
                                'phone_pd_id': '+79999999999_id',
                            },
                            'coordinates': [55.0, 55.0],
                            'full_text': 'some ' 'full_text',
                            'short_text': 'some ' 'short_text',
                            'type': 'source',
                            'uri': 'some ' 'uri',
                        },
                        {
                            'area_description': 'some ' 'area_description',
                            'contact': {
                                'name': 'some_name',
                                'phone_pd_id': '+79999999999_id',
                            },
                            'coordinates': [56.0, 56.0],
                            'full_text': 'some ' 'full_text',
                            'short_text': 'some ' 'short_text',
                            'type': 'destination',
                            'uri': 'some ' 'uri',
                        },
                    ],
                },
                'cargo_ref_id': 'some_cargo_ref_id',
                'lp_order_id': None,
                'order_provider_id': 'cargo-c2c',
                'commited_ts': matching.datetime_string,
                'created_ts': matching.datetime_string,
                'drafted_ts': matching.datetime_string,
                'offer_id': matching.uuid_string,
                'order_id': order_id,
                'pa_auth_context': {
                    'application': 'iphone',
                    'locale': 'en',
                    'phone_pd_id': 'phone_pd_id_3',
                    'user_agent': 'some_agent',
                    'user_id': 'some_user_id',
                    'yandex_uid': 'yandex_uid',
                    'remote_ip': '1.1.1.1',
                },
                'phone_pd_id': 'phone_pd_id_3',
                'postcard_download_url': None,
                'postcard_s3_path': None,
                'source': 'yandex_go',
                'updated_ts': matching.datetime_string,
                'brand': 'yataxi',
                'tips_percent_default': None,
                'creation_status': 'commited',
            },
            'processing_events': get_processing_order_events(
                matching_datetime=True,
            ),
        },
        'roles': ['sender'],
        'updated_ts': matching.datetime_string,
        'user_id': 'user_id_1_2',
    }
    if provider_processing_events:
        result['raw'][
            'provider_processing_events'
        ] = provider_processing_events
    return result


async def test_succes_fetch_processing_events(
        taxi_cargo_c2c, mockserver, create_cargo_c2c_orders,
):
    @mockserver.json_handler('/processing/v1/delivery/order/events')
    def _processing_order_events(request):
        return mockserver.make_response(
            json={'code': 'no_such_service', 'message': 'dostavka ne naidena'},
            status=400,
        )

    @mockserver.json_handler(
        '/processing/v1/delivery/c2c_flow_cargo_c2c/events',
    )
    def _processing_cargo_c2c_events(request):
        assert request.query == {'item_id': 'some_cargo_ref_id'}
        return mockserver.make_response(
            json={'code': 'internal_server_error', 'message': 'master failed'},
            status=500,
        )

    order_id = await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/v1/admin/delivery/info',
        headers={'Accept-Language': 'ru'},
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
            },
        },
    )
    assert response.status_code == 200
    assert 'processing_events' not in response.json()


async def test_admin_search_not_found(taxi_cargo_c2c):
    response = await taxi_cargo_c2c.post(
        '/v1/admin/delivery/info',
        headers={'Accept-Language': 'ru'},
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': uuid.uuid4().hex,
                'order_provider_id': 'cargo-c2c',
            },
        },
    )

    assert response.status_code == 404


async def test_cargo_c2c_admin_info_success(
        taxi_cargo_c2c, mockserver, create_cargo_c2c_orders,
):
    @mockserver.json_handler('/processing/v1/delivery/order/events')
    def _processing_order_events(request):
        return get_processing_order_events()

    @mockserver.json_handler(
        '/processing/v1/delivery/c2c_flow_cargo_c2c/events',
    )
    def _processing_cargo_c2c_events(request):
        assert request.query == {'item_id': 'some_cargo_ref_id'}
        return get_processing_cargo_c2c_events()

    order_id = await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/v1/admin/delivery/info',
        headers={'Accept-Language': 'ru'},
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
            },
        },
    )

    assert response.status_code == 200
    assert response.json() == get_admin_info_response(
        order_id, get_processing_cargo_c2c_events(matching_datetime=True),
    )


async def test_cargo_c2c_hide_private_data(
        taxi_cargo_c2c, mockserver, create_cargo_c2c_orders,
):
    @mockserver.json_handler('/processing/v1/delivery/order/events')
    def _processing_order_events(request):
        return get_processing_order_events()

    @mockserver.json_handler(
        '/processing/v1/delivery/c2c_flow_cargo_c2c/events',
    )
    def _processing_cargo_c2c_events(request):
        assert request.query == {'item_id': 'some_cargo_ref_id'}
        return get_processing_cargo_c2c_events()

    order_id = await create_cargo_c2c_orders(add_postcard=True)
    response = await taxi_cargo_c2c.post(
        '/v1/admin/delivery/info',
        headers={'Accept-Language': 'ru'},
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
            },
        },
    )

    assert response.status_code == 200

    resp = response.json()
    assert resp['raw']['order']['postcard_download_url'] is None
    s3_path = resp['raw']['order']['postcard_s3_path']

    assert resp['raw']['order']['postcard_s3_path'] == s3_path
    assert (
        resp['raw']['order']['additional_delivery_description']['postcard']
        == {
            'download_url': '<hidden data>',
            'path': s3_path,
            'user_message': 'hi, buddy!',
        }
    )

    resp['raw']['order']['postcard_download_url'] = None
    resp['raw']['order']['postcard_s3_path'] = None
    del resp['raw']['order']['additional_delivery_description']['postcard']
    assert resp == get_admin_info_response(
        order_id, get_processing_cargo_c2c_events(matching_datetime=True),
    )


async def test_cargo_claims_admin_info_success(
        taxi_cargo_c2c,
        mockserver,
        create_cargo_claims_orders,
        get_default_order_id,
):
    @mockserver.json_handler('/processing/v1/delivery/order/events')
    def _processing_order_events(request):
        return {'events': []}

    order_id = get_default_order_id()

    @mockserver.json_handler(
        '/processing/v1/delivery/c2c_flow_cargo_claims/events',
    )
    def _processing_cargo_claims_events(request):
        assert request.query == {'item_id': order_id}
        return get_processing_cargo_claims_events()

    response = await taxi_cargo_c2c.post(
        '/v1/admin/delivery/info',
        headers={'Accept-Language': 'ru'},
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': order_id,
                'order_provider_id': 'cargo-claims',
            },
        },
    )
    assert response.status_code == 200

    actual = response.json()
    assert actual['cargo_ref_id'] == get_default_order_id()
    assert actual['raw'][
        'provider_processing_events'
    ] == get_processing_cargo_claims_events(matching_datetime=True)


async def test_taxi_admin_info_success(
        taxi_cargo_c2c, mockserver, create_taxi_orders, get_default_order_id,
):
    @mockserver.json_handler('/processing/v1/delivery/order/events')
    def _events(request):
        return {'events': []}

    response = await taxi_cargo_c2c.post(
        '/v1/admin/delivery/info',
        headers={'Accept-Language': 'ru'},
        json={
            'id': {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': get_default_order_id(),
                'order_provider_id': 'taxi',
            },
        },
    )
    assert response.status_code == 200

    actual = response.json()
    assert actual['taxi_order_id'] == get_default_order_id()
    assert 'provider_processing_events' not in actual['raw']


# TODO: logistic-platform-c2c
