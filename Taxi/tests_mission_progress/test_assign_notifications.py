import datetime

# pylint: disable=import-error
from google.protobuf import timestamp_pb2
from mission_pb2 import MissionStatus
from mission_pb2 import ProgressStatus
from mission_progress_notification_pb2 import NotificationStatus
import pytest

NTF_STATUS_UPDATED = NotificationStatus.NOTIFICATION_STATUS_UPDATED
NTF_STATUS_ASSIGNED_BY_USER = (
    NotificationStatus.NOTIFICATION_STATUS_ASSIGNED_BY_USER
)
NTF_STATUS_ASSIGNED_BY_SEGMENT = (
    NotificationStatus.NOTIFICATION_STATUS_ASSIGNED_BY_SEGMENT
)

START_TIME = timestamp_pb2.Timestamp(
    seconds=int(
        datetime.datetime.fromisoformat(
            '2021-08-25T12:00:00+00:00',
        ).timestamp(),
    ),
)

STOP_TIME = timestamp_pb2.Timestamp(
    seconds=int(
        datetime.datetime.fromisoformat(
            '2021-09-25T11:00:00+00:00',
        ).timestamp(),
    ),
)


@pytest.mark.config(CASHBACK_LEVELS_MISSION_PROGRESS_CONSUMER_ENABLED=True)
@pytest.mark.now('2021-09-25T12:00:00+0000')
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.experiments3(filename='exp3_assign_notifications_enabled.json')
@pytest.mark.experiments3(
    filename='exp3_mission_completion_notify_disabled.json',
)
@pytest.mark.config(
    CASHBACK_LEVELS_STAGES_DESCRIPTION={
        'stage1': {
            'start_time': '2021-08-25T12:00:00+0000',
            'end_time': '2021-11-25T12:00:00+0000',
            'stage_id': 'stage1',
            'next_stage_id': 'stage2',
        },
    },
)
@pytest.mark.parametrize(
    ('notification_params', 'expected_missions_notifications_db_rows'),
    [
        pytest.param(
            [
                dict(
                    notification_status=NTF_STATUS_ASSIGNED_BY_USER,
                    yandex_uid='666',
                    external_id='task1_level1',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_IN_PROGRESS,
                    progress_type='cyclic_progress',
                    version=1,
                ),
            ],
            [],
            id='dont_assign_cyclic_missions',
        ),
        pytest.param(
            [
                dict(
                    notification_status=NTF_STATUS_ASSIGNED_BY_USER,
                    yandex_uid='666',
                    external_id='task1_level1',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_IN_PROGRESS,
                    progress_type='counter_progress',
                    counter_progress_target=10,
                    counter_progress_current=3,
                    version=1,
                ),
                dict(
                    notification_status=NTF_STATUS_ASSIGNED_BY_SEGMENT,
                    yandex_uid='555',
                    external_id='task2_level1',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_IN_PROGRESS,
                    progress_type='counter_progress',
                    counter_progress_target=10,
                    counter_progress_current=3,
                    start_time=START_TIME,
                    stop_time=STOP_TIME,
                    version=1,
                ),
            ],
            [
                (
                    '666',
                    'task1_level1',
                    'stage1',
                    0,
                    0,
                    'assigned',
                    '',
                    'new',
                    {'target': 10},
                ),
                (
                    '555',
                    'task2_level1',
                    'stage1',
                    0,
                    0,
                    'assigned',
                    '',
                    'new',
                    {
                        'target': 10,
                        'start_time': '2021-08-25T12:00:00+00:00',
                        'stop_time': '2021-09-25T11:00:00+00:00',
                    },
                ),
            ],
            id='test_assign_notifications_creation',
        ),
    ],
)
async def test_assign_notifications_creation(
        get_notification,
        send_message_to_logbroker,
        messages_to_b64_protoseq,
        testpoint,
        pgsql,
        notification_params,
        expected_missions_notifications_db_rows,
):
    @testpoint('logbroker_commit')
    def commit(cookie):
        pass

    notifications = [
        get_notification(**params) for params in notification_params
    ]
    response = await send_message_to_logbroker(
        consumer='cashback-levels-mission-progress-lb-consumer',
        data_b64=messages_to_b64_protoseq(*notifications),
    )

    await commit.wait_call()
    assert response.status_code == 200
    cursor = pgsql['cashback_levels'].cursor()

    cursor.execute(
        'SELECT yandex_uid, task_description_id, stage_id, completions, '
        'version, type, event_id, client_status, details '
        'from cashback_levels.missions_notifications',
    )
    expected_missions_notifications_db_rows.sort()
    cursor_res = [*cursor]
    cursor_res.sort()
    assert cursor_res == expected_missions_notifications_db_rows
