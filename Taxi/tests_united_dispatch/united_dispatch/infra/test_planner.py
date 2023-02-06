# pylint: disable=import-error
import datetime

import pytest

from testsuite.utils import matching

from tests_united_dispatch.plugins import cargo_dispatch_manager

ROUTER_ID = 'united-dispatch'


async def test_replace_old_waybill_version(
        cargo_dispatch: cargo_dispatch_manager.CargoDispatch,
        create_segment,
        mock_waybill_propose,
        state_segments_replicated,
        run_single_planner,
        stq,
):
    """
        Check for new proposition when waybill_building_version increased.
    """
    segment = create_segment(crutches={'force_crutch_builder': True})
    await state_segments_replicated()

    # first time proposed
    await run_single_planner()

    assert stq.united_dispatch_waybill_propose.has_calls
    stq.united_dispatch_waybill_propose.flush()

    # second time was not proposed
    await run_single_planner()

    assert not stq.united_dispatch_waybill_propose.has_calls

    # proposed again on new waybill_building_version
    cargo_dispatch.segments.inc_waybill_building_version(segment.id)
    await state_segments_replicated()
    await run_single_planner()

    assert stq.united_dispatch_waybill_propose.has_calls


async def test_proposition_sent_stq(
        create_segment,
        state_segments_replicated,
        run_single_planner,
        get_segment,
        get_waybill,
        stq,
):
    """
        Check stq was set.
    """
    segment = create_segment(crutches={'force_crutch_builder': True})
    await state_segments_replicated()

    await run_single_planner()

    assert stq.united_dispatch_waybill_propose.has_calls

    segment = get_segment(segment.id)
    assert segment.get('waybill_ref')
    waybill_ref = segment['waybill_ref']

    assert get_waybill(waybill_ref)


async def test_stored_waybill_data(
        create_segment, state_waybill_created, get_single_waybill, get_segment,
):
    """
        Check stored (serialized) waybill data.
    """
    segment = create_segment(crutches={'force_crutch_builder': True})

    await state_waybill_created()

    segment_pg = get_segment(segment_id=segment.id)
    stored_waybill = get_single_waybill()

    assert stored_waybill['waybill']['segments'] == [
        {
            'db_shard': 0,
            'proposition_revision': matching.any_integer,
            'created_ts': matching.any_string,
            'segment': segment_pg['segment_info'],
        },
    ]


async def test_proposed_waybill_data(
        create_segment,
        state_waybill_proposed,
        get_segment,
        propositions_manager: cargo_dispatch_manager.PropositionsManager,
        exp_planner_settings,
        waybill_building_version=2,
        planner_type='crutches',
):
    """
        Check proposed waybill data.
    """
    segment = create_segment(
        waybill_building_version=waybill_building_version,
        crutches={'force_crutch_builder': True},
    )

    await state_waybill_proposed()

    assert len(propositions_manager.propositions) == 1
    waybill = propositions_manager.propositions[0]

    segment_pg = get_segment(
        segment.id, waybill_building_version=waybill_building_version,
    )

    def convert_points(segment):
        result = []
        segment_info = segment['segment_info']['segment']
        for point in segment_info['points']:
            result.append(
                {
                    'point_id': point['point_id'],
                    'visit_order': point['visit_order'],
                    'segment_id': segment_info['id'],
                },
            )
        result.sort(key=lambda p: p['visit_order'])
        return result

    assert waybill == {
        'external_ref': matching.any_string,
        'router_id': ROUTER_ID,
        'points': convert_points(segment_pg),
        'segments': [
            {
                'segment_id': segment_pg['id'],
                'waybill_building_version': segment_pg[
                    'waybill_building_version'
                ],
            },
        ],
        'special_requirements': segment_pg['special_requirements'],
        'taxi_order_requirements': {
            'taxi_classes': segment_pg['taxi_classes'],
            **segment_pg['taxi_requirements'],
            'forced_soon': False,
        },
    }
    assert waybill['external_ref'].startswith(f'{ROUTER_ID}/0/{planner_type}/')


@pytest.mark.parametrize(
    'planner_type, expect_proposition',
    [('testsuite-candidates', True), ('crutches', False)],
)
async def test_exp_async_planners(
        create_candidates_segment,
        state_segments_replicated,
        run_planner,
        stq,
        performer_for_order,
        planner_type: str,
        expect_proposition: bool,
):
    """
        Check processed with specific planners only.
        'crutches-planner' skips proposition due to
        missing crutches comment.
    """
    create_candidates_segment('greedy')

    await state_segments_replicated()

    await run_planner(component_name=f'{planner_type}-planner')

    assert stq.united_dispatch_waybill_propose.has_calls == expect_proposition


async def test_waybill_geo_index_enabled(
        create_segment, state_taxi_order_performer_found, run_single_planner,
):
    create_segment(crutches={'force_crutch_builder': True})

    await state_taxi_order_performer_found()

    stats = await run_single_planner()

    assert (
        stats.find_metric(
            {'distlock_worker_alias': 'waybill-geoindex-size'},
        ).value
        > 0
    )


async def test_due_segment_delay(
        state_segments_replicated,
        exp_planner_settings,
        run_single_planner,
        create_segment,
        mocked_time,
        stq,
        wait_until_due_seconds=1800,
):
    """
        Check segment delayed till waybill_building_deadline horizon
        is not reached.
    """
    await exp_planner_settings(wait_until_due_seconds=wait_until_due_seconds)

    now = mocked_time.now().replace(tzinfo=datetime.timezone.utc)
    due = now + datetime.timedelta(seconds=2 * wait_until_due_seconds)

    create_segment(
        due=due.isoformat(), crutches={'force_crutch_builder': True},
    )

    await state_segments_replicated()

    await run_single_planner()

    assert not stq.united_dispatch_waybill_propose.has_calls


async def test_early_due_segment_proposed(
        state_segments_replicated,
        exp_planner_settings,
        run_single_planner,
        create_segment,
        mocked_time,
        stq,
):
    """
        Check segment with near due should be proposed.
    """
    await exp_planner_settings(wait_until_due_seconds=1800)

    now = mocked_time.now().replace(tzinfo=datetime.timezone.utc)
    create_segment(
        due=now.isoformat(), crutches={'force_crutch_builder': True},
    )

    await state_segments_replicated()
    await run_single_planner()

    assert stq.united_dispatch_waybill_propose.has_calls


async def test_resolved_segment_no_gambling(
        create_segment, state_segments_replicated, run_single_planner,
):
    """
        Check for resolved segment is not in proposition-builder input.
    """
    create_segment(
        resolution='cancelled_by_user',
        crutches={'force_crutch_builder': True},
    )
    old_stats = await run_single_planner()

    create_segment(
        resolution='cancelled_by_user',
        crutches={'force_crutch_builder': True},
    )
    await state_segments_replicated()

    stats = await run_single_planner()

    assert (
        stats.find_metric({'distlock_worker_alias': 'input-segments'}).value
        == old_stats.find_metric(
            {'distlock_worker_alias': 'input-segments'},
        ).value
    )


async def test_waybills_cache(
        create_segment,
        state_taxi_order_performer_found,
        state_segments_replicated,
        propositions_manager: cargo_dispatch_manager.PropositionsManager,
        increment_waybill_revision,
        run_single_planner,
        get_single_waybill,
        get_segment,
):
    """
        Check waybill with outdated revision is not processed.
    """
    # both segments proposed at once, seg2 should await seg1
    seg1 = create_segment(crutches={'force_crutch_builder': True})
    seg2 = create_segment(crutches={'live_batch_with': seg1.id})

    await state_taxi_order_performer_found()

    assert len(propositions_manager.propositions) == 1
    assert not propositions_manager.live_propositions

    previous_waybill_ref = get_single_waybill()['id']
    # second time there is waybill for seg1, live proposition proposed
    await state_segments_replicated()
    increment_waybill_revision(previous_waybill_ref)
    await run_single_planner(invalidate_caches=False)

    assert get_segment(seg2.id)['waybill_ref'] is None


async def test_passed_segment(
        create_segment,
        state_segments_replicated,
        list_segment_executors,
        run_single_planner,
        exp_segment_executors_selector,
        get_segment,
        performer_for_order,
):
    """
        Check passing segment activate next executor
    """
    segment = create_segment(
        crutches={'force_crutch_builder': True, 'forced_pass': True},
    )

    await exp_segment_executors_selector(
        executors=[
            {'planner_type': 'crutches', 'is_active': True},
            {'planner_type': 'testsuite-candidates', 'is_active': False},
        ],
    )

    await state_segments_replicated()

    segment_executors = list_segment_executors(segment.id)
    assert [
        (e['planner_type'], e['status'], e['passed_ts'])
        for e in segment_executors
    ] == [('crutches', 'active', None), ('testsuite-candidates', 'idle', None)]

    stats = await run_single_planner()

    segment_executors = list_segment_executors(segment.id)
    assert (
        [
            (e['planner_type'], e['status'], e['passed_ts'])
            for e in segment_executors
        ]
        == [
            ('crutches', 'active', matching.IsInstance(datetime.datetime)),
            ('testsuite-candidates', 'active', None),
        ]
    )

    assert (
        stats.find_metric(
            {'distlock_worker_alias': 'actual-passed-segments'},
        ).value
        == 1
    )
    old_datetime = segment_executors[0]['passed_ts']

    # second time to check unchanged passed_ts
    stats = await run_single_planner()

    segment_executors = list_segment_executors(segment.id)
    assert (
        [
            (e['planner_type'], e['status'], e['passed_ts'])
            for e in segment_executors
        ]
        == [
            ('crutches', 'active', old_datetime),
            ('testsuite-candidates', 'active', None),
        ]
    )
    assert (
        stats.find_metric(
            {'distlock_worker_alias': 'actual-passed-segments'},
        ).value
        == 1
    )


async def test_finished_segment(
        create_segment,
        state_segments_replicated,
        list_segment_executors,
        run_single_planner,
        exp_segment_executors_selector,
        get_segment,
):
    """
        Check finished segment used only once
    """
    segment = create_segment(crutches={'force_crutch_builder': True})

    await exp_segment_executors_selector(
        executors=[
            {'planner_type': 'crutches', 'is_active': True},
            {'planner_type': 'testsuite-candidates', 'is_active': False},
        ],
    )

    await state_segments_replicated()

    segment_executors = list_segment_executors(segment.id)
    assert [(e['planner_type'], e['status']) for e in segment_executors] == [
        ('crutches', 'active'),
        ('testsuite-candidates', 'idle'),
    ]

    stats = await run_single_planner()

    segment_executors = list_segment_executors(segment.id)
    assert [(e['planner_type'], e['status']) for e in segment_executors] == [
        ('crutches', 'finished'),
        ('testsuite-candidates', 'finished'),
    ]

    assert (
        stats.find_metric({'distlock_worker_alias': 'input-segments'}).value
        == 1
    )
    old_datetime = segment_executors[0]['updated_ts']

    # second time to check unchanged
    stats = await run_single_planner()

    segment_executors = list_segment_executors(segment.id)
    assert (
        [
            (e['planner_type'], e['status'], e['updated_ts'])
            for e in segment_executors
        ]
        == [
            ('crutches', 'finished', old_datetime),
            ('testsuite-candidates', 'finished', old_datetime),
        ]
    )
    assert (
        stats.find_metric({'distlock_worker_alias': 'input-segments'}).value
        == 0
    )
