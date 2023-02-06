import pytest


GAMBLE_SETTINGS_CONSUMER = 'united-dispatch/planner-run'
ROUTER_ID = 'united-dispatch'


async def test_fallback_algorithm_usage_no_config(
        testpoint, state_waybill_proposed, taxi_united_dispatch_delivery,
):
    """
    Fallback router should be used if no config for Delivery
    planner is available
    """

    @testpoint('delivery_planner::algorithm')
    def check_algorithm(data):
        assert data == 'fallback'

    await taxi_united_dispatch_delivery.invalidate_caches()
    await state_waybill_proposed()

    assert check_algorithm.times_called


@pytest.mark.parametrize(
    'config_use_taxi_dispatch, test_name',
    [
        (True, '`use_taxi_dispatch` is set as true'),
        (False, '`use_taxi_dispatch` is set as false'),
    ],
)
async def test_fallback_algorithm_usage(
        testpoint,
        state_waybill_proposed,
        exp_delivery_gamble_settings,
        exp_delivery_configs,
        propositions_manager,
        config_use_taxi_dispatch,
        test_name,
):
    should_use_fallback_algorithm = config_use_taxi_dispatch

    @testpoint('delivery_planner::algorithm')
    def check_algorithm(data):
        fallback_is_used = data == 'fallback'
        assert (
            fallback_is_used == should_use_fallback_algorithm
        ), f'failed test: {test_name}'

    await exp_delivery_gamble_settings(
        use_taxi_dispatch=config_use_taxi_dispatch,
    )
    await exp_delivery_configs(delivery_gamble_settings=False)

    await state_waybill_proposed()

    assert check_algorithm.times_called
    assert propositions_manager.propositions


@pytest.mark.parametrize('segments_count', [1, 2])
async def test_waybill_ref_from_route(
        testpoint,
        state_waybill_proposed,
        exp_delivery_gamble_settings,
        exp_delivery_configs,
        propositions_manager,
        load_json,
        mockserver,
        create_segment,
        segments_count,
):
    segment_ids = []
    for _ in range(segments_count):
        segment_ids.append(create_segment().id)

    candidates = load_json('candidates.json')

    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        return candidates

    built_waybill_refs = []
    generated_waybill_refs = []

    @testpoint('delivery_planner::pre_routes')
    def check_pre_routes_waybill_ref(data):
        for route in data['routes']:
            assert route['waybill_ref']

            if route['generator'] == 'single-segment':
                built_waybill_refs.append(route['waybill_ref'])
            else:
                generated_waybill_refs.append(route['waybill_ref'])

    await exp_delivery_gamble_settings(use_taxi_dispatch=False)
    await exp_delivery_configs(delivery_gamble_settings=False)

    await state_waybill_proposed()
    assert check_pre_routes_waybill_ref.times_called

    assert len(propositions_manager.propositions) == 1
    waybill = propositions_manager.propositions[0]

    if segments_count == 1:
        assert len(built_waybill_refs) == 1
        assert not generated_waybill_refs

        assert waybill['external_ref'] in built_waybill_refs
        assert waybill['external_ref'].startswith(f'{ROUTER_ID}/0/delivery/')

    else:
        assert len(built_waybill_refs) == 2
        assert len(generated_waybill_refs) == 2

        assert waybill['external_ref'] not in built_waybill_refs
        assert waybill['external_ref'] in generated_waybill_refs


@pytest.mark.parametrize(
    'custom_context, segments_count',
    [
        ({}, 1),
        ({'delivery_flags': {'assign_rover': True}}, 2),
        ({'delivery_flags': {'assign_rover': False}}, 2),
    ],
)
async def test_delivery_assign_rover_param(
        state_waybill_proposed,
        exp_delivery_gamble_settings,
        exp_delivery_configs,
        load_json,
        mockserver,
        create_segment,
        custom_context,
        segments_count,
):
    segment_ids = []
    for _ in range(segments_count):
        segment_ids.append(create_segment(custom_context=custom_context).id)

    candidates = load_json('candidates.json')

    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        if not custom_context:
            assert request.json.get('logistic') is None
        else:
            assert (
                request.json['logistic']['include_rovers']
                == custom_context['delivery_flags']['assign_rover']
            )
        return candidates

    await exp_delivery_gamble_settings(use_taxi_dispatch=False)
    await exp_delivery_configs(delivery_gamble_settings=False)
    await state_waybill_proposed()

    assert _order_search.times_called
