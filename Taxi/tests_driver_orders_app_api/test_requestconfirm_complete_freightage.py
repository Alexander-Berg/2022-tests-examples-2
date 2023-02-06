import json
import urllib

import pytest

import tests_driver_orders_app_api.auth_helpers as auth
import tests_driver_orders_app_api.redis_helpers as rh
import tests_driver_orders_app_api.requestconfirm_helpers as rch

DEFAULT_PARK_ID = 'park_id_0'
DEFAULT_DRIVER_ID = 'driver_id_0'
DEFAULT_ORDER_ID = 'order_id_0'


@pytest.mark.parametrize(
    'setcar_driver_freightage,freightage_saved',
    [(None, False), (False, False), (True, True)],
)
@pytest.mark.now('2020-03-20T11:22:33.123456Z')
@pytest.mark.config(
    DRIVER_ORDERS_APP_API_REDIS_LOCK_SETTINGS=rch.zero_retry_lock_settings(),
    TAXIMETER_FNS_SELF_EMPLOYMENT_SETTINGS=rch.self_employment_settings(),
    DRIVER_ORDERS_APP_API_PG_UPDATE_SETTINGS=rch.pg_update_settings(),
)
async def test_handle_requestconfirm_complete_freightage(
        taxi_driver_orders_app_api,
        driver_authorizer,
        fleet_parks,
        fleet_parks_shard,
        redis_store,
        yataxi_client,
        load,
        load_json,
        mockserver,
        stq,
        setcar_driver_freightage,
        freightage_saved,
):
    driver_id = DEFAULT_DRIVER_ID
    park_id = DEFAULT_PARK_ID
    order_id = DEFAULT_ORDER_ID
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

    alias_id = data_dict.get('order')
    status = data_dict.get('status')
    sum_field = float(data_dict.get('sum'))
    total = float(data_dict.get('total'))

    app_family = auth.get_app_family(auth.USER_AGENT_TAXIMETER)

    driver_authorizer.set_client_session(
        app_family, park_id, params['session'], driver_id,
    )
    yataxi_client.taximeter_version = auth.USER_AGENT_TAXIMETER
    yataxi_client.final_cost_meta = {'driver': {}, 'user': {}}

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

    setcar['internal'] = {
        'order_id': order_id,
        'driver_freightage': setcar_driver_freightage,
    }

    rh.set_redis_for_order_cancelling(
        redis_store, park_id, alias_id, driver_id, setcar_item=setcar,
    )

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

    assert response.status_code == 200
    assert response.json() == expected_body
    assert stq.driver_orders_save_driver_freightage.times_called == int(
        freightage_saved,
    )
    if freightage_saved:
        stq_params = stq.driver_orders_save_driver_freightage.next_call()
        assert stq_params['queue'] == 'driver_orders_save_driver_freightage'
        assert stq_params['id'] == alias_id
        assert stq_params['kwargs']['alias_id'] == alias_id
        assert stq_params['kwargs']['order_id'] == order_id
