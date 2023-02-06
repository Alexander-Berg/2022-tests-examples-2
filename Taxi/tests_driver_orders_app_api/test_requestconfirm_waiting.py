import pytest

import tests_driver_orders_app_api.auth_helpers as auth
import tests_driver_orders_app_api.redis_helpers as rh
import tests_driver_orders_app_api.requestconfirm_helpers as rch

REQUEST_DATE = '2020-04-14T16:02:02.000Z'

EXISTING_PARK_ID = 'park_id_0'

CONTENT_HEADER = {'Content-Type': 'application/x-www-form-urlencoded'}

SHOW_BOTH = {'show_driver_cost': True, 'show_passenger_cost': True}
SHOW_PASSENGER = {'show_driver_cost': False, 'show_passenger_cost': True}
SHOW_DRIVER = {'show_driver_cost': True, 'show_passenger_cost': False}
SHOW_NONE = {'show_driver_cost': False, 'show_passenger_cost': False}

USER_BASE_PRICE = {
    'boarding': 1.0,
    'destination_waiting': 2.0,
    'distance': 3.0,
    'requirements': 4.0,
    'time': 5.0,
    'transit_waiting': 6.0,
    'waiting': 7.0,
}

DRIVER_BASE_PRICE = {
    'boarding': 8.0,
    'destination_waiting': 9.0,
    'distance': 10.0,
    'requirements': 11.0,
    'time': 12.0,
    'transit_waiting': 13.0,
    'waiting': 14.0,
}

REVEALED_FIXED_PRICE_RESPONSE = {
    'driver_fixed_price': {
        'max_distance': 500.0,
        'price': 143.0,
        'show': True,
    },
    'fixed_price': {'max_distance': 500.0, 'price': 143.0, 'show': True},
    'phone_options': [
        {
            'call_dialog_message_prefix': 'Телефон пассажира',
            'label': 'Телефон пассажира.',
            'type': 'main',
        },
    ],
    'status': 3,
}


@pytest.mark.parametrize(
    'driver_id,params,data,code',
    [
        (
            'driver_id_0',
            {'session': 'test_session', 'park_id': EXISTING_PARK_ID},
            'provider=2&order=order_id_0&'
            'date=2020-04-14T16:02:02.0000000&status=3',
            200,
        ),
    ],
)
@pytest.mark.config(
    DRIVER_ORDERS_APP_API_REDIS_LOCK_SETTINGS=rch.zero_retry_lock_settings(),
    DRIVER_ORDERS_APP_API_PG_UPDATE_SETTINGS=rch.pg_update_settings(),
    DRIVER_ORDERS_APP_API_DRIVER_MODE_SETTINGS={
        'setcar_percent': 100,
        'enable_compare': False,
    },
)
@pytest.mark.parametrize('has_date_in_request', [True, False])
@pytest.mark.parametrize('message', [None, 'some_message'])
@pytest.mark.parametrize(
    'coupon',
    [
        None,
        {'value': 100, 'source': 'cost'},
        {'value': 100, 'source': 'tariff'},
    ],
)
@pytest.mark.parametrize(
    'api_schema', ['compatible', 'requestconfirm_status_v2'],
)
@pytest.mark.parametrize('do_send_on_setcar_change', [True, False])
@pytest.mark.parametrize('do_send_on_setcar_update', [True, False])
@pytest.mark.now('2020-03-20T11:22:33.123456Z')
async def test_handle_request_confirm_waiting(
        taxi_driver_orders_app_api,
        driver_authorizer,
        fleet_parks,
        yataxi_client,
        driver_trackstory,
        driver_work_rules,
        stq,
        taxi_config,
        load,
        load_json,
        redis_store,
        driver_id,
        params,
        data,
        code,
        has_date_in_request,
        message,
        mocked_time,
        coupon,
        api_schema,
        do_send_on_setcar_change,
        do_send_on_setcar_update,
        contractor_order_history,
):
    taxi_config.set_values(
        {
            'DRIVER_ORDERS_APP_API_SEND_MESSAGE_ON_SETCAR_CHANGES': (
                do_send_on_setcar_change
            ),
            'DRIVER_ORDERS_APP_API_SEND_MESSAGE_ON_SETCAR_UPDATE': (
                do_send_on_setcar_update
            ),
        },
    )
    park_id = params['park_id']
    if not has_date_in_request:
        data = data.replace('date=2020-04-14T16:02:02.0000000&', '')
    if message:
        data += '&message={}'.format(message)
    data_dict = {kv.split('=')[0]: kv.split('=')[1] for kv in data.split('&')}
    order_id = data_dict['order']
    status = data_dict.get('status')
    app_family = auth.get_app_family(auth.USER_AGENT_TAXIMETER)
    driver_authorizer.set_client_session(
        app_family, park_id, params['session'], driver_id,
    )
    yataxi_client.taximeter_version = auth.USER_AGENT_TAXIMETER

    if params['park_id'] == EXISTING_PARK_ID:
        park = load_json('parks.json')[0]
        events = park['integration_events'][:]
        events.append('setcar_on_requestconfirm')
        park['integration_events'] = events
        fleet_parks.parks = {'parks': [park]}

    setcar = load_json('full_setcar.json')
    setcar['id'] = order_id
    if coupon:
        if coupon['source'] == 'cost':
            setcar['cost_cupon'] = coupon['value']
        if coupon['source'] == 'tariff':
            setcar['tariff'] = {
                'id': 'tariff_id',
                'discount': {'limit': coupon['value']},
            }
    rh.set_redis_for_order_cancelling(
        redis_store, park_id, order_id, driver_id, setcar_item=setcar,
    )
    rh.set_setcar_xml(redis_store, park_id, order_id, load('setcar.xml'))

    url = rch.get_requestconfirm_url(api_schema, status)
    headers = rch.get_headers(auth.USER_AGENT_TAXIMETER, park_id, driver_id)
    data = rch.process_data(api_schema, data_dict, data)
    response = await taxi_driver_orders_app_api.post(
        url,
        headers={**rch.get_content_type(api_schema), **headers},
        data=data,
        params=params,
    )

    assert response.status_code == code
    assert stq.driver_orders_integrator_requestconfirm.times_called == 1

    kwargs = stq.driver_orders_integrator_requestconfirm.next_call()['kwargs']
    kwargs.pop('log_extra')
    args_date = (
        REQUEST_DATE
        if has_date_in_request
        else mocked_time.now().strftime(rch.TAXIMETER_DATE_FORMAT)[:-4] + 'Z'
    )
    assert kwargs == {
        'change_date': {'$date': args_date},
        'comment': '',
        'driver_id': 'driver_id_0',
        'order_id': 'order_id_0',
        'park_id': 'park_id_0',
        'status': 3,
        'total_cost': 0.0,
    }

    if message:
        expected_called = int(do_send_on_setcar_update) + int(
            do_send_on_setcar_change,
        )
        assert stq.send_driver_order_messages.times_called == expected_called
        for _ in range(expected_called):
            data = stq.send_driver_order_messages.next_call()
            kwargs = data['kwargs']
            kwargs.pop('log_extra')
            kwargs_base = {
                'park_id': park_id,
                'driver_id': driver_id,
                'order_id': order_id,
                'locale': 'ru',
                'success': False,
            }
            if 'sender' in kwargs:
                assert kwargs == {
                    'message_code': 'OrderMessage_Updated',
                    'sender': 'Яндекс',
                    **kwargs_base,
                }
            else:
                assert kwargs == {'message': message, **kwargs_base}

    coh_request_args = await contractor_order_history.update.wait_call()
    request = coh_request_args['self'].json
    order_fields = {
        item['name']: item['value'] for item in request['order_fields']
    }
    assert order_fields['status'] == str(rh.OrderStatus.Waiting.value)

    if coupon:
        assert float(order_fields['cost_cupon']) == coupon['value']


@pytest.mark.parametrize(
    'driver_id,params,data,code',
    [
        (
            'driver_id_0',
            {'session': 'test_session', 'park_id': EXISTING_PARK_ID},
            'provider=2&order=order_id_0&'
            'date=2020-04-14T16:02:02.0000000&status=3',
            200,
        ),
    ],
)
@pytest.mark.parametrize(
    'setcar_base_price, fixed_price_show, driver_fixed_price_show',
    [
        ({'user': USER_BASE_PRICE, 'driver': DRIVER_BASE_PRICE}, False, False),
        ({'user': USER_BASE_PRICE, 'driver': DRIVER_BASE_PRICE}, True, True),
        ({'user': USER_BASE_PRICE, 'driver': DRIVER_BASE_PRICE}, True, False),
        ({'user': USER_BASE_PRICE}, False, False),
        ({}, True, True),
    ],
)
@pytest.mark.config(
    DRIVER_ORDERS_APP_API_REDIS_LOCK_SETTINGS=rch.zero_retry_lock_settings(),
    DRIVER_ORDERS_APP_API_PG_UPDATE_SETTINGS=rch.pg_update_settings(),
    DRIVER_ORDERS_APP_API_SEND_MESSAGE_ON_SETCAR_CHANGES=True,
    DRIVER_ORDERS_APP_API_SEND_MESSAGE_ON_SETCAR_UPDATE=True,
    DRIVER_ORDERS_APP_API_DRIVER_MODE_SETTINGS={
        'setcar_percent': 100,
        'enable_compare': False,
    },
)
@pytest.mark.parametrize(
    'driver_mode,payment_type',
    [('orders', 'card'), ('driver_fix', 'cash'), ('driver_fix', 'card')],
)
@pytest.mark.now('2020-03-20T11:22:33.123456Z')
async def test_request_confirm_base_price_revealing(
        taxi_driver_orders_app_api,
        driver_authorizer,
        driver_ui_profile,
        fleet_parks,
        yataxi_client,
        stq,
        load,
        load_json,
        redis_store,
        driver_id,
        params,
        data,
        code,
        setcar_base_price,
        fixed_price_show,
        driver_fixed_price_show,
        driver_mode,
        payment_type,
        contractor_order_history,
):
    driver_ui_profile.set_response(driver_mode)
    park_id = params['park_id']
    data_dict = {kv.split('=')[0]: kv.split('=')[1] for kv in data.split('&')}
    order_id = data_dict['order']
    status = data_dict.get('status')
    app_family = auth.get_app_family(auth.USER_AGENT_TAXIMETER)
    driver_authorizer.set_client_session(
        app_family, park_id, params['session'], driver_id,
    )
    yataxi_client.taximeter_version = auth.USER_AGENT_TAXIMETER

    if park_id == EXISTING_PARK_ID:
        park = load_json('parks.json')[0]
        events = park['integration_events'][:]
        events.append('setcar_on_requestconfirm')
        park['integration_events'] = events
        fleet_parks.parks = {'parks': [park]}

    setcar = load_json('full_setcar.json')
    setcar['id'] = order_id
    setcar['base_price'] = setcar_base_price
    setcar['fixed_price']['show'] = fixed_price_show
    setcar['driver_fixed_price']['show'] = driver_fixed_price_show
    setcar['pay_type'] = 0 if payment_type == 'cash' else 1
    setcar['driver_mode_info'] = {'display_mode': driver_mode}
    rh.set_redis_for_order_cancelling(
        redis_store, park_id, order_id, driver_id, setcar_item=setcar,
    )
    rh.set_setcar_xml(redis_store, park_id, order_id, load('setcar.xml'))

    url = rch.get_requestconfirm_url('requestconfirm_status_v2', status)
    headers = rch.get_headers(auth.USER_AGENT_TAXIMETER, park_id, driver_id)
    data = rch.process_data('requestconfirm_status_v2', data_dict, data)
    response = await taxi_driver_orders_app_api.post(
        url,
        headers={
            **rch.get_content_type('requestconfirm_status_v2'),
            **headers,
        },
        data=data,
        params=params,
    )

    assert response.status_code == code
    assert stq.driver_orders_integrator_requestconfirm.times_called == 1
    any_fixed_price_revealed = (
        not fixed_price_show or not driver_fixed_price_show
    )
    response_json = response.json()
    if any_fixed_price_revealed and setcar_base_price:
        assert response_json['base_price'] == setcar_base_price
    else:
        assert 'base_price' not in response_json

    coh_request_args = await contractor_order_history.update.wait_call()
    request = coh_request_args['self'].json
    order_fields = {
        item['name']: item['value'] for item in request['order_fields']
    }
    assert order_fields['status'] == str(rh.OrderStatus.Waiting.value)
