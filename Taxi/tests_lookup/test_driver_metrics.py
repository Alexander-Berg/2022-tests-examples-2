import datetime
import json

import bson
import pytest

from tests_lookup import lookup_params
from tests_lookup import mock_candidates

DP_FIRST_VALUE = 66


@pytest.mark.parametrize(
    'return_priority, is_verybusy, alternative_type, '
    'has_hourly_rental, is_chain, is_autoaccept, is_driver_funded_discount, '
    'is_airport, is_intercity',
    [
        (True, True, 'not_existing', True, True, True, True, True, True),
        (
            False,
            False,
            'combo_outer',
            False,
            False,
            False,
            False,
            False,
            False,
        ),
    ],
)
@pytest.mark.parametrize(
    'should_fail,dp_values',
    [(False, {'c': 1, 'r': -1}), (False, {'c': 1, 'r': 0}), (True, {'c': 0})],
)
@pytest.mark.config(
    DRIVER_METRICS_PROPERTIES_FROM_REQUIREMENTS=['hourly_rental'],
    DRIVER_METRICS_FALLBACK_ACTIVITY_VALUE=67,
)
async def test_predictions(
        acquire_candidate,
        order_core,
        stq_runner,
        mockserver,
        should_fail,
        dp_values,
        is_chain,
        has_hourly_rental,
        is_verybusy,
        is_autoaccept,
        alternative_type,
        is_driver_funded_discount,
        return_priority,
        is_airport,
        is_intercity,
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
        return {'candidates': [candidate]}

    @mockserver.json_handler('/autoaccept/v1/decide-autoaccept')
    def _decide_autoaccept(request):
        return {'autoaccept': {'enabled': is_autoaccept}}

    @mockserver.json_handler('/driver-metrics/v2/lookup_info/')
    def _v2_lookup_info(request):
        body = json.loads(request.get_data())
        if is_chain:
            assert body['candidate']['distance_to_a'] == (211 - 125)
            assert body['candidate']['time_to_a'] == 60

        order_properties = body['order']['properties']
        assert has_hourly_rental == ('hourly_rental' in order_properties)
        assert is_verybusy == ('verybusy_offer' in order_properties)
        assert 'lookup_mode_direct' in order_properties
        assert alternative_type in order_properties
        assert is_autoaccept == ('autoaccept' in order_properties)
        assert is_driver_funded_discount == (
            'driver_funded_discount' in order_properties
        )
        assert is_airport == (
            (body['order'].get('source_object_type') == 'аэропорт')
            and body['order'].get('last_dest_object_type') == 'организация'
        )
        assert is_intercity == ('intercity' in order_properties)

        if not should_fail:
            response = {
                'prediction': (
                    {
                        'type': 'priority',
                        'value': DP_FIRST_VALUE,
                        'value_changes': dp_values,
                        'blocking': {'duration_sec': 172800, 'threshold': 30},
                        'scores_to_next_level': 4,
                    }
                    if return_priority
                    else {
                        'type': 'activity',
                        'value': DP_FIRST_VALUE,
                        'value_changes': dp_values,
                        'blocking': {'duration_sec': 172800, 'threshold': 30},
                    }
                ),
                'ident': 'dlsjfslkfj',
                'distance_type': 'long',
            }
            return response
        return mockserver.make_response(status=404)

    order = lookup_params.create_params()
    order['order']['calc']['alternative_type'] = alternative_type
    if has_hourly_rental:
        order['order']['request']['requirements'] = {'hourly_rental': 1}
    if is_driver_funded_discount:
        order['order']['pricing_data'] = {
            'user': {'meta': {'driver_funded_discount_value': 1.4}},
        }
    if is_airport:
        order['order']['request']['source']['object_type'] = 'аэропорт'
        order['order']['request']['destinations'][0][
            'object_type'
        ] = 'организация'
    if is_intercity:
        order['order']['intercity'] = {'enabled': True}

    candidate = await acquire_candidate(order)
    driver_metrics = candidate['driver_metrics']

    expected_driver_points = 67
    if should_fail:
        assert driver_metrics == {
            'activity': 67,
            'activity_blocking': {
                'activity_threshold': 30,
                'duration_sec': 3600,
            },
            'activity_prediction': {'c': 0},
            'dispatch': None,
            'id': None,
            'properties': None,
            'type': 'fallback',
        }
    else:
        if not return_priority:
            expected_driver_points = DP_FIRST_VALUE
        expected = (
            {
                'activity': 67,
                'activity_blocking': None,
                'activity_prediction': None,
                'dispatch': 'long',
                'id': 'dlsjfslkfj',
                'priority': DP_FIRST_VALUE,
                'priority_blocking': {'duration_sec': 172800, 'threshold': 30},
                'priority_prediction': dp_values,
                'properties': None,
                'scores_to_next_level': 4,
                'type': 'dm_service',
            }
            if return_priority
            else {
                'activity': DP_FIRST_VALUE,
                'activity_blocking': {
                    'duration_sec': 172800,
                    'activity_threshold': 30,
                },
                'activity_prediction': dp_values,
                'dispatch': 'long',
                'id': 'dlsjfslkfj',
                'properties': None,
                'type': 'dm_service',
            }
        )
        assert driver_metrics == expected
    assert candidate['driver_points'] == expected_driver_points


@pytest.mark.experiments3(
    name='lookup_contractor_usage',
    consumers=['lookup/acquire'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {'type': 'true'},
            'value': {'enable': True},
            'title': 'Title',
            'enabled': True,
        },
    ],
    default_value={'enable': True},
)
@pytest.mark.config(DRIVER_METRICS_FALLBACK_ACTIVITY_VALUE=73)
@pytest.mark.parametrize(
    'return_data, expected_data',
    [
        pytest.param(
            {
                'type': 'activity',
                'value': 10,
                'blocking': {'threshold': 30, 'duration_sec': 3600},
                'value_changes': {'c': 0},
            },
            {
                'activity': 10,
                'activity_blocking': {
                    'duration_sec': 3600,
                    'activity_threshold': 30,
                },
                'activity_prediction': {'c': 0},
                'dispatch': 'long',
                'id': 'dlsjfslkfj',
                'properties': None,
                'type': 'dm_service',
            },
            id='dm_activity',
        ),
        pytest.param(
            {
                'type': 'priority',
                'value': 10,
                'blocking': {'threshold': 30, 'duration_sec': 3600},
                'value_changes': {'c': 0},
            },
            {
                'activity': 73,
                'activity_blocking': None,
                'activity_prediction': None,
                'dispatch': 'long',
                'id': 'dlsjfslkfj',
                'priority': 10,
                'priority_blocking': {'duration_sec': 3600, 'threshold': 30},
                'priority_prediction': {'c': 0},
                'properties': None,
                'type': 'dm_service',
            },
            id='dm_priority',
        ),
        pytest.param(
            None,
            {
                'activity': 73,
                'activity_blocking': {
                    'duration_sec': 3600,
                    'activity_threshold': 30,
                },
                'activity_prediction': {'c': 0},
                'dispatch': None,
                'id': None,
                'properties': None,
                'type': 'fallback',
            },
            id='dm_fallback',
        ),
    ],
)
async def test_lookup_contractor_base(
        stq_runner, mockserver, mocked_time, return_data, expected_data,
):
    @mockserver.json_handler('/driver-metrics/v2/lookup_info/')
    def _v2_lookup_info(request):
        if not return_data:
            return mockserver.make_response(status=500)
        return {
            'prediction': return_data,
            'ident': 'dlsjfslkfj',
            'distance_type': 'long',
        }

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/new_driver_found',
    )
    def order_core_event(request):
        body = bson.BSON.decode(request.get_data())
        assert (
            body['extra_update']['$push']['candidates']['driver_metrics']
            == expected_data
        )
        assert (
            body['extra_update']['$push']['candidates']['driver_points']
            == expected_data['activity']
        )

        return mockserver.make_response('', 200)

    now_time = datetime.datetime(
        2021, 7, 14, 8, 57, 36, tzinfo=datetime.timezone.utc,
    )
    mocked_time.set(now_time)
    await stq_runner.lookup_contractor.call(
        task_id='order_id', args=[], kwargs={'order_id': 'id'},
    )
    assert order_core_event.has_calls
