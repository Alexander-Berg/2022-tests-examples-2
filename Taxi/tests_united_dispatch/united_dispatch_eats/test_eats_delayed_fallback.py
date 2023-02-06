import pytest


@pytest.mark.now('2021-09-23T15:30:47.185337+00:00')
async def test_eats_delayed_fallback_not_fastfood(
        taxi_united_dispatch_eats,
        create_segment,
        state_waybill_proposed,
        make_eats_custom_context,
        testpoint,
        scoring,
        experiments3,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='united_dispatch_eats_delayed_fallback',
        consumers=['united-dispatch/eats-delayed-kwargs'],
        clauses=[],
        default_value={
            'enabled': True,
            'timing_for_fast_food': 14 * 60,
            'timing_for_others': 6 * 60,
        },
    )
    exp3_recorder = experiments3.record_match_tries(
        'united_dispatch_eats_delayed_fallback',
    )
    await taxi_united_dispatch_eats.invalidate_caches(
        clean_update=False, cache_names=['experiments3-cache'],
    )

    scoring(
        {
            'responses': [
                {
                    'search': {},
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 10},
                        {'id': 'dbid1_uuid2', 'score': 3},
                    ],
                },
            ],
        },
    )

    @testpoint('eats_planner::delayed_fallback_skip')
    def delayed_fallback_skip(data):
        pass

    segment = create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(),
        due='2021-09-23T15:40:47.185337+00:00',
    )

    await state_waybill_proposed()

    assert delayed_fallback_skip.times_called > 0

    match_tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    segment_id_from_kwarg = match_tries[0].kwargs['segment_id']

    assert segment_id_from_kwarg == segment.id


@pytest.mark.now('2021-09-23T15:32:47.185337+00:00')
async def test_eats_delayed_fallback_fastfood(
        taxi_united_dispatch_eats,
        create_segment,
        state_waybill_proposed,
        make_eats_custom_context,
        testpoint,
        scoring,
        experiments3,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='united_dispatch_eats_delayed_fallback',
        consumers=['united-dispatch/eats-delayed-kwargs'],
        clauses=[],
        default_value={
            'enabled': True,
            'timing_for_fast_food': 14 * 60,
            'timing_for_others': 6 * 60,
        },
    )
    await taxi_united_dispatch_eats.invalidate_caches(
        clean_update=False, cache_names=['experiments3-cache'],
    )

    scoring(
        {
            'responses': [
                {
                    'search': {},
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 10},
                        {'id': 'dbid1_uuid2', 'score': 3},
                    ],
                },
            ],
        },
    )

    @testpoint('eats_planner::delayed_fallback_skip')
    def delayed_fallback_skip(data):
        pass

    create_segment(
        corp_client_id='eats_corp_id',
        taxi_classes={'eda'},
        custom_context=make_eats_custom_context(
            is_fast_food=True,
            order_confirmed_at='2021-09-23T15:25:47.185337+00:00',
        ),
        due='2021-09-23T15:55:47.185337+00:00',
    )

    await state_waybill_proposed()

    assert delayed_fallback_skip.times_called > 0
