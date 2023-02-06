import pytest

from testsuite.utils import matching

from .. import conftest

FIRST_DRIVER_INFO = {'park_id': 'park_id1', 'driver_profile_id': 'driver_id1'}

SECOND_DRIVER_INFO = {'park_id': 'park_id2', 'driver_profile_id': 'driver_id2'}

CALC_ID = 'cargo-pricing/v1/' + 'A' * 32


async def run_stq(stq_runner, claim_uuid):
    await stq_runner.cargo_claims_change_claim_order_price.call(
        task_id=claim_uuid,
        args=[claim_uuid, '123.0', 'initial_price'],
        expect_fail=False,
    )


@pytest.fixture(name='complete_segment')
def _complete_segment(taxi_cargo_claims, build_segment_update_request):
    async def wrapper(
            segment_id, taxi_order_id='taxi_order_id_1', resolution='complete',
    ):
        response = await taxi_cargo_claims.post(
            'v1/segments/dispatch/bulk-update-state',
            json={
                'segments': [
                    build_segment_update_request(
                        segment_id,
                        taxi_order_id,
                        revision=5,
                        resolution=resolution,
                    ),
                ],
            },
        )
        assert response.status_code == 200

    return wrapper


async def test_change_price_with_cargo_pricing(
        taxi_cargo_claims,
        state_controller,
        stq_runner,
        prepare_state,
        get_segment,
        mock_cargo_pricing_calc,
        complete_segment,
        get_final_pricing_id,
        mock_waybill_info,
        get_default_pricing_calc_request,
):
    additional_items = [
        {
            'title': 'new item 1',
            'cost_value': '10.40',
            'cost_currency': 'RUB',
            'weight': 4.1,
            'quantity': 4,
        },
        {
            'title': 'new item 2',
            'size': {'width': 2.1, 'length': 13.0, 'height': 3.1},
            'quantity': 5,
            'cost_value': '0.20',
            'cost_currency': 'RUB',
        },
    ]

    segment_id = await prepare_state(
        visit_order=3,
        cargo_pricing_flow=True,
        skip_arrive=True,
        additional_cargo_items=additional_items,
    )
    claim_uuid = (await get_segment(segment_id))['diagnostics']['claim_id']

    await complete_segment(segment_id)

    await run_stq(stq_runner, claim_uuid)

    new_claim_info = await state_controller.get_claim_info()
    assert (
        new_claim_info.claim_full_response['pricing']['final_price']
        == '241.1988'
    )
    calc_request = mock_cargo_pricing_calc.request
    waypoint_ids = []
    for waypoint in calc_request['waypoints']:
        waypoint['resolution_info'].pop('resolved_at')
        waypoint_ids.append(waypoint['id'])
    calc_request['resolution_info'].pop('resolved_at')
    expected_calc_request = get_default_pricing_calc_request(
        claim_uuid, waypoint_ids,
    )
    pickup_point_id = calc_request['waypoints'][0]['id']
    droppof_point_id = calc_request['waypoints'][1]['id']
    expected_calc_request['cargo_items'].extend(
        [
            {
                'dropoff_point_id': droppof_point_id,
                'pickup_point_id': pickup_point_id,
                'quantity': 4,
                'weight': 4.1,
            },
            {
                'dropoff_point_id': droppof_point_id,
                'pickup_point_id': pickup_point_id,
                'quantity': 5,
                'size': {'height': 3.1, 'length': 13.0, 'width': 2.1},
            },
        ],
    )

    assert calc_request == expected_calc_request

    assert CALC_ID == get_final_pricing_id(claim_uuid=claim_uuid)


async def test_change_price_with_cargo_pricing_and_pro_courier(
        taxi_cargo_claims,
        state_controller,
        stq_runner,
        prepare_state,
        get_segment,
        mock_cargo_pricing_calc,
        complete_segment,
        get_final_pricing_id,
        mock_waybill_info,
        get_default_pricing_calc_request,
):
    segment_id = await prepare_state(
        visit_order=3,
        cargo_pricing_flow=True,
        pro_courier=True,
        finish_estimate_pro_courier_requirements=True,
    )
    claim_uuid = (await get_segment(segment_id))['diagnostics']['claim_id']

    await complete_segment(segment_id)

    await run_stq(stq_runner, claim_uuid)

    new_claim_info = await state_controller.get_claim_info()
    assert (
        new_claim_info.claim_full_response['pricing']['final_price']
        == '241.1988'
    )
    calc_request = mock_cargo_pricing_calc.request
    waypoint_ids = []
    for waypoint in calc_request['waypoints']:
        waypoint['resolution_info'].pop('resolved_at')
        waypoint.pop('first_time_arrived_at', None)
        waypoint_ids.append(waypoint['id'])
    calc_request['resolution_info'].pop('resolved_at')
    expected_calc_request = get_default_pricing_calc_request(
        claim_uuid, waypoint_ids,
    )
    expected_calc_request['taxi_requirements']['pro_courier'] = 1
    assert calc_request == expected_calc_request

    assert CALC_ID == get_final_pricing_id(claim_uuid=claim_uuid)


async def test_change_price_with_cargo_pricing_and_extra_requirements(
        taxi_cargo_claims,
        state_controller,
        stq_runner,
        prepare_state,
        get_segment,
        mock_cargo_pricing_calc,
        complete_segment,
        get_final_pricing_id,
        mock_waybill_info,
):
    segment_id = await prepare_state(
        visit_order=3,
        cargo_pricing_flow=True,
        client_extra_requirement=17,
        finish_estimate_extra_requirement=18,
    )
    claim_uuid = (await get_segment(segment_id))['diagnostics']['claim_id']

    await complete_segment(segment_id)

    await run_stq(stq_runner, claim_uuid)

    calc_request = mock_cargo_pricing_calc.request
    assert calc_request['taxi_requirements']['extra_requirement'] == 18

    assert CALC_ID == get_final_pricing_id(claim_uuid=claim_uuid)


@pytest.mark.skip('TODO: fix in CARGODEV-11356')
@pytest.mark.parametrize('enable_driver_client_prices_differ', [True, False])
async def test_change_price_for_non_decoupling(
        taxi_cargo_claims,
        state_controller,
        stq_runner,
        prepare_state,
        get_segment,
        complete_segment,
        get_final_pricing_id,
        mockserver,
        load_json,
        taxi_config,
        enable_driver_client_prices_differ,
        mock_waybill_info,
        mock_create_event,
        mock_cargo_pricing_retrieve,
):
    mock_create_event()
    taxi_config.set_values(
        {
            'CARGO_CLAIMS_ENABLE_NONDECOUPLING_PRICES_DIFFERENCE': (
                enable_driver_client_prices_differ
            ),
        },
    )

    if enable_driver_client_prices_differ:
        expected_calc_id = 'cargo-pricing/v1/aaa_client'
    else:
        # old way
        expected_calc_id = 'cargo-pricing/v1/aaa_driver'

    @mockserver.json_handler('/int-authproxy/v1/profile')
    def _profile(request):
        return {
            'dont_ask_name': False,
            'experiments': [],
            'name': 'Насруло',
            'personal_phone_id': 'personal_phone_id_1',
            'user_id': 'taxi_user_id_1',
        }

    mock_cargo_pricing_retrieve.expected_calc_id = expected_calc_id

    state_controller.use_create_version('v2_cargo_c2c')
    state_controller.set_options(payment_type='card')
    state_controller.set_options(payment_method_id='card-123')
    state_controller.set_options(cargo_pricing_flow=True)

    segment_id = await prepare_state(
        visit_order=3, target_status='performer_found',
    )
    claim_uuid = (await get_segment(segment_id))['diagnostics']['claim_id']
    await complete_segment(segment_id)

    await run_stq(stq_runner, claim_uuid)

    assert mock_waybill_info.mock.times_called == 1
    assert mock_cargo_pricing_retrieve.mock.times_called == 1

    new_claim_info = await state_controller.get_claim_info()
    assert (
        new_claim_info.claim_full_response['pricing']['final_price']
        == '200.9990'
    )

    assert get_final_pricing_id(claim_uuid=claim_uuid) == expected_calc_id


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_execution_reset',
    consumers=['cargo-claims/geocoder'],
    clauses=[],
    default_value={
        'reset_points_on_new_driver_found': True,
        'validate_driver_on_arrive_at_point': False,
    },
    is_config=True,
)
async def test_first_arrived_timestamp_correctness_after_reorder(
        taxi_cargo_claims,
        stq_runner,
        prepare_state,
        get_segment,
        build_segment_update_request,
        get_claim_update_datetime,
        mock_cargo_pricing_calc,
        arrive_at_point,
        mock_waybill_info,
):
    """
    1) First driver arrived at point
    2) Taxi autoreorder was happened
    3) Second driver arrived at point

    Check first_arrived timestamp correctness
    """

    segment_id = await prepare_state(
        visit_order=1,
        cargo_pricing_flow=True,
        skip_arrive=True,
        last_arrive_at_point=False,
        last_exchange_init=False,
    )
    claim_uuid = (await get_segment(segment_id))['diagnostics']['claim_id']

    # First driver arrived
    await arrive_at_point(segment_id, 1, FIRST_DRIVER_INFO)
    # first_driver_timestamp = get_claim_update_datetime()

    # Second driver was found
    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    'taxi_order_id_1',
                    with_performer=True,
                    driver_id='new_driver_132',
                    revision=5,
                ),
            ],
        },
    )
    assert response.status_code == 200

    # Second driver arrived
    await arrive_at_point(segment_id, 1, SECOND_DRIVER_INFO)

    # TODO: CARGODEV-11296 maybe here we need exact resolution in segment info
    # second_driver_timestamp = get_claim_update_datetime()

    # Recalc price
    await run_stq(stq_runner, claim_uuid)

    # TODO: CARGODEV-11296 maybe here we need exact resolution in segment info
    # first_time_arrived_at = datetime.datetime.strptime(
    #     mock_cargo_pricing_calc.request['waypoints'][0][
    #         'first_time_arrived_at'
    #     ],
    #     '%Y-%m-%dT%H:%M:%S.%f%z',
    # )

    # assert first_time_arrived_at == second_driver_timestamp


async def test_failed_segment_calculation(
        taxi_cargo_claims,
        state_controller,
        stq_runner,
        prepare_state,
        get_segment,
        mock_cargo_pricing_calc,
        complete_segment,
        get_final_pricing_id,
        mock_waybill_info,
):

    segment_id = await prepare_state(visit_order=1, cargo_pricing_flow=True)
    claim_uuid = (await get_segment(segment_id))['diagnostics']['claim_id']
    await complete_segment(segment_id, resolution='failed')

    await stq_runner.cargo_claims_change_claim_order_price.call(
        task_id=claim_uuid,
        args=[claim_uuid, '', 'initial_price'],
        expect_fail=False,
    )

    calc_request = mock_cargo_pricing_calc.request
    resolution_info = calc_request.pop('resolution_info')
    assert resolution_info['resolution'] == 'failed_by_performer'
    for waypoint in calc_request['waypoints']:
        assert waypoint['resolution_info']['resolution'] == 'skipped'
    assert CALC_ID == get_final_pricing_id(claim_uuid=claim_uuid)


@pytest.mark.config(CARGO_CLAIMS_CHANGE_PRICE_IGNORE_REASONS=['ignored'])
@pytest.mark.parametrize('ignored', [True, False])
async def test_ignored_by_config(
        stq_runner,
        mock_waybill_info,
        ignored: bool,
        claim_uuid='no_such_claim',
):
    await stq_runner.cargo_claims_change_claim_order_price.call(
        task_id=claim_uuid,
        args=[claim_uuid, '123.0', 'ignored' if ignored else 'not_ignored'],
        expect_fail=not ignored,
    )


@pytest.mark.config(CARGO_CLAIMS_CHANGE_PRICE_IGNORE_REASONS=[])
async def test_fallback_pricing(
        create_segment_with_performer, stq_runner, get_claim_inner_v2,
):
    creator = await create_segment_with_performer(optional_return=True)

    await stq_runner.cargo_claims_change_claim_order_price.call(
        task_id=creator.claim_id,
        args=[creator.claim_id, '', 'dragon_initial_price'],
        expect_fail=False,
    )

    claim = await get_claim_inner_v2(creator.claim_id)
    assert claim['pricing']['final_price'] == '147.6000'


@pytest.mark.parametrize(
    ['cargo_pricing_price', 'expected_event_price'],
    [('733.213', '733.213'), ('12', '12.0'), ('0', '0.0')],
)
async def test_change_price_processing_callback(
        query_processing_events,
        stq_runner,
        prepare_state,
        get_segment,
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        mock_cargo_pricing_calc,
        cargo_pricing_price,
        expected_event_price,
        mock_waybill_info,
):
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()

    mock_cargo_pricing_calc.total_price = cargo_pricing_price
    segment_id = await prepare_state(visit_order=3, cargo_pricing_flow=True)
    claim_uuid = (await get_segment(segment_id))['diagnostics']['claim_id']

    await run_stq(stq_runner, claim_uuid=claim_uuid)

    event = query_processing_events(claim_uuid)[-1]
    assert event.payload['data'].pop('claim_revision') > 0
    # TODO: CARGODEV-11296 maybe here we need exact resolution in segment info
    # assert event.payload == {
    #     'data': {
    #         'total_price': expected_event_price,
    #         'phoenix_claim': False,
    #         'calc_id': CALC_ID,
    #     },
    #     'kind': 'price-changed',
    #     'status': 'delivered',
    # }


async def test_change_price_processing_callback_new_calc_id(
        query_processing_events,
        prepare_state,
        get_segment,
        procaas_claim_status_filter,
        procaas_event_kind_filter,
        set_offer_calc_id,
        set_final_calc_id,
):
    await procaas_claim_status_filter()
    await procaas_event_kind_filter()

    new_calc_id = 'cargo-pricing/v1/' + 'B' * 32
    segment_id = await prepare_state(visit_order=3, cargo_pricing_flow=True)
    claim_uuid = (await get_segment(segment_id))['diagnostics']['claim_id']

    set_offer_calc_id(claim_uuid, CALC_ID)
    first_event = query_processing_events(claim_uuid)[-1]

    set_final_calc_id(claim_uuid, new_calc_id)
    second_event = query_processing_events(claim_uuid)[-1]

    assert first_event.payload['data']['calc_id'] == CALC_ID
    assert second_event.payload['data']['calc_id'] == new_calc_id

    assert (
        first_event.payload['data']['calc_id']
        != second_event.payload['data']['calc_id']
    )


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_claims_execution_reset',
    consumers=['cargo-claims/geocoder'],
    clauses=[],
    default_value={
        'reset_points_on_new_driver_found': True,
        'validate_driver_on_arrive_at_point': False,
    },
    is_config=True,
)
async def test_cargo_pricing_request_waypoint_status_pending_reset(
        create_segment_with_performer,
        taxi_cargo_claims,
        get_segment,
        get_segment_id,
        claim_point_id_by_visit_order,
        get_default_cargo_order_id,
        build_segment_update_request,
        stq_runner,
        mock_cargo_pricing_calc,
        mock_waybill_info,
):
    """
    1) First driver arrived at point
    2) Taxi autoreorder was happened
    3) Check: calc price without points status for first driver
    """

    await create_segment_with_performer(cargo_pricing_flow=True)
    segment_id = await get_segment_id()

    # First driver arrived
    claim_point_id = await claim_point_id_by_visit_order(
        segment_id=segment_id, visit_order=1,
    )
    response = await taxi_cargo_claims.post(
        '/v1/segments/arrive_at_point',
        params={'segment_id': segment_id},
        json={
            'cargo_order_id': get_default_cargo_order_id,
            'last_known_status': 'new',
            'point_id': claim_point_id,
            'idempotency_token': '100500',
            'driver': {
                'park_id': 'park_id1',
                'driver_profile_id': 'driver_id1',
            },
        },
        headers={'X-Real-IP': '12.34.56.78'},
    )
    assert response.status_code == 200

    # New driver was found
    response = await taxi_cargo_claims.post(
        'v1/segments/dispatch/bulk-update-state',
        json={
            'segments': [
                build_segment_update_request(
                    segment_id,
                    'taxi_order_id_1',
                    with_performer=True,
                    driver_id='new_driver_132',
                    revision=3,
                ),
            ],
        },
    )
    assert response.status_code == 200

    # Check changelog
    segment = await get_segment(segment_id)
    first_point_changelog = next(
        p['changelog'] for p in segment['points'] if p['visit_order'] == 1
    )
    assert first_point_changelog == [
        {'status': 'pending', 'timestamp': matching.AnyString()},
        {
            'status': 'arrived',
            'driver_id': 'driver_id1',
            'cargo_order_id': get_default_cargo_order_id,
            'timestamp': matching.AnyString(),
        },
        {
            'status': 'pending',
            'timestamp': matching.AnyString(),
            'cargo_order_id': get_default_cargo_order_id,
        },
    ]

    claim_uuid = (await get_segment(segment_id))['diagnostics']['claim_id']
    await run_stq(stq_runner, claim_uuid)

    # Check reseted status of first waypoint in pricing request
    # TODO: CARGODEV-11296 maybe here we need exact resolution in segment info
    # calc_request = mock_cargo_pricing_calc.request
    # waypoints = calc_request['waypoints']
    # assert waypoints[0].get('first_time_arrived_at') is None


@pytest.mark.config(CARGO_CLAIMS_CHANGE_PRICE_IGNORE_REASONS=[])
async def test_cancelled_without_segments_pricing(
        taxi_cargo_claims, state_controller, stq_runner, get_default_headers,
):
    state_controller.set_options(cargo_pricing_flow=True)
    claim_info = await state_controller.apply(target_status='cancelled')
    claim_uuid = claim_info.claim_id

    await stq_runner.cargo_claims_change_claim_order_price.call(
        task_id=claim_uuid,
        args=[claim_uuid, '', 'dragon_initial_price'],
        expect_fail=False,
    )
    new_claim_info = await state_controller.get_claim_info()
    pricing_data = new_claim_info.claim_full_response['pricing']
    assert pricing_data['final_pricing_calc_id'] == conftest.NO_PRICING_CALC_ID
    assert pricing_data['final_price'] == '0.0000'


async def test_change_price_with_pricing_dragon_handlers(
        taxi_cargo_claims,
        state_controller,
        stq_runner,
        prepare_state,
        get_segment,
        mock_cargo_pricing_resolve_segment,
        complete_segment,
        get_final_pricing_id,
        mock_waybill_info,
        enable_use_pricing_dragon_handlers_feature,
        get_default_pricing_calc_request,
):

    segment_id = await prepare_state(
        visit_order=3,
        cargo_pricing_flow=True,
        skip_arrive=True,
        is_phoenix=True,
    )
    claim_id = (await get_segment(segment_id))['diagnostics']['claim_id']

    await complete_segment(segment_id)
    await run_stq(stq_runner, claim_id)
    new_claim_info = await state_controller.get_claim_info()
    assert (
        new_claim_info.claim_full_response['pricing']['final_price']
        == '200.9990'
    )
    calc_request = mock_cargo_pricing_resolve_segment.request
    waypoint_ids = []
    for waypoint in calc_request['v1_request']['waypoints']:
        waypoint['resolution_info'].pop('resolved_at')
        waypoint_ids.append(waypoint['id'])
    calc_request['v1_request']['resolution_info'].pop('resolved_at')
    calc_request['segment']['resolution'].pop('resolved_at')
    expected_v1_request = get_default_pricing_calc_request(
        claim_id, waypoint_ids,
    )
    assert calc_request == {
        'segment': {
            'id': segment_id,
            'taxi_order_id': new_claim_info.claim_full_response[
                'taxi_order_id'
            ],
            'payment_info': expected_v1_request['payment_info'],
            'resolution': expected_v1_request['resolution_info'],
        },
        'v1_request': expected_v1_request,
    }
    assert CALC_ID == get_final_pricing_id(claim_uuid=claim_id)


async def test_cancel_before_estimating(
        taxi_cargo_claims,
        mockserver,
        get_default_headers,
        state_controller,
        stq_runner,
):
    claim_info = await state_controller.apply(target_status='estimating')

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/cancel',
        params={'claim_id': claim_info.claim_id},
        json={'version': 1, 'cancel_state': 'free'},
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': claim_info.claim_id,
        'status': 'cancelled',
        'version': 1,
        'user_request_revision': '1',
        'skip_client_notify': False,
    }
    new_claim_info = await state_controller.get_claim_info()
    assert new_claim_info.current_state.status == 'cancelled'

    await stq_runner.cargo_claims_change_claim_order_price.call(
        task_id=f'{claim_info.claim_id}',
        args=[f'{claim_info.claim_id}', '', 'initial_price'],
        expect_fail=False,
    )
