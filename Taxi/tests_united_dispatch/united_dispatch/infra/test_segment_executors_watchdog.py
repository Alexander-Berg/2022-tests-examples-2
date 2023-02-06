import datetime

import pytest

from testsuite.utils import matching

WORKER_NAME = 'segments-watchdog'


def _make_run_stats(
        *,
        fetched_segments=0,
        fetched_executors=0,
        total_updated=0,
        total_passed=0,
        actual_updated=0,
        actual_passed=0,
):
    return {
        'total-fetched-segments-count': fetched_segments,
        'total-fetched-executors-count': fetched_executors,
        'total-passed-executors-count': total_passed,
        'total-updated-executors-count': total_updated,
        'actual-passed-executors-count': actual_passed,
        'actual-updated-executors-count': actual_updated,
    }


async def test_not_fetched_proposed(
        run_executor_watchdog,
        create_segment,
        state_segments_replicated,
        run_single_planner,
        exp_segment_executors_selector,
        get_worker_state,
):
    create_segment(crutches={'force_crutch_builder': True})

    await exp_segment_executors_selector(
        executors=[{'planner_type': 'crutches', 'is_active': True}],
    )

    await state_segments_replicated()
    await run_single_planner()

    stats = await run_executor_watchdog()

    assert stats == _make_run_stats()

    new_worker_state = get_worker_state(WORKER_NAME)
    assert new_worker_state == {'segment_id_by_db_shard': {}}


@pytest.mark.config(
    UNITED_DISPATCH_SEGMENTS_WATCHDOG={
        'enabled': True,
        'launches_pause_ms': 1,
        'processing_limit': 1,
        'checker_settings': {
            'simultaneous_limit': 10,
            'check_executors_update': {'work_mode': 'enabled'},
            'check_executors_force_pass': {
                'work_mode': 'enabled',
                'dead_time_limit_seconds': {'__default__': 10},
            },
        },
    },
)
async def test_fetch_paged(
        run_executor_watchdog,
        create_segment,
        state_segments_replicated,
        exp_segment_executors_selector,
        get_worker_state,
):
    segment1 = create_segment(segment_id='aaaa')
    segment2 = create_segment(segment_id='bbbb')

    await exp_segment_executors_selector(
        executors=[
            {'planner_type': 'crutches', 'is_active': True},
            {'planner_type': 'delivery', 'is_active': False},
        ],
    )

    await state_segments_replicated()

    # first page
    stats = await run_executor_watchdog()
    assert stats == _make_run_stats(fetched_executors=2, fetched_segments=1)
    new_worker_state = get_worker_state(WORKER_NAME)
    assert new_worker_state == {'segment_id_by_db_shard': {'0': segment1.id}}

    # second page
    stats = await run_executor_watchdog()
    assert stats == _make_run_stats(fetched_executors=2, fetched_segments=1)
    new_worker_state = get_worker_state(WORKER_NAME)
    assert new_worker_state == {'segment_id_by_db_shard': {'0': segment2.id}}

    # empty page
    stats = await run_executor_watchdog()
    assert stats == _make_run_stats(fetched_executors=0, fetched_segments=0)
    new_worker_state = get_worker_state(WORKER_NAME)
    assert new_worker_state == {'segment_id_by_db_shard': {}}


@pytest.mark.config(
    UNITED_DISPATCH_SEGMENTS_WATCHDOG={
        'enabled': True,
        'launches_pause_ms': 1,
        'processing_limit': 10,
        'checker_settings': {
            'simultaneous_limit': 10,
            'check_executors_update': {'work_mode': 'enabled'},
            'check_executors_force_pass': {
                'work_mode': 'enabled',
                'dead_time_limit_seconds': {'__default__': 10},
            },
        },
    },
)
async def test_need_update(
        run_executor_watchdog,
        create_segment,
        state_segments_replicated,
        exp_planner_shard,
        exp_segment_executors_selector,
        list_segment_executors,
):
    segment = create_segment()

    await exp_planner_shard(shard='default')
    await exp_segment_executors_selector(
        executors=[
            {'planner_type': 'crutches', 'is_active': True},
            {'planner_type': 'delivery', 'is_active': False},
        ],
    )

    await state_segments_replicated()

    await exp_planner_shard(shard='moscow')
    await exp_segment_executors_selector(
        executors=[
            {'planner_type': 'eats', 'is_active': True},
            {'planner_type': 'crutches', 'is_active': False},
            {'planner_type': 'grocery', 'is_active': True},
        ],
    )

    stats = await run_executor_watchdog()
    assert stats == _make_run_stats(
        fetched_executors=2,
        fetched_segments=1,
        total_updated=3,
        actual_updated=3,
    )

    segment_executors = list_segment_executors(segment.id)
    assert (
        [
            (
                e['planner_type'],
                e['planner_shard'],
                e['status'],
                e['execution_order'],
            )
            for e in segment_executors
        ]
        == [
            ('eats', 'moscow', 'active', 0),
            ('crutches', 'moscow', 'idle', 1),
            ('grocery', 'moscow', 'active', 2),
        ]
    )


@pytest.mark.config(
    UNITED_DISPATCH_SEGMENTS_WATCHDOG={
        'enabled': True,
        'launches_pause_ms': 1,
        'processing_limit': 10,
        'checker_settings': {
            'simultaneous_limit': 10,
            'check_executors_update': {'work_mode': 'dry_run'},
            'check_executors_force_pass': {
                'work_mode': 'enabled',
                'dead_time_limit_seconds': {'__default__': 10},
            },
        },
    },
)
async def test_need_update_but_dry_run(
        run_executor_watchdog,
        create_segment,
        state_segments_replicated,
        exp_planner_shard,
        exp_segment_executors_selector,
        list_segment_executors,
):
    segment = create_segment(revision=1)

    await exp_planner_shard(shard='default')
    await exp_segment_executors_selector(
        executors=[
            {'planner_type': 'crutches', 'is_active': True},
            {'planner_type': 'delivery', 'is_active': False},
        ],
    )

    await state_segments_replicated()

    await exp_planner_shard(shard='moscow')
    await exp_segment_executors_selector(
        executors=[
            {'planner_type': 'eats', 'is_active': True},
            {'planner_type': 'crutches', 'is_active': False},
            {'planner_type': 'grocery', 'is_active': True},
        ],
    )

    stats = await run_executor_watchdog()
    assert stats == _make_run_stats(
        fetched_executors=2,
        fetched_segments=1,
        total_updated=3,
        actual_updated=0,
    )

    segment_executors = list_segment_executors(segment.id)
    assert (
        [
            (
                e['planner_type'],
                e['planner_shard'],
                e['status'],
                e['execution_order'],
            )
            for e in segment_executors
        ]
        == [
            ('crutches', 'default', 'active', 0),
            ('delivery', 'default', 'idle', 1),
        ]
    )


@pytest.mark.config(
    UNITED_DISPATCH_SEGMENTS_WATCHDOG={
        'enabled': True,
        'launches_pause_ms': 1,
        'processing_limit': 10,
        'checker_settings': {
            'simultaneous_limit': 10,
            'check_executors_update': {'work_mode': 'disabled'},
            'check_executors_force_pass': {
                'work_mode': 'enabled',
                'dead_time_limit_seconds': {'__default__': 10},
            },
        },
    },
)
async def test_need_update_but_disabled(
        run_executor_watchdog,
        create_segment,
        state_segments_replicated,
        exp_planner_shard,
        exp_segment_executors_selector,
        list_segment_executors,
):
    segment = create_segment(revision=1)

    await exp_planner_shard(shard='default')
    await exp_segment_executors_selector(
        executors=[
            {'planner_type': 'crutches', 'is_active': True},
            {'planner_type': 'delivery', 'is_active': False},
        ],
    )

    await state_segments_replicated()

    await exp_planner_shard(shard='moscow')
    await exp_segment_executors_selector(
        executors=[
            {'planner_type': 'eats', 'is_active': True},
            {'planner_type': 'crutches', 'is_active': False},
            {'planner_type': 'grocery', 'is_active': True},
        ],
    )

    stats = await run_executor_watchdog()
    assert stats == _make_run_stats(
        fetched_executors=2,
        fetched_segments=1,
        total_updated=0,
        actual_updated=0,
    )

    segment_executors = list_segment_executors(segment.id)
    assert (
        [
            (
                e['planner_type'],
                e['planner_shard'],
                e['status'],
                e['execution_order'],
            )
            for e in segment_executors
        ]
        == [
            ('crutches', 'default', 'active', 0),
            ('delivery', 'default', 'idle', 1),
        ]
    )


@pytest.mark.config(
    UNITED_DISPATCH_SEGMENTS_WATCHDOG={
        'enabled': True,
        'launches_pause_ms': 1,
        'processing_limit': 10,
        'checker_settings': {
            'simultaneous_limit': 10,
            'check_executors_update': {'work_mode': 'enabled'},
            'check_executors_force_pass': {
                'work_mode': 'enabled',
                'dead_time_limit_seconds': {
                    '__default__': 100,
                    'crutches': 12,
                },
            },
        },
    },
)
@pytest.mark.now('2022-01-01T12:00:00+0000')
async def test_no_need_force_pass(
        run_executor_watchdog,
        create_segment,
        state_segments_replicated,
        exp_segment_executors_selector,
        list_segment_executors,
        update_segment_executor_record,
        mocked_time,
):
    segment = create_segment()

    await exp_segment_executors_selector(
        executors=[
            {'planner_type': 'eats', 'is_active': True},
            {'planner_type': 'crutches', 'is_active': True},
            {'planner_type': 'delivery', 'is_active': False},
            {'planner_type': 'grocery', 'is_active': False},
        ],
    )

    await state_segments_replicated()

    update_segment_executor_record(
        segment.id, 1, new_updated_ts=mocked_time.now(),
    )
    mocked_time.sleep(11)

    stats = await run_executor_watchdog()

    assert stats == _make_run_stats(
        fetched_executors=4,
        fetched_segments=1,
        total_passed=0,
        actual_passed=0,
    )

    segment_executors = list_segment_executors(segment.id)
    assert (
        [
            (e['planner_type'], e['status'], e['passed_ts'])
            for e in segment_executors
        ]
        == [
            ('eats', 'active', None),
            ('crutches', 'active', None),
            ('delivery', 'idle', None),
            ('grocery', 'idle', None),
        ]
    )


@pytest.mark.config(
    UNITED_DISPATCH_SEGMENTS_WATCHDOG={
        'enabled': True,
        'launches_pause_ms': 1,
        'processing_limit': 10,
        'checker_settings': {
            'simultaneous_limit': 10,
            'check_executors_update': {'work_mode': 'enabled'},
            'check_executors_force_pass': {
                'work_mode': 'enabled',
                'dead_time_limit_seconds': {
                    '__default__': 100,
                    'crutches': 10,
                },
            },
        },
    },
)
@pytest.mark.now('2022-01-01T12:00:00+0000')
async def test_need_force_pass(
        run_executor_watchdog,
        create_segment,
        state_segments_replicated,
        exp_segment_executors_selector,
        list_segment_executors,
        update_segment_executor_record,
        mocked_time,
):
    segment = create_segment()

    await exp_segment_executors_selector(
        executors=[
            {'planner_type': 'eats', 'is_active': True},
            {'planner_type': 'crutches', 'is_active': True},
            {'planner_type': 'delivery', 'is_active': False},
            {'planner_type': 'grocery', 'is_active': False},
        ],
    )

    await state_segments_replicated()

    update_segment_executor_record(
        segment.id, 1, new_updated_ts=mocked_time.now(),
    )
    mocked_time.sleep(11)

    stats = await run_executor_watchdog()

    assert stats == _make_run_stats(
        fetched_executors=4,
        fetched_segments=1,
        total_passed=1,
        actual_passed=1,
    )

    segment_executors = list_segment_executors(segment.id)
    assert (
        [
            (e['planner_type'], e['status'], e['passed_ts'])
            for e in segment_executors
        ]
        == [
            ('eats', 'active', None),
            ('crutches', 'active', matching.IsInstance(datetime.datetime)),
            ('delivery', 'active', None),
            ('grocery', 'idle', None),
        ]
    )


@pytest.mark.config(
    UNITED_DISPATCH_SEGMENTS_WATCHDOG={
        'enabled': True,
        'launches_pause_ms': 1,
        'processing_limit': 10,
        'checker_settings': {
            'simultaneous_limit': 10,
            'check_executors_update': {'work_mode': 'enabled'},
            'check_executors_force_pass': {
                'work_mode': 'dry_run',
                'dead_time_limit_seconds': {
                    '__default__': 100,
                    'crutches': 10,
                },
            },
        },
    },
)
@pytest.mark.now('2022-01-01T12:00:00+0000')
async def test_need_force_pass_but_dry_run(
        run_executor_watchdog,
        create_segment,
        state_segments_replicated,
        exp_segment_executors_selector,
        list_segment_executors,
        update_segment_executor_record,
        mocked_time,
):
    segment = create_segment()

    await exp_segment_executors_selector(
        executors=[
            {'planner_type': 'eats', 'is_active': True},
            {'planner_type': 'crutches', 'is_active': True},
            {'planner_type': 'delivery', 'is_active': False},
            {'planner_type': 'grocery', 'is_active': False},
        ],
    )

    await state_segments_replicated()

    update_segment_executor_record(
        segment.id, 1, new_updated_ts=mocked_time.now(),
    )
    mocked_time.sleep(11)

    stats = await run_executor_watchdog()

    assert stats == _make_run_stats(
        fetched_executors=4,
        fetched_segments=1,
        total_passed=1,
        actual_passed=0,
    )

    segment_executors = list_segment_executors(segment.id)
    assert (
        [
            (e['planner_type'], e['status'], e['passed_ts'])
            for e in segment_executors
        ]
        == [
            ('eats', 'active', None),
            ('crutches', 'active', None),
            ('delivery', 'idle', None),
            ('grocery', 'idle', None),
        ]
    )


@pytest.mark.config(
    UNITED_DISPATCH_SEGMENTS_WATCHDOG={
        'enabled': True,
        'launches_pause_ms': 1,
        'processing_limit': 10,
        'checker_settings': {
            'simultaneous_limit': 10,
            'check_executors_update': {'work_mode': 'enabled'},
            'check_executors_force_pass': {
                'work_mode': 'disabled',
                'dead_time_limit_seconds': {
                    '__default__': 100,
                    'crutches': 10,
                },
            },
        },
    },
)
@pytest.mark.now('2022-01-01T12:00:00+0000')
async def test_need_force_pass_but_disabled(
        run_executor_watchdog,
        create_segment,
        state_segments_replicated,
        exp_segment_executors_selector,
        list_segment_executors,
        update_segment_executor_record,
        mocked_time,
):
    segment = create_segment()

    await exp_segment_executors_selector(
        executors=[
            {'planner_type': 'eats', 'is_active': True},
            {'planner_type': 'crutches', 'is_active': True},
            {'planner_type': 'delivery', 'is_active': False},
            {'planner_type': 'grocery', 'is_active': False},
        ],
    )

    await state_segments_replicated()

    update_segment_executor_record(
        segment.id, 1, new_updated_ts=mocked_time.now(),
    )
    mocked_time.sleep(11)

    stats = await run_executor_watchdog()

    assert stats == _make_run_stats(
        fetched_executors=4,
        fetched_segments=1,
        total_passed=0,
        actual_passed=0,
    )

    segment_executors = list_segment_executors(segment.id)
    assert (
        [
            (e['planner_type'], e['status'], e['passed_ts'])
            for e in segment_executors
        ]
        == [
            ('eats', 'active', None),
            ('crutches', 'active', None),
            ('delivery', 'idle', None),
            ('grocery', 'idle', None),
        ]
    )


@pytest.mark.config(
    UNITED_DISPATCH_SEGMENTS_WATCHDOG={
        'enabled': True,
        'launches_pause_ms': 1,
        'processing_limit': 10,
        'checker_settings': {
            'simultaneous_limit': 10,
            'check_executors_update': {'work_mode': 'enabled'},
            'check_executors_force_pass': {
                'work_mode': 'enabled',
                'dead_time_limit_seconds': {'__default__': 1},
            },
        },
    },
)
@pytest.mark.now('2022-01-01T12:00:00+0000')
async def test_need_force_pass_but_no_idle_executors(
        testpoint,
        run_executor_watchdog,
        create_segment,
        state_segments_replicated,
        exp_segment_executors_selector,
        list_segment_executors,
        update_segment_executor_record,
        mocked_time,
):
    segment = create_segment()

    await exp_segment_executors_selector(
        executors=[
            {'planner_type': 'crutches', 'is_active': True},
            {'planner_type': 'delivery', 'is_active': True},
        ],
    )

    await state_segments_replicated()

    @testpoint('segments-watchdog::cannot_pass')
    def cannot_pass(data):
        pass

    update_segment_executor_record(
        segment.id, 1, new_updated_ts=mocked_time.now(),
    )
    mocked_time.sleep(11)

    stats = await run_executor_watchdog()

    assert stats == _make_run_stats(
        fetched_executors=2,
        fetched_segments=1,
        total_passed=0,
        actual_passed=0,
    )

    segment_executors = list_segment_executors(segment.id)
    assert [
        (e['planner_type'], e['status'], e['passed_ts'])
        for e in segment_executors
    ] == [('crutches', 'active', None), ('delivery', 'active', None)]

    assert cannot_pass.times_called
