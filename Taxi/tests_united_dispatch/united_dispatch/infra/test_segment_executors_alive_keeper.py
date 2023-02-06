import datetime

import pytest

PERIODIC_TASK_NAME = 'segment_executors_alive_keeper'
METRICS_NAME = 'segment-executors-alive-keeper-stats'


@pytest.fixture(name='reset_stats')
async def _reset_stats(taxi_united_dispatch, testpoint):
    await taxi_united_dispatch.tests_control(reset_metrics=True)

    @testpoint('segment-executors-alive-keeper::with-current-epoch')
    def _with_current_epoch(param):
        return {'with_current_epoch': True}


@pytest.fixture(name='keeper_reset')
async def _keeper_reset(testpoint):
    async def wrapper(reset=True):
        @testpoint('segment-executors-alive-keeper::reset')
        def _reset(param):
            return reset

    return wrapper


@pytest.fixture(name='state_segments_keeper')
async def _state_segments_keeper(
        state_segments_replicated,
        run_single_planner,
        exp_segment_executors_selector,
        exp_planner_settings,
        keeper_reset,
        reset_stats,
):
    # initialization goes before any call,
    # so it can be overwritten by other tests
    await exp_planner_settings()
    await exp_segment_executors_selector(
        executors=[{'planner_type': 'crutches', 'is_active': True}],
    )

    async def wrapper(reset=True):
        await keeper_reset(reset)

        stats = await run_single_planner()

        return stats

    return wrapper


@pytest.mark.now('2022-01-01T12:00:00+0000')
async def test_proposed_segment_to_be_updated(
        testpoint,
        create_segment,
        state_segments_replicated,
        state_segments_keeper,
        update_segment_executor_record,
        mocked_time,
):
    """
        Check proposed segment will be updated
    """

    segment = create_segment(crutches={'force_crutch_builder': True})

    @testpoint('segment-executors-alive-keeper::put')
    def check_keeper_segment_executors(data):
        assert data == [
            {
                'planner_type': 'crutches',
                'put_time': '2022-01-01T12:01:40+0000',
                'segment_id': segment.id,
            },
        ]

    await state_segments_replicated()

    update_segment_executor_record(segment.id, 0)
    mocked_time.sleep(100)

    await state_segments_keeper()

    assert check_keeper_segment_executors.times_called == 1


@pytest.mark.now('2022-01-01T12:00:00+0000')
async def test_passed_segment_to_be_updated(
        testpoint,
        create_segment,
        state_segments_replicated,
        state_segments_keeper,
        update_segment_executor_record,
        mocked_time,
):
    """
        Check passing segment will be updated
    """

    segment = create_segment(
        crutches={'force_crutch_builder': True, 'forced_pass': True},
    )

    @testpoint('segment-executors-alive-keeper::put')
    def check_keeper_segment_executors(data):
        assert data == [
            {
                'planner_type': 'crutches',
                'put_time': '2022-01-01T12:01:40+0000',
                'segment_id': segment.id,
            },
        ]

    await state_segments_replicated()

    update_segment_executor_record(segment.id, 0)
    mocked_time.sleep(100)

    stats = await state_segments_keeper()

    assert (
        stats.find_metric(
            {'distlock_worker_alias': 'output-pass-segments'},
        ).value
        == 1
    )

    assert check_keeper_segment_executors.times_called == 1


@pytest.mark.now('2022-01-01T12:00:00+0000')
async def test_skipped_segment_to_be_updated(
        testpoint,
        create_segment,
        state_segments_replicated,
        state_segments_keeper,
        update_segment_executor_record,
        mocked_time,
):
    """
        Check skipping segment will be updated
    """

    segment = create_segment(
        crutches={'force_crutch_builder': True, 'batch_with': 'not-exists'},
    )

    @testpoint('segment-executors-alive-keeper::put')
    def check_keeper_segment_executors(data):
        assert data == [
            {
                'planner_type': 'crutches',
                'put_time': '2022-01-01T12:01:40+0000',
                'segment_id': segment.id,
            },
        ]

    await state_segments_replicated()

    update_segment_executor_record(segment.id, 0)
    mocked_time.sleep(100)

    stats = await state_segments_keeper()

    assert (
        stats.find_metric(
            {'distlock_worker_alias': 'output-skip-segments'},
        ).value
        == 1
    )

    assert check_keeper_segment_executors.times_called == 1


@pytest.mark.now('2022-01-01T12:00:00+0000')
async def test_no_put_twice_same_segment(
        testpoint,
        create_segment,
        state_segments_replicated,
        state_segments_keeper,
        update_segment_executor_record,
        mocked_time,
):
    """
        Check put time same for one segment
    """

    segment = create_segment(
        crutches={'force_crutch_builder': True, 'forced_skip': True},
    )

    @testpoint('segment-executors-alive-keeper::put')
    def check_keeper_segment_executors(data):
        assert data == [
            {
                'planner_type': 'crutches',
                'put_time': '2022-01-01T12:01:40+0000',
                'segment_id': segment.id,
            },
        ]

    await state_segments_replicated()

    update_segment_executor_record(segment.id, 0)
    mocked_time.sleep(100)

    await state_segments_keeper()

    mocked_time.sleep(10)
    await state_segments_keeper(reset=False)

    assert check_keeper_segment_executors.times_called == 2


@pytest.mark.config(
    UNITED_DISPATCH_SEGMENT_EXECUTORS_ALIVE_KEEPER_SETTINGS={
        'dry_run': False,
        'last_change_delay_seconds': 60,
        'launches_pause_ms': 10000,
        'processing_limit': 10,
    },
)
@pytest.mark.now('2022-01-01T12:00:00+0000')
async def test_new_segment_not_updated(
        testpoint,
        create_segment,
        state_segments_replicated,
        state_segments_keeper,
        update_segment_executor_record,
        mocked_time,
):
    """
        Check segment will not be updated because it is new
    """

    segment = create_segment(crutches={'force_crutch_builder': True})

    @testpoint('segment-executors-alive-keeper::put')
    def check_keeper_segment_executors(data):
        assert data == []

    await state_segments_replicated()

    update_segment_executor_record(segment.id, 0)
    mocked_time.sleep(10)

    await state_segments_keeper()

    assert check_keeper_segment_executors.times_called == 1


@pytest.mark.now('2022-01-01T12:00:00+0000')
async def test_passed_one_segment_two_planners(
        testpoint,
        create_segment,
        keeper_reset,
        state_segments_replicated,
        run_planner,
        exp_segment_executors_selector,
        mocked_time,
        reset_stats,
        update_segment_executor_record,
):
    """
        Check passing same segment from two planners
    """

    segment = create_segment(
        crutches={'force_crutch_builder': True, 'forced_pass': True},
    )

    await exp_segment_executors_selector(
        executors=[
            {'planner_type': 'crutches', 'is_active': True},
            {'planner_type': 'testsuite-candidates', 'is_active': True},
        ],
    )

    await state_segments_replicated()

    update_segment_executor_record(segment.id, 0)
    update_segment_executor_record(segment.id, 1)
    mocked_time.sleep(100)

    await keeper_reset(reset=True)

    await state_segments_replicated()

    stats = await run_planner(component_name='crutches-planner')
    assert (
        stats.find_metric(
            {'distlock_worker_alias': 'output-pass-segments'},
        ).value
        == 1
    )

    @testpoint('segment-executors-alive-keeper::put')
    def check_keeper_segment_executors(data):
        assert sorted(data, key=lambda d: d['planner_type']) == [
            {
                'planner_type': 'crutches',
                'put_time': '2022-01-01T12:01:40+0000',
                'segment_id': segment.id,
            },
            {
                'planner_type': 'testsuite-candidates',
                'put_time': '2022-01-01T12:01:50+0000',
                'segment_id': segment.id,
            },
        ]

    await keeper_reset(reset=False)
    mocked_time.sleep(10)
    await run_planner(component_name='testsuite-candidates-planner')

    assert check_keeper_segment_executors.times_called


@pytest.mark.config(
    UNITED_DISPATCH_SEGMENT_EXECUTORS_ALIVE_KEEPER_SETTINGS={
        'dry_run': False,
        'last_change_delay_seconds': 60,
        'launches_pause_ms': 10000,
        'processing_limit': 10,
    },
)
@pytest.mark.now('2022-01-01T12:00:00+0000')
async def test_update_all(
        taxi_united_dispatch,
        taxi_united_dispatch_monitor,
        testpoint,
        create_segment,
        state_segments_replicated,
        state_segments_keeper,
        update_segment_executor_record,
        mocked_time,
        list_segment_executors,
):
    """
        Check updated all queued executors
    """

    segment1 = create_segment(
        crutches={'force_crutch_builder': True, 'forced_skip': True},
    )
    segment2 = create_segment(
        crutches={'force_crutch_builder': True, 'forced_skip': True},
    )

    @testpoint('segment-executors-alive-keeper::remaining')
    def check_keeper_segment_executors(data):
        assert data == []

    await state_segments_replicated()

    update_segment_executor_record(segment1.id, 0)
    update_segment_executor_record(segment2.id, 0)
    mocked_time.sleep(100)

    await state_segments_keeper()

    mocked_time.sleep(50)

    await taxi_united_dispatch.run_task(PERIODIC_TASK_NAME)

    stats = await taxi_united_dispatch_monitor.get_metric(METRICS_NAME)
    assert stats == {
        'per_planner': {
            '$meta': {'solomon_children_labels': 'planner_type'},
            'crutches': {
                'count': 2,
                'lag': {
                    '$meta': {'solomon_children_labels': 'percentile'},
                    'p0': 50,
                    'p100': 50,
                    'p50': 50,
                    'p99': 50,
                },
            },
        },
        'total_queue_size': 2,
        'failed_tasks_count': 0,
    }

    for segment in (segment1, segment2):
        segment_executors = list_segment_executors(segment.id)
        assert len(segment_executors) == 1
        assert segment_executors[0]['updated_ts'] > mocked_time.now().replace(
            tzinfo=datetime.timezone.utc,
        )

    assert check_keeper_segment_executors.times_called


@pytest.mark.config(
    UNITED_DISPATCH_SEGMENT_EXECUTORS_ALIVE_KEEPER_SETTINGS={
        'dry_run': True,
        'last_change_delay_seconds': 60,
        'launches_pause_ms': 10000,
        'processing_limit': 10,
    },
)
@pytest.mark.now('2022-01-01T12:00:00+0000')
async def test_dry_run(
        taxi_united_dispatch,
        taxi_united_dispatch_monitor,
        testpoint,
        create_segment,
        state_segments_replicated,
        state_segments_keeper,
        mocked_time,
        list_segment_executors,
        update_segment_executor_record,
):
    """
        Check need to update all, but dry run is on
    """

    segment = create_segment(
        crutches={'force_crutch_builder': True, 'forced_skip': True},
    )

    @testpoint('segment-executors-alive-keeper::remaining')
    def check_keeper_segment_executors(data):
        assert data == []

    await state_segments_replicated()

    update_segment_executor_record(segment.id, 0)
    mocked_time.sleep(100)

    await state_segments_keeper()

    mocked_time.sleep(50)

    await taxi_united_dispatch.run_task(PERIODIC_TASK_NAME)

    stats = await taxi_united_dispatch_monitor.get_metric(METRICS_NAME)
    assert stats == {
        'per_planner': {
            '$meta': {'solomon_children_labels': 'planner_type'},
            'crutches': {
                'count': 1,
                'lag': {
                    '$meta': {'solomon_children_labels': 'percentile'},
                    'p0': 50,
                    'p100': 50,
                    'p50': 50,
                    'p99': 50,
                },
            },
        },
        'total_queue_size': 1,
        'failed_tasks_count': 0,
    }

    segment_executors = list_segment_executors(segment.id)
    assert len(segment_executors) == 1
    assert segment_executors[0]['updated_ts'] < mocked_time.now().replace(
        tzinfo=datetime.timezone.utc,
    )

    assert check_keeper_segment_executors.times_called


@pytest.mark.config(
    UNITED_DISPATCH_SEGMENT_EXECUTORS_ALIVE_KEEPER_SETTINGS={
        'dry_run': False,
        'last_change_delay_seconds': 60,
        'launches_pause_ms': 10000,
        'processing_limit': 1,
    },
)
@pytest.mark.now('2022-01-01T12:00:00+0000')
async def test_update_part_limit(
        taxi_united_dispatch,
        taxi_united_dispatch_monitor,
        testpoint,
        create_segment,
        state_segments_replicated,
        state_segments_keeper,
        mocked_time,
        list_segment_executors,
        update_segment_executor_record,
):
    """
        Check updated part because of processing limit
    """

    segment1 = create_segment(
        crutches={'force_crutch_builder': True, 'forced_skip': True},
    )
    segment2 = create_segment(
        crutches={'force_crutch_builder': True, 'forced_skip': True},
    )

    segment_id_updated = None
    segment_id_not_updated = None

    @testpoint('segment-executors-alive-keeper::remaining')
    def check_keeper_segment_executors(data):
        nonlocal segment_id_not_updated
        nonlocal segment_id_updated

        assert len(data) == 1
        assert data[0]['segment_id'] in {segment1.id, segment2.id}
        assert data[0]['planner_type'] == 'crutches'
        assert data[0]['put_time'] == '2022-01-01T12:01:40+0000'

        segment_id_not_updated = data[0]['segment_id']
        segment_id_updated = (
            segment2.id
            if segment_id_not_updated == segment1.id
            else segment1.id
        )

    await state_segments_replicated()

    update_segment_executor_record(segment1.id, 0)
    update_segment_executor_record(segment2.id, 0)
    mocked_time.sleep(100)

    await state_segments_keeper()

    mocked_time.sleep(50)

    await taxi_united_dispatch.run_task(PERIODIC_TASK_NAME)

    stats = await taxi_united_dispatch_monitor.get_metric(METRICS_NAME)
    assert stats == {
        'per_planner': {
            '$meta': {'solomon_children_labels': 'planner_type'},
            'crutches': {
                'count': 1,
                'lag': {
                    '$meta': {'solomon_children_labels': 'percentile'},
                    'p0': 50,
                    'p100': 50,
                    'p50': 50,
                    'p99': 50,
                },
            },
        },
        'total_queue_size': 2,
        'failed_tasks_count': 0,
    }

    assert check_keeper_segment_executors.times_called

    segment_executors = list_segment_executors(segment_id_updated)
    assert len(segment_executors) == 1
    assert segment_executors[0]['updated_ts'] > mocked_time.now().replace(
        tzinfo=datetime.timezone.utc,
    )

    segment_executors = list_segment_executors(segment_id_not_updated)
    assert len(segment_executors) == 1
    assert segment_executors[0]['updated_ts'] < mocked_time.now().replace(
        tzinfo=datetime.timezone.utc,
    )


@pytest.mark.now('2022-01-01T12:00:00+0000')
async def test_delayed_segment_watchdog(
        testpoint,
        create_segment,
        state_segments_replicated,
        state_segments_keeper,
        update_segment_executor_record,
        exp_planner_settings,
        mocked_time,
        wait_until_due_seconds=1800,
):
    """
        Check proposed segment will be updated
    """

    await exp_planner_settings(wait_until_due_seconds=wait_until_due_seconds)

    now = mocked_time.now().replace(tzinfo=datetime.timezone.utc)
    due = now + datetime.timedelta(seconds=2 * wait_until_due_seconds)

    segment = create_segment(
        due=due.isoformat(), crutches={'force_crutch_builder': True},
    )

    @testpoint('segment-executors-alive-keeper::put')
    def check_keeper_segment_executors(data):
        assert data == [
            {
                'planner_type': 'crutches',
                'put_time': '2022-01-01T12:01:40+0000',
                'segment_id': segment.id,
            },
        ]

    await state_segments_replicated()

    update_segment_executor_record(segment.id, 0)
    mocked_time.sleep(100)

    stats = await state_segments_keeper()
    assert (
        stats.find_metric({'distlock_worker_alias': 'input-segments'}).value
        == 0
    )
    assert (
        stats.find_metric(
            {'distlock_worker_alias': 'input-delayed-segments'},
        ).value
        == 1
    )

    assert check_keeper_segment_executors.times_called == 1
