# pylint: disable=import-error
import base64

from mission_pb2 import MissionStatus
from mission_pb2 import ProgressStatus
from mission_progress_notification_pb2 import NotificationStatus
import pytest

NOTIFICATION_STATUS_UPDATED = NotificationStatus.NOTIFICATION_STATUS_UPDATED
NOTIFICATION_STATUS_ASSIGNED = (
    NotificationStatus.NOTIFICATION_STATUS_ASSIGNED_BY_SEGMENT
)


def compare_metrics(actual_metrics, expected_metrics):
    # pop time, assert truthy, compare the rest
    assert actual_metrics['consumer'].pop('batch_read_time')['1min']
    assert actual_metrics['consumer'].pop('batch_process_time')['1min']
    assert actual_metrics['consumer'].pop('batch_commit_time')['1min']
    assert actual_metrics['consumer'].pop('batch_size')['1min']
    assert actual_metrics == expected_metrics


@pytest.mark.config(CASHBACK_LEVELS_MISSION_PROGRESS_CONSUMER_ENABLED=True)
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_offers.json')
@pytest.mark.experiments3(
    filename='exp3_mission_completion_notify_disabled.json',
)
@pytest.mark.experiments3(filename='exp3_trigger_promotion_enabled.json')
@pytest.mark.experiments3(filename='exp3_store_progress_enabled.json')
@pytest.mark.now('2021-09-25T12:00:00+0000')
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
    ('notification_params', 'expected_metrics'),
    [
        pytest.param(
            [
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='123',
                    external_id='task1_level1',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='456',
                    external_id='task1_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=10,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_ASSIGNED,
                    yandex_uid='123',
                    external_id='task1_level1',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                ),
            ],
            {
                'consumer': {'batch_errors': {'1min': 0}},
                'process': {
                    'unpack_failed_count': {'1min': 0},
                    'parse_failed_count': {'1min': 0},
                    'skipped_no_stage_count': {'1min': 0},
                    'progress_applied_count': {'1min': 2},
                },
            },
            id='simple-missions',
        ),
        pytest.param(
            [],
            {
                'consumer': {'batch_errors': {'1min': 0}},
                'process': {
                    'unpack_failed_count': {'1min': 0},
                    'parse_failed_count': {'1min': 0},
                    'skipped_no_stage_count': {'1min': 0},
                    'progress_applied_count': {'1min': 0},
                },
            },
            id='no-messages-works-ok',
        ),
    ],
)
async def test_missions_progress_metrics_ok(
        taxi_cashback_levels,
        get_notification,
        send_message_to_logbroker,
        messages_to_b64_protoseq,
        testpoint,
        notification_params,
        taxi_cashback_levels_monitor,
        expected_metrics,
):
    await taxi_cashback_levels.invalidate_caches()

    @testpoint('logbroker_commit')
    def commit(cookie):
        pass

    notifications = [
        get_notification(**params) for params in notification_params
    ]
    if notifications:
        response = await send_message_to_logbroker(
            consumer='cashback-levels-mission-progress-lb-consumer',
            data_b64=messages_to_b64_protoseq(*notifications),
        )

        await commit.wait_call()
        assert response.status_code == 200

    result = await taxi_cashback_levels_monitor.get_metric(
        'cashback-levels-mission-progress-lb-consumer',
    )
    compare_metrics(result, expected_metrics)


@pytest.mark.config(CASHBACK_LEVELS_MISSION_PROGRESS_CONSUMER_ENABLED=True)
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_offers.json')
@pytest.mark.experiments3(
    filename='exp3_mission_completion_notify_disabled.json',
)
@pytest.mark.config(CASHBACK_LEVELS_STAGES_DESCRIPTION={})
@pytest.mark.experiments3(filename='exp3_trigger_promotion_enabled.json')
@pytest.mark.experiments3(filename='exp3_store_progress_enabled.json')
@pytest.mark.parametrize(
    ('notification_params', 'expected_metrics'),
    [
        pytest.param(
            [
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='123',
                    external_id='unknown_task',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='12345',
                    external_id='unknown_task2',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                ),
            ],
            {
                'consumer': {'batch_errors': {'1min': 0}},
                'process': {
                    'unpack_failed_count': {'1min': 0},
                    'parse_failed_count': {'1min': 0},
                    'skipped_no_stage_count': {'1min': 2},
                    'progress_applied_count': {'1min': 0},
                },
            },
            id='no_stage_found_for_task',
        ),
    ],
)
async def test_missions_progress_metrics_no_stage_found_for_task(
        taxi_cashback_levels,
        get_notification,
        send_message_to_logbroker,
        messages_to_b64_protoseq,
        testpoint,
        notification_params,
        taxi_cashback_levels_monitor,
        expected_metrics,
):
    await taxi_cashback_levels.invalidate_caches()

    @testpoint('logbroker_commit')
    def commit(cookie):
        pass

    notifications = [
        get_notification(**params) for params in notification_params
    ]
    if notifications:
        response = await send_message_to_logbroker(
            consumer='cashback-levels-mission-progress-lb-consumer',
            data_b64=messages_to_b64_protoseq(*notifications),
        )

        await commit.wait_call()
        assert response.status_code == 200

    result = await taxi_cashback_levels_monitor.get_metric(
        'cashback-levels-mission-progress-lb-consumer',
    )
    compare_metrics(result, expected_metrics)


@pytest.mark.config(CASHBACK_LEVELS_MISSION_PROGRESS_CONSUMER_ENABLED=True)
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
async def test_missions_progress_metrics_parse_failed(
        taxi_cashback_levels,
        send_message_to_logbroker,
        messages_to_b64_protoseq,
        testpoint,
        taxi_cashback_levels_monitor,
):
    await taxi_cashback_levels.invalidate_caches()

    @testpoint('logbroker_commit')
    def commit(cookie):
        pass

    response = await send_message_to_logbroker(
        consumer='cashback-levels-mission-progress-lb-consumer',
        data_b64=messages_to_b64_protoseq(b'kek', b'lol'),
    )

    await commit.wait_call()
    assert response.status_code == 200

    k_expected_metrics = {
        'consumer': {'batch_errors': {'1min': 0}},
        'process': {
            'unpack_failed_count': {'1min': 0},
            'parse_failed_count': {'1min': 2},
            'skipped_no_stage_count': {'1min': 0},
            'progress_applied_count': {'1min': 0},
        },
    }

    result = await taxi_cashback_levels_monitor.get_metric(
        'cashback-levels-mission-progress-lb-consumer',
    )
    compare_metrics(result, k_expected_metrics)


@pytest.mark.config(CASHBACK_LEVELS_MISSION_PROGRESS_CONSUMER_ENABLED=True)
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
async def test_missions_progress_metrics_unpack_failed(
        taxi_cashback_levels,
        send_message_to_logbroker,
        testpoint,
        taxi_cashback_levels_monitor,
):
    await taxi_cashback_levels.invalidate_caches()

    @testpoint('logbroker_commit')
    def commit(cookie):
        pass

    k_count = 2

    for _ in range(k_count):
        response = await send_message_to_logbroker(
            consumer='cashback-levels-mission-progress-lb-consumer',
            data_b64=str(base64.b64encode(b'kek')),
        )

        await commit.wait_call()
        assert response.status_code == 200

    k_expected_metrics = {
        'consumer': {'batch_errors': {'1min': 0}},
        'process': {
            'unpack_failed_count': {'1min': k_count},
            'parse_failed_count': {'1min': 0},
            'skipped_no_stage_count': {'1min': 0},
            'progress_applied_count': {'1min': 0},
        },
    }

    result = await taxi_cashback_levels_monitor.get_metric(
        'cashback-levels-mission-progress-lb-consumer',
    )
    compare_metrics(result, k_expected_metrics)
