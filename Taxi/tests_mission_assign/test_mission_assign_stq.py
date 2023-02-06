import datetime
import uuid

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import common_pb2
from google.protobuf import timestamp_pb2
import mission_pb2
import pytest


STAGE_START_TIME_CONFIG_FORMAT = '2021-08-25T12:00:00+0000'
STAGE_START_TIME_PYTHON_ISOFORMAT = '2021-08-25T12:00:00+00:00'

STAGE_END_TIME_CONFIG_FORMAT = '2021-11-25T12:00:00+0000'
STAGE_END_TIME_PYTHON_ISOFORMAT = '2021-11-25T12:00:00+00:00'

STAGE_START_SECONDS = int(
    datetime.datetime.fromisoformat(
        STAGE_START_TIME_PYTHON_ISOFORMAT,
    ).timestamp(),
)
STAGE_END_SECONDS = int(
    datetime.datetime.fromisoformat(
        STAGE_END_TIME_PYTHON_ISOFORMAT,
    ).timestamp(),
)

TASK_SEGMENT_UIDS = sorted([str(uuid.uuid4()) for _ in range(4)])
ASSIGN_UIDS = sorted([str(uuid.uuid4()) for _ in range(4)])

ASSIGN_PROGRESS_IN_PROGRESS = 'in_progress'
ASSIGN_PROGRESS_FAILED = 'failed'
ASSIGN_PROGRESS_COMPLETE = 'complete'

ASSIGN_STATUS_REQUESTED = 'assign_requested'
ASSIGN_STATUS_SKIPPED = 'assign_skipped'
ASSIGN_STATUS_FAILED = 'assign_failed'


def get_assign_progress(cursor):
    cursor.execute(
        f"""
                SELECT stage_id, status, row_offset
                from cashback_levels.assign_progress;
            """,
    )
    return [*cursor]


def set_assign_progress(cursor, assign_progress_params):
    for params in assign_progress_params:
        cursor.execute(
            f"""
                    INSERT INTO cashback_levels.assign_progress
                    (id, stage_id, status)
                    VALUES {params};
                """,
        )


def get_assign_status(cursor, assign_id):
    cursor.execute(
        f"""
                SELECT assign_id, stage_id, yt_table, task_description_id,
                segment, mc_ticket, status
                FROM cashback_levels.assign_status
                WHERE assign_id='{assign_id}';
            """,
    )
    return [*cursor]


def set_segments_tasks_data(cursor, segments_tasks_data):
    for params in segments_tasks_data:
        cursor.execute(
            f"""
                    INSERT INTO cashback_levels.segments_tasks
                    (id, segment, task_description_id, stage_id)
                    VALUES {params}
                """,
        )


@pytest.mark.config(
    CASHBACK_LEVELS_STAGES_DESCRIPTION={
        'stage1': {
            'start_time': STAGE_START_TIME_CONFIG_FORMAT,
            'end_time': STAGE_END_TIME_CONFIG_FORMAT,
            'stage_id': 'stage1',
            'next_stage_id': 'stage2',
        },
    },
)
@pytest.mark.config(
    CASHBACK_LEVELS_MISSION_CONTROL_ENDPOINTS=['localhost:1083'],
)
@pytest.mark.experiments3(filename='config3_cashback_levels_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.now('2021-09-25T12:00:00+0000')
@pytest.mark.parametrize(
    (
        'stq_data',
        'stage_id',
        'segments_tasks_data',
        'assign_progress_data',
        'assign_status_expected',
        'expected_requests',
        'expected_responses',
        'assign_progress_result',
    ),
    [
        pytest.param(
            {
                'assign_id': ASSIGN_UIDS[0],
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_folder': '//home/testsuite/segments',
                'need_accept': False,
            },
            'stage1',
            [
                f'(\'{TASK_SEGMENT_UIDS[0]}\', \'segment_one\', '
                f'\'task1_level1\', \'stage1\')',
                f'(\'{TASK_SEGMENT_UIDS[1]}\', \'segment_one\', '
                f'\'task1_level2\', \'stage1\')',
                f'(\'{TASK_SEGMENT_UIDS[2]}\', \'segment_two\', '
                f'\'task2_level1\', \'stage1\')',
                f'(\'{TASK_SEGMENT_UIDS[3]}\', \'segment_two\', '
                f'\'task2_level2\', \'stage1\')',
            ],
            [
                f'(\'{ASSIGN_UIDS[0]}\', \'stage1\', '
                f'\'{ASSIGN_PROGRESS_IN_PROGRESS}\')',
            ],
            [
                (
                    ASSIGN_UIDS[0],
                    'stage1',
                    '//home/testsuite/segments/segment_one-1',
                    'task1_level1',
                    'segment_one',
                    'ticket1',
                    ASSIGN_STATUS_REQUESTED,
                ),
                (
                    ASSIGN_UIDS[0],
                    'stage1',
                    '//home/testsuite/segments/segment_one-2',
                    'task1_level2',
                    'segment_one',
                    'ticket2',
                    ASSIGN_STATUS_REQUESTED,
                ),
                (
                    ASSIGN_UIDS[0],
                    'stage1',
                    '//home/testsuite/segments/segment_two-1',
                    'task2_level1',
                    'segment_two',
                    'ticket3',
                    ASSIGN_STATUS_REQUESTED,
                ),
                (
                    ASSIGN_UIDS[0],
                    'stage1',
                    '//home/testsuite/segments/segment_two-2',
                    'task2_level2',
                    'segment_two',
                    'ticket4',
                    ASSIGN_STATUS_REQUESTED,
                ),
            ],
            [
                dict(
                    yt_path='//home/testsuite/segments/segment_one-1',
                    customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                    external_id='task1_level1',
                    start_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_START_SECONDS,
                    ),
                    stop_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_END_SECONDS,
                    ),
                    template_id='template_id1',
                    parameters={'target': '5'},
                    await_of_accept=False,
                ),
                dict(
                    yt_path='//home/testsuite/segments/segment_one-2',
                    customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                    external_id='task1_level2',
                    start_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_START_SECONDS,
                    ),
                    stop_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_END_SECONDS,
                    ),
                    template_id='template_id1',
                    parameters={'target': '5'},
                    await_of_accept=False,
                ),
                dict(
                    yt_path='//home/testsuite/segments/segment_two-1',
                    customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                    external_id='task2_level1',
                    start_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_START_SECONDS,
                    ),
                    stop_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_END_SECONDS,
                    ),
                    template_id='template_id2',
                    parameters={'target': '10'},
                    await_of_accept=False,
                ),
                dict(
                    yt_path='//home/testsuite/segments/segment_two-2',
                    customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                    external_id='task2_level2',
                    start_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_START_SECONDS,
                    ),
                    stop_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_END_SECONDS,
                    ),
                    template_id='template_id2',
                    parameters={'target': '10'},
                    await_of_accept=False,
                ),
            ],
            [
                dict(
                    status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS,
                    assign_ticket='ticket1',
                ),
                dict(
                    status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS,
                    assign_ticket='ticket2',
                ),
                dict(
                    status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS,
                    assign_ticket='ticket3',
                ),
                dict(
                    status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS,
                    assign_ticket='ticket4',
                ),
            ],
            ('stage1', ASSIGN_PROGRESS_COMPLETE, 100),
            id='different_tasks_segments',
        ),
        pytest.param(
            {
                'assign_id': ASSIGN_UIDS[0],
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_folder': '//home/testsuite/segments',
                'need_accept': True,
            },
            'stage1',
            [
                f'(\'{TASK_SEGMENT_UIDS[0]}\', \'segment_one\', '
                f'\'task1_level1\', \'stage1\')',
                f'(\'{TASK_SEGMENT_UIDS[1]}\', '
                f'\'segment_that_is_not_in_folder\', '
                f'\'task1_level2\', \'stage1\')',
                f'(\'{TASK_SEGMENT_UIDS[2]}\', \'segment_one\', '
                f'\'task1_level3\', \'stage1\')',
            ],
            [
                f'(\'{ASSIGN_UIDS[0]}\', \'stage1\', '
                f'\'{ASSIGN_PROGRESS_IN_PROGRESS}\')',
            ],
            [
                (
                    ASSIGN_UIDS[0],
                    'stage1',
                    '//home/testsuite/segments/segment_one-1',
                    'task1_level1',
                    'segment_one',
                    'ticket1',
                    ASSIGN_STATUS_REQUESTED,
                ),
                (
                    ASSIGN_UIDS[0],
                    'stage1',
                    '//home/testsuite/segments/'
                    'segment_that_is_not_in_folder-2',
                    'task1_level2',
                    'segment_that_is_not_in_folder',
                    '',
                    ASSIGN_STATUS_SKIPPED,
                ),
                (
                    ASSIGN_UIDS[0],
                    'stage1',
                    '//home/testsuite/segments/segment_one-3',
                    'task1_level3',
                    'segment_one',
                    '',
                    ASSIGN_STATUS_SKIPPED,
                ),
            ],
            [
                dict(
                    yt_path='//home/testsuite/segments/segment_one-1',
                    customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                    external_id='task1_level1',
                    start_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_START_SECONDS,
                    ),
                    stop_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_END_SECONDS,
                    ),
                    template_id='template_id1',
                    parameters={'target': '5'},
                    await_of_accept=True,
                ),
            ],
            [
                dict(
                    status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS,
                    assign_ticket='ticket1',
                ),
            ],
            ('stage1', ASSIGN_PROGRESS_COMPLETE, 100),
            id='segment_not_in_folder_and_level_not_in_folder',
        ),
        pytest.param(
            {
                'assign_id': ASSIGN_UIDS[0],
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_folder': '//home/testsuite/segments',
                'need_accept': True,
            },
            'stage1',
            [
                f'(\'{TASK_SEGMENT_UIDS[0]}\', \'segment_one\', '
                f'\'task1_level1\', \'stage1\')',
                f'(\'{TASK_SEGMENT_UIDS[1]}\', \'segment_one\', '
                f'\'task1_level2\', \'stage2\')',
            ],
            [
                f'(\'{ASSIGN_UIDS[0]}\', \'stage1\', '
                f'\'{ASSIGN_PROGRESS_IN_PROGRESS}\')',
            ],
            [
                (
                    ASSIGN_UIDS[0],
                    'stage1',
                    '//home/testsuite/segments/segment_one-1',
                    'task1_level1',
                    'segment_one',
                    'ticket1',
                    ASSIGN_STATUS_REQUESTED,
                ),
            ],
            [
                dict(
                    yt_path='//home/testsuite/segments/segment_one-1',
                    customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                    external_id='task1_level1',
                    start_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_START_SECONDS,
                    ),
                    stop_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_END_SECONDS,
                    ),
                    template_id='template_id1',
                    parameters={'target': '5'},
                    await_of_accept=True,
                ),
            ],
            [
                dict(
                    status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS,
                    assign_ticket='ticket1',
                ),
            ],
            ('stage1', ASSIGN_PROGRESS_COMPLETE, 100),
            id='different_stage_ignored',
        ),
    ],
)
async def test_mission_assign_stq_success(
        yt_apply,
        stq_runner,
        pgsql,
        stq_data,
        stage_id,
        segments_tasks_data,
        assign_progress_data,
        assign_status_expected,
        expected_requests,
        expected_responses,
        mock_mc_segment_mission_service,
        assign_progress_result,
):
    async with mock_mc_segment_mission_service(
            expected_requests, expected_responses,
    ):
        cursor = pgsql['cashback_levels'].cursor()
        set_segments_tasks_data(cursor, segments_tasks_data)
        set_assign_progress(cursor, assign_progress_data)

        values = get_assign_progress(cursor)
        assert len(values) == 1
        assert values[0] == (stage_id, ASSIGN_PROGRESS_IN_PROGRESS, 0)

        await stq_runner.cashback_levels_segments_assign.call(
            task_id=stq_data['stage_id'], kwargs=stq_data,
        )

        values = get_assign_progress(cursor)
        assert len(values) == 1
        assert values[0] == assign_progress_result

        values = get_assign_status(cursor, stq_data['assign_id'])
        assert assign_status_expected == values


@pytest.mark.config(
    CASHBACK_LEVELS_STAGES_DESCRIPTION={
        'stage1': {
            'start_time': STAGE_START_TIME_CONFIG_FORMAT,
            'end_time': STAGE_END_TIME_CONFIG_FORMAT,
            'stage_id': 'stage1',
            'next_stage_id': 'stage2',
        },
    },
)
@pytest.mark.config(
    CASHBACK_LEVELS_MISSION_CONTROL_ENDPOINTS=['localhost:1083'],
)
@pytest.mark.experiments3(filename='config3_cashback_levels_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.now('2021-09-25T12:00:00+0000')
@pytest.mark.parametrize(
    (
        'stq_data',
        'stage_id',
        'segments_tasks_data',
        'assign_progress_data',
        'assign_status_expected',
        'expected_requests',
        'expected_responses',
        'reschedule',
        'assign_progress_result',
    ),
    [
        pytest.param(
            {
                'assign_id': ASSIGN_UIDS[0],
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_folder': '//home/testsuite/segments',
                'need_accept': False,
            },
            'stage1',
            [
                f'(\'{TASK_SEGMENT_UIDS[0]}\', \'segment_one\', '
                f'\'task1_level1\', \'stage1\')',
            ],
            [
                f'(\'{ASSIGN_UIDS[0]}\', \'stage1\', '
                f'\'{ASSIGN_PROGRESS_IN_PROGRESS}\')',
            ],
            [
                (
                    ASSIGN_UIDS[0],
                    'stage1',
                    '//home/testsuite/segments/segment_one-1',
                    'task1_level1',
                    'segment_one',
                    'ticket1',
                    ASSIGN_STATUS_FAILED,
                ),
            ],
            [
                dict(
                    yt_path='//home/testsuite/segments/segment_one-1',
                    customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                    external_id='task1_level1',
                    start_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_START_SECONDS,
                    ),
                    stop_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_END_SECONDS,
                    ),
                    template_id='template_id1',
                    parameters={'target': '5'},
                    await_of_accept=False,
                ),
            ],
            [
                dict(
                    status=common_pb2.ResponseStatus.RESPONSE_STATUS_ERROR,
                    assign_ticket='ticket1',
                ),
            ],
            True,
            ('stage1', ASSIGN_PROGRESS_IN_PROGRESS, 0),
            id='error_grpc_response_stq_is_rescheduled',
        ),
        pytest.param(
            {
                'assign_id': ASSIGN_UIDS[0],
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_folder': '//home/testsuite/segments',
                'need_accept': False,
            },
            'stage1',
            [
                f'(\'{TASK_SEGMENT_UIDS[0]}\', \'segment_one\', '
                f'\'unknown_task\', \'stage1\')',
            ],
            [
                f'(\'{ASSIGN_UIDS[0]}\', \'stage1\', '
                f'\'{ASSIGN_PROGRESS_IN_PROGRESS}\')',
            ],
            [],
            [],
            [],
            False,
            ('stage1', ASSIGN_PROGRESS_FAILED, 0),
            id='non_existent_task_fails',
        ),
    ],
)
async def test_mission_assign_stq_error(
        yt_apply,
        mockserver,
        stq_runner,
        pgsql,
        stq_data,
        stage_id,
        segments_tasks_data,
        assign_progress_data,
        assign_status_expected,
        expected_requests,
        expected_responses,
        mock_mc_segment_mission_service,
        reschedule,
        assign_progress_result,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def _mock_stq_reschedule(request):
        return {}

    async with mock_mc_segment_mission_service(
            expected_requests, expected_responses,
    ):
        cursor = pgsql['cashback_levels'].cursor()
        set_segments_tasks_data(cursor, segments_tasks_data)
        set_assign_progress(cursor, assign_progress_data)

        values = get_assign_progress(cursor)
        assert len(values) == 1
        assert values[0] == (stage_id, ASSIGN_PROGRESS_IN_PROGRESS, 0)

        await stq_runner.cashback_levels_segments_assign.call(
            task_id=stq_data['stage_id'], kwargs=stq_data,
        )
        if reschedule:
            assert _mock_stq_reschedule.has_calls

        values = get_assign_progress(cursor)
        assert len(values) == 1
        assert values[0] == assign_progress_result

        values = get_assign_status(cursor, stq_data['assign_id'])
        assert assign_status_expected == values


@pytest.mark.config(
    CASHBACK_LEVELS_STAGES_DESCRIPTION={
        'stage1': {
            'start_time': STAGE_START_TIME_CONFIG_FORMAT,
            'end_time': STAGE_END_TIME_CONFIG_FORMAT,
            'stage_id': 'stage1',
            'next_stage_id': 'stage2',
        },
    },
    CASHBACK_LEVELS_SEGMENTS_ASSIGN_STQ_PARAMS={
        'items_per_iteration': 2,
        'reschedule_delay': 500,
        'reschedules_limit': 5,
    },
)
@pytest.mark.config(
    CASHBACK_LEVELS_MISSION_CONTROL_ENDPOINTS=['localhost:1083'],
)
@pytest.mark.experiments3(filename='config3_cashback_levels_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.now('2021-09-25T12:00:00+0000')
@pytest.mark.parametrize(
    (
        'stq_data',
        'stage_id',
        'segments_tasks_data',
        'assign_progress_data',
        'assign_status_expected',
        'expected_requests',
        'expected_responses',
        'assign_progress_result',
    ),
    [
        pytest.param(
            {
                'assign_id': ASSIGN_UIDS[0],
                'stage_id': 'stage1',
                'yt_cluster': 'hahn',
                'yt_folder': '//home/testsuite/segments',
                'need_accept': True,
            },
            'stage1',
            [
                f'(\'{TASK_SEGMENT_UIDS[0]}\', \'segment_one\', '
                f'\'task1_level1\', \'stage1\')',
                f'(\'{TASK_SEGMENT_UIDS[1]}\', \'segment_one\', '
                f'\'task1_level2\', \'stage1\')',
                f'(\'{TASK_SEGMENT_UIDS[2]}\', \'segment_two\', '
                f'\'task2_level1\', \'stage1\')',
                f'(\'{TASK_SEGMENT_UIDS[3]}\', \'segment_two\', '
                f'\'task2_level2\', \'stage1\')',
            ],
            [
                f'(\'{ASSIGN_UIDS[0]}\', \'stage1\', '
                f'\'{ASSIGN_PROGRESS_IN_PROGRESS}\')',
            ],
            [
                (
                    ASSIGN_UIDS[0],
                    'stage1',
                    '//home/testsuite/segments/segment_one-1',
                    'task1_level1',
                    'segment_one',
                    'ticket1',
                    ASSIGN_STATUS_REQUESTED,
                ),
                (
                    ASSIGN_UIDS[0],
                    'stage1',
                    '//home/testsuite/segments/segment_one-2',
                    'task1_level2',
                    'segment_one',
                    'ticket2',
                    ASSIGN_STATUS_REQUESTED,
                ),
                (
                    ASSIGN_UIDS[0],
                    'stage1',
                    '//home/testsuite/segments/segment_two-1',
                    'task2_level1',
                    'segment_two',
                    'ticket3',
                    ASSIGN_STATUS_REQUESTED,
                ),
                (
                    ASSIGN_UIDS[0],
                    'stage1',
                    '//home/testsuite/segments/segment_two-2',
                    'task2_level2',
                    'segment_two',
                    'ticket4',
                    ASSIGN_STATUS_REQUESTED,
                ),
            ],
            [
                dict(
                    yt_path='//home/testsuite/segments/segment_one-1',
                    customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                    external_id='task1_level1',
                    start_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_START_SECONDS,
                    ),
                    stop_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_END_SECONDS,
                    ),
                    template_id='template_id1',
                    parameters={'target': '5'},
                    await_of_accept=True,
                ),
                dict(
                    yt_path='//home/testsuite/segments/segment_one-2',
                    customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                    external_id='task1_level2',
                    start_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_START_SECONDS,
                    ),
                    stop_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_END_SECONDS,
                    ),
                    template_id='template_id1',
                    parameters={'target': '5'},
                    await_of_accept=True,
                ),
                dict(
                    yt_path='//home/testsuite/segments/segment_two-1',
                    customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                    external_id='task2_level1',
                    start_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_START_SECONDS,
                    ),
                    stop_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_END_SECONDS,
                    ),
                    template_id='template_id2',
                    parameters={'target': '10'},
                    await_of_accept=True,
                ),
                dict(
                    yt_path='//home/testsuite/segments/segment_two-2',
                    customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                    external_id='task2_level2',
                    start_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_START_SECONDS,
                    ),
                    stop_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_END_SECONDS,
                    ),
                    template_id='template_id2',
                    parameters={'target': '10'},
                    await_of_accept=True,
                ),
            ],
            [
                dict(
                    status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS,
                    assign_ticket='ticket1',
                ),
                dict(
                    status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS,
                    assign_ticket='ticket2',
                ),
                dict(
                    status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS,
                    assign_ticket='ticket3',
                ),
                dict(
                    status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS,
                    assign_ticket='ticket4',
                ),
            ],
            ('stage1', ASSIGN_PROGRESS_COMPLETE, 4),
            id='different_tasks_segments',
        ),
    ],
)
async def test_mission_assign_stq_chunk_read_ok(
        yt_apply,
        stq_runner,
        pgsql,
        stq_data,
        stage_id,
        segments_tasks_data,
        assign_progress_data,
        assign_status_expected,
        expected_requests,
        expected_responses,
        mock_mc_segment_mission_service,
        assign_progress_result,
):
    async with mock_mc_segment_mission_service(
            expected_requests, expected_responses,
    ):
        cursor = pgsql['cashback_levels'].cursor()
        set_segments_tasks_data(cursor, segments_tasks_data)
        set_assign_progress(cursor, assign_progress_data)

        values = get_assign_progress(cursor)
        assert len(values) == 1
        assert values[0] == (stage_id, ASSIGN_PROGRESS_IN_PROGRESS, 0)

        await stq_runner.cashback_levels_segments_assign.call(
            task_id=stq_data['stage_id'], kwargs=stq_data,
        )

        values = get_assign_progress(cursor)
        assert len(values) == 1
        assert values[0] == assign_progress_result

        values = get_assign_status(cursor, stq_data['assign_id'])
        assert assign_status_expected == values


@pytest.mark.config(
    CASHBACK_LEVELS_STAGES_DESCRIPTION={
        'stage1': {
            'start_time': STAGE_START_TIME_CONFIG_FORMAT,
            'end_time': STAGE_END_TIME_CONFIG_FORMAT,
            'stage_id': 'stage1',
            'next_stage_id': 'stage2',
        },
        'stage2': {
            'start_time': STAGE_START_TIME_CONFIG_FORMAT,
            'end_time': STAGE_END_TIME_CONFIG_FORMAT,
            'stage_id': 'stage2',
            'next_stage_id': 'stage2',
        },
    },
)
@pytest.mark.config(
    CASHBACK_LEVELS_MISSION_CONTROL_ENDPOINTS=['localhost:1083'],
)
@pytest.mark.experiments3(filename='config3_cashback_levels_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.now('2021-09-25T12:00:00+0000')
@pytest.mark.parametrize(
    (
        'stq_data',
        'segments_tasks_data',
        'assign_progress_data',
        'assign_status_expected',
        'expected_requests',
        'expected_responses',
        'assign_progress_result',
    ),
    [
        pytest.param(
            {
                'assign_id': ASSIGN_UIDS[0],
                'stage_id': 'stage2',
                'yt_cluster': 'hahn',
                'yt_folder': '//home/testsuite/segments',
                'need_accept': True,
            },
            [
                f'(\'{TASK_SEGMENT_UIDS[0]}\', \'segment_one\', '
                f'\'task1_level1\', \'stage1\')',
                f'(\'{TASK_SEGMENT_UIDS[1]}\', \'segment_two\', '
                f'\'task2_level2\', \'stage1\')',
                f'(\'{TASK_SEGMENT_UIDS[2]}\', \'segment_one\', '
                f'\'stage2_task\', \'stage2\')',
                f'(\'{TASK_SEGMENT_UIDS[3]}\', \'segment_two\', '
                f'\'stage2_task_level2\', \'stage2\')',
            ],
            [
                f'(\'{ASSIGN_UIDS[0]}\', \'stage2\', '
                f'\'{ASSIGN_PROGRESS_IN_PROGRESS}\')',
                f'(\'{ASSIGN_UIDS[1]}\', \'stage1\', '
                f'\'{ASSIGN_PROGRESS_COMPLETE}\')',
            ],
            [
                (
                    ASSIGN_UIDS[0],
                    'stage2',
                    '//home/testsuite/segments/segment_one-1',
                    'stage2_task',
                    'segment_one',
                    'ticket3',
                    ASSIGN_STATUS_REQUESTED,
                ),
                (
                    ASSIGN_UIDS[0],
                    'stage2',
                    '//home/testsuite/segments/segment_two-2',
                    'stage2_task_level2',
                    'segment_two',
                    'ticket4',
                    ASSIGN_STATUS_REQUESTED,
                ),
            ],
            [
                dict(
                    yt_path='//home/testsuite/segments/segment_one-1',
                    customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                    external_id='stage2_task',
                    start_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_START_SECONDS,
                    ),
                    stop_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_END_SECONDS,
                    ),
                    template_id='template_id2',
                    parameters={'target': 'whatever'},
                    await_of_accept=True,
                ),
                dict(
                    yt_path='//home/testsuite/segments/segment_two-2',
                    customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                    external_id='stage2_task_level2',
                    start_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_START_SECONDS,
                    ),
                    stop_time=timestamp_pb2.Timestamp(
                        seconds=STAGE_END_SECONDS,
                    ),
                    template_id='template_id2',
                    parameters={'target': 'whatever'},
                ),
            ],
            [
                dict(
                    status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS,
                    assign_ticket='ticket3',
                ),
                dict(
                    status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS,
                    assign_ticket='ticket4',
                ),
            ],
            ('stage2', ASSIGN_PROGRESS_COMPLETE, 100),
            id='different_tasks_segments',
        ),
    ],
)
async def test_mission_assign_stage_when_multiple_available_for_user(
        yt_apply,
        stq_runner,
        pgsql,
        stq_data,
        segments_tasks_data,
        assign_progress_data,
        assign_status_expected,
        expected_requests,
        expected_responses,
        mock_mc_segment_mission_service,
        assign_progress_result,
):
    async with mock_mc_segment_mission_service(
            expected_requests, expected_responses,
    ):
        cursor = pgsql['cashback_levels'].cursor()
        set_segments_tasks_data(cursor, segments_tasks_data)
        set_assign_progress(cursor, assign_progress_data)

        await stq_runner.cashback_levels_segments_assign.call(
            task_id=stq_data['stage_id'], kwargs=stq_data,
        )

        values = get_assign_progress(cursor)
        assert len(values) == 2
        assert values[1] == assign_progress_result

        values = get_assign_status(cursor, stq_data['assign_id'])
        assert assign_status_expected == values
