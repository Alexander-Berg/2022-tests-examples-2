import copy
import json
import urllib.parse
import uuid

import pytest

import tests_driver_orders_app_api.auth_helpers as auth
import tests_driver_orders_app_api.redis_helpers as rh
import tests_driver_orders_app_api.requestconfirm_helpers as rch

DEFAULT_PARK_ID = 'park_id_0'
DEFAULT_DRIVER_ID = 'driver_id_0'


class _DoesntMatterType:
    def __eq__(self, other):
        return True


# Used to skip check of some value
DOESNT_MATTER = _DoesntMatterType()


@pytest.mark.now('2020-03-20T11:22:33.123456Z')
@pytest.mark.config(
    DRIVER_ORDERS_APP_API_REDIS_LOCK_SETTINGS=rch.zero_retry_lock_settings(),
    TAXIMETER_FNS_SELF_EMPLOYMENT_SETTINGS=rch.self_employment_settings(),
    DRIVER_ORDERS_APP_API_PG_UPDATE_SETTINGS=rch.pg_update_settings(),
)
@pytest.mark.parametrize(
    'api_schema', ['compatible', 'requestconfirm_status_v2'],
)
@pytest.mark.parametrize(
    'price_calc_v2_data_in_request, pricing_resp_code,'
    'pricing_resp_required, expect_result_code',
    [
        (False, None, False, 200),
        (False, None, True, 200),
        (True, 200, False, 200),
        (True, 200, True, 200),
        (True, 400, False, 200),
        (True, 400, True, 500),
        (True, 500, False, 200),
        (True, 500, True, 500),
        (True, 404, True, 404),
        (True, 404, False, 200),
    ],
)
async def test_handle_requestconfirm_complete_and_send_data_to_pricing(
        taxi_driver_orders_app_api,
        taxi_config,
        mockserver,
        driver_authorizer,
        driver_profiles,
        fleet_parks,
        yataxi_client,
        load_json,
        load,
        taximeter_xservice,
        fleet_parks_shard,
        redis_store,
        pgsql,
        stq,
        mocked_time,
        api_schema,
        price_calc_v2_data_in_request,
        pricing_resp_code,
        pricing_resp_required,
        expect_result_code,
):
    taxi_config.set(
        DRIVER_ORDERS_APP_API_REQUIRE_PRICING_RESPONSE=pricing_resp_required,
    )

    price_calc_v2_data = load_json('price_calc_v2_data.json')
    price_calc_v2_data_str = '&price_calc_v2_data=' + urllib.parse.quote(
        json.dumps(price_calc_v2_data),
    )

    @mockserver.json_handler('/pricing-taximeter/v1/save_order_details')
    def _mock_pricing_taximeter_save_order_details(request):
        assert price_calc_v2_data_in_request
        assert request.args['order_id'] == 'eb5a0030d0b72561866a22af0f79f17e'
        assert request.args['taximeter_app'] == auth.USER_AGENT_TAXIMETER
        assert request.json == price_calc_v2_data
        if pricing_resp_code == 200:
            return {
                'price': {
                    'user': {'total': 202, 'meta': {}, 'extra': {}},
                    'driver': {'total': 200, 'meta': {}, 'extra': {}},
                },
                'price_verifications': {
                    'uuids': {'recalculated': str(uuid.uuid4())},
                },
            }
        if pricing_resp_code == 400:
            return mockserver.make_response(
                json={'code': 'error', 'message': 'bad request'}, status=400,
            )
        if pricing_resp_code == 404:
            return mockserver.make_response(
                json={'code': 'ORDER_NOT_FOUND', 'message': 'bad request'},
                status=404,
            )
        return mockserver.make_response(
            json={'code': 'error', 'message': 'internal error'}, status=500,
        )

    driver_id = DEFAULT_DRIVER_ID
    park_id = DEFAULT_PARK_ID
    params = {'session': 'test_session', 'park_id': park_id}
    user_agent = auth.USER_AGENT_TAXIMETER

    data = load('complete_req.txt').strip()
    if price_calc_v2_data_in_request:
        data += price_calc_v2_data_str
    data_dict = {kv.split('=')[0]: kv.split('=')[1] for kv in data.split('&')}

    order_id = data_dict['order']
    cost_total = float(data_dict.get('total'))
    status = data_dict.get('status')
    app_family = auth.get_app_family(user_agent)
    driver_authorizer.set_client_session(
        app_family, park_id, params['session'], driver_id,
    )
    yataxi_client.taximeter_version = user_agent
    driver_profiles.set_taximeter_version(user_agent)
    yataxi_client.final_cost = {'driver': cost_total, 'user': cost_total}

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

    response = await taxi_driver_orders_app_api.post(
        url,
        headers={**rch.get_content_type(api_schema), **headers},
        data=data,
        params=params,
    )

    assert response.status_code == expect_result_code
    if expect_result_code == 200:
        assert stq.driver_orders_xservice_calcservice.times_called == 1

        if api_schema == 'internal_order_status_v1':
            assert response.json()['status'] == 'complete'
            assert response.json()['cost'] == cost_total

    if price_calc_v2_data_in_request:
        await _mock_pricing_taximeter_save_order_details.wait_call()
    else:
        assert _mock_pricing_taximeter_save_order_details.times_called == 0


TAXIMETER = 1
FIXED_PRICE = 2

PRICE_CHANGED_COMMUNICATION = {
    'message': {
        'message': {
            'keyset': 'taximeter_backend_driver_messages',
            'key': 'pricing_antifraud_price_changed',
            'params': {'price': '100.00 ₽'},
        },
        'flags': ['high_priority'],
        'id': '0',
    },
}

PRICING_ADDITIONAL_PAYLOADS = {
    'requirements': [
        {
            'count': 0,
            'included': 0,
            'name': 'waiting_in_destination',
            'price': {'per_unit': 0, 'total': 50},
            'text': {
                'keyset': 'tariff',
                'tanker_key': 'service_name.waiting_in_destination',
            },
        },
        {
            'count': 0,
            'included': 0,
            'name': 'waiting',
            'price': {'per_unit': 0, 'total': 50},
            'text': {'keyset': 'tariff', 'tanker_key': 'service_name.waiting'},
        },
        {
            'count': 0,
            'included': 0,
            'name': 'waiting_in_transit',
            'price': {'per_unit': 0, 'total': 50},
            'text': {
                'keyset': 'tariff',
                'tanker_key': 'service_name.waiting_in_transit',
            },
        },
        {
            'count': 0,
            'included': 0,
            'name': 'child_chair',
            'price': {'per_unit': 50, 'total': 50},
            'text': {
                'keyset': 'tariff',
                'tanker_key': 'service_name.child_chair',
            },
        },
    ],
    'services': [
        {
            'name': 'surge_delta_raw',
            'price': 10,
            'text': {
                'keyset': 'taximeter_driver_messages',
                'tanker_key': 'surge_delta_raw',
            },
        },
        {
            'name': 'gepard_toll_road_payment_price',
            'price': 0,
            'text': {
                'keyset': 'taximeter_driver_messages',
                'tanker_key': 'toll_road_payment_title',
            },
        },
    ],
}

COMPLETE_DATA = {
    'payment_type_is_cash': False,
    'driver_price_with_subventions': 234,
    'user_price': 123,
}

COMPLETE_DATA_PAYLOADS = [
    {
        'text': 'Подождал в конце',
        'time_in_seconds': 0,
        'total_price': 50.0,
        'type': 'with_time',
    },
    {
        'text': 'Подождал в начале',
        'time_in_seconds': 0,
        'total_price': 50.0,
        'type': 'with_time',
    },
    {
        'text': 'Подождал по пути',
        'time_in_seconds': 0,
        'total_price': 50.0,
        'type': 'with_time',
    },
]


@pytest.mark.now('2020-03-20T11:22:33.123456Z')
@pytest.mark.config(
    DRIVER_ORDERS_APP_API_SKIP_YANDEX_ORDERS_FOR_XCALC=True,
    DRIVER_ORDERS_APP_API_REDIS_LOCK_SETTINGS=rch.zero_retry_lock_settings(),
    TAXIMETER_FNS_SELF_EMPLOYMENT_SETTINGS=rch.self_employment_settings(),
    DRIVER_ORDERS_APP_API_PG_UPDATE_SETTINGS=rch.pg_update_settings(),
)
@pytest.mark.parametrize(
    'api_schema', ['compatible', 'requestconfirm_status_v2'],
)
@pytest.mark.parametrize(
    'calc_method, '
    'provider, '
    'user_price, '
    'driver_price, '
    'user_meta, '
    'use_antifraud, '
    'expected_user_price, '
    'expected_db_costs, '
    'expected_driver_price, '
    'use_payloads, '
    'exp_use_complete_data_enabled, '
    'taximeter_version, '
    'complete_data_is_expected, ',
    [
        (
            FIXED_PRICE,
            '2',
            123,
            234,
            {'user_recalculated': 1.0},
            False,
            {'total': 123, 'sum': 123},
            {'total': 123, 'sum': 123},
            {'total': 234, 'sum': 234},
            False,
            False,
            'Taximeter 9.9 (1234)',
            False,
        ),
        (
            TAXIMETER,
            '2',
            123,
            234,
            {'user_recalculated': 1.0},
            False,
            {'total': 123, 'sum': 123},
            {'total': 123, 'sum': 123},
            {'total': 234, 'sum': 234},
            False,
            False,
            'Taximeter 9.9 (1234)',
            False,
        ),
        (
            TAXIMETER,
            '1',
            123,
            234,
            {'user_recalculated': 1.0},
            False,
            {'total': 200, 'sum': 200},
            {'total': 200, 'sum': 200},
            {'total': 200, 'sum': 200},
            False,
            False,
            'Taximeter 9.9 (1234)',
            False,
        ),
        (
            TAXIMETER,
            '2',
            123,
            234,
            {'price_before_coupon': 345, 'user_recalculated': 1.0},
            False,
            {'total': 345, 'sum': 123},
            {'total': 345, 'sum': 123},
            {'total': 234, 'sum': 234},
            False,
            False,
            'Taximeter 9.9 (1234)',
            False,
        ),
        (
            FIXED_PRICE,
            '2',
            123,
            234,
            {'user_recalculated': 1.0},
            True,
            {'total': 123, 'sum': 123},
            {'total': 123, 'sum': 123},
            {'total': 234, 'sum': 234},
            False,
            False,
            'Taximeter 9.9 (1234)',
            False,
        ),
        (
            FIXED_PRICE,
            '2',
            123,
            234,
            {'user_recalculated': 1.0},
            True,
            {'total': 123, 'sum': 123},
            {'total': 123, 'sum': 123},
            {'total': 234, 'sum': 234},
            True,
            False,
            'Taximeter 9.9 (1234)',
            False,
        ),
        (
            FIXED_PRICE,
            '2',
            123,
            234,
            {'user_recalculated': 1.0},
            True,
            {'total': 123, 'sum': 123},
            {'total': 123, 'sum': 123},
            {'total': 234, 'sum': 234},
            True,
            True,
            'Taximeter 9.7 (1234)',
            False,
        ),
        (
            FIXED_PRICE,
            '2',
            123,
            234,
            {'user_recalculated': 1.0},
            True,
            {'total': 123, 'sum': 123},
            {'total': 123, 'sum': 123},
            {'total': 234, 'sum': 234},
            True,
            True,
            'Taximeter 9.9 (1234)',
            True,
        ),
        (
            FIXED_PRICE,
            '2',
            123,
            234,
            {'user_recalculated': 1.0},
            False,
            {'total': 123, 'sum': 123},
            {'total': 123, 'sum': 123},
            {'total': 234, 'sum': 234},
            True,
            True,
            'Taximeter 9.9 (1234)',
            True,
        ),
        (
            TAXIMETER,
            '2',
            900,
            900,
            {'cashback_fixed_price': 100},
            False,
            {'total': 900, 'sum': 900},
            {'total': 900, 'sum': 900},
            {'total': 900, 'sum': 900},
            False,
            False,
            'Taximeter 9.9 (1234)',
            False,
        ),
        (
            TAXIMETER,
            '2',
            720,  # 1000 - 200 coupon - 80 cashback
            920,
            {
                'cashback_with_coupon_enabled': 1,
                'price_before_coupon': 1000,
                'cashback_fixed_price': 80,
            },
            False,
            {'total': 1000, 'sum': 720},
            {'total': 920, 'sum': 720},
            {'total': 920, 'sum': 920},
            False,
            False,
            'Taximeter 9.9 (1234)',
            False,
        ),
        (
            TAXIMETER,
            '2',
            1000,
            900,
            {
                'unite_total_price_enabled': 1,
                'user_ride_price': 900,
                'cashback_fixed_price': 100,
            },
            False,
            {'total': 1000, 'sum': 1000},
            {'total': 900, 'sum': 900},
            {'total': 900, 'sum': 900},
            False,
            False,
            'Taximeter 9.9 (1234)',
            False,
        ),
        (
            TAXIMETER,
            '2',
            800,  # 1000 -  200 coupon
            920,
            {
                'cashback_with_coupon_enabled': 1,
                'price_before_coupon': 1000,
                'unite_total_price_enabled': 1,
                'user_ride_price': 920,
                'cashback_fixed_price': 80,
            },
            False,
            {'total': 1000, 'sum': 800},
            {'total': 920, 'sum': 920},
            {'total': 920, 'sum': 920},
            False,
            False,
            'Taximeter 9.9 (1234)',
            False,
        ),
    ],
    ids=[
        'with_fixed_price',
        'simple',
        'non_yandex_provider',
        'with_coupon',
        'price_changed_message',
        'with_payloads',
        'without_complete_data_if_old_taximeter',
        'complete_data_instead_push',
        'complete_data_no_antifraud',
        'cashback_no_unite_total',
        'cashback_with_coupon_no_unite_total',
        'cashback_unite_total',
        'cashback_with_coupon_unite_total',
    ],
)
async def test_handle_replace_cost_from_new_pricing(
        taxi_driver_orders_app_api,
        taxi_config,
        experiments3,
        mockserver,
        driver_authorizer,
        fleet_parks,
        load_json,
        load,
        taximeter_xservice,
        fleet_parks_shard,
        redis_store,
        pgsql,
        stq,
        mocked_time,
        api_schema,
        yataxi_client,
        provider,
        calc_method,
        user_price,
        driver_price,
        user_meta,
        use_antifraud,
        expected_user_price,
        expected_db_costs,
        expected_driver_price,
        use_payloads,
        exp_use_complete_data_enabled,
        taximeter_version,
        complete_data_is_expected,
        contractor_order_history,
):
    if exp_use_complete_data_enabled:
        experiments3.add_experiments_json(
            load_json('exp3_use_server_complete_data.json'),
        )

    price_calc_v2_data = load_json('price_calc_v2_data.json')
    price_calc_v2_data_str = '&price_calc_v2_data=' + urllib.parse.quote(
        json.dumps(price_calc_v2_data),
    )
    driver_meta = {'driver_recalculated': 1.0}

    expected_final_cost_meta = {'user': user_meta, 'driver': driver_meta}

    @mockserver.json_handler('/pricing-taximeter/v1/save_order_details')
    def _mock_pricing_taximeter_save_order_details(request):
        assert request.args['order_id'] == 'eb5a0030d0b72561866a22af0f79f17e'
        assert request.args['taximeter_app'] == taximeter_version
        assert request.json == price_calc_v2_data
        response = {
            'price_verifications': {
                'uuids': {'recalculated': str(uuid.uuid4())},
            },
            'price': {
                'user': {
                    'total': user_price,
                    'meta': user_meta,
                    'extra': {'without_surge': user_price},
                },
                'driver': {
                    'total': driver_price,
                    'meta': driver_meta,
                    'extra': {},
                },
            },
        }
        if use_antifraud:
            response['recalculated_reason'] = 'antifraud'
            response[
                'price_changed_communication'
            ] = PRICE_CHANGED_COMMUNICATION
        if use_payloads:
            response['price']['user']['additional_payloads'] = {}
            response['price']['user']['additional_payloads'][
                'details'
            ] = PRICING_ADDITIONAL_PAYLOADS
        return response

    @mockserver.json_handler('/client-notify/v2/push')
    def _mock_client_notify_v2_push(request):
        assert not complete_data_is_expected
        assert (
            request.json['notification']['text']
            == PRICE_CHANGED_COMMUNICATION['message']['message']
        )
        assert (
            request.json['data']['flags']
            == PRICE_CHANGED_COMMUNICATION['message']['flags']
        )
        assert (
            request.json['data']['id']
            == PRICE_CHANGED_COMMUNICATION['message']['id']
        )
        return mockserver.make_response(json={}, status=200)

    driver_id = DEFAULT_DRIVER_ID
    park_id = DEFAULT_PARK_ID
    params = {'session': 'test_session', 'park_id': park_id}
    user_agent = taximeter_version
    yataxi_client.taximeter_version = taximeter_version

    data = load('complete_req.txt').strip() + price_calc_v2_data_str
    data_dict = {kv.split('=')[0]: kv.split('=')[1] for kv in data.split('&')}

    data_dict['provider'] = provider
    receipt_json = json.loads(urllib.parse.unquote(data_dict['receipt']))
    driver_receipt_json = json.loads(
        urllib.parse.unquote(data_dict['driver_calc_receipt_overrides']),
    )

    receipt_json['calc_method'] = calc_method
    driver_receipt_json['calc_method'] = calc_method

    data_dict['receipt'] = urllib.parse.quote(json.dumps(receipt_json))
    data_dict['driver_calc_receipt_overrides'] = urllib.parse.quote(
        json.dumps(driver_receipt_json),
    )
    data = '&'.join([k + '=' + str(v) for k, v in data_dict.items()])

    order_id = data_dict['order']
    status = data_dict.get('status')
    auth.create_session(
        driver_authorizer, user_agent, driver_id, park_id, params['session'],
    )

    taximeter_xservice.set_response({'code': 200})
    rh.set_order_status(
        redis_store, park_id, order_id, rh.OrderStatus.Transporting,
    )
    setcar = load_json('complete_setcar.json')
    rh.set_redis_for_order_cancelling(
        redis_store, park_id, order_id, driver_id, setcar_item=setcar,
    )
    park_json = load_json('parks.json')[0]
    fleet_parks.parks = {'parks': [park_json]}
    params['with_push'] = 'true'

    url = rch.get_requestconfirm_url(api_schema, status)
    headers = rch.get_headers(taximeter_version, park_id, driver_id)

    driver_receipt_json['sum'] = expected_driver_price['sum']
    driver_receipt_json['total'] = expected_driver_price['total']
    if use_antifraud:
        driver_receipt_json['calc_class'] = 'pricing_antifraud'

    receipt_json['sum'] = expected_user_price['total']
    receipt_json['total'] = expected_user_price['sum']
    if use_antifraud:
        receipt_json['calc_class'] = 'pricing_antifraud'

    yataxi_client.receipt = receipt_json
    yataxi_client.driver_calc_receipt_overrides = driver_receipt_json

    data = rch.process_data(api_schema, data_dict, data)
    yataxi_client.status_distance = float(data_dict.get('statusDistance'))
    yataxi_client.final_cost = None
    yataxi_client.final_cost_meta = expected_final_cost_meta

    response = await taxi_driver_orders_app_api.post(
        url,
        headers={**rch.get_content_type(api_schema), **headers},
        data=data,
        params=params,
    )

    assert stq.driver_orders_xservice_calcservice.times_called == int(
        provider != '2',
    )

    assert response.status_code == 200
    response_data = response.json()

    if complete_data_is_expected:
        assert 'complete_data' in response_data
        complete_data = copy.deepcopy(COMPLETE_DATA)
        if use_antifraud:
            complete_data[
                'price_correction_warning'
            ] = 'Цена изменена антифродом прайсинга'
        if use_payloads:
            complete_data['user_details'] = COMPLETE_DATA_PAYLOADS
        assert response_data['complete_data'] == complete_data
        assert not _mock_client_notify_v2_push.has_calls
    else:
        assert 'complete_data' not in response_data

        if use_antifraud:
            assert _mock_client_notify_v2_push.has_calls

    if stq.driver_orders_xservice_calcservice.has_calls:
        calcservice_kwargs = (
            stq.driver_orders_xservice_calcservice.next_call()['kwargs']
        )

        assert calcservice_kwargs['cost_total'] == expected_user_price['total']
        assert calcservice_kwargs['sum'] == expected_user_price['sum']

    coh_request_args = await contractor_order_history.update.wait_call()
    request = coh_request_args['self'].json
    order_fields = {
        item['name']: item['value'] for item in request['order_fields']
    }
    assert float(order_fields['cost_total']) == expected_db_costs['total']
    assert float(order_fields['cost_pay']) == expected_db_costs['sum']


@pytest.mark.parametrize(
    'soc_response, expected',
    [
        (
            {'driver_income_details_constructor': [{'some': 'element'}]},
            [{'some': 'element'}],
        ),
        (404, None),
        (429, None),
        (500, None),
    ],
)
@pytest.mark.parametrize(
    'api_schema', ['compatible', 'requestconfirm_status_v2'],
)
@pytest.mark.config(
    DRIVER_ORDERS_APP_API_SKIP_500_FROM_SUBVENTION_ORDER_CONTEXT=True,
)
async def test_request_driver_income_details_screen(
        taxi_driver_orders_app_api,
        experiments3,
        mockserver,
        driver_authorizer,
        fleet_parks,
        redis_store,
        yataxi_client,
        load_json,
        load,
        api_schema,
        soc_response,
        expected,
):
    @mockserver.json_handler('/pricing-taximeter/v1/save_order_details')
    def _mock_pricing_taximeter_save_order_details(request):
        return {
            'price_verifications': {
                'uuids': {'recalculated': str(uuid.uuid4())},
            },
            'price': {
                'user': {
                    'total': 10,
                    'meta': {'user_recalculated': 1.0},
                    'extra': {'without_surge': 10},
                },
                'driver': {
                    'total': 20,
                    'meta': {'driver_recalculated': 1.0},
                    'extra': {},
                },
            },
        }

    experiments3.add_experiments_json(
        load_json('exp3_use_server_complete_data.json'),
    )
    experiments3.add_experiments_json(
        load_json(
            'exp3_use_subvention_order_context_driver_income_details.json',
        ),
    )

    params = {'session': 'test_session', 'park_id': DEFAULT_PARK_ID}
    user_agent = 'Taximeter 9.9 (1234)'

    yataxi_client.taximeter_version = user_agent
    yataxi_client.receipt = DOESNT_MATTER
    yataxi_client.status_distance = DOESNT_MATTER
    yataxi_client.final_cost_meta = DOESNT_MATTER
    yataxi_client.driver_calc_receipt_overrides = DOESNT_MATTER

    price_calc_v2_data_str = '&price_calc_v2_data=' + urllib.parse.quote(
        json.dumps(load_json('price_calc_v2_data.json')),
    )
    data = load('complete_req.txt').strip() + price_calc_v2_data_str
    data_dict = {kv.split('=')[0]: kv.split('=')[1] for kv in data.split('&')}

    receipt_json = json.loads(urllib.parse.unquote(data_dict['receipt']))
    driver_receipt_json = json.loads(
        urllib.parse.unquote(data_dict['driver_calc_receipt_overrides']),
    )
    receipt_json['calc_method'] = FIXED_PRICE
    driver_receipt_json['calc_method'] = FIXED_PRICE
    data_dict['receipt'] = urllib.parse.quote(json.dumps(receipt_json))
    data_dict['driver_calc_receipt_overrides'] = urllib.parse.quote(
        json.dumps(driver_receipt_json),
    )
    data = '&'.join([k + '=' + str(v) for k, v in data_dict.items()])

    auth.create_session(
        driver_authorizer,
        user_agent,
        DEFAULT_DRIVER_ID,
        DEFAULT_PARK_ID,
        params['session'],
    )

    fleet_parks.parks = {'parks': [load_json('parks.json')[0]]}

    url = rch.get_requestconfirm_url(api_schema, data_dict.get('status'))
    headers = rch.get_headers(user_agent, DEFAULT_PARK_ID, DEFAULT_DRIVER_ID)

    data = rch.process_data(api_schema, data_dict, data)
    order_id = data_dict['order']

    setcar = load_json('complete_setcar.json')
    setcar['id'] = order_id
    setcar['internal'] = {'order_id': 'taxi_order_id'}
    rh.set_redis_for_order_cancelling(
        redis_store,
        DEFAULT_PARK_ID,
        order_id,
        DEFAULT_DRIVER_ID,
        setcar_item=setcar,
    )

    @mockserver.json_handler(
        '/subvention-order-context/internal/subvention-order-context'
        '/v1/subvention-details-screen',
    )
    def _mock_soc_subvention_details_screen(request):
        assert request.query['order_id'] == 'taxi_order_id'
        assert request.query['driver_profile_id'] == DEFAULT_DRIVER_ID
        assert request.query['park_id'] == DEFAULT_PARK_ID
        assert float(request.query['driver_price']) == 20.0
        assert bool(request.query['payment_type_is_cash']) is True
        assert float(request.query['user_price']) == 10.0
        assert request.query['application'] == user_agent

        if isinstance(soc_response, int):
            return mockserver.make_response(
                json={'code': str(soc_response), 'message': 'some_message'},
                status=soc_response,
            )

        return soc_response

    response = await taxi_driver_orders_app_api.post(
        url,
        headers={**rch.get_content_type(api_schema), **headers},
        data=data,
        params=params,
    )

    assert response.status_code == 200

    assert (
        response.json()['complete_data'].get(
            'driver_income_details_constructor',
        )
        == expected
    )


def _make_send_wallet_balance_to_subventions_config(value):
    return pytest.mark.experiments3(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        is_config=True,
        name='send_wallet_balance_to_subventions',
        consumers=['driver-orders-app-api/requestconfirm'],
        clauses=[],
        default_value=value,
    )


@pytest.mark.parametrize(
    'pricing_response_meta, expected_yaplus_amount',
    [
        pytest.param(
            {},
            None,
            marks=[
                _make_send_wallet_balance_to_subventions_config(
                    {'enabled': True, 'meta_name': 'wallet_balance'},
                ),
            ],
            id='enabled_no_meta',
        ),
        pytest.param(
            {'wallet_balance': 42.5},
            '42.500000',
            marks=[
                _make_send_wallet_balance_to_subventions_config(
                    {'enabled': True, 'meta_name': 'wallet_balance'},
                ),
            ],
            id='enabled_with_meta',
        ),
        pytest.param(
            {'wallet_balance': 42.5},
            None,
            marks=[
                _make_send_wallet_balance_to_subventions_config(
                    {'enabled': False, 'meta_name': 'wallet_balance'},
                ),
            ],
            id='disabled_with_meta',
        ),
    ],
)
@pytest.mark.parametrize(
    'api_schema', ['compatible', 'requestconfirm_status_v2'],
)
@pytest.mark.config(
    DRIVER_ORDERS_APP_API_SKIP_500_FROM_SUBVENTION_ORDER_CONTEXT=True,
)
async def test_request_subventions_plus_amount_passing(
        taxi_driver_orders_app_api,
        experiments3,
        mockserver,
        driver_authorizer,
        fleet_parks,
        redis_store,
        yataxi_client,
        load_json,
        load,
        api_schema,
        pricing_response_meta,
        expected_yaplus_amount,
):
    @mockserver.json_handler('/pricing-taximeter/v1/save_order_details')
    def _mock_pricing_taximeter_save_order_details(request):
        return {
            'price_verifications': {
                'uuids': {'recalculated': str(uuid.uuid4())},
            },
            'price': {
                'user': {
                    'total': 10,
                    'meta': pricing_response_meta,
                    'extra': {'without_surge': 10},
                },
                'driver': {'total': 20, 'meta': {}, 'extra': {}},
            },
        }

    experiments3.add_experiments_json(
        load_json('exp3_use_server_complete_data.json'),
    )
    experiments3.add_experiments_json(
        load_json(
            'exp3_use_subvention_order_context_driver_income_details.json',
        ),
    )

    params = {'session': 'test_session', 'park_id': DEFAULT_PARK_ID}
    user_agent = 'Taximeter 9.9 (1234)'

    yataxi_client.taximeter_version = user_agent
    yataxi_client.receipt = DOESNT_MATTER
    yataxi_client.status_distance = DOESNT_MATTER
    yataxi_client.final_cost_meta = DOESNT_MATTER
    yataxi_client.driver_calc_receipt_overrides = DOESNT_MATTER

    price_calc_v2_data_str = '&price_calc_v2_data=' + urllib.parse.quote(
        json.dumps(load_json('price_calc_v2_data.json')),
    )
    data = load('complete_req.txt').strip() + price_calc_v2_data_str
    data_dict = {kv.split('=')[0]: kv.split('=')[1] for kv in data.split('&')}

    receipt_json = json.loads(urllib.parse.unquote(data_dict['receipt']))
    driver_receipt_json = json.loads(
        urllib.parse.unquote(data_dict['driver_calc_receipt_overrides']),
    )
    receipt_json['calc_method'] = FIXED_PRICE
    driver_receipt_json['calc_method'] = FIXED_PRICE
    data_dict['receipt'] = urllib.parse.quote(json.dumps(receipt_json))
    data_dict['driver_calc_receipt_overrides'] = urllib.parse.quote(
        json.dumps(driver_receipt_json),
    )
    data = '&'.join([k + '=' + str(v) for k, v in data_dict.items()])

    auth.create_session(
        driver_authorizer,
        user_agent,
        DEFAULT_DRIVER_ID,
        DEFAULT_PARK_ID,
        params['session'],
    )

    fleet_parks.parks = {'parks': [load_json('parks.json')[0]]}

    url = rch.get_requestconfirm_url(api_schema, data_dict.get('status'))
    headers = rch.get_headers(user_agent, DEFAULT_PARK_ID, DEFAULT_DRIVER_ID)

    data = rch.process_data(api_schema, data_dict, data)
    order_id = data_dict['order']

    setcar = load_json('complete_setcar.json')
    setcar['id'] = order_id
    setcar['internal'] = {'order_id': 'taxi_order_id'}
    rh.set_redis_for_order_cancelling(
        redis_store,
        DEFAULT_PARK_ID,
        order_id,
        DEFAULT_DRIVER_ID,
        setcar_item=setcar,
    )

    @mockserver.json_handler(
        '/subvention-order-context/internal/subvention-order-context'
        '/v1/subvention-details-screen',
    )
    def _mock_soc_subvention_details_screen(request):
        assert request.query.get('ya_plus_amount') == expected_yaplus_amount
        return {'driver_income_details_constructor': [{'some': 'element'}]}

    response = await taxi_driver_orders_app_api.post(
        url,
        headers={**rch.get_content_type(api_schema), **headers},
        data=data,
        params=params,
    )

    assert response.status_code == 200
