import json
import urllib

import pytest

import tests_driver_orders_app_api.auth_helpers as auth
import tests_driver_orders_app_api.redis_helpers as rh
import tests_driver_orders_app_api.requestconfirm_helpers as rch

SOME_DATE = '2019-05-01T16:18:00.000000Z'
DEFAULT_PARK_ID = 'park_id_0'
DEFAULT_DRIVER_ID = 'driver_id_0'
CONTENT_HEADER_FORM = {'Content-Type': 'application/x-www-form-urlencoded'}

CUSTOM_DETAILS = [
    {
        'meter_type': 'distance',
        'meter_value': 31208.336816545561,
        'per': 1000.0,
        'price': 9.0,
        'service_type': 'free_route',
        'sum': 280.87503134891006,
        'zone_names': ['moscow'],
    },
    {
        'meter_type': 'time',
        'meter_value': 1703.0,
        'per': 60.0,
        'price': 8.1,
        'service_type': 'free_route',
        'sum': 229.905,
        'zone_names': ['moscow'],
    },
    {
        'count': 1,
        'name': 'door_to_door',
        'price': 150.0,
        'service_type': 'service',
        'sum': 150.0,
    },
]


@pytest.mark.parametrize(
    'exp3_json_file_name, match_enabled',
    [
        ('exp3_use_contractor_order_setcar_false.json', False),
        ('exp3_use_contractor_order_setcar_true.json', True),
    ],
)
@pytest.mark.parametrize(
    'driver_id,params,data_filename,code,output',
    [
        (
            DEFAULT_DRIVER_ID,
            {'session': 'test_session', 'park_id': DEFAULT_PARK_ID},
            'complete_req.txt',
            200,
            {'status': 7},
        ),
    ],
)
@pytest.mark.parametrize('has_setcar', [True, False])
@pytest.mark.parametrize('self_employed', [True, False])
@pytest.mark.parametrize(
    'self_employed_check_skipped',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                TAXIMETER_FNS_SELF_EMPLOYMENT_SETTINGS=rch.self_employment_settings(  # noqa: E501
                    skip_driver_partner_source_check=True,
                ),
            ),
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                TAXIMETER_FNS_SELF_EMPLOYMENT_SETTINGS=rch.self_employment_settings(  # noqa: E501
                    skip_driver_partner_source_check=False,
                ),
            ),
        ),
    ],
)
@pytest.mark.parametrize('is_agent_corp', [True, False])
@pytest.mark.parametrize('custom_details', [None, CUSTOM_DETAILS])
@pytest.mark.parametrize('taximeter_cost', [None, 1234.0])
@pytest.mark.parametrize(
    'cargo_pricing_receipt, cargo_expected_receipt_data',
    [
        (None, None),
        (
            {'total': 10020.0, 'total_distance': 10030.0},
            {'sum': 10020.0, 'total': 10020.0, 'total_distance': 10030.0},
        ),
        (
            {
                'total': 10020.0,
                'total_distance': 10030.0,
                'waiting': {'sum': 107.0, 'time': 18.0, 'cost': 19.0},
                'waiting_in_transit': {
                    'sum': 104.0,
                    'time': 15.0,
                    'cost': 16.0,
                },
                'services': [
                    {
                        'name': 'door_to_door',
                        'count': 3,
                        'sum': 150.0,
                        'price': 450.0,
                    },
                ],
            },
            {
                'sum': 10020.0,
                'total': 10020.0,
                'total_distance': 10030.0,
                'waiting_in_transit_sum': 104.0,
                'waiting_in_transit_time': 15.0,
                'waiting_in_transit_cost': 16.0,
                'waiting_sum': 107.0,
                'waiting_time': 18.0,
                'waiting_cost': 19.0,
                'services_count': {
                    'door_to_door': {'count': 3, 'sum': 150.0, 'price': 450.0},
                },
            },
        ),
    ],
)
@pytest.mark.now('2020-03-20T11:22:33.123456Z')
@pytest.mark.config(
    DRIVER_ORDERS_APP_API_SKIP_YANDEX_ORDERS_FOR_XCALC=True,
    DRIVER_ORDERS_APP_API_REDIS_LOCK_SETTINGS=rch.zero_retry_lock_settings(),
    DRIVER_ORDERS_APP_API_PG_UPDATE_SETTINGS=rch.pg_update_settings(),
)
@pytest.mark.parametrize(
    'api_schema,extra_options',
    [
        ('compatible', None),
        ('requestconfirm_status_v2', None),
        ('internal_order_status_v1', None),
        ('internal_order_status_v1', {'should_notify': True}),
        ('internal_order_status_v1', {'has_dispatch_login': True}),
        (
            'internal_order_status_v1',
            {
                'has_dispatch_login': True,
                'dispatch_selected_price': 'fixed',
                'need_manual_accept': True,
            },
        ),
    ],
    ids=[
        'compatible',
        'requestconfirm_status_v2',
        'internal_order_status_v1',
        'internal_order_status_v1_with_notify',
        'internal_order_status_v1_with_dispatcher_login',
        'internal_order_status_v1_dispatch_selected_price',
    ],
)
async def test_handle_requestconfirm_complete(
        taxi_driver_orders_app_api,
        driver_authorizer,
        driver_profiles,
        driver_orders,
        fleet_parks,
        load_json,
        load,
        taximeter_xservice,
        yataxi_client,
        fleet_parks_shard,
        redis_store,
        stq,
        has_setcar,
        self_employed,
        self_employed_check_skipped,
        is_agent_corp,
        custom_details,
        driver_id,
        params,
        data_filename,
        code,
        output,
        mocked_time,
        api_schema,
        taximeter_cost,
        cargo_pricing_receipt,
        cargo_expected_receipt_data,
        contractor_order_history,
        extra_options,
        exp3_json_file_name,
        experiments3,
        match_enabled,
        contractor_order_setcar,
):
    experiments3.add_experiments_json(load_json(exp3_json_file_name))
    await taxi_driver_orders_app_api.invalidate_caches()

    user_agent = (
        auth.USER_AGENT_TAXIMETER
        if driver_id == 'driver_id_0'
        else auth.USER_AGENT_UBER
    )
    data = load(data_filename).strip()
    park_id = params['park_id']
    data_dict = {kv.split('=')[0]: kv.split('=')[1] for kv in data.split('&')}
    order_id = data_dict['order']
    total_distance = float(data_dict.get('total_distance'))
    sum_field = float(data_dict.get('sum'))
    total = float(data_dict.get('total'))
    receipt_data = {
        'total_distance': total_distance,
        'sum': sum_field,
        'total': total,
    }
    cost_total = total
    if cargo_pricing_receipt is not None:
        total = cargo_pricing_receipt['total']
        cost_total = total
        sum_field = total
        receipt_data = cargo_expected_receipt_data
    elif taximeter_cost is not None:
        cost_total = taximeter_cost
    yataxi_client.final_cost = {'driver': cost_total, 'user': sum_field}
    status = data_dict.get('status')
    app_family = auth.get_app_family(user_agent)
    driver_authorizer.set_client_session(
        app_family, park_id, params['session'], driver_id,
    )
    yataxi_client.taximeter_version = user_agent
    driver_profiles.set_taximeter_version(user_agent)

    taximeter_xservice.set_response({'code': 200})
    rh.set_order_status(
        redis_store, park_id, order_id, rh.OrderStatus.Transporting,
    )
    setcar = load_json('complete_setcar.json')
    if is_agent_corp:
        setcar.update({'agent': {'is_corp': True}})
    if has_setcar:
        rh.set_redis_for_order_cancelling(
            redis_store, park_id, order_id, driver_id, setcar_item=setcar,
        )
    if params['park_id'] == 'park_id_0':
        park_json = load_json('parks.json')[0]
        if self_employed:
            park_json['driver_partner_source'] = 'selfemployed_fns'
        fleet_parks.parks = {'parks': [park_json]}
    params['with_push'] = 'true'

    def _get_receipt(name):
        result = data_dict.get(name)
        if not result:
            return None
        return json.loads(urllib.parse.unquote(result))

    receipt = _get_receipt('receipt')
    if custom_details:
        receipt['details'] = custom_details
        data_dict['receipt'] = urllib.parse.quote(json.dumps(receipt))
        data = '&'.join(['{}={}'.format(k, v) for k, v in data_dict.items()])
    if api_schema != 'internal_order_status_v1':
        yataxi_client.receipt = receipt
        yataxi_client.driver_calc_receipt_overrides = _get_receipt(
            'driver_calc_receipt_overrides',
        )
        yataxi_client.status_distance = float(data_dict.get('statusDistance'))
        yataxi_client.taximeter_cost = taximeter_cost
        yataxi_client.cargo_pricing_receipt = cargo_pricing_receipt

    url = rch.get_requestconfirm_url(api_schema, status)
    headers = rch.get_headers(user_agent, park_id, driver_id)
    data = rch.process_data(api_schema, data_dict, data)
    if api_schema == 'internal_order_status_v1':
        sum_field = cost_total
        new_data = {
            'origin': 'yandex_dispatch',
            'park_id': park_id,
            'driver_profile_id': driver_id,
            'setcar_id': order_id,
            'should_notify': False,
        }
        if extra_options:
            if extra_options.get('has_dispatch_login'):
                headers['X-Yandex-Login'] = 'dispatch_login'
            if extra_options.get('should_notify'):
                new_data['should_notify'] = True
            if extra_options.get('dispatch_selected_price'):
                value = extra_options.get('dispatch_selected_price')
                new_data['dispatch_selected_price'] = value
                yataxi_client.dispatch_selected_price = value
            if extra_options.get('need_manual_accept') is not None:
                value = extra_options.get('need_manual_accept')
                new_data['need_manual_accept'] = value
                yataxi_client.need_manual_accept = value

        data = json.dumps(new_data)
        yataxi_client.current_cost = cost_total
        driver_orders.park_id = park_id
        driver_orders.order_id = order_id
        driver_orders.driver_id = driver_id
        driver_orders.provider = 2
        driver_orders.status = 40
        driver_orders.category = 1
        driver_orders.cost_pay = str(cost_total)
        driver_orders.cost_sub = str(cost_total)
        driver_orders.cost_total = str(cost_total)

    response = await taxi_driver_orders_app_api.post(
        url,
        headers={**rch.get_content_type(api_schema), **headers},
        data=data,
        params=params,
    )

    should_notify = bool(extra_options and extra_options.get('should_notify'))
    assert (
        stq.driver_orders_send_communications_notifications.has_calls
        == should_notify
    )
    if match_enabled and response.status_code == 200:
        assert contractor_order_setcar.complete_handler.has_calls
    elif not match_enabled:
        assert not contractor_order_setcar.complete_handler.has_calls

    assert stq.driver_orders_xservice_calcservice.times_called == int(
        not has_setcar and api_schema != 'internal_order_status_v1',
    )

    if stq.driver_orders_xservice_calcservice.has_calls:
        kwargs = stq.driver_orders_xservice_calcservice.next_call()['kwargs']
        kwargs.pop('log_extra')
        user_login = (
            'dispatch_login'
            if (extra_options and extra_options.get('has_dispatch_login'))
            else ''  # empty user
        )
        assert kwargs == {
            'operation_type': 'start',
            'park_id': park_id,
            'driver_id': driver_id,
            'order_id': order_id,
            'cost_total': float(data_dict.get('total')),  # cost total
            'sum': float(data_dict.get('sum')),  # cost pay
            'user': user_login,
        }

    if has_setcar:
        coh_request_args = await contractor_order_history.update.wait_call()
        request = coh_request_args['self'].json
        order_fields = {
            item['name']: item['value'] for item in request['order_fields']
        }

        assert order_fields['status'] == str(rh.OrderStatus.Complete.value)
        if api_schema != 'internal_order_status_v1':
            receipt_data_requested = json.loads(order_fields['receipt_data'])
            if cargo_pricing_receipt:
                assert receipt_data_requested == receipt_data
            elif not custom_details:
                assert receipt_data_requested == receipt_data
            else:
                assert receipt_data_requested == {
                    'services': {'door_to_door': 150.0},
                    'services_count': {
                        'door_to_door': {
                            'count': 1,
                            'sum': 150.0,
                            'price': 150.0,
                        },
                    },
                    'sum': sum_field,
                    'total': total,
                    'total_distance': total_distance,
                }
        else:
            assert yataxi_client.current_cost_called == 0

    assert response.status_code == code
    if api_schema == 'internal_order_status_v1':
        assert response.json()['status'] == 'complete'
        assert response.json()['cost'] == cost_total


@pytest.mark.redis_store(
    [
        'sadd',
        f'Order:Driver:Delayed:Items:{DEFAULT_PARK_ID}:{DEFAULT_DRIVER_ID}',
        'delayed_order_id',
    ],
)
@pytest.mark.parametrize(
    'driver_id,params,data_filename,code,output',
    [
        (
            DEFAULT_DRIVER_ID,
            {'session': 'test_session', 'park_id': DEFAULT_PARK_ID},
            'complete_req.txt',
            200,
            {'status': 7},
        ),
    ],
)
@pytest.mark.now('2020-03-20T11:22:33.123456Z')
@pytest.mark.config(
    DRIVER_ORDERS_APP_API_SKIP_YANDEX_ORDERS_FOR_XCALC=True,
    DRIVER_ORDERS_APP_API_REDIS_LOCK_SETTINGS=rch.zero_retry_lock_settings(),
    TAXIMETER_FNS_SELF_EMPLOYMENT_SETTINGS=rch.self_employment_settings(),
    DRIVER_ORDERS_APP_API_PG_UPDATE_SETTINGS=rch.pg_update_settings(),
)
@pytest.mark.parametrize(
    'api_schema',
    ['compatible', 'requestconfirm_status_v2', 'internal_order_status_v1'],
)
async def test_handle_requestconfirm_complete_delayed_order(
        taxi_driver_orders_app_api,
        driver_authorizer,
        driver_profiles,
        driver_orders,
        fleet_parks,
        load_json,
        load,
        taximeter_xservice,
        yataxi_client,
        fleet_parks_shard,
        redis_store,
        stq,
        driver_id,
        params,
        data_filename,
        code,
        output,
        mocked_time,
        api_schema,
        contractor_order_history,
):
    user_agent = (
        auth.USER_AGENT_TAXIMETER
        if driver_id == 'driver_id_0'
        else auth.USER_AGENT_UBER
    )
    data = load(data_filename).strip()
    park_id = params['park_id']
    data_dict = {kv.split('=')[0]: kv.split('=')[1] for kv in data.split('&')}
    order_id = data_dict['order']
    sum_field = float(data_dict.get('sum'))
    total = float(data_dict.get('total'))
    cost_total = total
    status = data_dict.get('status')
    app_family = auth.get_app_family(user_agent)
    driver_authorizer.set_client_session(
        app_family, park_id, params['session'], driver_id,
    )
    yataxi_client.taximeter_version = user_agent
    driver_profiles.set_taximeter_version(user_agent)
    yataxi_client.final_cost = {'driver': cost_total, 'user': sum_field}

    taximeter_xservice.set_response({'code': 200})
    rh.set_order_status(
        redis_store, park_id, order_id, rh.OrderStatus.Transporting,
    )
    setcar = load_json('complete_setcar.json')
    rh.set_redis_for_order_cancelling(
        redis_store, park_id, order_id, driver_id, setcar_item=setcar,
    )
    if params['park_id'] == 'park_id_0':
        park_json = load_json('parks.json')[0]
        fleet_parks.parks = {'parks': [park_json]}
    params['with_push'] = 'true'

    def _get_receipt(name):
        result = data_dict.get(name)
        if not result:
            return None
        return json.loads(urllib.parse.unquote(result))

    receipt = _get_receipt('receipt')
    if api_schema != 'internal_order_status_v1':
        yataxi_client.receipt = receipt
        yataxi_client.driver_calc_receipt_overrides = _get_receipt(
            'driver_calc_receipt_overrides',
        )
        yataxi_client.status_distance = float(data_dict.get('statusDistance'))

    url = rch.get_requestconfirm_url(api_schema, status)
    headers = rch.get_headers(user_agent, park_id, driver_id)
    data = rch.process_data(api_schema, data_dict, data)
    if api_schema == 'internal_order_status_v1':
        headers['X-Yandex-Login'] = 'user_login'
        sum_field = cost_total
        new_data = {
            'origin': 'yandex_dispatch',
            'park_id': park_id,
            'driver_profile_id': driver_id,
            'setcar_id': order_id,
        }
        data = json.dumps(new_data)
        yataxi_client.current_cost = cost_total
        driver_orders.park_id = park_id
        driver_orders.order_id = order_id
        driver_orders.driver_id = driver_id
        driver_orders.provider = 2
        driver_orders.status = 40
        driver_orders.category = 1
        driver_orders.cost_pay = str(cost_total)
        driver_orders.cost_sub = str(cost_total)
        driver_orders.cost_total = str(cost_total)

    response = await taxi_driver_orders_app_api.post(
        url,
        headers={**rch.get_content_type(api_schema), **headers},
        data=data,
        params=params,
    )

    assert stq.driver_orders_xservice_calcservice.times_called == 0

    coh_request_args = await contractor_order_history.update.wait_call()
    request = coh_request_args['self'].json
    order_fields = {
        item['name']: item['value'] for item in request['order_fields']
    }
    assert order_fields['status'] == str(rh.OrderStatus.Complete.value)

    assert response.status_code == code
    if api_schema == 'internal_order_status_v1':
        assert response.json()['status'] == 'complete'
        assert response.json()['cost'] == cost_total

    assert (
        redis_store.smembers(
            f'Order:Driver:Delayed:Items:'
            f'{DEFAULT_PARK_ID}:{DEFAULT_DRIVER_ID}',
        )
        == set()
    )


@pytest.mark.parametrize('operation', ['start', 'remove'])
async def test_stq_driver_orders_xservice_calcservice(
        stq_runner, fleet_parks, taximeter_xservice, operation, load_json,
):
    order_id = 'dummy_order'
    park = load_json('parks.json')[0]
    fleet_parks.parks = {'parks': [park]}

    await stq_runner.driver_orders_xservice_calcservice.call(
        task_id='task-id',
        args=[
            operation,
            DEFAULT_PARK_ID,
            DEFAULT_DRIVER_ID,
            order_id,
            200.0,  # cost total
            200.0,  # cost pay
            '',  # empty user
        ],
        expect_fail=False,
    )

    called = (
        taximeter_xservice.called_start
        if operation == 'start'
        else taximeter_xservice.called_remove
    )
    assert called == 1


@pytest.mark.parametrize(
    'driver_id,params,data_filename,code',
    [
        (
            DEFAULT_DRIVER_ID,
            {'session': 'test_session', 'park_id': DEFAULT_PARK_ID},
            'complete_req.txt',
            400,
        ),
    ],
)
@pytest.mark.config(
    DRIVER_ORDERS_APP_API_REDIS_LOCK_SETTINGS=rch.zero_retry_lock_settings(),
)
@pytest.mark.parametrize(
    'receipt_field', ['receipt', 'driver_calc_receipt_overrides'],
)
@pytest.mark.parametrize('api_schema', ['compatible'])
async def test_handle_requestconfirm_complete_invalid_receipt(
        taxi_driver_orders_app_api,
        driver_authorizer,
        fleet_parks,
        yataxi_client,
        load_json,
        load,
        fleet_parks_shard,
        redis_store,
        driver_id,
        params,
        data_filename,
        code,
        receipt_field,
        api_schema,
):
    user_agent = (
        auth.USER_AGENT_TAXIMETER
        if driver_id == 'driver_id_0'
        else auth.USER_AGENT_UBER
    )
    data = load(data_filename).strip()
    data = data.replace(
        '&{}='.format(receipt_field), '&{}=%22'.format(receipt_field),
    )
    park_id = params['park_id']
    data_dict = {kv.split('=')[0]: kv.split('=')[1] for kv in data.split('&')}
    order_id = data_dict['order']
    status = data_dict.get('status')
    app_family = auth.get_app_family(user_agent)
    driver_authorizer.set_client_session(
        app_family, park_id, params['session'], driver_id,
    )
    yataxi_client.taximeter_version = user_agent

    rh.set_order_status(
        redis_store, park_id, order_id, rh.OrderStatus.Complete,
    )
    setcar = load_json('complete_setcar.json')
    rh.set_redis_for_order_cancelling(
        redis_store, park_id, order_id, driver_id, setcar_item=setcar,
    )
    if params['park_id'] == 'park_id_0':
        park_json = load_json('parks.json')[0]
        fleet_parks.parks = {'parks': [park_json]}
    params['with_push'] = 'true'

    url = rch.get_requestconfirm_url(api_schema, status)
    headers = rch.get_headers(user_agent, park_id, driver_id)
    data = rch.process_data(api_schema, data_dict, data)
    response = await taxi_driver_orders_app_api.post(
        url,
        headers={**rch.get_content_type(api_schema), **headers},
        data=data,
        params=params,
    )
    assert response.status_code == code
    assert response.text == 'Unable to parse \'{}\' field as json.'.format(
        receipt_field,
    )


@pytest.mark.parametrize(
    'driver_id,params,data_filename,code',
    [
        (
            DEFAULT_DRIVER_ID,
            {'session': 'test_session', 'park_id': DEFAULT_PARK_ID},
            'complete_req_null.txt',
            400,
        ),
    ],
)
@pytest.mark.config(
    DRIVER_ORDERS_APP_API_REDIS_LOCK_SETTINGS=rch.zero_retry_lock_settings(),
)
@pytest.mark.parametrize('api_schema', ['requestconfirm_status_v2'])
async def test_handle_requestconfirm_complete_null_values(
        taxi_driver_orders_app_api,
        driver_authorizer,
        fleet_parks,
        yataxi_client,
        load_json,
        load,
        fleet_parks_shard,
        redis_store,
        driver_id,
        params,
        data_filename,
        code,
        api_schema,
):
    user_agent = (
        auth.USER_AGENT_TAXIMETER
        if driver_id == 'driver_id_0'
        else auth.USER_AGENT_UBER
    )
    data = load(data_filename).strip()
    park_id = params['park_id']
    data_dict = {kv.split('=')[0]: kv.split('=')[1] for kv in data.split('&')}
    order_id = data_dict['order']
    status = data_dict.get('status')
    app_family = auth.get_app_family(user_agent)
    driver_authorizer.set_client_session(
        app_family, park_id, params['session'], driver_id,
    )
    yataxi_client.taximeter_version = user_agent

    rh.set_order_status(
        redis_store, park_id, order_id, rh.OrderStatus.Complete,
    )
    setcar = load_json('complete_setcar.json')
    rh.set_redis_for_order_cancelling(
        redis_store, park_id, order_id, driver_id, setcar_item=setcar,
    )
    if params['park_id'] == 'park_id_0':
        park_json = load_json('parks.json')[0]
        fleet_parks.parks = {'parks': [park_json]}
    params['with_push'] = 'true'

    url = rch.get_requestconfirm_url(api_schema, status)
    headers = rch.get_headers(user_agent, park_id, driver_id)
    data = rch.process_data(api_schema, data_dict, data)
    response = await taxi_driver_orders_app_api.post(
        url,
        headers={**rch.get_content_type(api_schema), **headers},
        data=data,
        params=params,
    )
    assert response.status_code == code


@pytest.mark.parametrize(
    'driver_id,params,code,output',
    [
        (
            DEFAULT_DRIVER_ID,
            {'session': 'test_session', 'park_id': DEFAULT_PARK_ID},
            200,
            {'status': 7},
        ),
    ],
)
@pytest.mark.now('2020-03-20T11:22:33.123456Z')
@pytest.mark.config(
    DRIVER_ORDERS_APP_API_REDIS_LOCK_SETTINGS=rch.zero_retry_lock_settings(),
    TAXIMETER_FNS_SELF_EMPLOYMENT_SETTINGS=rch.self_employment_settings(),
    DRIVER_ORDERS_APP_API_PG_UPDATE_SETTINGS=rch.pg_update_settings(),
)
async def test_handle_requestconfirm_complete_corpweb(
        taxi_driver_orders_app_api,
        driver_authorizer,
        fleet_parks,
        load_json,
        load,
        taximeter_xservice,
        yataxi_client,
        fleet_parks_shard,
        redis_store,
        pgsql,
        stq,
        driver_id,
        params,
        code,
        output,
        mocked_time,
        contractor_order_history,
):
    user_agent = (
        auth.USER_AGENT_TAXIMETER
        if driver_id == 'driver_id_0'
        else auth.USER_AGENT_UBER
    )
    data = load('complete_req.txt').strip()
    park_id = params['park_id']
    data_dict = {kv.split('=')[0]: kv.split('=')[1] for kv in data.split('&')}

    def _get_receipt(name):
        result = data_dict.get(name)
        if not result:
            return None
        return json.loads(urllib.parse.unquote(result))

    order_id = data_dict['order']
    total_distance = float(data_dict.get('total_distance'))
    sum_field = float(data_dict.get('sum'))
    total = float(data_dict.get('total'))
    receipt_data = {
        'total_distance': total_distance,
        'sum': sum_field,
        'total': total,
    }
    cost_total = float(_get_receipt('driver_calc_receipt_overrides')['total'])
    status = data_dict.get('status')
    app_family = auth.get_app_family(user_agent)
    driver_authorizer.set_client_session(
        app_family, park_id, params['session'], driver_id,
    )
    yataxi_client.taximeter_version = user_agent

    taximeter_xservice.set_response({'code': 200})
    rh.set_order_status(
        redis_store, park_id, order_id, rh.OrderStatus.Transporting,
    )
    setcar = load_json('complete_setcar.json')
    setcar['pay_type'] = 5
    rh.set_redis_for_order_cancelling(
        redis_store, park_id, order_id, driver_id, setcar_item=setcar,
    )

    if params['park_id'] == 'park_id_0':
        park_json = load_json('parks.json')[0]
        fleet_parks.parks = {'parks': [park_json]}
    params['with_push'] = 'true'

    url = rch.get_requestconfirm_url('compatible', status)
    headers = rch.get_headers(user_agent, park_id, driver_id)
    data = rch.process_data('compatible', data_dict, data)

    receipt = _get_receipt('receipt')
    yataxi_client.receipt = receipt
    yataxi_client.driver_calc_receipt_overrides = _get_receipt(
        'driver_calc_receipt_overrides',
    )
    yataxi_client.status_distance = float(data_dict.get('statusDistance'))

    response = await taxi_driver_orders_app_api.post(
        url,
        headers={**rch.get_content_type('compatible'), **headers},
        data=data,
        params=params,
    )

    coh_request_args = await contractor_order_history.update.wait_call()
    request = coh_request_args['self'].json
    order_fields = {
        item['name']: item['value'] for item in request['order_fields']
    }
    assert order_fields['status'] == str(rh.OrderStatus.Complete.value)
    receipt_data_requested = json.loads(order_fields['receipt_data'])
    assert receipt_data_requested == receipt_data
    assert float(order_fields['cost_total']) == cost_total
    assert float(order_fields['cost_pay']) == cost_total

    assert response.status_code == code
