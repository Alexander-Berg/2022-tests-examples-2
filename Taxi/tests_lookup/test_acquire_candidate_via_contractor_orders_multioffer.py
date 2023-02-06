import json

import pytest

from tests_lookup import lookup_params
from tests_lookup import mock_candidates


@pytest.mark.parametrize('callback', [True, False])
@pytest.mark.config(LOOKUP_PGAAS_CALLBACKS_ENABLE=True)
async def test_response_200(
        acquire_candidate, mockserver, taxi_config, callback,
):
    taxi_config.set_values(
        {
            'LOOKUP_DISPATCH_SETTINGS': {
                '__default__': {'enabled': True, 'fallback': True},
                'multioffer': {'enabled': True, 'callback': callback},
            },
        },
    )

    @mockserver.json_handler(
        '/contractor-orders-multioffer/v1/contractor-for-order',
    )
    def contractor_orders_multioffer(request):
        body = json.loads(request.get_data())
        assert 'order_id' in body
        assert 'order' in body
        assert 'request' in body['order']
        assert 'zone_id' in body
        assert 'allowed_classes' in body
        if callback:
            assert 'callback' in body
        else:
            assert 'callback' not in body
        response = {
            'candidate': mock_candidates.make_candidates()['candidates'][0],
        }
        return response

    @mockserver.json_handler('/driver-freeze/freeze')
    def freeze(request):
        return {'freezed': True}

    @mockserver.json_handler('/driver-freeze/defreeze')
    def _defreeze(request):
        assert False, 'should not be called'

    order = lookup_params.create_params()
    assert order['order']['nz'] == 'moscow'

    candidate = await acquire_candidate(order)
    assert candidate

    await contractor_orders_multioffer.wait_call(timeout=1)
    await freeze.wait_call(timeout=1)


async def test_error(acquire_candidate, mockserver):
    @mockserver.json_handler('/candidates/order-search')
    def order_search(request):
        return mockserver.make_response(
            '{"candidates":[]}', 200, content_type='application/json',
        )

    @mockserver.json_handler(
        '/contractor-orders-multioffer/v1/contractor-for-order',
    )
    def contractor_orders_multioffer(request):
        return mockserver.make_response(
            '{}', 500, content_type='application/json',
        )

    order = lookup_params.create_params()

    await acquire_candidate(order, expect_fail=True)

    assert contractor_orders_multioffer.has_calls
    assert not order_search.has_calls


@pytest.mark.experiments3(
    name='multioffer_check',
    consumers=['lookup/acquire'],
    match={
        'predicate': {
            'type': 'in_set',
            'init': {
                'set': ['moscow'],
                'arg_name': 'zone',
                'set_elem_type': 'string',
            },
        },
        'enabled': True,
        'value': {},
    },
    clauses=[
        {
            'predicate': {
                'type': 'in_set',
                'init': {
                    'set': ['order_id'],
                    'arg_name': 'order_id',
                    'set_elem_type': 'string',
                },
            },
            'enabled': True,
            'title': 'Title',
            'value': {'enabled': True},
        },
    ],
    default_value={},
)
async def test_experiment(acquire_candidate, mockserver):
    @mockserver.json_handler(
        '/contractor-orders-multioffer/v1/contractor-for-order',
    )
    def contractor_orders_multioffer(request):
        body = json.loads(request.get_data())
        assert 'order_id' in body
        assert 'order' in body
        assert 'request' in body['order']
        assert 'zone_id' in body
        assert 'allowed_classes' in body
        response = {
            'candidate': mock_candidates.make_candidates()['candidates'][0],
        }
        return response

    order = lookup_params.create_params()
    assert order['order']['nz'] == 'moscow'

    candidate = await acquire_candidate(order)
    assert candidate
    assert not contractor_orders_multioffer.has_calls

    order['_id'] = 'order_id'

    candidate = await acquire_candidate(order)
    assert candidate
    await contractor_orders_multioffer.wait_call(timeout=1)

    order['order']['nz'] = 'himki'
    order['_id'] = '123'
    candidate = await acquire_candidate(order)
    assert candidate
    await contractor_orders_multioffer.wait_call(timeout=1)
