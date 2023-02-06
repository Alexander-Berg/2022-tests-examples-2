# pylint: disable=too-many-lines

import datetime

import pytest

from . import utils


@pytest.fixture(name='check_response')
def _check_response(assert_response, assert_mocks):
    async def do_check_response(
            expected_status,
            orders_retrieve_called,
            order_revision_list_called,
            order_revision_details_called,
            place_assortment_details_called,
            retrieve_places_called,
            get_picker_order_called,
            cart_diff_called,
            eda_candidates_list_called,
            performer_location_called,
            vgw_api_forwardings_called,
            cargo_driver_voiceforwardings_called,
            expected_response=None,
    ):
        # второй итерацией проверяем, что при повторном запросе данные берутся
        # из базы, а ручки других сервисов не трогаем
        for _ in range(2):
            await assert_response(expected_status, expected_response)
            assert_mocks(
                orders_retrieve_called,
                order_revision_list_called,
                order_revision_details_called,
                place_assortment_details_called,
                retrieve_places_called,
                get_picker_order_called,
                cart_diff_called,
                eda_candidates_list_called,
                performer_location_called,
                vgw_api_forwardings_called,
                cargo_driver_voiceforwardings_called,
            )

    return do_check_response


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
async def test_get_order_history_200(
        create_order, load_json, environment, check_response,
):
    create_order(yandex_uid=None)
    environment.set_default()
    await check_response(
        expected_status=200,
        orders_retrieve_called=1,
        order_revision_list_called=1,
        order_revision_details_called=2,
        place_assortment_details_called=2,
        retrieve_places_called=1,
        get_picker_order_called=1,
        cart_diff_called=1,
        eda_candidates_list_called=1,
        performer_location_called=0,
        vgw_api_forwardings_called=1,
        cargo_driver_voiceforwardings_called=0,
        expected_response=load_json('expected_response.json'),
    )


@pytest.mark.parametrize('order_in_db', [False, True])
async def test_get_order_history_no_user_id_401(
        taxi_eats_retail_order_history, create_order, order_in_db,
):
    if order_in_db:
        create_order(yandex_uid=None, order_nr=utils.ORDER_ID)
    response = await taxi_eats_retail_order_history.get(
        '/eats/v1/retail-order-history/customer/order/history',
        params={'order_nr': utils.ORDER_ID},
    )
    assert response.status_code == 401


@pytest.mark.parametrize('pass_yandex_uid', [False, True])
async def test_get_order_history_db_missing_fields_404(
        taxi_eats_retail_order_history, create_order, pass_yandex_uid,
):
    create_order()
    headers = {'X-Eats-User': f'user_id={utils.CUSTOMER_ID}'}
    if pass_yandex_uid:
        headers['X-Yandex-UID'] = utils.YANDEX_UID
    response = await taxi_eats_retail_order_history.get(
        '/eats/v1/retail-order-history/customer/order/history',
        params={'order_nr': utils.ORDER_ID},
        headers=headers,
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'order_not_found'


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@pytest.mark.parametrize(
    'currency_code, currency_sign, region_id',
    [
        ['RUB', '₽', utils.REGION_ID_RU],
        ['KZT', '₸', utils.REGION_ID_KZ],
        ['BYN', None, utils.REGION_ID_BY],
    ],
)
async def test_get_order_history_from_db_200(
        load_json,
        create_order_from_json,
        assert_response,
        assert_response_body,
        currency_code,
        currency_sign,
        region_id,
):
    order_data = load_json('db_order.json')
    order_data['order']['currency_code'] = currency_code
    order_data['order']['region_id'] = str(region_id)
    create_order_from_json(order_data)
    response = await assert_response(200)
    expected_response = load_json('expected_response.json')
    expected_response['currency']['code'] = currency_code
    if currency_sign is not None:
        expected_response['currency']['sign'] = currency_sign
    else:
        del expected_response['currency']['sign']
    assert_response_body(response.json(), expected_response)


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@pytest.mark.parametrize('has_picked_items', [False, True])
@pytest.mark.parametrize('has_soft_delete', [False, True])
async def test_get_order_history_from_db_optional_diff_keys_200(
        taxi_eats_retail_order_history,
        load_json,
        create_order_from_json,
        assert_response_body,
        has_picked_items,
        has_soft_delete,
):
    order_data = load_json('db_order.json')
    expected_response = load_json('expected_response.json')

    if not has_picked_items:
        del order_data['order']['diff']['picked_items']
        del expected_response['diff']['picked_items']
    if not has_soft_delete:
        del order_data['order']['diff']['soft_delete']
        del expected_response['diff']['soft_delete']

    create_order_from_json(order_data)
    response = await taxi_eats_retail_order_history.get(
        '/eats/v1/retail-order-history/customer/order/history',
        params={'order_nr': utils.ORDER_ID},
        headers={
            'X-Eats-User': 'user_id=123',
            'X-Yandex-UID': utils.YANDEX_UID,
        },
    )
    assert response.status_code == 200
    assert_response_body(response.json(), expected_response)


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@pytest.mark.parametrize('expired_phone', ['courier_phone', 'picker_phone'])
@pytest.mark.parametrize('seconds_expired', [5, 1, 0, -1, -5])
async def test_get_order_history_from_db_phone_expired_200(
        load_json,
        assert_response,
        create_order_from_json,
        assert_response_body,
        expired_phone,
        seconds_expired,
        now,
):
    order_data = load_json('db_order.json')
    order_data['status_for_customer'] = 'cooking'
    order_data['picking_status'] = 'picked_up'
    order_data['order'][expired_phone][
        'expires_at'
    ] = now - datetime.timedelta(seconds=seconds_expired)
    create_order_from_json(order_data)
    response = await assert_response(200)
    expected_response = load_json('expected_response.json')
    if seconds_expired >= 0:
        del expected_response[f'forwarded_{expired_phone}']
    assert_response_body(response.json(), expected_response)


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@pytest.mark.parametrize(
    'orders_response',
    [
        {'status': 500},
        {'status': 404},
        {'status': 200, 'json': {'orders': []}},
    ],
)
async def test_get_order_history_core_order_not_found_404(
        create_order, mockserver, environment, orders_response, check_response,
):
    create_order(yandex_uid=None)
    environment.set_default()

    @mockserver.json_handler('/eats-core-orders-retrieve/orders/retrieve')
    def _eats_core_orders_retrieve(request):
        return mockserver.make_response(**orders_response)

    environment.mock_orders_retrieve = _eats_core_orders_retrieve

    await check_response(
        expected_status=404,
        orders_retrieve_called=1,
        order_revision_list_called=0,
        order_revision_details_called=0,
        place_assortment_details_called=0,
        retrieve_places_called=0,
        get_picker_order_called=0,
        cart_diff_called=0,
        eda_candidates_list_called=0,
        performer_location_called=0,
        vgw_api_forwardings_called=0,
        cargo_driver_voiceforwardings_called=0,
    )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@pytest.mark.parametrize(
    'order_kwargs',
    [
        {'customer_id': 'another_customer_id'},
        {'customer_id': ''},
        {'customer_id': None},
        None,
    ],
)
async def test_get_order_history_order_not_found_404(
        create_order, check_response, order_kwargs,
):
    if order_kwargs is not None:
        create_order(**order_kwargs)

    await check_response(
        expected_status=404,
        orders_retrieve_called=0,
        order_revision_list_called=0,
        order_revision_details_called=0,
        place_assortment_details_called=0,
        retrieve_places_called=0,
        get_picker_order_called=0,
        cart_diff_called=0,
        eda_candidates_list_called=0,
        performer_location_called=0,
        vgw_api_forwardings_called=0,
        cargo_driver_voiceforwardings_called=0,
    )


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
async def test_get_order_history_no_yandex_uid_400(
        taxi_eats_retail_order_history, create_order,
):
    create_order(yandex_uid=None)
    response = await taxi_eats_retail_order_history.get(
        '/eats/v1/retail-order-history/customer/order/history',
        params={'order_nr': utils.ORDER_ID},
        headers={'X-Eats-User': 'user_id=123'},
    )
    assert response.status_code == 400


@pytest.mark.parametrize('service_fee', [None, 0, 25])
@pytest.mark.parametrize('service_fee_enabled', [True, False])
@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
@utils.extra_fee_tanker_ids_config3()
@utils.get_fee_description_config3()
async def test_get_order_history_from_db_service_fee(
        taxi_eats_retail_order_history,
        load_json,
        create_order_from_json,
        service_fee,
        service_fee_enabled,
        experiments3,
):
    experiments3.add_config(**utils.zero_fee_enabled(service_fee_enabled))
    await taxi_eats_retail_order_history.invalidate_caches()

    order_data = load_json('db_order.json')
    order_data['order']['service_fee'] = service_fee
    create_order_from_json(order_data)
    response = await taxi_eats_retail_order_history.get(
        '/eats/v1/retail-order-history/customer/order/history',
        params={'order_nr': utils.ORDER_ID},
        headers={
            'X-Eats-User': 'user_id=123',
            'X-Yandex-UID': utils.YANDEX_UID,
        },
    )
    assert response.status_code == 200
    service_fee_expected = (
        (service_fee > 0 or service_fee_enabled)
        if service_fee is not None
        else False
    )

    if service_fee_expected:
        assert 'extra_fees' in response.json()
        extra_fees = response.json()['extra_fees']
        assert len(extra_fees) == 1
        extra_fee = extra_fees[0]
        assert extra_fee['code'] == 'service_fee'
        assert extra_fee['value'] == str(service_fee)
    else:
        assert 'extra_fees' not in response.json()

    expected_response = load_json('expected_response.json')
    expected_total_cost = expected_response['total_cost_for_customer']
    expected_delivery_cost = expected_response['delivery_cost_for_customer']

    assert float(response.json()['total_cost_for_customer']) == float(
        expected_total_cost,
    ) + (service_fee if service_fee_expected else 0.0)

    assert float(response.json()['delivery_cost_for_customer']) == float(
        expected_delivery_cost,
    ) + (service_fee if service_fee_expected else 0.0)


@utils.polling_config3()
@pytest.mark.parametrize(
    'status, polling', [(200, True), (400, False), (401, False), (404, True)],
)
async def test_get_order_history_polling(
        taxi_eats_retail_order_history,
        load_json,
        create_order,
        create_order_from_json,
        status,
        polling,
):
    if status == 200:
        order_data = load_json('db_order.json')
        create_order_from_json(order_data)
    elif status == 400:
        create_order(yandex_uid=None)
    else:
        create_order()

    headers = None
    if status != 401:
        headers = {'X-Eats-User': f'user_id={utils.CUSTOMER_ID}'}

    response = await taxi_eats_retail_order_history.get(
        '/eats/v1/retail-order-history/customer/order/history',
        params={'order_nr': utils.ORDER_ID},
        headers=headers,
    )
    assert response.status_code == status

    if polling:
        assert response.headers['X-Polling-Delay'] == '30'
    else:
        assert 'X-Polling-Delay' not in response.headers


@pytest.mark.now('2022-02-03T12:05:00+00:00')
@pytest.mark.parametrize(
    'started_at, duration, expected_duration',
    [
        (None, None, None),
        ('2022-02-03T12:01:00+00:00', 180, 0),
        ('2022-02-03T12:02:00+00:00', 180, 0),
        ('2022-02-03T12:03:00+00:00', 180, 60),
        ('2022-02-03T12:04:00+00:00', 180, 120),
        ('2022-02-03T12:05:00+00:00', 180, 180),
        ('2022-02-03T12:06:00+00:00', 180, 240),
        ('2022-02-03T12:04:42+00:00', 99, 81),
    ],
)
@pytest.mark.parametrize(
    'picking_status', ['picking', 'waiting_confirmation', 'picked_up'],
)
async def test_get_order_history_remaining_confirmation_duration(
        taxi_eats_retail_order_history,
        environment,
        load_json,
        create_order_from_json,
        started_at,
        duration,
        expected_duration,
        picking_status,
):
    order_data = load_json('db_order.json')
    order_data['order']['picking_status'] = picking_status
    create_order_from_json(order_data)
    environment.set_default()
    environment.order_confirmation_timers[order_data['order']['order_nr']][
        'confirmation'
    ] = {'started_at': started_at, 'duration': duration}

    headers = {'X-Eats-User': f'user_id={utils.CUSTOMER_ID}'}
    response = await taxi_eats_retail_order_history.get(
        '/eats/v1/retail-order-history/customer/order/history',
        params={'order_nr': utils.ORDER_ID},
        headers=headers,
    )
    assert response.status_code == 200

    if (
            picking_status == 'waiting_confirmation'
            and expected_duration is not None
    ):
        assert (
            response.json()['remaining_confirmation_duration']
            == expected_duration
        )
    else:
        assert 'remaining_confirmation_duration' not in response.json()


@pytest.mark.now('2021-07-01T12:00:00.123456+00:00')
async def test_get_order_history_from_db_optional_costs_200(
        load_json,
        create_order_from_json,
        assert_response,
        assert_response_body,
):
    order_data = load_json('db_order.json')
    del order_data['order']['original_cost_without_discounts']
    del order_data['order']['final_cost_without_discounts']
    create_order_from_json(order_data)
    response = await assert_response(200)
    expected_response = load_json('expected_response.json')
    assert_response_body(response.json(), expected_response)
