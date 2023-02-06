# pylint: disable=C5521
from datetime import datetime
from datetime import timezone

import bson
import pytest

from tests_lookup import lookup_params
from tests_lookup import mock_candidates


async def test_lookup_ttl_due_calc_exp_mismatch(acquire_candidate, mockserver):
    @mockserver.json_handler('/manual-dispatch/v1/lookup')
    def _manual_dispatch(request):
        candidate = mock_candidates.make_candidates()['candidates'][0]
        candidate['due'] = datetime.utcnow().timestamp()
        return mockserver.make_response(
            status=200, json={'candidate': candidate},
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/new_driver_found',
    )
    def order_core_event(request):
        body = bson.BSON.decode(request.get_data())
        aliases = body['extra_update']['$push']['aliases']
        assert (
            aliases.get('due').replace(tzinfo=timezone.utc).timestamp() + 500
            < order['order']['request']['due']
        )
        return mockserver.make_response('', 200)

    order = lookup_params.create_params(generation=1, version=1)
    order['manual_dispatch'] = {'a': 'b'}
    order['order']['request']['due'] = datetime.utcnow().timestamp() + 600
    order['order']['request']['lookup_ttl'] = (
        datetime.utcnow().timestamp() + 6000
    )
    await acquire_candidate(order)
    assert order_core_event.has_calls


@pytest.mark.experiments3(
    name='lookup_ttl_due_calc',
    consumers=['lookup/acquire'],
    match={
        'predicate': {
            'type': 'in_set',
            'init': {
                'arg_name': 'order_type',
                'set': ['soon'],
                'set_elem_type': 'string',
            },
        },
        'enabled': True,
    },
    clauses=[
        {
            'predicate': {
                'type': 'in_set',
                'init': {
                    'set': ['phone_id'],
                    'arg_name': 'user_phone_id',
                    'set_elem_type': 'string',
                },
            },
            'enabled': True,
            'title': 'Title',
            'value': {'use_order_due_with_lookup_ttl': True},
        },
    ],
    default_value={'use_order_due_with_lookup_ttl': False},
)
async def test_lookup_ttl_due_calc_exp_match(acquire_candidate, mockserver):
    @mockserver.json_handler('/manual-dispatch/v1/lookup')
    def _manual_dispatch(request):
        candidate = mock_candidates.make_candidates()['candidates'][0]
        candidate['route_info']['time'] = 0
        return mockserver.make_response(
            status=200, json={'candidate': candidate},
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/new_driver_found',
    )
    def order_core_event(request):
        body = bson.BSON.decode(request.get_data())
        aliases = body['extra_update']['$push']['aliases']
        assert int(
            aliases.get('due').replace(tzinfo=timezone.utc).timestamp(),
        ) == int(order['order']['request']['due'])
        return mockserver.make_response('', 200)

    order = lookup_params.create_params(generation=1, version=1)
    order['manual_dispatch'] = {'a': 'b'}
    order['order']['request']['due'] = datetime.now().timestamp() + 600
    order['order']['request']['lookup_ttl'] = datetime.now().timestamp() + 6000
    await acquire_candidate(order)
    assert order_core_event.has_calls
