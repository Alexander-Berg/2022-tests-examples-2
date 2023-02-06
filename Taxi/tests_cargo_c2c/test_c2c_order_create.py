import datetime

import pytest
import json


async def test_commit(
        taxi_cargo_c2c,
        default_pa_headers,
        order_processing_order_create_requested,
):
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/commit',
        json={'delivery_id': 'cargo-c2c/3b8d1af142664fde824626a7c19e2bd9'},
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200

    assert order_processing_order_create_requested.next_call() == {
        'arg': {
            'data': {
                'order_id': '3b8d1af142664fde824626a7c19e2bd9',
                'order_provider_id': 'cargo-c2c',
                'phone_pd_id': 'phone_pd_id_1',
                'roles': ['initiator'],
            },
            'kind': 'order-create-requested',
            'trait': 'is-create',
        },
    }


async def test_create_c2c_order_no_draft(taxi_cargo_c2c):
    response = await taxi_cargo_c2c.post(
        '/v1/processing/delivery-order/create-c2c-order',
        json={
            'id': {
                'order_id': 'some_order_id',
                'order_provider_id': 'cargo-c2c',
                'phone_pd_id': 'phone_pd_id_3',
            },
        },
    )
    assert response.status_code == 400
    assert response.json()['message'] == 'Не удалось создать заказ'


async def test_create_c2c_order_no_offer(
        taxi_cargo_c2c, default_pa_headers, get_default_draft_request,
):
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/draft',
        json=get_default_draft_request(),
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200

    order_id = response.json()['delivery_id'].split('/')[1]
    response = await taxi_cargo_c2c.post(
        '/v1/processing/delivery-order/create-c2c-order',
        json={
            'id': {
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
                'phone_pd_id': 'phone_pd_id_1',
            },
        },
    )
    assert response.status_code == 400
    assert response.json()['message'] == 'Не удалось создать заказ'


async def test_create_c2c_order_by_encrypted_offer(
        taxi_cargo_c2c,
        default_pa_headers,
        get_default_draft_request,
        get_default_offer,
        default_calc_response,
        aes_encrypt,
        pgsql,
        mockserver,
):

    offer = get_default_offer()
    draft_request = get_default_draft_request()
    serialized_offer = json.dumps(offer).encode('utf-8')
    encrypted_offer = aes_encrypt(serialized_offer)
    draft_request['offer_id'] = encrypted_offer

    @mockserver.json_handler('/uantifraud/v1/delivery/can_make_order')
    def _mock_can_make_order(request):
        return mockserver.make_response(json={'status': 'allow'})

    @mockserver.json_handler('/cargo-pricing/v1/taxi/calc/retrieve')
    def _calc(request):
        response = default_calc_response.copy()
        response['request'] = {}
        return response

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/draft',
        json=draft_request,
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200

    cursor = pgsql['cargo_c2c'].cursor()
    cursor.execute(
        f"""
    SELECT estimate_response, expectations, driver_eta_request_link_id
    FROM cargo_c2c.offers
        """,
    )
    assert list(cursor) == [
        (
            offer['estimate_response'],
            offer['expectations'],
            offer['driver_eta_request_link_id'],
        ),
    ]
    # another draft request with the same offer
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/draft',
        json=draft_request,
        headers=default_pa_headers('phone_pd_id_1'),
    )
    assert response.status_code == 200
    cursor.execute('SELECT COUNT(*) FROM cargo_c2c.offers')
    assert list(cursor) == [(1,)]


@pytest.mark.config(CARGO_C2C_USERS_BLACKLIST=['phone_pd_id_3'])
async def test_create_c2c_order_blacklisted_user(
        taxi_cargo_c2c, default_pa_headers, get_default_draft_request,
):
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/draft',
        json=get_default_draft_request(),
        headers=default_pa_headers('phone_pd_id_3'),
    )
    assert response.status_code == 403


async def test_create_c2c_order_blocked_by_antifraud(
        taxi_cargo_c2c,
        default_pa_headers,
        mockserver,
        create_cargo_c2c_orders,
        get_default_draft_request,
        get_default_estimate_request,
):
    @mockserver.json_handler('/uantifraud/v1/delivery/can_make_order')
    def _mock_can_make_order(request):
        assert request.json == {
            'delivery_description': {
                'comment': 'some_comment',
                'payment_info': {'id': 'card-123', 'type': 'card'},
                'route_points': [
                    {
                        'comment': 'comment',
                        'contact': {
                            'name': 'some_name',
                            'phone_pd_id': '+79999999999_id',
                        },
                        'full_text': 'some full_text',
                        'position': {'lat': 55.0, 'lon': 55.0},
                        'type': 'source',
                    },
                    {
                        'contact': {
                            'name': 'some_name',
                            'phone_pd_id': '+79999999999_id',
                        },
                        'full_text': 'some full_text',
                        'position': {'lat': 56.0, 'lon': 56.0},
                        'type': 'destination',
                    },
                ],
            },
            'user_agent': 'some_agent',
            'application': 'iphone',
        }
        return mockserver.make_response(json={'status': 'block'})

    response = await taxi_cargo_c2c.post(
        '/v1/delivery/estimate',
        json=get_default_estimate_request(),
        headers=default_pa_headers('phone_pd_id_3'),
    )
    assert response.status_code == 200

    draft_request = get_default_draft_request()
    draft_request['offer_id'] = response.json()['estimations'][0]['offer_id']
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/draft',
        json=draft_request,
        headers=default_pa_headers('phone_pd_id_3'),
    )
    assert response.status_code == 200

    order_id = response.json()['delivery_id'].split('/')[1]
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
    assert response.status_code == 400


async def test_create_c2c_order(
        taxi_cargo_c2c, create_cargo_c2c_orders, pgsql,
):
    await create_cargo_c2c_orders()
    cursor = pgsql['cargo_c2c'].cursor()
    cursor.execute(
        """
          SELECT cargo_ref_id,
                 source,
                 creation_status
          FROM cargo_c2c.orders
      """,
    )
    assert list(cursor) == [('some_cargo_ref_id', 'yandex_go', 'commited')]


async def test_claim_not_created(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        pgsql,
        mockserver,
        get_default_estimate_request,
        get_default_draft_request,
        default_pa_headers,
        default_calc_response,
        mock_cargo_pricing,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/c2c/create')
    def _create_claim(request):
        return mockserver.make_response(
            json={'code': 'bad_request', 'message': 'bad_request'}, status=400,
        )

    @mockserver.json_handler('/uantifraud/v1/delivery/can_make_order')
    def _mock_can_make_order(request):
        return mockserver.make_response(json={'status': 'allow'})

    @mockserver.json_handler('/cargo-pricing/v1/taxi/calc/retrieve')
    def _calc(request):
        response = default_calc_response.copy()
        response['request'] = mock_cargo_pricing.v2_calc_mock.next_call()[
            'request'
        ].json
        return response

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

    cursor = pgsql['cargo_c2c'].cursor()
    cursor.execute(
        """
          SELECT cargo_ref_id,
                 source,
                 creation_status
          FROM cargo_c2c.orders
      """,
    )
    assert list(cursor) == [(None, 'yandex_go', 'drafted')]

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

    cursor = pgsql['cargo_c2c'].cursor()
    cursor.execute(
        """
          SELECT cargo_ref_id,
                 source,
                 creation_status
          FROM cargo_c2c.orders
      """,
    )
    assert list(cursor) == [(None, 'yandex_go', 'commit-requested')]

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
    assert response.status_code == 400

    response = await taxi_cargo_c2c.post(
        '/v1/processing/delivery-order/change-creation-status',
        json={
            'id': {
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
                'phone_pd_id': 'phone_pd_id_3',
            },
            'status': 'failed-to-create',
        },
    )
    assert response.status_code == 200

    cursor = pgsql['cargo_c2c'].cursor()
    cursor.execute(
        """
          SELECT cargo_ref_id,
                 source,
                 creation_status
          FROM cargo_c2c.orders
      """,
    )
    assert list(cursor) == [(None, 'yandex_go', 'failed-to-create')]


@pytest.mark.parametrize(
    'yamaps_uri, claim_uri',
    [
        (None, 'ymapsbm1://geo?ll=55%2C55'),
        ('ymapsbm1://geo?exit1', 'ymapsbm1://geo?exit1'),
    ],
)
async def test_create_without_point_uri_fallback(
        taxi_cargo_c2c,
        default_pa_headers,
        get_default_draft_request,
        create_cargo_c2c_orders,
        get_default_claims_request,
        yamaps,
        yamaps_uri,
        claim_uri,
):
    @yamaps.set_fmt_geo_objects_callback
    def _mock_maps(request):
        result = [
            {
                'description': 'Москва, Россия',
                'geocoder': {
                    'address': {
                        'country': 'Россия',
                        'formatted_address': (
                            'Россия, Москва, Садовническая улица'
                        ),
                        'locality': 'Москва',
                        'street': 'Садовническая улица',
                    },
                    'id': '8063585',
                },
                'geometry': [37.615928, 55.757333],
                'name': 'Садовническая улица',
            },
        ]
        if yamaps_uri:
            result[0]['uri'] = yamaps_uri
        return result

    expected_claims_request = get_default_claims_request()
    expected_claims_request['claim']['route_points'][0]['address'][
        'uri'
    ] = claim_uri

    draft_request = get_default_draft_request()
    draft_request['additional_delivery_description']['route_points'][0].pop(
        'uri',
    )

    await create_cargo_c2c_orders(
        draft_request=draft_request,
        expected_claims_request=expected_claims_request,
    )


async def test_create_without_contact(
        taxi_cargo_c2c,
        default_pa_headers,
        get_default_draft_request,
        create_cargo_c2c_orders,
        get_default_claims_request,
):
    expected_claims_request = get_default_claims_request()
    expected_claims_request['claim']['skip_client_notify'] = True
    for point in expected_claims_request['claim']['route_points']:
        point['contact']['phone'] = 'phone_pd_i'

    draft_request = get_default_draft_request()
    for point in draft_request['additional_delivery_description'][
            'route_points'
    ]:
        point.pop('contact')

    await create_cargo_c2c_orders(
        draft_request=draft_request,
        expected_claims_request=expected_claims_request,
    )


async def test_initiator_saved_order_many_roles(
        taxi_cargo_c2c,
        default_pa_headers,
        create_cargo_c2c_orders,
        save_client_order,
        mockserver,
        load_json,
):
    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    def _phones_bulk_store(request):
        return {
            'items': [
                {'id': 'phone_pd_id_3', 'value': item['value']}
                for item in request.json['items']
            ],
        }

    save_client_order.expected_roles = ['initiator', 'sender', 'recipient']

    await create_cargo_c2c_orders(
        expected_claims_request=load_json(
            'cargo_claims_create_expected_request_with_many_roles.json',
        ),
    )


async def test_initiator_saved_order_one_role(
        taxi_cargo_c2c,
        default_pa_headers,
        create_cargo_c2c_orders,
        save_client_order,
        mockserver,
):
    save_client_order.expected_roles = ['initiator']
    await create_cargo_c2c_orders()


@pytest.mark.config(CARGO_C2C_ENABLE_ADDRESS_LOCALIZE=True)
async def test_address_localization(
        taxi_cargo_c2c, create_cargo_c2c_orders, yamaps, load_json, mockserver,
):
    await create_cargo_c2c_orders(
        expected_claims_request=load_json(
            'cargo_claims_create_expected_request_with_localization.json',
        ),
    )


async def test_create_c2c_order_corp_payment(
        taxi_cargo_c2c,
        get_default_draft_request,
        get_default_estimate_request,
        default_pa_headers,
):
    estimate_request = get_default_estimate_request()
    draft_request = get_default_draft_request()
    estimate_request['delivery_description']['payment_info'] = {
        'id': 'corp-123',
        'type': 'corp',
    }
    draft_request['additional_delivery_description']['payment_info'] = {
        'id': 'corp-123',
        'type': 'corp',
    }
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
        '/v1/processing/delivery-order/create-c2c-order',
        json={
            'id': {
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
                'phone_pd_id': 'phone_pd_id_3',
            },
        },
    )
    assert response.status_code == 400
    assert (
        response.json()['message'] == 'Не удалось создать заказ. '
        'Пожалуйста, выберите другой способ оплаты.'
    )


# тк время в тестах заморожено (wiki/backend/testsuite/#rabotasovremenem),
# получась что оффер создавался якобы позднее чем отдает now в create_order,
# поэтому сдвигаем немного вперед now в этом тесте
@pytest.mark.config(CARGO_C2C_CLIENT_OFFER_TTL=0)
@pytest.mark.now(
    (datetime.datetime.utcnow() + datetime.timedelta(minutes=15)).strftime(
        '%Y-%m-%dT%H:%M:%S.%f',
    ),
)
async def test_create_c2c_order_with_ttl_offer(
        taxi_cargo_c2c,
        get_default_draft_request,
        get_default_estimate_request,
        default_pa_headers,
):
    draft_request = get_default_draft_request()

    response = await taxi_cargo_c2c.post(
        '/v1/delivery/estimate',
        json=get_default_estimate_request(),
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
        '/v1/processing/delivery-order/create-c2c-order',
        json={
            'id': {
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
                'phone_pd_id': 'phone_pd_id_3',
            },
        },
    )
    assert response.status_code == 400
    assert (
        response.json()['message'] == 'Не удалось создать заказ. '
        'Время действия оффера истекло.'
    )


@pytest.mark.experiments3(filename='experiment.json')
async def test_create_c2c_order_with_coupon(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        pgsql,
        mockserver,
        get_default_estimate_request,
        get_default_claims_request,
):
    expected_claims_request = get_default_claims_request()
    expected_claims_request['estimation_result']['requirements'][
        'coupon'
    ] = 'LUCKY_ONE_2000'

    estimate_request = get_default_estimate_request()
    estimate_request['delivery_description']['payment_info'][
        'coupon'
    ] = 'LUCKY_ONE_2000'

    await create_cargo_c2c_orders(
        estimate_request=estimate_request,
        expected_claims_request=expected_claims_request,
        add_coupon=True,
    )


async def test_create_c2c_order_with_d2d(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        pgsql,
        mockserver,
        get_default_estimate_request,
        get_default_claims_request,
):
    expected_claims_request = get_default_claims_request()
    expected_claims_request['estimation_result']['requirements'][
        'door_to_door'
    ] = True
    expected_claims_request['claim']['skip_door_to_door'] = False

    estimate_request = get_default_estimate_request()
    estimate_request['taxi_tariffs'][0]['taxi_requirements'][
        'door_to_door'
    ] = True
    estimate_request['taxi_tariffs'][1]['taxi_requirements'][
        'door_to_door'
    ] = True

    await create_cargo_c2c_orders(
        estimate_request=estimate_request,
        expected_claims_request=expected_claims_request,
    )


@pytest.mark.experiments3(filename='experiment.json')
async def test_create_without_country_code(
        taxi_cargo_c2c,
        default_pa_headers,
        get_default_draft_request,
        create_cargo_c2c_orders,
        get_default_claims_request,
):
    expected_claims_request = get_default_claims_request()
    expected_claims_request['claim']['skip_client_notify'] = True

    # just to make a claim

    draft_request = get_default_draft_request()
    for point in draft_request['additional_delivery_description'][
            'route_points'
    ]:
        point['contact']['phone'] = '9999999999'

    # this is what we actually test:
    #  9999999999 becoming +79999999999
    #  because point B matched RU and +7 code was used

    await create_cargo_c2c_orders(
        draft_request=draft_request,
        expected_claims_request=expected_claims_request,
    )


@pytest.mark.experiments3(filename='experiment.json')
async def test_logistic_platform_c2c(
        taxi_cargo_c2c,
        default_pa_headers,
        pgsql,
        create_logistic_platform_c2c_orders,
):
    order_id = await create_logistic_platform_c2c_orders()

    response = await taxi_cargo_c2c.post(
        '/v1/clients-orders',
        json={
            'order_id': order_id,
            'order_provider_id': 'logistic-platform-c2c',
        },
    )
    assert response.status_code == 200
    assert len(response.json()['orders']) == 3

    cursor = pgsql['cargo_c2c'].cursor()
    cursor.execute('SELECT lp_order_id FROM cargo_c2c.orders')
    assert list(cursor) == [('some_request_id',)]
