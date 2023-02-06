import json

import pytest


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enable_cashbox_integration_request': True},
)
@pytest.mark.parametrize('has_cashbox_id', [True, False])
async def test_cashbox_integration(
        taxi_driver_orders_builder,
        load_json,
        redis_store,
        mockserver,
        has_cashbox_id,
        setcar_create_params,
):
    @mockserver.json_handler(
        '/cashbox-integration/v1/parks/cashboxes/current/retrieve',
    )
    def _mock_cashbox_integration(request):
        resp = {'park_id': 'id'}
        if has_cashbox_id:
            resp['cashbox_id'] = 'cashbox_id'
        return resp

    setcar_json = load_json('setcar.json')
    response = await taxi_driver_orders_builder.post(**setcar_create_params)
    assert response.status_code == 200

    redis_str = redis_store.hget('Order:SetCar:Items:park1', setcar_json['id'])
    redis_dict = json.loads(redis_str)
    assert redis_dict['has_online_cashbox'] == has_cashbox_id
