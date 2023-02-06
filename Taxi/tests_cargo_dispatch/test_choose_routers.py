import pytest


def test_happy_path_works(happy_path_state_routers_chosen):
    result = happy_path_state_routers_chosen
    assert result['stats']['new-segments-to-process'] == 5
    assert result['stats']['segments-to-update'] == 5
    assert result['stats']['routers-to-insert'] == 8
    assert result['stats']['updated-segments'] == 5
    assert result['stats']['inserted-routers'] == 8


async def test_process_only_new_segments(
        happy_path_state_routers_chosen, run_choose_routers,
):
    result = await run_choose_routers()
    assert result['stats']['new-segments-to-process'] == 0


@pytest.mark.now('2020-08-14T18:37:00.00+00:00')
async def test_without_due(happy_path_state_routers_chosen, get_segment_info):
    seginfo = await get_segment_info('seg1')
    assert (
        seginfo['dispatch']['waybill_building_deadline']
        == '2020-08-14T18:42:00+00:00'
    )


@pytest.mark.parametrize('with_shifting_lookup_ttl', [False, True])
@pytest.mark.now('2020-08-14T18:37:00.00+00:00')
async def test_with_lookup_ttl(
        happy_path_state_first_import,
        run_choose_routers,
        get_segment_info,
        happy_path_claims_segment_db,
        taxi_cargo_dispatch,
        taxi_config,
        with_shifting_lookup_ttl,
):
    if with_shifting_lookup_ttl:
        taxi_config.set(CARGO_DISPATCH_LOOKUP_TTL_SHIFT=15 * 60)
        await taxi_cargo_dispatch.invalidate_caches()

    shifted_lookup_ttl = lookup_ttl = '2020-08-14T17:15:00+00:00'
    segment = happy_path_claims_segment_db.get_segment('seg1')
    segment.json['lookup_ttl'] = lookup_ttl
    await run_choose_routers()

    if with_shifting_lookup_ttl:
        shifted_lookup_ttl = '2020-08-14T17:00:00+00:00'

    seginfo = await get_segment_info('seg1')
    assert (
        seginfo['dispatch']['waybill_building_deadline'] == shifted_lookup_ttl
    )


@pytest.mark.now('2020-08-14T18:37:00.00+00:00')
async def test_with_build_window(
        happy_path_state_first_import,
        run_choose_routers,
        get_segment_info,
        set_up_segment_routers_exp,
):
    await set_up_segment_routers_exp(build_window_seconds=600)
    await run_choose_routers()

    seginfo = await get_segment_info('seg1')
    assert (
        seginfo['dispatch']['waybill_building_deadline']
        == '2020-08-14T18:50:00+00:00'
    )


@pytest.mark.now('2020-08-14T18:37:00.00+00:00')
async def test_flag_allow_alive_batch_v1(
        happy_path_state_first_import,
        run_choose_routers,
        get_segment_info,
        set_up_segment_routers_exp,
):
    await set_up_segment_routers_exp(allow_alive_batch_v1=True)
    await run_choose_routers()

    seginfo = await get_segment_info('seg1')
    assert seginfo['segment']['allow_alive_batch_v1']


@pytest.mark.now('2020-08-14T18:37:00.00+00:00')
async def test_flag_allow_alive_batch_v2(
        happy_path_state_first_import,
        run_choose_routers,
        get_segment_info,
        set_up_segment_routers_exp,
):
    await set_up_segment_routers_exp(allow_alive_batch_v2=True)
    await run_choose_routers()

    seginfo = await get_segment_info('seg1')
    assert seginfo['segment']['allow_alive_batch_v2']


@pytest.mark.now('2020-08-14T18:37:00.00+00:00')
async def test_with_due(
        happy_path_state_first_import,
        run_choose_routers,
        get_segment_info,
        happy_path_claims_segment_db,
):
    segment = happy_path_claims_segment_db.get_segment('seg1')
    segment.json['due'] = '2020-08-14T20:45:00+00:00'
    await run_choose_routers()

    seginfo = await get_segment_info('seg1')
    assert (
        seginfo['dispatch']['waybill_building_deadline']
        == '2020-08-14T20:25:00+00:00'
    )


@pytest.mark.now('2020-08-14T18:37:00.00+00:00')
async def test_with_due_and_building_deadline_from_now(
        happy_path_state_first_import,
        run_choose_routers,
        get_segment_info,
        happy_path_claims_segment_db,
        set_up_segment_routers_exp,
):
    segment = happy_path_claims_segment_db.get_segment('seg1')
    segment.json['due'] = '2020-08-14T19:37:00+00:00'
    await set_up_segment_routers_exp(build_interval_for_due_segments=2460)
    await run_choose_routers()

    seginfo = await get_segment_info('seg1')
    assert (
        seginfo['dispatch']['waybill_building_deadline']
        == '2020-08-14T19:18:00+00:00'
    )


@pytest.mark.now('2020-08-14T18:37:00.00+00:00')
async def test_segment_after_reorder(
        happy_path_segment_after_reorder,
        run_choose_routers,
        get_segment_info,
        set_up_segment_routers_exp,
):
    await run_choose_routers()

    seginfo = await get_segment_info('seg3')
    assert (
        seginfo['dispatch']['waybill_building_deadline']
        == '2020-08-14T18:38:00+00:00'
    )
    assert seginfo['dispatch']['waybill_building_version'] == 2
    assert seginfo['dispatch']['waybill_building_awaited']


@pytest.mark.parametrize('recipient_phone', ['+70000000001', '+7_fb_only'])
async def test_segment_routers_exp_phones(
        happy_path_state_first_import,
        run_choose_routers,
        propose_from_segments,
        set_up_segment_routers_exp,
        recipient_phone: str,
        segment_id='seg1',
):
    await set_up_segment_routers_exp(recipient_phone=recipient_phone)

    await run_choose_routers()

    await propose_from_segments(
        'smart_router',
        'waybill_not_fb',
        segment_id,
        status_code=200 if recipient_phone == '+70000000001' else 400,
    )


@pytest.mark.parametrize('use_valid_coordinates', [False, True])
async def test_segment_routers_exp_coordinates(
        happy_path_state_first_import,
        run_choose_routers,
        propose_from_segments,
        set_up_segment_routers_exp,
        use_valid_coordinates: bool,
        segment_id='seg1',
):
    if use_valid_coordinates:
        source_point = [37.5, 55.7]
    else:
        source_point = [12.3456, 12.3456]

    await set_up_segment_routers_exp(source_point=source_point)

    await run_choose_routers()

    await propose_from_segments(
        'smart_router',
        'waybill_not_fb',
        segment_id,
        status_code=200 if use_valid_coordinates else 400,
    )


@pytest.mark.parametrize('router_intent_is_valid', [True, False])
async def test_segment_routers_exp_router_intent(
        happy_path_state_first_import,
        happy_path_claims_segment_db,
        run_choose_routers,
        propose_from_segments,
        set_up_segment_routers_exp,
        router_intent_is_valid: bool,
        segment_id='seg1',
):
    valid_router_intent = 'valid_intent'

    segment = happy_path_claims_segment_db.get_segment(segment_id)
    segment.json['custom_context']['router_intent'] = valid_router_intent

    await set_up_segment_routers_exp(
        router_intent=valid_router_intent
        if router_intent_is_valid
        else 'invalid_intent',
    )

    await run_choose_routers()

    await propose_from_segments(
        'smart_router',
        'waybill_not_fb',
        segment_id,
        status_code=200 if router_intent_is_valid else 400,
    )


@pytest.mark.parametrize(
    'enable_config, send_min_version', [(False, False), (True, True)],
)
async def test_sending_revisions(
        happy_path_state_first_import,
        run_choose_routers,
        happy_path_claims_segment_bulk_info_handler,
        taxi_cargo_dispatch,
        taxi_config,
        enable_config,
        send_min_version,
):
    taxi_config.set_values(
        dict(
            CARGO_DISPATCH_READ_SEGMENTS_WITH_REVISION={
                'choose_routers': enable_config,
                'fallback_router': enable_config,
            },
        ),
    )
    await taxi_cargo_dispatch.invalidate_caches()

    await run_choose_routers()
    assert happy_path_claims_segment_bulk_info_handler.times_called == 1

    if send_min_version:
        assert (
            happy_path_claims_segment_bulk_info_handler.next_call()[
                'request'
            ].json['segment_ids'][0]['min_revision']
            == 1
        )
    else:
        assert (
            'min_revision'
            not in happy_path_claims_segment_bulk_info_handler.next_call()[
                'request'
            ].json['segment_ids'][0]
        )


@pytest.mark.now('2020-04-01T10:35:01+0000')
async def test_lag(happy_path_state_first_import, run_choose_routers, pgsql):

    cursor = pgsql['cargo_dispatch'].cursor()
    cursor.execute(
        """
            UPDATE cargo_dispatch.segments
            SET updated_ts='2020-04-01T10:35:00+0000'
        """,
    )

    result = await run_choose_routers()
    assert result['stats']['new-segments-to-process'] == 5

    assert result['stats']['oldest-segment-lag-ms'] == 1000


@pytest.mark.config(
    CARGO_DISPATCH_CHOOSE_ROUTERS_SETTINGS={
        'enabled': True,
        'unprocessed_limit': 1000,
        'rate_limit': {'limit': 10, 'interval': 1, 'burst': 20},
    },
)
@pytest.mark.parametrize(
    'quota, expected_segments_count', [(10, 5), (2, 2), (1, 1)],
)
async def test_rate_limit(
        happy_path_state_first_import,
        taxi_cargo_dispatch_monitor,
        run_choose_routers,
        rps_limiter,
        quota,
        expected_segments_count,
):
    rps_limiter.set_budget('cargo-dispatch-choose-routers', quota)

    result = await run_choose_routers()
    assert (
        result['stats']['new-segments-to-process'] == expected_segments_count
    )

    statistics = await taxi_cargo_dispatch_monitor.get_metric('rps-limiter')
    limiter = statistics['cargo-dispatch-distlocks-limiter']
    assert limiter['quota-requests-failed'] == 0

    resource = limiter['resource_stat']['cargo-dispatch-choose-routers']
    assert resource['decision']['rejected'] == 0
    assert resource['quota-assigned'] == quota
    assert resource['limit'] == 10


@pytest.mark.parametrize(
    'claim_features, allow_batch',
    [
        (
            # Not phoenix claim. Don't forbid batching
            [],
            True,
        ),
        (
            # Phoenix claim. Forbid batching
            [{'id': 'phoenix_claim'}, {'id': 'agent_scheme'}],
            False,
        ),
    ],
)
@pytest.mark.now('2020-08-14T18:37:00.00+00:00')
async def test_forbid_alive_batch_v1_for_phoenix(
        happy_path_state_first_import,
        run_choose_routers,
        get_segment_info,
        set_up_segment_routers_exp,
        mockserver,
        happy_path_claims_segment_db,
        claim_features: list,
        allow_batch: bool,
        segment_id='seg1',
):
    segment = happy_path_claims_segment_db.get_segment(segment_id)
    segment.set_claim_features(claim_features)
    await set_up_segment_routers_exp(allow_alive_batch_v1=True)

    await run_choose_routers()

    seginfo = await get_segment_info(segment_id)
    assert seginfo['segment']['allow_alive_batch_v1'] == allow_batch


@pytest.mark.parametrize(
    'claim_features, allow_batch',
    [
        (
            # Not phoenix claim. Don't forbid batching
            [],
            True,
        ),
        (
            # Phoenix claim. Forbid batching
            [{'id': 'phoenix_claim'}, {'id': 'agent_scheme'}],
            False,
        ),
    ],
)
@pytest.mark.now('2020-08-14T18:37:00.00+00:00')
async def test_forbid_alive_batch_v2_for_phoenix(
        happy_path_state_first_import,
        run_choose_routers,
        get_segment_info,
        set_up_segment_routers_exp,
        mockserver,
        happy_path_claims_segment_db,
        claim_features: list,
        allow_batch: bool,
        segment_id='seg1',
):
    segment = happy_path_claims_segment_db.get_segment(segment_id)
    segment.set_claim_features(claim_features)
    await set_up_segment_routers_exp(allow_alive_batch_v2=True)

    await run_choose_routers()

    seginfo = await get_segment_info(segment_id)
    assert seginfo['segment']['allow_alive_batch_v2'] == allow_batch


@pytest.mark.now('2020-08-14T18:37:00.00+00:00')
async def test_clause_logging(
        happy_path_state_first_import,
        run_choose_routers,
        get_segment_info,
        set_up_segment_routers_exp,
        taxi_cargo_dispatch,
):
    await set_up_segment_routers_exp(build_window_seconds=600)
    async with taxi_cargo_dispatch.capture_logs() as capture:
        await run_choose_routers()

    records = capture.select(
        segment_id='seg1', level='INFO', event_name='segment_routers_match',
    )
    assert len(records) == 1
    assert records[0]['clause'] == '0'


async def test_blocklisting_router(
        happy_path_state_first_import,
        taxi_cargo_dispatch,
        run_choose_routers,
        get_segment_info,
        experiments3,
        taxi_config,
        segment_id='seg1',
        router_id='some_router',
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='segment_routers',
        consumers=['cargo-dispatch/route_building_init'],
        clauses=[],
        default_value={
            'build_interval_seconds': 300,
            'create_before_due_seconds': 1200,
            'routers': [
                {
                    'priority': 10,
                    'router_id': router_id,
                    'autoreorder_flow': 'newway',
                },
            ],
        },
    )
    taxi_config.set(
        CARGO_DISPATCH_ROUTERS_BLOCKLIST={'routers_blocklist': [router_id]},
    )
    await taxi_cargo_dispatch.invalidate_caches()

    await run_choose_routers()

    # Segment should not have chosen the router
    seginfo = await get_segment_info(segment_id)
    assert seginfo['dispatch']['status'] == 'new'


@pytest.mark.parametrize(
    'is_same_day_claim, expected_best_router_id, expected_deadline',
    [
        (False, 'fallback_router', '2022-03-05T12:36:00+00:00'),
        (True, 'cargo_same_day_delivery_router', '2022-03-05T15:05:00+00:00'),
    ],
)
@pytest.mark.now('2022-03-05T12:35:00.00+00:00')
async def test_sdd_segment(
        happy_path_state_first_import,
        happy_path_claims_segment_db,
        taxi_cargo_dispatch,
        run_choose_routers,
        get_segment_info,
        experiments3,
        taxi_config,
        is_same_day_claim,
        expected_best_router_id,
        expected_deadline,
        segment_id='seg1',
        router_id='some_router',
):
    if is_same_day_claim:
        segment = happy_path_claims_segment_db.get_segment(segment_id)
        segment.json['same_day_data'] = {
            'delivery_interval': {
                'from': '2022-03-05T13:35:00.00+00:00',
                'to': '2022-03-05T15:35:00.00+00:00',
            },
        }

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='segment_routers',
        consumers=['cargo-dispatch/route_building_init'],
        clauses=[
            {
                'title': 'clause',
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {'arg_name': 'is_same_day_claim'},
                                'type': 'bool',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'value': {
                    'build_interval_seconds': 60,
                    'create_before_due_seconds': 1200,
                    'routers': [
                        {
                            'priority': 100,
                            'router_id': 'cargo_same_day_delivery_router',
                            'autoreorder_flow': 'newway',
                        },
                    ],
                },
            },
        ],
        default_value={
            'build_interval_seconds': 60,
            'create_before_due_seconds': 1200,
            'routers': [
                {
                    'priority': 100,
                    'router_id': 'fallback_router',
                    'autoreorder_flow': 'newway',
                },
            ],
        },
    )
    await taxi_cargo_dispatch.invalidate_caches()

    await run_choose_routers()

    seginfo = await get_segment_info(segment_id)
    assert seginfo['dispatch']['best_router_id'] == expected_best_router_id
    assert (
        seginfo['dispatch']['waybill_building_deadline'] == expected_deadline
    )


# TODO(sazikov-a): remove after CARGODEV-12252
@pytest.mark.now('2020-08-14T18:37:00.00+00:00')
async def test_segment_routers_new_experiments(
        taxi_cargo_dispatch,
        experiments3,
        taxi_config,
        run_choose_routers,
        get_segment_info,
        happy_path_claims_segment_db,
        happy_path_state_first_import,
        segment_id='seg1',
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='segment_routers',
        consumers=['cargo-dispatch/route_building_init'],
        default_value={
            'build_interval_seconds': 60,
            'create_before_due_seconds': 1200,
            'routers': [
                {
                    'priority': 100,
                    'router_id': 'fallback_router',
                    'autoreorder_flow': 'newway',
                },
            ],
        },
    )

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_dispatch_waybill_building_deadline_settings',
        consumers=['cargo-dispatch/route_building_init'],
        default_value={
            'build_interval_seconds': 90,
            'create_before_due_seconds': 2400,
        },
    )

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='cargo_dispatch_batch_settings',
        consumers=['cargo-dispatch/route_building_init'],
        default_value={
            'allow_semilive_batches': True,
            'allow_alive_batches': True,
        },
    )

    taxi_config.set_values(
        {'CARGO_DISPATCH_SEGMENT_ROUTERS_MIGRATION': {'mode': 'enable'}},
    )

    await taxi_cargo_dispatch.invalidate_caches()

    await run_choose_routers()

    seginfo = await get_segment_info(segment_id)

    assert seginfo['dispatch']['best_router_id'] == 'fallback_router'
    assert (
        seginfo['dispatch']['waybill_building_deadline']
        == '2020-08-14T18:38:30+00:00'
    )
    assert seginfo['segment']['allow_alive_batch_v1']
    assert seginfo['segment']['allow_alive_batch_v2']
