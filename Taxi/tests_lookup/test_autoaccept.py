import json

import pytest

from tests_lookup import lookup_params
from tests_lookup import mock_candidates


@pytest.mark.parametrize('is_verybusy', [True, False])
@pytest.mark.parametrize('has_hourly_rental', [True, False])
@pytest.mark.parametrize('is_chain', [True, False])
@pytest.mark.parametrize('is_check_in', [True, False])
@pytest.mark.parametrize('is_combo_active', [True, False])
@pytest.mark.config(
    DRIVER_METRICS_PROPERTIES_FROM_REQUIREMENTS=['hourly_rental'],
    LOOKUP_PARAM_ENRICHERS=['dispatch_check_in'],
)
async def test_autoaccept(
        acquire_candidate,
        mockserver,
        is_chain,
        has_hourly_rental,
        is_verybusy,
        is_check_in,
        is_combo_active,
):
    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        candidate = mock_candidates.make_candidates()['candidates'][0]
        candidate['route_info'] = {'distance': 211, 'time': 0}
        candidate['metadata'] = {'lookup': {'mode': 'direct'}}
        if is_verybusy:
            candidate['metadata'].update({'verybusy_order': True})
        if is_chain:
            candidate['chain_info'] = {
                'destination': [55.0, 35.0],
                'left_dist': 125,
                'left_time': 0,
                'order_id': 'some_order_id',
            }
        if is_check_in:
            candidate['metadata'].update(
                {'airport_queue': {'is_check_in': True}},
            )
        if is_combo_active:
            candidate['metadata'].update({'combo': {'active': True}})
        return {'candidates': [candidate]}

    @mockserver.json_handler('/autoaccept/v1/decide-autoaccept')
    def _decide_autoaccept(request):
        body = json.loads(request.get_data())
        if is_chain:
            assert body['distance_to_a'] == (211 - 125)
            assert body['time_to_a'] == 60
            assert body['has_chain_parent']
        else:
            assert not body['has_chain_parent']

        assert body['check_in_candidate'] == is_check_in

        order_properties = body['properties']
        assert has_hourly_rental == ('hourly_rental' in order_properties)
        assert is_verybusy == ('verybusy_offer' in order_properties)
        assert 'lookup_mode_direct' in order_properties

        assert body['combo_active'] == is_combo_active

        return {'autoaccept': {'enabled': True}}

    order = lookup_params.create_params()
    if has_hourly_rental:
        order['order']['request']['requirements'] = {'hourly_rental': 1}
    if is_check_in:
        order['dispatch_check_in'] = {
            'check_in_time': 1628790759.55,
            'pickup_line': 'pickup_line_0',
        }

    candidate = await acquire_candidate(order)
    assert candidate['autoaccept']['enabled']
