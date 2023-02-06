import json

import pytest


ORDER_ID = 'dc3bdfc6493d3d959d7ecd5019231b8d'
PARK_ID = 'a3608f8f7ee84e0b9c21862beef7e48d'
DRIVER_PROFILE_ID = 'ee103bbe49434519ba346bf9452894ab'
ALIAS_ID = 'a0e5e02eddbb3bbb80b1750350f4c2ed'


@pytest.mark.parametrize('is_need_to_send_custom_push', {False, True})
async def test_order_update(
        taxi_driver_orders_app_api,
        stq,
        mockserver,
        contractor_order_history,
        is_need_to_send_custom_push,
):
    await taxi_driver_orders_app_api.tests_control(reset_metrics=True)

    @mockserver.json_handler(
        '/driver-orders-builder/v2/setcar/update/user_ready',
    )
    def _mock_setcar_data(request):
        if is_need_to_send_custom_push:
            return {
                'setcar': {},
                'setcar_push': {},
                'update_push': {
                    'message': 'some_message',
                    'order': 'some_order',
                },
            }
        return {'setcar': {}, 'setcar_push': {}}

    response = await taxi_driver_orders_app_api.post(
        '/internal/v1/order/update/user_ready',
        headers={'Content-type': 'application/json'},
        data=json.dumps(
            {
                'order_id': ORDER_ID,
                'driver': {
                    'park_id': PARK_ID,
                    'driver_profile_id': DRIVER_PROFILE_ID,
                    'alias_id': ALIAS_ID,
                },
                'change_id': 'test',
            },
        ),
    )

    assert response.status_code == 200
    if is_need_to_send_custom_push:
        assert (
            stq.driver_orders_send_communications_notifications.times_called
            == 2
        )
    else:
        assert (
            stq.driver_orders_send_communications_notifications.times_called
            == 1
        )

    coh_request_args = await contractor_order_history.update.wait_call()
    coh_request = coh_request_args['self'].json
    assert coh_request['park_id'] == PARK_ID
    assert coh_request['alias_id'] == ALIAS_ID
    for item in coh_request['order_fields']:
        name = item['name']
        if name == 'driver_id':
            assert item['value'] == DRIVER_PROFILE_ID


@pytest.mark.parametrize('should_add_track', {True, False})
async def test_client_geo_sharing_update(
        taxi_driver_orders_app_api, mockserver, should_add_track, taxi_config,
):
    @mockserver.json_handler(
        '/driver-orders-builder/v2/setcar/update/client_geo_sharing',
    )
    def _mock_dob_geo_sharing_update(request):
        geo_sharing_obj = {'track_id': 'user_id'}
        if should_add_track:
            geo_sharing_obj['is_enabled'] = True
        return {
            'setcar': {'client_geo_sharing': geo_sharing_obj},
            'setcar_push': {},
        }

    taxi_config.set_values({'TAXIMETER_USE_COS_FOR_GEO_SHARING': True})

    @mockserver.json_handler(
        '/contractor-order-setcar/v1/order/client-geo-sharing',
    )
    def _mock_cos_geo_sharing(request):
        expected_method = 'PUT' if should_add_track else 'DELETE'
        assert request.method == expected_method
        return mockserver.make_response(status=200)

    response = await taxi_driver_orders_app_api.post(
        '/internal/v1/order/update/client_geo_sharing',
        headers={'Content-type': 'application/json'},
        data=json.dumps(
            {
                'order_id': ORDER_ID,
                'driver': {
                    'park_id': PARK_ID,
                    'driver_profile_id': DRIVER_PROFILE_ID,
                    'alias_id': ALIAS_ID,
                },
                'change_id': 'test',
            },
        ),
    )

    assert _mock_cos_geo_sharing.times_called == 1
    assert response.status_code == 200
