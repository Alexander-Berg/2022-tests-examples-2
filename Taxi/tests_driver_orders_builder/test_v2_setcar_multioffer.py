# pylint: disable=too-many-lines

import json

import pytest

from tests_driver_orders_builder import utils

SETCAR_CREATE_URL = '/v2/setcar'
PARAMS = {
    'driver': {
        'park_id': 'park1',
        'driver_profile_id': 'driver1',
        'alias_id': '4d605a2849d747079b5d8c7012830419',
    },
    'order_id': 'test_order_id',
}

MOCKED_NOW = '2021-08-18T09:00:00+03:00'


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_processings_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'__default__': False},
)
@pytest.mark.parametrize('use_stq_for_driving', [True, False])
@pytest.mark.now(MOCKED_NOW)
async def test_create_setcar_with_multioffer_ok(
        taxi_driver_orders_builder,
        redis_store,
        load_json,
        contractor_orders_multioffer,
        mockserver,
        order_proc,
        taxi_config,
        use_stq_for_driving,
        stq,
):
    @mockserver.json_handler(
        '/driver-orders-app-api/internal/v1/order/status/driving',
    )
    def status_driving(self):
        return mockserver.make_response(json={'status': 'driving'}, status=200)

    order_proc_json = load_json('order_core_orderproc_alias_id.json')
    taxi_config.set(MULTIOFFER_USE_STQ_FOR_DRIVING=use_stq_for_driving)

    order_proc.order_proc = order_proc_json

    multioffer_section = load_json('multioffer.json')
    candidates = order_proc_json['fields']['candidates']
    driver_id_section = candidates[0]['driver_id'].split('_')[1]

    setcar_json = load_json('setcar.json')
    setcar_json['multioffer'] = multioffer_section
    setcar_json['driver_id'] = driver_id_section

    setcar_push = load_json('setcar_push.json')
    setcar_push['multioffer'] = load_json('multioffer.json')
    setcar_push['driver_id'] = driver_id_section

    alias_id = setcar_json['id']

    # this asserts have never calculated
    # def order_proc_assert(params):
    #    def _cmp(req):
    #        assert req.json['order_id'] == params['order_id']
    #        assert req.json['update']['set']['aliases.0.id'] == alias_id
    #        assert (
    #            req.json['update']['set']['candidates.0.alias_id'] == alias_id
    #        )
    #
    #    return _cmp
    #
    # TODO if it necessary write order_proc.set_request_query_assert
    # order_proc.set_fields_request_assert = order_proc_assert(PARAMS)
    request = PARAMS
    request['original_setcar'] = setcar_json
    response = await taxi_driver_orders_builder.post(
        SETCAR_CREATE_URL, json=request,
    )
    assert response.status_code == 200, response.text
    assert response.json()['setcar_push'] == setcar_push
    redis_str = redis_store.hget('Order:SetCar:Items:park1', alias_id)
    redis_dict = json.loads(redis_str)
    utils.add_accents(setcar_json)
    assert redis_dict == setcar_json
    assert contractor_orders_multioffer.state_by_order.times_called == 1
    next_call = contractor_orders_multioffer.state_by_order.next_call()

    request_json = next_call['self'].json
    assert request_json['order_id'] == PARAMS['order_id']
    assert request_json['park_id'] == PARAMS['driver']['park_id']
    assert request_json['driver_profile_id'] == setcar_json['driver_id']

    assert status_driving.times_called == int(not use_stq_for_driving)
    if use_stq_for_driving:
        assert (
            stq.driver_orders_builder_multioffer_move_to_driving.times_called
            == 1
        )
        kwargs = (
            stq.driver_orders_builder_multioffer_move_to_driving.next_call()[
                'kwargs'
            ]
        )
        assert kwargs['park_id'] == PARAMS['driver']['park_id']
        assert kwargs['setcar_id'] == alias_id
        assert kwargs['driver_profile_id'] == setcar_json['driver_id']
