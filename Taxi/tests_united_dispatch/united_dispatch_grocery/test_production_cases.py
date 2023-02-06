import pytest

from tests_united_dispatch.plugins import cargo_dispatch_manager
from tests_united_dispatch.united_dispatch_grocery import common


@common.set_common_limits(
    max_orders=2,
    max_grocery_orders=2,
    max_market_orders=2,
    cte_limit=2400,
    distance_diff_limit=1200,
)
@common.set_candidate_limits(
    speed=2.3, max_weight=25000, dropoff_time=300, max_distance=10000,
)
@pytest.mark.now('2022-05-17T11:49:57+00:00')
async def test_production_case_1(
        taxi_united_dispatch_grocery,
        mockserver,
        create_segment,
        propositions_manager: cargo_dispatch_manager.PropositionsManager,
        state_waybill_proposed,
        grocery_depots,
        candidates,
        experiments3,
):
    experiments3.add_config(
        name='united_dispatch_grocery_matching_algorithm',
        consumers=['united-dispatch/grocery_kwargs'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[],
        default_value={'primary': 'match_couriers_to_orders_v2'},
    )

    grocery_depots.add_depot(
        123, location={'lon': 30.338209, 'lat': 59.820286},
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
                    'position': [30.338209, 59.820286],
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
                    'checkin_timestamp': '2022-05-17T11:45:57+00:00',
                },
            ],
        }

    create_segment(
        corp_client_id='grocery_corp_id1',
        taxi_classes={'lavka'},
        custom_context={
            'depot_id': '123',
            'dispatch_id': '55ae949f-656b-4246-8396-90fe572c6d05',
            'order_id': '984788a4796f49e693a05fb2cfda09dc-grocery',
            'dispatch_wave': 0,
            'weight': 10888,
            'created': '2022-05-17T11:45:42.597129+00:00',
            'delivery_flags': {},
            'region_id': 2,
        },
        pickup_coordinates=[30.338209, 59.820286],
        dropoff_coordinates=[30.343482313198862, 59.82446143517658],
    )

    create_segment(
        corp_client_id='grocery_corp_id1',
        taxi_classes={'lavka'},
        custom_context={
            'depot_id': '123',
            'dispatch_id': 'e6bcfdc6-1d83-4ff6-bee9-61a31858f5b7',
            'order_id': '41a6eb0bafb848a48f9eca41f901bfdd-grocery',
            'dispatch_wave': 0,
            'weight': 3280,
            'created': '2022-05-17T11:46:16.247055+00:00',
            'delivery_flags': {},
            'region_id': 2,
        },
        pickup_coordinates=[30.338209, 59.820286],
        dropoff_coordinates=[30.332163540618954, 59.82039946201968],
    )

    await state_waybill_proposed()
    assert len(propositions_manager.propositions) == 1
    assert len(propositions_manager.propositions[0]['segments']) == 2
