import pytest

from tests_united_dispatch.plugins import cargo_dispatch_manager


async def test_eats_waybill_with_candidate_true(
        create_segment,
        propositions_manager: cargo_dispatch_manager.PropositionsManager,
        state_waybill_proposed,
        get_segment,
        get_waybill,
        make_eats_custom_context,
        scoring,
        testpoint,
):
    @testpoint('eats_planner::assign_segment')
    def eats_assign(data):
        pass

    scoring(
        {
            'responses': [
                {
                    'search': {'retention_score': 100},
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 8},
                        {'id': 'dbid1_uuid2', 'score': 17},
                    ],
                },
                {
                    'search': {'retention_score': 100},
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 3},
                        {'id': 'dbid1_uuid2', 'score': 15},
                    ],
                },
            ],
        },
    )

    segment1 = create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(),
    )
    segment2 = create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(),
    )

    await state_waybill_proposed()

    segment1_info = get_segment(segment1.id)
    segment2_info = get_segment(segment2.id)

    waybill1 = get_waybill(segment1_info['waybill_ref'])
    waybill2 = get_waybill(segment2_info['waybill_ref'])

    assert len(propositions_manager.propositions) == 2
    assert eats_assign.times_called == 2
    assert waybill1['candidate']['info']['id'] == 'dbid1_uuid2'
    assert waybill2['candidate']['info']['id'] == 'dbid1_uuid1'


async def test_eats_waybill_with_candidate_is_none(
        create_segment,
        state_waybill_proposed,
        make_eats_custom_context,
        testpoint,
        candidates,
):
    @testpoint('eats_planner::assign_segment')
    def eats_assign(data):
        pass

    @testpoint('eats_planner::pass')
    def eats_pass(data):
        pass

    candidates({'candidates': []})

    create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(),
    )

    await state_waybill_proposed()

    assert not eats_assign.times_called
    assert eats_pass.times_called > 0


async def test_eats_waybill_skipped_retention_score_won(
        create_segment,
        state_waybill_proposed,
        make_eats_custom_context,
        scoring,
        testpoint,
):
    @testpoint('eats_planner::assign_segment')
    def eats_assign(data):
        pass

    @testpoint('eats_planner::skip')
    def eats_skip(data):
        pass

    scoring(
        {
            'responses': [
                {
                    'search': {'retention_score': 5},
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 8},
                        {'id': 'dbid1_uuid2', 'score': 17},
                    ],
                },
                {
                    'search': {'retention_score': 1},
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 3},
                        {'id': 'dbid1_uuid2', 'score': 15},
                    ],
                },
            ],
        },
    )

    create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(),
    )
    create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(),
    )

    await state_waybill_proposed()

    assert not eats_assign.times_called
    assert eats_skip.times_called > 0


async def test_eats_waybill_passed_fallback_score_less_then_retention_score(
        create_segment,
        state_waybill_proposed,
        make_eats_custom_context,
        scoring,
        testpoint,
):
    @testpoint('eats_planner::assign_segment')
    def eats_assign(data):
        pass

    @testpoint('eats_planner::pass')
    def eats_pass(data):
        pass

    scoring(
        {
            'responses': [
                {
                    'search': {
                        'retention_score': 5,
                        'misc': {'fallback_score': 3},
                    },
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 8},
                        {'id': 'dbid1_uuid2', 'score': 17},
                    ],
                },
                {
                    'search': {
                        'retention_score': 2,
                        'misc': {'fallback_score': 1},
                    },
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 3},
                        {'id': 'dbid1_uuid2', 'score': 15},
                    ],
                },
            ],
        },
    )

    create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(),
    )
    create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(),
    )

    await state_waybill_proposed()

    assert not eats_assign.times_called
    assert eats_pass.times_called == 2


async def test_eats_waybill_pass_with_vehicle_zone_type(
        create_segment,
        state_waybill_proposed,
        make_eats_custom_context,
        scoring,
        testpoint,
):
    @testpoint('eats_planner::pass')
    def eats_pass(data):
        pass

    scoring(
        {
            'responses': [
                {
                    'search': {'retention_score': 0},
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 8},
                        {'id': 'dbid1_uuid2', 'score': 17},
                    ],
                },
                {
                    'search': {'retention_score': 0},
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 3},
                        {'id': 'dbid1_uuid2', 'score': 15},
                    ],
                },
            ],
        },
    )

    create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(zone_type='vehicle'),
    )

    await state_waybill_proposed()

    assert eats_pass.times_called > 0


async def test_eats_custom_context_passed_correctly(
        create_segment,
        state_waybill_proposed,
        make_eats_custom_context,
        mockserver,
):
    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _score_bulk(request):
        eats_batch = request.json['requests'][0]['search']['order']['request'][
            'eats_batch'
        ]
        assert len(eats_batch) == 1

        assert eats_batch[0]['context'] == {
            'orders_count': 1,
            'device_id': '___??',
            'estimations': [{'offer_id': 'id', 'offer_price': '100'}],
            'weight': '0.234',
            'items_cost': {'value': '18', 'currency': 'RUB'},
            'delivery_cost': {'value': '4', 'currency': 'RUB'},
            'order_id': 110000,
            'region_id': 1,
            'order_confirmed_at': '2021-12-14T15:15:00.425521+00:00',
            'promise_min_at': '2021-12-14T15:40:00.425521+00:00',
            'promise_max_at': '2021-12-14T15:50:00.425521+00:00',
            'cooking_time': 480,
            'send_to_place_at': '2021-12-14T15:20:00.425521+00:00',
            'order_cancel_at': '2021-12-14T16:10:00.425521+00:00',
            'order_flow_type': 'native',
            'delivery_flow_type': 'courier',
            'is_asap': True,
            'is_fast_food': False,
            'has_slot': False,
            'sender_is_picker': False,
            'place_id': 10,
            'route_to_client': {
                'auto': {'distance': 1200, 'time': 260, 'is_precise': True},
                'transit': {'distance': 800, 'time': 300, 'is_precise': True},
                'pedestrian': {
                    'distance': 600,
                    'time': 120,
                    'is_precise': True,
                },
            },
            'surge_data': {'currency_code': 'RUB', 'price': '30'},
        }
        return (
            {
                'responses': [
                    {
                        'search': {'retention_score': 0},
                        'candidates': [
                            {'id': 'dbid1_uuid1', 'score': 8},
                            {'id': 'dbid1_uuid2', 'score': 17},
                        ],
                    },
                ],
            },
        )

    create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(),
        estimations=[{'offer_id': 'id', 'offer_price': '100'}],
    )

    await state_waybill_proposed()


async def test_eats_waybill_repeat_search(
        taxi_united_dispatch_eats,
        state_taxi_order_created,
        set_waybill_candidate,
        set_waybill_lookup_flow,
        get_single_waybill,
        run_single_planner,
        experiments3,
        scoring,
        create_segment,
        make_eats_custom_context,
        testpoint,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='united_dispatch_performer_for_order_repeat_search',
        consumers=['united-dispatch/performer-for-order'],
        clauses=[],
        default_value={'enabled': True},
    )
    await taxi_united_dispatch_eats.invalidate_caches(
        clean_update=False, cache_names=['experiments3-cache'],
    )

    scoring(
        {
            'responses': [
                {
                    'search': {'retention_score': 100},
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 18},
                        {'id': 'dbid1_uuid2', 'score': 17},
                    ],
                },
            ],
        },
    )

    create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(),
    )

    await state_taxi_order_created()

    waybill = get_single_waybill()
    set_waybill_candidate(
        waybill_ref=waybill['id'], performer_id='dbid1_uuid2',
    )
    set_waybill_lookup_flow(
        waybill_ref=waybill['id'], lookup_flow='united-dispatch',
    )

    response = await taxi_united_dispatch_eats.post(
        '/performer-for-order',
        json={
            'order_id': waybill['waybill']['taxi_order_id'],
            'allowed_classes': ['eda'],
            'lookup': {'generation': 1, 'version': 1, 'wave': 1},
            'order': {'created': 1584378627.69, 'nearest_zone': 'moscow'},
        },
    )

    assert response.status_code == 200
    assert response.json()['candidate']['id'] == 'dbid1_uuid2'

    # Increase lookup version, this should trigger waybill update and mark
    # waybill for new search

    response = await taxi_united_dispatch_eats.post(
        '/performer-for-order',
        json={
            'order_id': waybill['waybill']['taxi_order_id'],
            'allowed_classes': ['eda'],
            'lookup': {'generation': 1, 'version': 2, 'wave': 1},
            'order': {'created': 1584378627.69, 'nearest_zone': 'moscow'},
        },
    )

    assert response.status_code == 200
    assert response.json() == {'message': 'updated'}

    # Start planner which should find new candidate for waybill
    @testpoint('eats_planner::assign_waybill')
    def eats_assign(data):
        pass

    await run_single_planner()
    assert eats_assign.times_called == 1


@pytest.mark.parametrize('exclude_rejected_candidates', [False, True])
async def test_exclude_rejected_candidate(
        make_eats_custom_context,
        # scoring,
        state_segments_replicated,
        exp_eats_dispatch_settings,
        exp_rejected_candidates_load_settings,
        run_single_planner,
        mockserver,
        create_segment,
        add_rejected_candidate,
        exclude_rejected_candidates: bool,
):
    # scoring({'responses': [{'search': {}, 'candidates': []}]})
    """
        Check request to candidates for rejected candidate.
    """
    await exp_eats_dispatch_settings(
        enable_live_batches=False,
        exclude_rejected_candidates=exclude_rejected_candidates,
    )
    await exp_rejected_candidates_load_settings()

    seg = create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(),
    )
    add_rejected_candidate(segment=seg, candidate_id='some_id')

    await state_segments_replicated()

    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        assert request.json['order']['request']['rejected_candidates']
        if exclude_rejected_candidates:
            assert 'excluded_contractor_ids' in request.json
        else:
            assert 'excluded_contractor_ids' not in request.json
        return {'candidates': []}

    await run_single_planner()

    assert _order_search.times_called
