import copy

import pytest

from tests_united_dispatch.plugins import cargo_dispatch_manager
from tests_united_dispatch.united_dispatch_grocery import common


@common.set_common_limits(
    max_orders=3, max_grocery_orders=2, max_market_orders=2,
)
@common.set_candidate_limits()
@common.FOR_EACH_ALGORITHM
@pytest.mark.now(common.NOW)
@pytest.mark.experiments3(
    name='united_dispatch_grocery_market_slot_rules',
    consumers=['united-dispatch/grocery_market_slot_kwargs'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'stage_name': 'default',
        'created_offset': 0,
        'treat_as_grocery_segment': False,
        'allow_batching_without_grocery_segment': False,
    },
    is_config=True,
)
async def test_market_orders_batch_with_grocery_order(
        taxi_united_dispatch_grocery,
        mockserver,
        create_segment,
        propositions_manager: cargo_dispatch_manager.PropositionsManager,
        state_waybill_proposed,
        grocery_depots,
        candidates,
        experiments3,
        algorithm,
):
    experiments3.add_config(
        name='united_dispatch_grocery_matching_algorithm',
        consumers=['united-dispatch/grocery_kwargs'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={'primary': algorithm},
    )

    depot_location = [37.410, 55.720]
    grocery_depots.add_depot(
        123, location={'lon': depot_location[0], 'lat': depot_location[1]},
    )
    await taxi_united_dispatch_grocery.invalidate_caches()

    candidates(
        {
            'candidates': [
                {
                    'classes': ['lavka'],
                    'dbid': '420',
                    'uuid': '123',
                    'id': '420_123',
                    'position': [37.0, 55.0],
                    'route_info': {
                        'approximate': False,
                        'distance': 120,
                        'time': 10,
                    },
                    'status': {'orders': [], 'status': 'online'},
                    'transport': {'type': 'pedestrian'},
                },
            ],
        },
    )

    @mockserver.json_handler(
        '/grocery-checkins/internal/checkins/v2/queue-info',
    )
    def _queue_info(request):
        assert request.json == {'depot_id': '123'}

        return {
            'couriers': [
                {
                    'courier_id': '420_123',
                    'checkin_timestamp': '2020-10-05T16:28:00.000Z',
                },
            ],
        }

    market_custom_context = copy.deepcopy(common.VALID_CUSTOM_CTX)
    market_custom_context['grocery_market_slot'] = {
        'interval_start': common.NOW,
        'interval_end': common.NOW_PAST_ONE_HOUR,
    }

    for _ in range(5):
        create_segment(
            corp_client_id='grocery_corp_id1',
            taxi_classes={'lavka'},
            custom_context=market_custom_context,
            pickup_coordinates=depot_location,
            dropoff_coordinates=[37.412, 55.723],
            planner='grocery',
        )

    await state_waybill_proposed()
    assert not propositions_manager.propositions

    grocery_segment = create_segment(
        corp_client_id='grocery_corp_id1',
        taxi_classes={'lavka'},
        custom_context=common.VALID_CUSTOM_CTX,
        pickup_coordinates=depot_location,
        dropoff_coordinates=[37.412, 55.723],
        planner='grocery',
    )

    await state_waybill_proposed()
    assert len(propositions_manager.propositions) == 1
    assert len(propositions_manager.propositions[0]['segments']) == 3
    assert (
        propositions_manager.propositions[0]['segments'][0]['segment_id']
        == grocery_segment.id
    )


@common.set_common_limits(
    max_orders=3, max_grocery_orders=2, max_market_orders=2,
)
@common.set_candidate_limits()
@common.FOR_EACH_ALGORITHM
@pytest.mark.now(common.NOW)
@pytest.mark.experiments3(
    name='united_dispatch_grocery_market_slot_rules',
    consumers=['united-dispatch/grocery_market_slot_kwargs'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={
        'stage_name': 'default',
        'created_offset': 0,
        'treat_as_grocery_segment': False,
        'allow_batching_without_grocery_segment': True,
    },
    is_config=True,
)
async def test_market_orders_batch_without_grocery_order(
        taxi_united_dispatch_grocery,
        mockserver,
        create_segment,
        propositions_manager: cargo_dispatch_manager.PropositionsManager,
        state_waybill_proposed,
        grocery_depots,
        candidates,
        experiments3,
        algorithm,
):
    experiments3.add_config(
        name='united_dispatch_grocery_matching_algorithm',
        consumers=['united-dispatch/grocery_kwargs'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={'primary': algorithm},
    )

    depot_location = [37.410, 55.720]
    grocery_depots.add_depot(
        123, location={'lon': depot_location[0], 'lat': depot_location[1]},
    )
    await taxi_united_dispatch_grocery.invalidate_caches()

    candidates(
        {
            'candidates': [
                {
                    'classes': ['lavka'],
                    'dbid': '420',
                    'uuid': '123',
                    'id': '420_123',
                    'position': [37.0, 55.0],
                    'route_info': {
                        'approximate': False,
                        'distance': 120,
                        'time': 10,
                    },
                    'status': {'orders': [], 'status': 'online'},
                    'transport': {'type': 'pedestrian'},
                },
            ],
        },
    )

    @mockserver.json_handler(
        '/grocery-checkins/internal/checkins/v2/queue-info',
    )
    def _queue_info(request):
        assert request.json == {'depot_id': '123'}

        return {
            'couriers': [
                {
                    'courier_id': '420_123',
                    'checkin_timestamp': '2020-10-05T16:28:00.000Z',
                },
            ],
        }

    market_custom_context = copy.deepcopy(common.VALID_CUSTOM_CTX)
    market_custom_context['grocery_market_slot'] = {
        'interval_start': common.NOW,
        'interval_end': common.NOW_PAST_ONE_HOUR,
    }

    create_segment(
        corp_client_id='grocery_corp_id1',
        taxi_classes={'lavka'},
        custom_context=market_custom_context,
        pickup_coordinates=depot_location,
        dropoff_coordinates=[37.412, 55.723],
        planner='grocery',
    )

    await state_waybill_proposed()
    assert not propositions_manager.propositions

    create_segment(
        corp_client_id='grocery_corp_id1',
        taxi_classes={'lavka'},
        custom_context=market_custom_context,
        pickup_coordinates=depot_location,
        dropoff_coordinates=[37.412, 55.723],
        planner='grocery',
    )

    await state_waybill_proposed()
    assert len(propositions_manager.propositions) == 1
    assert len(propositions_manager.propositions[0]['segments']) == 2
