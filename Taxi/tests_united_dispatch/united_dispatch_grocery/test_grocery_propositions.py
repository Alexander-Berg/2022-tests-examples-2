import pytest

from tests_united_dispatch.plugins import cargo_dispatch_manager
from tests_united_dispatch.united_dispatch_grocery import common

ROUTER_ID = 'united-dispatch'


@common.set_common_limits()
@common.set_candidate_limits()
@common.FOR_EACH_ALGORITHM
@pytest.mark.now(common.NOW)
async def test_grocery_matching(
        taxi_united_dispatch_grocery,
        mockserver,
        create_segment,
        propositions_manager: cargo_dispatch_manager.PropositionsManager,
        state_waybill_proposed,
        get_segment,
        get_waybill,
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
    await taxi_united_dispatch_grocery.invalidate_caches(
        cache_names=['grocery-depots-cache', 'experiments3-cache'],
    )

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
                {
                    'courier_id': '27_123',
                    'checkin_timestamp': '2020-10-05T16:28:00.000Z',
                },
            ],
        }

    seg1 = create_segment(
        corp_client_id='grocery_corp_id1',
        taxi_classes={'lavka'},
        custom_context=common.VALID_CUSTOM_CTX,
        pickup_coordinates=depot_location,
        dropoff_coordinates=[37.412, 55.723],
        planner='grocery',
    )
    seg2 = create_segment(
        corp_client_id='grocery_corp_id1',
        taxi_classes={'lavka'},
        custom_context=common.VALID_CUSTOM_CTX,
        pickup_coordinates=depot_location,
        dropoff_coordinates=[37.415, 55.721],
        planner='grocery',
    )

    await state_waybill_proposed()
    assert len(propositions_manager.propositions) == 1

    segment_info1 = get_segment(seg1.id)
    segment_info2 = get_segment(seg2.id)

    assert segment_info1['waybill_ref'] == segment_info2['waybill_ref']

    waybill = get_waybill(segment_info1['waybill_ref'])
    assert waybill['candidate']['info']['id'] == '420_123'
