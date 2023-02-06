import datetime

import pytest

CURRENT_TIME = '2021-03-01T12:00:00'


@pytest.fixture(name='get_single_segment_executor')
async def _get_single_segment_executor(list_segment_executors):
    def wrapper(segment_id):
        segment_executors = list_segment_executors(segment_id)
        assert len(segment_executors) == 1

        return segment_executors[0]

    return wrapper


async def test_gamble_history_disables(
        create_segment,
        state_segments_replicated,
        exp_segment_executors_selector,
        exp_planner_settings,
        get_single_segment_executor,
        run_single_planner,
):
    """
        Check disabled, no gamble_count updated.
    """
    await exp_segment_executors_selector(
        executors=[{'planner_type': 'crutches', 'is_active': True}],
    )
    await exp_planner_settings(enable_store_segment_gambles=False)

    seg = create_segment(crutches={'forced_pass': True})
    await state_segments_replicated()

    await run_single_planner()

    segment_executor = get_single_segment_executor(seg.id)
    assert segment_executor['gamble_count'] == 0
    assert segment_executor['throttled_until_ts'] is None


async def test_gamble_count_increased(
        create_segment,
        state_segments_replicated,
        exp_segment_executors_selector,
        exp_planner_settings,
        get_single_segment_executor,
        run_single_planner,
):
    """
        Check gambles_count increased for processed segment.
    """
    await exp_segment_executors_selector(
        executors=[{'planner_type': 'crutches', 'is_active': True}],
    )
    await exp_planner_settings(
        enable_store_segment_gambles=True,
        throttle_segment_schedule=[
            {'gambles_count': 5, 'throttle_duration_sec': 10},
        ],
    )

    seg = create_segment(crutches={'forced_pass': True})
    await state_segments_replicated()

    await run_single_planner()

    segment_executor = get_single_segment_executor(seg.id)
    assert segment_executor['gamble_count'] == 1
    assert segment_executor['throttled_until_ts'] is None


@pytest.mark.now(CURRENT_TIME)
async def test_throttling_delay_stored(
        create_segment,
        state_segments_replicated,
        exp_planner_settings,
        exp_segment_executors_selector,
        get_single_segment_executor,
        run_single_planner,
        mocked_time,
        delta_seconds=10,
):
    """
        Check throttling info stored for segment.
    """
    await exp_segment_executors_selector(
        executors=[{'planner_type': 'crutches', 'is_active': True}],
    )
    await exp_planner_settings(
        enable_store_segment_gambles=True,
        throttle_segment_schedule=[
            {'gambles_count': 0, 'throttle_duration_sec': delta_seconds},
        ],
    )

    seg = create_segment(crutches={'forced_pass': True})
    await state_segments_replicated()

    await run_single_planner()

    segment_executor = get_single_segment_executor(seg.id)
    assert segment_executor['gamble_count'] == 1
    assert segment_executor['throttled_until_ts'] == mocked_time.now().replace(
        tzinfo=datetime.timezone.utc,
    ) + datetime.timedelta(seconds=delta_seconds)


@pytest.mark.parametrize('check_throttled_segment_on_apply', [True, False])
async def test_throttled_segment_not_updated(
        create_segment,
        state_segments_replicated,
        exp_planner_settings,
        exp_segment_executors_selector,
        get_single_segment_executor,
        run_single_planner,
        update_segment_executor_record,
        mocked_time,
        check_throttled_segment_on_apply: bool,
        prev_delta_seconds=5,
        delta_seconds=10,
):
    """
        Check gamble_count not updated for throttled segment.

        check_throttled_segment_on_apply:
          1. True - gamble_count would be updated becouse planner
            actually processed segment;
          2. False - gamble_count would not be updated;
    """
    await exp_segment_executors_selector(
        executors=[{'planner_type': 'crutches', 'is_active': True}],
    )
    await exp_planner_settings(
        enable_store_segment_gambles=True,
        throttle_segment_schedule=[
            {'gambles_count': 0, 'throttle_duration_sec': delta_seconds},
        ],
        check_throttled_segment_on_apply=check_throttled_segment_on_apply,
    )

    seg = create_segment(crutches={'forced_pass': True})
    await state_segments_replicated()

    update_segment_executor_record(
        segment_id=seg.id,
        execution_order=0,
        new_throttled_until_ts=mocked_time.now()
        + datetime.timedelta(seconds=prev_delta_seconds),
    )

    await run_single_planner()

    segment_executor = get_single_segment_executor(seg.id)

    if check_throttled_segment_on_apply:
        assert segment_executor['gamble_count'] == 1
        expected_throttled_until_ts = mocked_time.now().replace(
            tzinfo=datetime.timezone.utc,
        ) + datetime.timedelta(seconds=delta_seconds)
    else:
        # not changed
        assert segment_executor['gamble_count'] == 0
        expected_throttled_until_ts = mocked_time.now().replace(
            tzinfo=datetime.timezone.utc,
        ) + datetime.timedelta(seconds=prev_delta_seconds)

    assert (
        segment_executor['throttled_until_ts'] == expected_throttled_until_ts
    )


@pytest.mark.parametrize('wait_until_due_seconds', [0, 1800])
async def test_due_segment_delay(
        create_segment,
        state_segments_replicated,
        exp_planner_settings,
        exp_segment_executors_selector,
        get_single_segment_executor,
        run_single_planner,
        mocked_time,
        wait_until_due_seconds: int,
):
    """
        Check gambles_count not updated for delayed segment.
    """
    await exp_segment_executors_selector(
        executors=[{'planner_type': 'crutches', 'is_active': True}],
    )
    await exp_planner_settings(
        wait_until_due_seconds=wait_until_due_seconds,
        enable_store_segment_gambles=True,
    )

    now = mocked_time.now().replace(tzinfo=datetime.timezone.utc)
    due = now + datetime.timedelta(seconds=2 * wait_until_due_seconds)

    seg = create_segment(
        due=due.isoformat(), crutches={'force_crutch_builder': True},
    )

    await state_segments_replicated()

    await run_single_planner()

    segment_executor = get_single_segment_executor(seg.id)
    if wait_until_due_seconds == 1800:
        assert segment_executor['gamble_count'] == 0
    elif wait_until_due_seconds == 0:
        assert segment_executor['gamble_count'] == 1
    else:
        assert False
