import json
import urllib

import pytest

import tests_driver_orders_app_api.auth_helpers as auth
import tests_driver_orders_app_api.redis_helpers as rh
import tests_driver_orders_app_api.requestconfirm_helpers as rch

DEFAULT_PARK_ID = 'park_id_0'
DEFAULT_DRIVER_ID = 'driver_id_0'


@pytest.mark.parametrize(
    'spb_fallback_mode,spb_success,spb_reset_success',
    [
        ('disabled', False, True),
        ('monkey_patch', False, True),
        ('wait_moved_to_cash', False, False),
        ('wait_moved_to_cash', False, True),
        ('wait_moved_to_cash', True, False),
    ],
)
@pytest.mark.now('2020-03-20T11:22:33.123456Z')
@pytest.mark.config(
    DRIVER_ORDERS_APP_API_REDIS_LOCK_SETTINGS=rch.zero_retry_lock_settings(),
    TAXIMETER_FNS_SELF_EMPLOYMENT_SETTINGS=rch.self_employment_settings(),
    DRIVER_ORDERS_APP_API_PG_UPDATE_SETTINGS=rch.pg_update_settings(),
)
async def test_handle_requestconfirm_complete_sbp_move_to_cash(
        taxi_driver_orders_app_api,
        driver_authorizer,
        fleet_parks,
        experiments3,
        load_json,
        load,
        taximeter_xservice,
        yataxi_client,
        fleet_parks_shard,
        redis_store,
        pgsql,
        stq,
        spb_fallback_mode,
        spb_success,
        spb_reset_success,
        mockserver,
        contractor_order_history,
):
    driver_id = DEFAULT_DRIVER_ID
    park_id = DEFAULT_PARK_ID
    params = {
        'session': 'test_session',
        'park_id': park_id,
        'with_push': 'true',
    }

    price_calc_v2_data = load_json('price_calc_v2_data.json')
    price_calc_v2_data_str = '&price_calc_v2_data=' + urllib.parse.quote(
        json.dumps(price_calc_v2_data),
    )
    setcar = load_json('complete_setcar.json')

    data = load('complete_req.txt').strip() + price_calc_v2_data_str
    data_dict = {kv.split('=')[0]: kv.split('=')[1] for kv in data.split('&')}

    def _get_receipt(name):
        result = data_dict.get(name)
        if not result:
            return None
        return json.loads(urllib.parse.unquote(result))

    experiments3.add_experiments_json(
        load_json('exp3_use_server_complete_data.json'),
    )
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='driver_orders_app_api_sbp_fallback',
        consumers=['driver-orders-app-api/requestconfirm'],
        clauses=[],
        default_value={
            'mode': spb_fallback_mode,
            'wait_update_interval': 0,
            'wait_update_attempts': 1,
        },
    )

    order_id = data_dict['order']
    sum_field = float(data_dict.get('sum'))
    total = float(data_dict.get('total'))

    status = data_dict.get('status')
    app_family = auth.get_app_family(auth.USER_AGENT_TAXIMETER)

    driver_authorizer.set_client_session(
        app_family, park_id, params['session'], driver_id,
    )
    yataxi_client.taximeter_version = auth.USER_AGENT_TAXIMETER
    yataxi_client.final_cost_meta = {'driver': {}, 'user': {}}

    @mockserver.json_handler('/pricing-taximeter/v1/save_order_details')
    def _mock_pricing_taximeter_save_order_details(request):
        response = {
            'price_verifications': {'uuids': {'recalculated': ''}},
            'price': {
                'user': {'total': total, 'meta': {}, 'extra': {}},
                'driver': {'total': total, 'meta': {}, 'extra': {}},
            },
        }
        return response

    @mockserver.json_handler(
        '/payment-methods/v1/sbp/complete_order_check_move_to_cash',
    )
    def _mock_payment_methods_sbp_check(request):
        if spb_reset_success:
            setcar['pay_type'] = 0  # cash
            setcar.setdefault('internal', {})['payment_type'] = 'cash'
            rh.set_redis_for_order_cancelling(
                redis_store, park_id, order_id, driver_id, setcar_item=setcar,
            )
        response = {'moved_to_cash': not spb_success}
        return response

    taximeter_xservice.set_response({'code': 200})
    rh.set_order_status(
        redis_store, park_id, order_id, rh.OrderStatus.Transporting,
    )
    setcar['pay_type'] = 1  # cashless
    setcar.setdefault('internal', {})['payment_type'] = 'sbp'
    rh.set_redis_for_order_cancelling(
        redis_store, park_id, order_id, driver_id, setcar_item=setcar,
    )

    park_json = load_json('parks.json')[0]
    fleet_parks.parks = {'parks': [park_json]}

    url = rch.get_requestconfirm_url('compatible', status)
    headers = rch.get_headers(auth.USER_AGENT_TAXIMETER, park_id, driver_id)
    data = rch.process_data('compatible', data_dict, data)

    receipt = _get_receipt('receipt')
    receipt['sum'] = sum_field
    receipt['total'] = total

    yataxi_client.receipt = receipt
    yataxi_client.driver_calc_receipt_overrides = receipt
    yataxi_client.status_distance = float(data_dict.get('statusDistance'))

    response = await taxi_driver_orders_app_api.post(
        url,
        headers={**rch.get_content_type('compatible'), **headers},
        data=data,
        params=params,
    )

    expected_body = {
        'phone_options': [
            {
                'call_dialog_message_prefix': 'Телефон пассажира',
                'label': 'Телефон пассажира.',
                'type': 'main',
            },
        ],
        'status': 7,
    }
    if spb_fallback_mode != 'disabled' and not spb_success:
        expected_body['pay_type'] = 0  # cash
    if spb_reset_success or spb_success:
        assert response.status_code == 200
        assert response.json() == expected_body
    else:
        assert response.status_code == 500
