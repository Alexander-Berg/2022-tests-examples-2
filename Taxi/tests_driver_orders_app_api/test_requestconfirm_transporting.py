import copy

import pytest

import tests_driver_orders_app_api.auth_helpers as auth
import tests_driver_orders_app_api.redis_helpers as rh
import tests_driver_orders_app_api.requestconfirm_helpers as rch

CONTENT_HEADER = {'Content-Type': 'application/x-www-form-urlencoded'}
REQUESTCONFIRM_OK = {
    'superapp_voice_promo': {
        'file_url': (
            'https://static.rostaxi.org/taximeter_welcome_sound/'
            'welcome_mask_rus.ogg'
        ),
    },
    'phone_options': [
        {
            'call_dialog_message_prefix': 'Телефон пассажира',
            'label': 'Телефон пассажира.',
            'type': 'main',
        },
    ],
}


@pytest.mark.parametrize(
    'driver_id,params,data,code',
    [
        (
            'driver_id_0',
            {'session': 'test_session', 'park_id': 'park_id_0'},
            'provider=2&order=order_id_0&'
            'date=2020-04-14T16%3A02%3A02.0000000&status=5',
            200,
        ),
    ],
)
@pytest.mark.parametrize('custom_driver', [None, 'custom_driver'])
@pytest.mark.config(
    DRIVER_ORDERS_APP_API_REDIS_LOCK_SETTINGS=rch.zero_retry_lock_settings(),
    DRIVER_ORDERS_APP_API_PG_UPDATE_SETTINGS=rch.pg_update_settings(),
    DRIVER_ORDERS_APP_API_DRIVER_MODE_SETTINGS={
        'setcar_percent': 100,
        'enable_compare': False,
    },
)
@pytest.mark.parametrize('has_aggregator', [True, False])
@pytest.mark.parametrize('has_superapp_voice_promo', [True, False])
@pytest.mark.parametrize(
    'api_schema', ['compatible', 'requestconfirm_status_v2'],
)
@pytest.mark.now('2020-03-20T11:22:33.123456Z')
async def test_handle_request_confirm_transporting(
        taxi_driver_orders_app_api,
        driver_authorizer,
        fleet_parks,
        yataxi_client,
        load_json,
        redis_store,
        custom_driver,
        driver_id,
        params,
        data,
        code,
        mocked_time,
        has_aggregator,
        has_superapp_voice_promo,
        api_schema,
        contractor_order_history,
):
    park_id = params['park_id']
    data_dict = {kv.split('=')[0]: kv.split('=')[1] for kv in data.split('&')}
    order_id = data_dict['order']
    status = data_dict.get('status')
    app_family = auth.get_app_family(auth.USER_AGENT_TAXIMETER)
    driver_authorizer.set_client_session(
        app_family, park_id, params['session'], driver_id,
    )
    yataxi_client.taximeter_version = auth.USER_AGENT_TAXIMETER

    if params['park_id'] == 'park_id_0':
        fleet_parks.parks = {'parks': [load_json('parks.json')[0]]}

    setcar = load_json('full_setcar.json')
    agg_id = setcar['agg']
    setcar['id'] = order_id
    rh.set_redis_for_order_cancelling(
        redis_store, park_id, order_id, driver_id, setcar_item=setcar,
    )
    if custom_driver:
        rh.remove_setcar_driver_reserv(
            redis_store, park_id, driver_id, order_id,
        )
        rh.set_driver_for_order(
            redis_store, params['park_id'], 'order_id_0', custom_driver,
        )

    if has_aggregator:
        rh.set_aggregator_name(redis_store, agg_id, 'some_agg_name')
    yataxi_client.requestconfirm_response = copy.deepcopy(REQUESTCONFIRM_OK)
    if not has_superapp_voice_promo:
        yataxi_client.requestconfirm_response.pop('superapp_voice_promo')

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
    assert 'phone_options' in response.json()
    if has_superapp_voice_promo:
        assert 'superapp_voice_promo' in response.json()
    else:
        assert 'superapp_voice_promo' not in response.json()

    rh.check_update_status_for_driver(redis_store, park_id, driver_id)
    rh.check_order_setcar_items(redis_store, park_id, order_id)
    rh.check_setcar_driver_reserv(redis_store, park_id, driver_id, order_id)

    coh_request_args = await contractor_order_history.update.wait_call()
    request = coh_request_args['self'].json
    order_fields = {
        item['name']: item['value'] for item in request['order_fields']
    }
    assert order_fields['agg_id'] == agg_id
    if has_aggregator:
        assert order_fields['agg_name'] == 'some_agg_name'
    else:
        assert 'agg_name' not in order_fields


@pytest.mark.parametrize(
    'driver_id,params,data,code',
    [
        (
            'driver_id_0',
            {'session': 'test_session', 'park_id': 'park_id_0'},
            'provider=2&order=order_id_0&'
            'date=2020-04-14T16%3A02%3A02.0000000&status='
            + str(rch.STATUS_VALUES['transporting']),
            200,
        ),
    ],
)
@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {'feature_support': {'feature_pay_type_show': '8.80'}},
    },
)
@pytest.mark.parametrize(
    'hide_statuses', [([]), (['transporting']), (['driving'])],
)
@pytest.mark.parametrize(
    'api_schema', ['compatible', 'requestconfirm_status_v2'],
)
@pytest.mark.now('2020-03-20T11:22:33.123456Z')
async def test_handle_request_confirm_pay_type_show(
        taxi_driver_orders_app_api,
        taxi_config,
        driver_authorizer,
        fleet_parks,
        yataxi_client,
        load_json,
        redis_store,
        driver_id,
        params,
        data,
        code,
        mocked_time,
        hide_statuses,
        api_schema,
):
    taxi_config.set_values(
        {'SETCAR_REMOVE_PAY_TYPE_FOR_CLIENT': hide_statuses},
    )
    park_id = params['park_id']
    data_dict = {kv.split('=')[0]: kv.split('=')[1] for kv in data.split('&')}
    order_id = data_dict['order']
    status = data_dict.get('status')
    app_family = auth.get_app_family(auth.USER_AGENT_TAXIMETER)
    driver_authorizer.set_client_session(
        app_family, park_id, params['session'], driver_id,
    )
    yataxi_client.taximeter_version = auth.USER_AGENT_TAXIMETER
    fleet_parks.parks = {'parks': [load_json('parks.json')[0]]}
    setcar = load_json('full_setcar.json')
    setcar['id'] = order_id
    rh.set_redis_for_order_cancelling(
        redis_store, park_id, order_id, driver_id, setcar_item=setcar,
    )
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
    if 'transporting' in hide_statuses:
        assert 'pay_type' not in response.json()
    else:
        assert response.json()['pay_type'] == 0


@pytest.mark.parametrize(
    'api_schema', ['compatible', 'requestconfirm_status_v2'],
)
async def test_handle_request_confirm_delivery_batching(
        taxi_driver_orders_app_api,
        taxi_config,
        driver_authorizer,
        fleet_parks,
        yataxi_client,
        load_json,
        redis_store,
        stq,
        api_schema,
):
    batching_order_id = 'aaaffff4444eeee1222'

    params = {'session': 'test_session', 'park_id': 'park_id_0'}
    driver_id = 'driver_id_0'
    data = (
        f'provider=2&order=order_id_0&date=2020-04-14T16%3A02%3A02.0000000&'
        + f'status={rch.STATUS_VALUES["transporting"]}'
    )

    park_id = params['park_id']
    data_dict = {kv.split('=')[0]: kv.split('=')[1] for kv in data.split('&')}
    order_id = data_dict['order']
    status = data_dict.get('status')

    app_family = auth.get_app_family(auth.USER_AGENT_TAXIMETER)
    driver_authorizer.set_client_session(
        app_family, park_id, params['session'], driver_id,
    )
    yataxi_client.taximeter_version = auth.USER_AGENT_TAXIMETER
    fleet_parks.parks = {'parks': [load_json('parks.json')[0]]}
    setcar = load_json('full_setcar.json')
    setcar['id'] = order_id
    setcar['batching_info'] = {'delayed_order_id': batching_order_id}
    rh.set_redis_for_order_cancelling(
        redis_store, park_id, order_id, driver_id, setcar_item=setcar,
    )

    url = rch.get_requestconfirm_url(api_schema, status)
    headers = rch.get_headers(auth.USER_AGENT_TAXIMETER, park_id, driver_id)
    data = rch.process_data(api_schema, data_dict, data)
    await taxi_driver_orders_app_api.post(
        url,
        headers={**rch.get_content_type(api_schema), **headers},
        data=data,
        params=params,
    )

    assert redis_store.smembers(
        'Order:Driver:Delayed:Items:park_id_0:driver_id_0',
    ) == {batching_order_id.encode()}
    assert stq.order_notify_combo_order_driving.times_called == 1
    stq_kwargs = stq.order_notify_combo_order_driving.next_call()['kwargs']
    stq_kwargs.pop('log_extra')
    assert stq_kwargs == {
        'outer_order_id': batching_order_id,
        'inner_order_id': order_id,
    }


@pytest.mark.parametrize(
    'api_schema', ['compatible', 'requestconfirm_status_v2'],
)
async def test_handle_request_confirm_combo_notifications(
        taxi_driver_orders_app_api,
        taxi_config,
        driver_authorizer,
        fleet_parks,
        yataxi_client,
        load_json,
        redis_store,
        stq,
        api_schema,
):
    params = {'session': 'test_session', 'park_id': 'park_id_0'}
    driver_id = 'driver_id_0'
    data = (
        f'provider=2&order=order_id_0&date=2020-04-14T16%3A02%3A02.0000000&'
        + f'status={rch.STATUS_VALUES["transporting"]}'
    )
    park_id = params['park_id']
    data_dict = {kv.split('=')[0]: kv.split('=')[1] for kv in data.split('&')}
    order_id = data_dict['order']
    status = data_dict.get('status')

    app_family = auth.get_app_family(auth.USER_AGENT_TAXIMETER)
    driver_authorizer.set_client_session(
        app_family, park_id, params['session'], driver_id,
    )
    yataxi_client.taximeter_version = auth.USER_AGENT_TAXIMETER
    fleet_parks.parks = {'parks': [load_json('parks.json')[0]]}
    setcar = load_json('full_setcar.json')
    setcar['id'] = order_id
    setcar['internal'] = {
        'order_id': 'inner',
        'combo': {
            'route': [
                {'order_id': 'outer', 'passed': False, 'type': 'start'},
                {'order_id': 'inner', 'passed': False, 'type': 'start'},
                {'order_id': 'outer', 'passed': False, 'type': 'finish'},
                {'order_id': 'inner', 'passed': False, 'type': 'finish'},
            ],
        },
    }
    rh.set_redis_for_order_cancelling(
        redis_store, park_id, order_id, driver_id, setcar_item=setcar,
    )
    url = rch.get_requestconfirm_url(api_schema, status)
    headers = rch.get_headers(auth.USER_AGENT_TAXIMETER, park_id, driver_id)
    data = rch.process_data(api_schema, data_dict, data)
    await taxi_driver_orders_app_api.post(
        url,
        headers={**rch.get_content_type(api_schema), **headers},
        data=data,
        params=params,
    )
    assert stq.order_notify_combo_order_driving.times_called == 1
    stq_kwargs = stq.order_notify_combo_order_driving.next_call()['kwargs']
    stq_kwargs.pop('log_extra')
    assert stq_kwargs == {
        'outer_order_id': '',
        'inner_order_id': '',
        'outer_taxi_order_id': 'outer',
        'inner_taxi_order_id': 'inner',
    }
