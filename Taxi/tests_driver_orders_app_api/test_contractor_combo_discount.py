import json
import urllib.parse
import uuid

import pytest

import tests_driver_orders_app_api.auth_helpers as auth
import tests_driver_orders_app_api.redis_helpers as rh
import tests_driver_orders_app_api.requestconfirm_helpers as rch

DEFAULT_PARK_ID = 'park_id_0'
DEFAULT_DRIVER_ID = 'driver_id_0'


@pytest.mark.now('2020-03-20T11:22:33.123456Z')
@pytest.mark.config(
    DRIVER_ORDERS_APP_API_CHECK_COMBO_ORDERS_DISCOUNT=True,
    DRIVER_ORDERS_APP_API_REDIS_LOCK_SETTINGS=rch.zero_retry_lock_settings(),
    TAXIMETER_FNS_SELF_EMPLOYMENT_SETTINGS=rch.self_employment_settings(),
    DRIVER_ORDERS_APP_API_PG_UPDATE_SETTINGS=rch.pg_update_settings(),
)
@pytest.mark.parametrize(
    'api_schema', ['compatible', 'requestconfirm_status_v2'],
)
@pytest.mark.parametrize(
    'complete_order, add_combo_order',
    [(True, True), (True, False), (False, True), (False, False)],
)
async def test_combo_orders_statuses(
        taxi_driver_orders_app_api,
        driver_authorizer,
        driver_profiles,
        fleet_parks,
        yataxi_client,
        load_json,
        load,
        taximeter_xservice,
        redis_store,
        api_schema,
        complete_order,
        add_combo_order,
):
    driver_id = DEFAULT_DRIVER_ID
    park_id = DEFAULT_PARK_ID
    params = {'session': 'test_session', 'park_id': park_id}
    user_agent = auth.USER_AGENT_TAXIMETER

    data = load('complete_req.txt').strip()
    if not complete_order:
        data = data.replace('status=7', 'status=2')
    data_dict = {kv.split('=')[0]: kv.split('=')[1] for kv in data.split('&')}

    order_id = data_dict['order']
    status = data_dict.get('status')
    app_family = auth.get_app_family(user_agent)
    driver_authorizer.set_client_session(
        app_family, park_id, params['session'], driver_id,
    )
    yataxi_client.taximeter_version = user_agent
    if complete_order:
        receipt_json = json.loads(urllib.parse.unquote(data_dict['receipt']))
        yataxi_client.receipt = receipt_json
        driver_receipt_json = json.loads(
            urllib.parse.unquote(data_dict['driver_calc_receipt_overrides']),
        )
        yataxi_client.driver_calc_receipt_overrides = driver_receipt_json
    yataxi_client.status_distance = float(data_dict.get('statusDistance'))
    driver_profiles.set_taximeter_version(user_agent)

    taximeter_xservice.set_response({'code': 200})
    rh.set_order_status(
        redis_store, park_id, order_id, rh.OrderStatus.Transporting,
    )
    park_json = load_json('parks.json')[0]
    fleet_parks.parks = {'parks': [park_json]}
    params['with_push'] = 'true'

    url = rch.get_requestconfirm_url(api_schema, status)
    headers = rch.get_headers(user_agent, park_id, driver_id)
    data = rch.process_data(api_schema, data_dict, data)

    setcar = load_json('complete_setcar.json')

    setcar['id'] = order_id
    setcar['internal'] = {'combo': {}}

    rh.set_redis_for_order_cancelling(
        redis_store, park_id, order_id, driver_id, setcar_item=setcar,
    )

    rh.set_setcar_xml(redis_store, park_id, order_id, load('setcar.xml'))

    expected_order_statuses = {
        order_id: {
            'is_outer_reason': False,
            'order_id': order_id,
            'status': 50 if complete_order else 10,  # complete or driving
            'end_transporting': 1584703353 if complete_order else None,
            'start_transporting': 1584703353 if complete_order else None,
        },
    }
    if add_combo_order:
        # another order in 'transporting' status prevents statuses cleanup
        combo_order_id = 'anothercomboorderid'
        combo_order_status = {
            'order_id': combo_order_id,
            'is_outer_reason': True,
            'status': 40,
            'start_transporting': 1584703353,
        }
        rh.add_combo_orders_status_item(
            redis_store, driver_id, combo_order_id, combo_order_status,
        )
        expected_order_statuses[combo_order_id] = combo_order_status
    if not add_combo_order and complete_order:
        # all complete - cleanup
        expected_order_statuses = dict()

    response = await taxi_driver_orders_app_api.post(
        url,
        headers={**rch.get_content_type(api_schema), **headers},
        data=data,
        params=params,
    )

    assert response.status_code == 200
    combo_orders_statuses = rh.get_combo_orders_status_items(
        redis_store, driver_id,
    )
    assert combo_orders_statuses == expected_order_statuses


@pytest.mark.now('2020-03-20T11:22:33.123456Z')
@pytest.mark.config(
    DRIVER_ORDERS_APP_API_CHECK_COMBO_ORDERS_DISCOUNT=True,
    DRIVER_ORDERS_APP_API_REDIS_LOCK_SETTINGS=rch.zero_retry_lock_settings(),
    TAXIMETER_FNS_SELF_EMPLOYMENT_SETTINGS=rch.self_employment_settings(),
    DRIVER_ORDERS_APP_API_PG_UPDATE_SETTINGS=rch.pg_update_settings(),
)
@pytest.mark.experiments3(filename='exp3_config_discard_combo_discount.json')
@pytest.mark.parametrize('add_combo_order', [True, False])
async def test_combo_orders_discount(
        taxi_driver_orders_app_api,
        mockserver,
        experiments3,
        driver_authorizer,
        driver_profiles,
        fleet_parks,
        yataxi_client,
        load_json,
        load,
        taximeter_xservice,
        redis_store,
        add_combo_order,
):
    api_schema = 'requestconfirm_status_v2'
    pricing_combo_match_flag = None

    @mockserver.json_handler('/pricing-taximeter/v1/save_order_details')
    def _mock_pricing_taximeter_save_order_details(request):
        nonlocal pricing_combo_match_flag
        pricing_combo_match_flag = request.json.get('combo_order_was_matched')
        return {
            'price': {
                'user': {'total': 200, 'meta': {}, 'extra': {}},
                'driver': {'total': 200, 'meta': {}, 'extra': {}},
            },
            'price_verifications': {
                'uuids': {'recalculated': str(uuid.uuid4())},
            },
        }

    driver_id = DEFAULT_DRIVER_ID
    park_id = DEFAULT_PARK_ID
    params = {'session': 'test_session', 'park_id': park_id}
    user_agent = auth.USER_AGENT_TAXIMETER

    price_calc_v2_data = load_json('price_calc_v2_data.json')
    price_calc_v2_data_str = '&price_calc_v2_data=' + urllib.parse.quote(
        json.dumps(price_calc_v2_data),
    )

    data = load('complete_req.txt').strip()
    data += price_calc_v2_data_str
    data_dict = {kv.split('=')[0]: kv.split('=')[1] for kv in data.split('&')}

    order_id = data_dict['order']
    status = data_dict.get('status')
    app_family = auth.get_app_family(user_agent)
    driver_authorizer.set_client_session(
        app_family, park_id, params['session'], driver_id,
    )
    yataxi_client.taximeter_version = user_agent
    receipt_json = json.loads(urllib.parse.unquote(data_dict['receipt']))
    yataxi_client.receipt = receipt_json
    driver_receipt_json = json.loads(
        urllib.parse.unquote(data_dict['driver_calc_receipt_overrides']),
    )
    driver_receipt_json['sum'] = 200
    driver_receipt_json['total'] = 200
    yataxi_client.driver_calc_receipt_overrides = driver_receipt_json
    yataxi_client.status_distance = float(data_dict.get('statusDistance'))
    yataxi_client.final_cost_meta = {'user': {}, 'driver': {}}
    driver_profiles.set_taximeter_version(user_agent)

    taximeter_xservice.set_response({'code': 200})
    rh.set_order_status(
        redis_store, park_id, order_id, rh.OrderStatus.Transporting,
    )
    park_json = load_json('parks.json')[0]
    fleet_parks.parks = {'parks': [park_json]}
    params['with_push'] = 'true'

    url = rch.get_requestconfirm_url(api_schema, status)
    headers = rch.get_headers(user_agent, park_id, driver_id)
    data = rch.process_data(api_schema, data_dict, data)

    setcar = load_json('complete_setcar.json')

    setcar['id'] = order_id
    setcar['internal'] = {'combo': {}}

    rh.set_redis_for_order_cancelling(
        redis_store, park_id, order_id, driver_id, setcar_item=setcar,
    )

    rh.set_setcar_xml(redis_store, park_id, order_id, load('setcar.xml'))

    if add_combo_order:
        # add another complete order
        combo_order_id = 'anothercomboorderid'
        combo_order_status = {
            'order_id': combo_order_id,
            'is_outer_reason': False,
            'status': 50,
        }
        rh.add_combo_orders_status_item(
            redis_store, driver_id, combo_order_id, combo_order_status,
        )

    response = await taxi_driver_orders_app_api.post(
        url,
        headers={**rch.get_content_type(api_schema), **headers},
        data=data,
        params=params,
    )

    assert response.status_code == 200
    combo_orders_statuses = rh.get_combo_orders_status_items(
        redis_store, driver_id,
    )
    # should be cleaned up
    assert not combo_orders_statuses
    assert pricing_combo_match_flag == add_combo_order


@pytest.mark.experiments3(filename='exp3_skip_chain_autocancel_event.json')
@pytest.mark.config(
    DRIVER_ORDERS_APP_API_CHECK_COMBO_ORDERS_DISCOUNT=True,
    DRIVER_ORDERS_APP_API_REDIS_LOCK_SETTINGS=rch.zero_retry_lock_settings(),
    DRIVER_ORDERS_APP_API_SKIP_CHAIN_EVENT_SETTINGS=100,
)
@pytest.mark.now('2020-03-20T11:22:33.123456Z')
async def test_driver_reject(
        taxi_driver_orders_app_api,
        driver_authorizer,
        fleet_parks,
        load_json,
        taximeter_xservice,
        yataxi_client,
        redis_store,
):
    api_schema = 'requestconfirm_status_v2'
    comment = 'reject'
    user_agent = auth.USER_AGENT_TAXIMETER
    driver_id = DEFAULT_DRIVER_ID
    params = {'session': 'test_session', 'park_id': DEFAULT_PARK_ID}
    data = (
        'order=order_id_0&status=9&statusDistance=20.20&'
        'is_offline=false&is_captcha=true&is_fallback=false&'
        'is_airplanemode=true&driver_status=rejected'
    )

    provider = 1
    data += '&provider={}'.format(provider)
    data += '&comment={}'.format(comment)

    data_dict = {kv.split('=')[0]: kv.split('=')[1] for kv in data.split('&')}
    park_id = DEFAULT_PARK_ID
    order_id = data_dict['order']
    status = data_dict.get('status')
    app_family = auth.get_app_family(user_agent)
    driver_authorizer.set_client_session(
        app_family, park_id, params['session'], driver_id,
    )
    yataxi_client.taximeter_version = user_agent

    with_push = False
    taximeter_xservice.set_response({'code': 200})
    rh.set_order_status(
        redis_store, park_id, order_id, rh.OrderStatus.Transporting,
    )
    setcar_item = load_json('full_setcar.json')
    setcar_item['provider'] = provider
    setcar_item['id'] = order_id
    setcar_item['internal'] = {'combo': {}}
    rh.set_redis_for_order_cancelling(
        redis_store, park_id, order_id, driver_id, setcar_item=setcar_item,
    )
    fleet_parks.parks = {'parks': [load_json('parks.json')[0]]}
    params['with_push'] = with_push

    yataxi_client.status_distance = float(data_dict.get('statusDistance'))

    # add another combo order in `transporting` to prevent cleanup
    combo_order_id = 'anothercomboorderid'
    combo_order_status = {
        'order_id': combo_order_id,
        'is_outer_reason': False,
        'status': 40,
    }
    rh.add_combo_orders_status_item(
        redis_store, driver_id, combo_order_id, combo_order_status,
    )

    url = rch.get_reject_url(api_schema, status)
    headers = rch.get_headers(user_agent, park_id, driver_id)
    data = rch.process_data(api_schema, data_dict, data)
    response = await taxi_driver_orders_app_api.post(
        url,
        headers={**rch.get_content_type(api_schema), **headers},
        data=data,
        params=params,
    )

    assert response.status_code == 200

    combo_orders_statuses = rh.get_combo_orders_status_items(
        redis_store, driver_id,
    )
    assert combo_orders_statuses[order_id]['is_outer_reason'] is False


@pytest.mark.now('2020-03-20T11:22:33.123456Z')
@pytest.mark.config(
    DRIVER_ORDERS_APP_API_CHECK_COMBO_ORDERS_DISCOUNT=True,
    DRIVER_ORDERS_APP_API_REDIS_LOCK_SETTINGS=rch.zero_retry_lock_settings(),
    TAXIMETER_FNS_SELF_EMPLOYMENT_SETTINGS=rch.self_employment_settings(),
    DRIVER_ORDERS_APP_API_PG_UPDATE_SETTINGS=rch.pg_update_settings(),
)
@pytest.mark.parametrize(
    'api_schema', ['compatible', 'requestconfirm_status_v2'],
)
async def test_second_transporting_status(
        taxi_driver_orders_app_api,
        driver_authorizer,
        driver_profiles,
        fleet_parks,
        yataxi_client,
        load_json,
        load,
        taximeter_xservice,
        redis_store,
        api_schema,
):
    # check if second transporting requestconfirm do not erases
    # start_transporting in redis
    driver_id = DEFAULT_DRIVER_ID
    park_id = DEFAULT_PARK_ID
    params = {'session': 'test_session', 'park_id': park_id}
    user_agent = auth.USER_AGENT_TAXIMETER

    data = load('complete_req.txt').strip().replace('status=7', 'status=5')
    data_dict = {kv.split('=')[0]: kv.split('=')[1] for kv in data.split('&')}

    order_id = data_dict['order']
    status = data_dict.get('status')
    app_family = auth.get_app_family(user_agent)
    driver_authorizer.set_client_session(
        app_family, park_id, params['session'], driver_id,
    )
    yataxi_client.taximeter_version = user_agent
    yataxi_client.status_distance = float(data_dict.get('statusDistance'))
    driver_profiles.set_taximeter_version(user_agent)

    taximeter_xservice.set_response({'code': 200})
    rh.set_order_status(
        redis_store, park_id, order_id, rh.OrderStatus.Transporting,
    )
    park_json = load_json('parks.json')[0]
    fleet_parks.parks = {'parks': [park_json]}
    params['with_push'] = 'true'

    url = rch.get_requestconfirm_url(api_schema, status)
    headers = rch.get_headers(user_agent, park_id, driver_id)
    data = rch.process_data(api_schema, data_dict, data)

    setcar = load_json('complete_setcar.json')

    setcar['id'] = order_id
    setcar['internal'] = {'combo': {}}

    rh.set_redis_for_order_cancelling(
        redis_store, park_id, order_id, driver_id, setcar_item=setcar,
    )

    rh.set_setcar_xml(redis_store, park_id, order_id, load('setcar.xml'))

    now_ts = 1584703293
    start_transporting_ts = now_ts - 60
    combo_order_status = {
        'order_id': order_id,
        'is_outer_reason': True,
        'status': 40,
        'start_transporting': start_transporting_ts,  # not now
    }
    rh.add_combo_orders_status_item(
        redis_store, driver_id, order_id, combo_order_status,
    )

    response = await taxi_driver_orders_app_api.post(
        url,
        headers={**rch.get_content_type(api_schema), **headers},
        data=data,
        params=params,
    )

    assert response.status_code == 200
    combo_orders_statuses = rh.get_combo_orders_status_items(
        redis_store, driver_id,
    )
    assert (
        combo_orders_statuses[order_id]['start_transporting']
        == start_transporting_ts
    )
