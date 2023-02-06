import datetime

import pytest

import tests_driver_orders_app_api.auth_helpers as auth
import tests_driver_orders_app_api.redis_helpers as rh
import tests_driver_orders_app_api.requestconfirm_helpers as rch

EXISTING_PARK_ID = 'park_id_0'

CONTENT_HEADER = {'Content-Type': 'application/x-www-form-urlencoded'}

MULTIOFFER_BLOCK = {
    'id': 'multioffer-id',
    'is_accepted': True,
    'start_date': '2020-03-20T11:22:33.123456Z',
    'timeout': 0,
    'play_timeout': 0,
}


@pytest.mark.parametrize(
    'driver_id,params,data,code',
    [
        (
            'driver_id_0',
            {'session': 'test_session', 'park_id': EXISTING_PARK_ID},
            'provider=2&order=order_id_0&'
            'date=2020-04-14T16%3A02%3A02.0000000&status=2',
            200,
        ),
    ],
)
@pytest.mark.config(
    DRIVER_ORDERS_APP_API_REDIS_LOCK_SETTINGS=rch.zero_retry_lock_settings(),
    DRIVER_ORDERS_APP_API_DRIVER_MODE_SETTINGS={
        'setcar_percent': 100,
        'enable_compare': False,
    },
)
@pytest.mark.now('2020-03-20T11:22:33.123456Z')
@pytest.mark.parametrize('has_setcar_xml', [True, False])
@pytest.mark.parametrize(
    'setcar_on_requestconfirm_event_enabled', [True, False],
)
@pytest.mark.parametrize(
    'api_schema', ['compatible', 'requestconfirm_status_v2'],
)
@pytest.mark.parametrize(
    'redis_status,config_code',
    [
        (rh.OrderStatus.Complete, 200),
        (rh.OrderStatus.Expired, 404),
        (None, 200),
    ],
)
@pytest.mark.parametrize('is_multioffer', [True, False])
async def test_handle_request_confirm_driving(
        taxi_driver_orders_app_api,
        driver_authorizer,
        fleet_parks,
        yataxi_client,
        stq,
        load,
        load_json,
        redis_store,
        has_setcar_xml,
        setcar_on_requestconfirm_event_enabled,
        driver_id,
        params,
        data,
        code,
        api_schema,
        redis_status,
        config_code,
        experiments3,
        is_multioffer,
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
    if params['park_id'] == EXISTING_PARK_ID:
        park = load_json('parks.json')[0]
        if setcar_on_requestconfirm_event_enabled:
            events = park['integration_events'][:]
            events.append('setcar_on_requestconfirm')
            park['integration_events'] = events
        fleet_parks.parks = {'parks': [park]}

    setcar = load_json('full_setcar.json')

    setcar['id'] = order_id
    if is_multioffer:
        setcar['multioffer'] = MULTIOFFER_BLOCK

    rh.set_redis_for_order_cancelling(
        redis_store, park_id, order_id, driver_id, setcar_item=setcar,
    )

    if has_setcar_xml:
        rh.set_setcar_xml(redis_store, park_id, order_id, load('setcar.xml'))
    else:
        rh.delete_setcar_xml(redis_store, park_id, order_id)

    if redis_status is not None:
        exp_json = load_json('exp3_terminal_status_config.json')
        exp_json['configs'][0]['default_value']['return_code'] = str(
            config_code,
        )
        experiments3.add_experiments_json(exp_json)
        rh.set_order_status(redis_store, park_id, order_id, redis_status)
    url = rch.get_requestconfirm_url(api_schema, status)
    headers = rch.get_headers(auth.USER_AGENT_TAXIMETER, park_id, driver_id)
    data = rch.process_data(api_schema, data_dict, data)
    response = await taxi_driver_orders_app_api.post(
        url,
        headers={**rch.get_content_type(api_schema), **headers},
        data=data,
        params=params,
    )

    assert_code = config_code if redis_status is not None else code
    assert response.status_code == assert_code
    if redis_status is not None:
        return
    assert rh.get_event_queue_size(redis_store) == 1
    assert stq.driver_orders_integrator_requestconfirm.times_called == 1

    kwargs = stq.driver_orders_integrator_requestconfirm.next_call()['kwargs']
    kwargs.pop('log_extra')
    assert kwargs == {
        'change_date': {'$date': '2020-04-14T16:02:02.000Z'},
        'comment': '',
        'driver_id': 'driver_id_0',
        'order_id': 'order_id_0',
        'park_id': 'park_id_0',
        'status': 2,
        'total_cost': 0.0,
    }

    need_call_setcar_xml = int(
        has_setcar_xml and setcar_on_requestconfirm_event_enabled,
    )
    assert (
        stq.driver_orders_integrator_setcar_xml.times_called
        == need_call_setcar_xml
    )


@pytest.mark.parametrize('missing_park', [True, False])
async def test_driver_orders_integrator_requestconfirm(
        stq_runner, fleet_parks, driver_trackstory, load_json, missing_park,
):
    park_id = 'dummy_park' if missing_park else EXISTING_PARK_ID
    if park_id == EXISTING_PARK_ID:
        park = load_json('parks.json')[0]
        fleet_parks.parks = {'parks': [park]}
    await stq_runner.driver_orders_integrator_requestconfirm.call(
        task_id='task-id',
        kwargs={
            'park_id': park_id,
            'driver_id': 'dummy_driver',
            'order_id': 'dummy_order',
            'status': 2,
            'comment': '123',
            'total_cost': 456,
            'change_date': datetime.datetime.now(),
        },
        expect_fail=missing_park,
    )


@pytest.mark.parametrize('missing_park', [True, False])
async def test_driver_orders_integrator_setcar_xml(
        stq_runner, fleet_parks, redis_store, load_json, load, missing_park,
):
    park_id = 'dummy_park' if missing_park else EXISTING_PARK_ID
    order_id = 'dummy_order'
    if park_id == EXISTING_PARK_ID:
        park = load_json('parks.json')[0]
        fleet_parks.parks = {'parks': [park]}

    rh.set_setcar_xml(redis_store, park_id, order_id, load('setcar.xml'))
    await stq_runner.driver_orders_integrator_setcar_xml.call(
        task_id='task-id',
        kwargs={
            'park_id': park_id,
            'driver_id': 'dummy_driver',
            'order_id': order_id,
            'setcar_xml': '<xml></xml>',
        },
        expect_fail=missing_park,
    )

    assert rh.exists_setcar_xml(redis_store, park_id, order_id) == missing_park
