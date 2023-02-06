import pytest

import tests_driver_orders_app_api.auth_helpers as auth
import tests_driver_orders_app_api.redis_helpers as rh
import tests_driver_orders_app_api.requestconfirm_helpers as rch


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


@pytest.mark.config(
    DRIVER_ORDERS_APP_API_PG_UPDATE_SETTINGS=rch.pg_update_settings(),
)
async def test_update(
        taxi_config,
        taxi_driver_orders_app_api,
        driver_authorizer,
        fleet_parks,
        contractor_order_history,
        yataxi_client,
        load_json,
        redis_store,
):
    params = {'session': 'test_session', 'park_id': 'park_id_0'}
    park_id = params['park_id']
    driver_id = 'driver_id_0'
    api_schema = 'requestconfirm_status_v2'
    data = (
        'provider=2&order=order_id_0&'
        'date=2020-04-14T16%3A02%3A02.0000000&status=5'
    )
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
    assert response.status_code == 200

    coh_request_args = await contractor_order_history.update.wait_call()
    request = coh_request_args['self'].json
    assert request['park_id'] == park_id
    assert request['alias_id'] == order_id
