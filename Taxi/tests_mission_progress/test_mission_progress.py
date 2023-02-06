# pylint: disable=import-error, too-many-lines
from mission_pb2 import MissionStatus
from mission_pb2 import ProgressStatus
from mission_progress_notification_pb2 import NotificationStatus
import pytest

NOTIFICATION_STATUS_UPDATED = NotificationStatus.NOTIFICATION_STATUS_UPDATED


async def _test_mission_progress(
        get_notification,
        send_message_to_logbroker,
        messages_to_b64_protoseq,
        testpoint,
        pgsql,
        notification_params,
        expected_db_rows,
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
        'SELECT yandex_uid, task_description_id, completions, version '
        'from cashback_levels.missions_completed',
    )
    assert not set(expected_db_rows) ^ set(cursor)


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
    (
        'notification_params',
        'expected_db_rows',
        'promotion_stq_times_called',
        'reward_stq_times_called',
        'reward_stq_call_kwargs',
        'mission_completion_times_called',
    ),
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
                    yandex_uid='222',
                    external_id='task1_level1',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='333',
                    external_id='task1_level1',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_IN_PROGRESS,
                    version=2,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='444',
                    external_id='task1_level2',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    taxi_order_id='order_id_1',
                    version=1,
                ),
            ],
            [
                ('333', 'task1_level1', 0, 2),
                ('222', 'task1_level1', 0, 0),
                ('123', 'task1_level1', 1, 0),
                ('444', 'task1_level2', 1, 1),
            ],
            4,
            1,
            {
                'task_id': 'task1_level2',
                'yandex_uid': '444',
                'order_id': 'order_id_1',
            },
            2,
            id='counter-missions',
        ),
        pytest.param(
            [
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='123',
                    external_id='task1_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_ACHIEVED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_ACHIEVED,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=10,
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
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='789',
                    external_id='task1_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=5,
                    version=10,
                ),
            ],
            [
                ('789', 'task1_level1', 5, 10),
                ('456', 'task1_level1', 10, 0),
                ('123', 'task1_level1', 10, 0),
            ],
            3,
            0,
            {},
            1,
            id='cyclic-missions',
        ),
        pytest.param(
            [
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='456',
                    external_id='task1_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=5,
                    version=0,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='456',
                    external_id='task1_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=5,
                    version=0,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='111',
                    external_id='task1_level3',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=9,
                    version=1,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='111',
                    external_id='task1_level3',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=8,
                    version=0,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='123',
                    external_id='task2_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=5,
                    version=3,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='123',
                    external_id='task2_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=7,
                    version=4,
                ),
            ],
            [
                ('123', 'task2_level1', 7, 4),
                ('111', 'task1_level3', 9, 1),
                ('456', 'task1_level1', 5, 0),
            ],
            3,
            0,
            {},
            0,
            id='idempotency-and-message-order',
        ),
        pytest.param(
            [
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='456',
                    external_id='task2_level1',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    version=0,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='456',
                    external_id='task2_level2',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    version=0,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='456',
                    external_id='task2_level2',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    version=1,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='789',
                    external_id='task2_level2',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    version=1,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='789',
                    external_id='task2_level2',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    version=1,
                ),
            ],
            [
                ('456', 'task2_level2', 1, 1),
                ('456', 'task2_level1', 1, 0),
                ('789', 'task2_level2', 1, 1),
            ],
            3,
            0,
            {},
            2,
            id='idempotency-and-message-order-2',
        ),
        pytest.param(
            [
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='111',
                    external_id='task1_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_IN_PROGRESS,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=5,
                    version=0,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='111',
                    external_id='task1_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_IN_PROGRESS,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=2,
                    version=1,
                ),
            ],
            [('111', 'task1_level1', 2, 1)],
            1,
            0,
            {},
            0,
            id='later-message-with-smaller-value-refund-case',
        ),
    ],
)
async def test_missions_progress_empty_base(
        get_notification,
        send_message_to_logbroker,
        messages_to_b64_protoseq,
        testpoint,
        pgsql,
        stq,
        notification_params,
        expected_db_rows,
        promotion_stq_times_called,
        reward_stq_times_called,
        reward_stq_call_kwargs,
        mission_completion_times_called,
):
    await _test_mission_progress(
        get_notification,
        send_message_to_logbroker,
        messages_to_b64_protoseq,
        testpoint,
        pgsql,
        notification_params,
        expected_db_rows,
    )

    assert (
        stq.cashback_levels_promotion.times_called
        == promotion_stq_times_called
    )

    # todo Aidar - should move reward stq specific tests out of here
    assert stq.cashback_levels_reward.times_called == reward_stq_times_called
    if reward_stq_times_called:
        call_kwargs = stq.cashback_levels_reward.next_call()['kwargs']
        yandex_uid = reward_stq_call_kwargs['yandex_uid']
        task_id = reward_stq_call_kwargs['task_id']
        ext_ref_id = '{}/{}/{}'.format(yandex_uid, 'stage1', task_id)
        assert call_kwargs['ext_ref_id'] == ext_ref_id
        assert call_kwargs['task_id'] == task_id
        assert call_kwargs['yandex_uid'] == yandex_uid
        assert call_kwargs['order_id'] == reward_stq_call_kwargs['order_id']


@pytest.mark.config(CASHBACK_LEVELS_MISSION_PROGRESS_CONSUMER_ENABLED=True)
@pytest.mark.now('2021-09-25T12:00:00+0000')
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_offers.json')
@pytest.mark.experiments3(filename='exp3_trigger_promotion_enabled.json')
@pytest.mark.experiments3(filename='exp3_store_progress_enabled.json')
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
@pytest.mark.pgsql('cashback_levels', files=['mission_progress_test.sql'])
@pytest.mark.parametrize(
    (
        'notification_params',
        'expected_db_rows',
        'promotion_stq_times_called',
        'reward_stq_times_called',
    ),
    [
        pytest.param(
            [
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='333',
                    external_id='task1_level1',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    version=1,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='111',
                    external_id='task1_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_IN_PROGRESS,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=5,
                    version=1,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='222',
                    external_id='task1_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_IN_PROGRESS,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=3,
                    version=1,
                ),
            ],
            [
                ('222', 'task1_level1', 3, 1),
                ('111', 'task1_level1', 5, 1),
                ('333', 'task1_level1', 1, 1),
                ('789', 'task1_level1', 3, 5),
            ],
            3,
            0,
            id='overwrite-existing-db-rows',
        ),
        pytest.param(
            [
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='111',
                    external_id='task1_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_IN_PROGRESS,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=5,
                    version=0,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='789',
                    external_id='task1_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_IN_PROGRESS,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=10,
                    version=4,
                ),
            ],
            [
                ('222', 'task1_level1', 5, 0),
                ('111', 'task1_level1', 1, 0),
                ('333', 'task1_level1', 0, 0),
                ('789', 'task1_level1', 3, 5),
            ],
            0,
            0,
            id='db-has-same-or-bigger-version',
        ),
    ],
)
async def test_progress_on_missions_with_base(
        get_notification,
        send_message_to_logbroker,
        messages_to_b64_protoseq,
        testpoint,
        pgsql,
        stq,
        notification_params,
        expected_db_rows,
        promotion_stq_times_called,
        reward_stq_times_called,
):
    await _test_mission_progress(
        get_notification,
        send_message_to_logbroker,
        messages_to_b64_protoseq,
        testpoint,
        pgsql,
        notification_params,
        expected_db_rows,
    )

    assert (
        stq.cashback_levels_promotion.times_called
        == promotion_stq_times_called
    )
    assert stq.cashback_levels_reward.times_called == reward_stq_times_called


@pytest.mark.config(CASHBACK_LEVELS_MISSION_PROGRESS_CONSUMER_ENABLED=True)
@pytest.mark.now('2021-09-25T12:00:00+0000')
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_offers.json')
@pytest.mark.experiments3(filename='exp3_trigger_promotion_enabled.json')
@pytest.mark.experiments3(filename='exp3_store_progress_enabled.json')
@pytest.mark.experiments3(
    filename='exp3_mission_completion_notify_disabled.json',
)
@pytest.mark.config(CASHBACK_LEVELS_STAGES_DESCRIPTION={})
@pytest.mark.pgsql('cashback_levels', files=['mission_progress_test.sql'])
@pytest.mark.parametrize(
    ('notification_params',),
    [
        pytest.param(
            [
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='333',
                    external_id='external_id3',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                ),
            ],
        ),
    ],
)
async def test_progress_when_no_stage_for_user_message_is_committed(
        get_notification,
        send_message_to_logbroker,
        messages_to_b64_protoseq,
        testpoint,
        notification_params,
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


@pytest.mark.config(CASHBACK_LEVELS_MISSION_PROGRESS_CONSUMER_ENABLED=True)
@pytest.mark.now('2021-09-25T12:00:00+0000')
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_offers.json')
@pytest.mark.experiments3(filename='exp3_trigger_promotion_enabled.json')
@pytest.mark.experiments3(
    filename='exp3_mission_completion_notify_disabled.json',
)
@pytest.mark.experiments3(filename='exp3_store_progress_disabled.json')
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
@pytest.mark.pgsql('cashback_levels', files=['mission_progress_test.sql'])
@pytest.mark.parametrize(
    ('notification_params', 'expected_db_rows'),
    [
        pytest.param(
            [
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='333',
                    external_id='task1_level1',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='111',
                    external_id='task1_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_IN_PROGRESS,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=5,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='222',
                    external_id='task1_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_IN_PROGRESS,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=3,
                ),
            ],
            [
                ('222', 'task1_level1', 5, 0),
                ('111', 'task1_level1', 1, 0),
                ('333', 'task1_level1', 0, 0),
                ('789', 'task1_level1', 3, 5),
            ],
        ),
    ],
)
async def test_progress_on_missions_store_exp_disabled(
        stq,
        get_notification,
        send_message_to_logbroker,
        messages_to_b64_protoseq,
        testpoint,
        pgsql,
        notification_params,
        expected_db_rows,
):
    await _test_mission_progress(
        get_notification,
        send_message_to_logbroker,
        messages_to_b64_protoseq,
        testpoint,
        pgsql,
        notification_params,
        expected_db_rows,
    )
    assert stq.cashback_levels_promotion.times_called == 0
    assert stq.cashback_levels_reward.times_called == 0
    assert stq.cashback_levels_mission_completion_notify.times_called == 0


@pytest.mark.config(CASHBACK_LEVELS_MISSION_PROGRESS_CONSUMER_ENABLED=True)
@pytest.mark.now('2021-09-25T12:00:00+0000')
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_offers.json')
@pytest.mark.experiments3(filename='exp3_trigger_promotion_disabled.json')
@pytest.mark.experiments3(
    filename='exp3_mission_completion_notify_disabled.json',
)
@pytest.mark.experiments3(filename='exp3_store_progress_enabled.json')
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
@pytest.mark.pgsql('cashback_levels', files=['mission_progress_test.sql'])
@pytest.mark.parametrize(
    ('notification_params', 'expected_db_rows', 'reward_stq_times_called'),
    [
        pytest.param(
            [
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='333',
                    external_id='task1_level1',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    version=1,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='111',
                    external_id='task1_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_IN_PROGRESS,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=5,
                    version=1,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='222',
                    external_id='task1_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_IN_PROGRESS,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=3,
                    version=1,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='444',
                    external_id='task1_level2',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                ),
            ],
            [
                ('222', 'task1_level1', 3, 1),
                ('111', 'task1_level1', 5, 1),
                ('333', 'task1_level1', 1, 1),
                ('444', 'task1_level2', 1, 0),
                ('789', 'task1_level1', 3, 5),
            ],
            1,
        ),
    ],
)
async def test_progress_on_missions_promote_exp_disabled(
        stq,
        get_notification,
        send_message_to_logbroker,
        messages_to_b64_protoseq,
        testpoint,
        pgsql,
        notification_params,
        expected_db_rows,
        reward_stq_times_called,
):
    await _test_mission_progress(
        get_notification,
        send_message_to_logbroker,
        messages_to_b64_protoseq,
        testpoint,
        pgsql,
        notification_params,
        expected_db_rows,
    )
    assert stq.cashback_levels_promotion.times_called == 0
    assert stq.cashback_levels_reward.times_called == reward_stq_times_called
    assert stq.cashback_levels_mission_completion_notify.times_called == 0


@pytest.mark.config(CASHBACK_LEVELS_MISSION_PROGRESS_CONSUMER_ENABLED=True)
@pytest.mark.now('2021-09-25T12:00:00+0000')
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_offers.json')
@pytest.mark.experiments3(filename='exp3_trigger_promotion_enabled.json')
@pytest.mark.experiments3(filename='exp3_store_progress_enabled.json')
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
@pytest.mark.pgsql('cashback_levels', files=['mission_progress_test.sql'])
@pytest.mark.parametrize(
    (
        'notification_params',
        'expected_db_rows',
        'promotion_stq_times_called',
        'reward_stq_times_called',
        'expected_stq_data',
    ),
    [
        pytest.param(
            [
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='111',
                    external_id='task1_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_IN_PROGRESS,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=5,
                    version=1,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='111',
                    external_id='stage2_task',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_IN_PROGRESS,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=6,
                    version=2,
                ),
            ],
            [
                ('111', 'task1_level1', 5, 1),
                ('111', 'stage2_task', 6, 2),
                ('222', 'task1_level1', 5, 0),
                ('333', 'task1_level1', 0, 0),
                ('789', 'task1_level1', 3, 5),
            ],
            2,
            0,
            [
                {
                    'stage_id': 'stage1',
                    'task_description_id': 'task1_level1',
                    'version': 1,
                    'yandex_uid': '111',
                },
                {
                    'stage_id': 'stage2',
                    'task_description_id': 'stage2_task',
                    'version': 2,
                    'yandex_uid': '111',
                },
            ],
            id='parallel-mission-progress',
        ),
    ],
)
async def test_parallel_mission_progress(
        get_notification,
        send_message_to_logbroker,
        messages_to_b64_protoseq,
        testpoint,
        pgsql,
        stq,
        notification_params,
        expected_db_rows,
        promotion_stq_times_called,
        reward_stq_times_called,
        expected_stq_data,
):
    await _test_mission_progress(
        get_notification,
        send_message_to_logbroker,
        messages_to_b64_protoseq,
        testpoint,
        pgsql,
        notification_params,
        expected_db_rows,
    )

    assert (
        stq.cashback_levels_promotion.times_called
        == promotion_stq_times_called
    )
    ids = []
    for i in range(promotion_stq_times_called):
        task = stq.cashback_levels_promotion.next_call()
        ids.append(task['id'])
        task['kwargs'].pop('log_extra')
        assert task['kwargs'] == expected_stq_data[i]

    assert len(set(ids)) == len(ids)
    assert stq.cashback_levels_reward.times_called == reward_stq_times_called


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
    ('notification_params', 'send_notifications_stq_times_called'),
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
                    yandex_uid='222',
                    external_id='task1_level1',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='333',
                    external_id='task1_level1',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_IN_PROGRESS,
                    version=2,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='444',
                    external_id='task1_level2',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    taxi_order_id='order_id_1',
                    version=1,
                ),
            ],
            2,
            id='counter-missions',
        ),
        pytest.param(
            [
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='123',
                    external_id='task1_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_ACHIEVED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_ACHIEVED,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=10,
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
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='789',
                    external_id='task1_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=5,
                    version=10,
                ),
            ],
            2,
            id='cyclic-missions',
        ),
        pytest.param(
            [
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='123',
                    external_id='task1_level1',
                    progress_type='transaction_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_IN_PROGRESS,
                    transaction_progress_target=10000,
                    transaction_progress_current_achieved=5000,
                    transaction_progress_current_completed=0,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='456',
                    external_id='task1_level1',
                    progress_type='transaction_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_ACHIEVED,
                    transaction_progress_target=10000,
                    transaction_progress_current_achieved=10000,
                    transaction_progress_current_completed=0,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='789',
                    external_id='task1_level1',
                    progress_type='transaction_progress',
                    mission_status=MissionStatus.MISSION_STATUS_ACHIEVED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    transaction_progress_target=10000,
                    transaction_progress_current_achieved=0,
                    transaction_progress_current_completed=10000,
                    version=10,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='444',
                    external_id='task1_level1',
                    progress_type='transaction_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    transaction_progress_target=10000,
                    transaction_progress_current_achieved=0,
                    transaction_progress_current_completed=10000,
                    version=10,
                ),
            ],
            1,
            id='transaction-missions',
        ),
        pytest.param(
            [
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='456',
                    external_id='task1_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=5,
                    version=0,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='456',
                    external_id='task1_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=5,
                    version=0,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='111',
                    external_id='task1_level3',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=9,
                    version=1,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='111',
                    external_id='task1_level3',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=8,
                    version=0,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='123',
                    external_id='task2_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=5,
                    version=3,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='123',
                    external_id='task2_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=7,
                    version=4,
                ),
            ],
            3,
            id='idempotency-and-message-order',
        ),
        pytest.param(
            [
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='456',
                    external_id='task2_level1',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    version=0,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='456',
                    external_id='task2_level2',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    version=0,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='456',
                    external_id='task2_level2',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    version=1,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='789',
                    external_id='task2_level2',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    version=1,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='789',
                    external_id='task2_level2',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    version=1,
                ),
            ],
            0,
            id='idempotency-and-message-order-2',
        ),
        pytest.param(
            [
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='111',
                    external_id='task1_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_IN_PROGRESS,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=5,
                    version=0,
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='111',
                    external_id='task1_level1',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_IN_PROGRESS,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=2,
                    version=1,
                ),
            ],
            1,
            id='later-message-with-smaller-value-refund-case',
        ),
    ],
)
async def test_mission_progress_call_silent_push(
        get_notification,
        send_message_to_logbroker,
        messages_to_b64_protoseq,
        testpoint,
        stq,
        notification_params,
        send_notifications_stq_times_called,
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
    assert (
        stq.cashback_levels_send_mission_notifications.times_called
        == send_notifications_stq_times_called
    )
