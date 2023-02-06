# pylint: disable=import-error
from event_pb2 import EventType
import google.protobuf.json_format
from mission_completion_notify_v1_pb2 import MissionCompletionNotification
from mission_pb2 import MissionStatus
from mission_pb2 import ProgressStatus
from mission_progress_notification_pb2 import NotificationStatus
import pytest


NOTIFICATION_STATUS_UPDATED = NotificationStatus.NOTIFICATION_STATUS_UPDATED
PROTO_JSON_FORMAT_KWARGS = {
    'including_default_value_fields': True,
    'preserving_proto_field_name': True,
    'float_precision': 4,
}


def set_mission_notification_values(cursor, params_list):
    for params in params_list:
        cursor.execute(
            f"""
                    INSERT INTO cashback_levels.missions_notifications
                    (yandex_uid, stage_id, task_description_id, type,
                    version, event_id, completions)
                    VALUES {params};
                """,
        )


def get_mission_notification_values(cursor):
    cursor.execute(
        f"""
                SELECT yandex_uid, stage_id, task_description_id, type,
                       version, event_id, completions
                from cashback_levels.missions_notifications;
            """,
    )
    return [*cursor]


@pytest.mark.config(CASHBACK_LEVELS_MISSION_PROGRESS_CONSUMER_ENABLED=True)
@pytest.mark.now('2021-09-25T12:00:00+0000')
@pytest.mark.experiments3(filename='exp3_mission_completion_lbkx_enabled.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_offers.json')
@pytest.mark.experiments3(filename='exp3_trigger_promotion_enabled.json')
@pytest.mark.experiments3(filename='exp3_store_progress_enabled.json')
@pytest.mark.experiments3(
    filename='exp3_mission_completion_notify_enabled.json',
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
    ('notification_params', 'notify_stq_times_called', 'expected_stq_kwargs'),
    [
        pytest.param(
            [
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='111',
                    external_id='task1_level1',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_ACHIEVED,
                    event_id='event_id1',
                    event_type=EventType.EVENT_TYPE_KINOPOISK_VIEW,
                    version=1,
                    client_id='client1',
                    service='go',
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='222',
                    external_id='task1_level1',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    event_id='event_id2',
                    event_type=EventType.EVENT_TYPE_ZAPRAVKI_ORDER,
                    version=1,
                    client_id='client1',
                    service='go',
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='111',
                    external_id='task1_level2',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_IN_PROGRESS,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=10,
                    event_id='event_id3',
                    event_type=EventType.EVENT_TYPE_TAXI_ORDER,
                    version=1,
                    client_id='client1',
                    service='go',
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='222',
                    external_id='task1_level2',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_ACHIEVED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_IN_PROGRESS,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=10,
                    event_id='event_id4',
                    event_type=EventType.EVENT_TYPE_TAXI_ORDER,
                    version=1,
                    client_id='client1',
                    service='go',
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='333',
                    external_id='task1_level2',
                    progress_type='cyclic_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_IN_PROGRESS,
                    cyclic_progress_target_completed_iteration=10,
                    cyclic_progress_current_completed_iteration=5,
                    event_id='event_id5',
                    event_type=EventType.EVENT_TYPE_EDA_ORDER,
                    version=1,
                    client_id='client1',
                    service='go',
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='333',
                    external_id='task1_level3',
                    progress_type='counter_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_IN_PROGRESS,
                    event_id='event_id6',
                    event_type=EventType.EVENT_TYPE_TAXI_ORDER,
                    version=1,
                    client_id='client1',
                    service='go',
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='444',
                    external_id='task1_level3',
                    progress_type='transaction_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_ACHIEVED,
                    transaction_progress_target=10000,
                    transaction_progress_current_achieved=10000,
                    transaction_progress_current_completed=0,
                    event_id='event_id7',
                    event_type=EventType.EVENT_TYPE_MARKET_ORDER,
                    version=1,
                    client_id='client1',
                    service='market',
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='555',
                    external_id='task1_level3',
                    progress_type='transaction_progress',
                    mission_status=MissionStatus.MISSION_STATUS_IN_PROGRESS,
                    progress_status=ProgressStatus.PROGRESS_STATUS_IN_PROGRESS,
                    transaction_progress_target=10000,
                    transaction_progress_current_achieved=5000,
                    transaction_progress_current_completed=0,
                    event_id='event_id8',
                    event_type=EventType.EVENT_TYPE_MARKET_ORDER,
                    version=1,
                    client_id='client1',
                    service='market',
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='666',
                    external_id='task1_level3',
                    progress_type='transaction_progress',
                    mission_status=MissionStatus.MISSION_STATUS_COMPLETED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_ACHIEVED,
                    transaction_progress_target=10000,
                    transaction_progress_current_achieved=0,
                    transaction_progress_current_completed=10000,
                    event_id='event_id9',
                    event_type=EventType.EVENT_TYPE_MARKET_ORDER,
                    version=1,
                    client_id='client1',
                    service='market',
                ),
                dict(
                    notification_status=NOTIFICATION_STATUS_UPDATED,
                    yandex_uid='777',
                    external_id='task1_level3',
                    progress_type='transaction_progress',
                    mission_status=MissionStatus.MISSION_STATUS_ACHIEVED,
                    progress_status=ProgressStatus.PROGRESS_STATUS_COMPLETED,
                    transaction_progress_target=10000,
                    transaction_progress_current_achieved=0,
                    transaction_progress_current_completed=10000,
                    event_id='event_id10',
                    event_type=EventType.EVENT_TYPE_MARKET_ORDER,
                    version=1,
                    client_id='client1',
                    service='market',
                ),
            ],
            8,
            [
                {
                    'completions': 1,
                    'event_id': 'event_id1',
                    'event_type': 'EVENT_TYPE_KINOPOISK_VIEW',
                    'is_fully_completed': True,
                    'log_extra': {'_link': ''},
                    'stage_id': 'stage1',
                    'version': 1,
                    'task_description_id': 'task1_level1',
                    'yandex_uid': '111',
                    'notification_payload': {
                        'client_id': 'client1',
                        'service': 'go',
                        'locale': '',
                        'device_id': '',
                        'app_install_id': '',
                    },
                },
                {
                    'completions': 10,
                    'event_id': 'event_id3',
                    'event_type': 'EVENT_TYPE_TAXI_ORDER',
                    'is_fully_completed': True,
                    'log_extra': {'_link': ''},
                    'stage_id': 'stage1',
                    'version': 1,
                    'task_description_id': 'task1_level2',
                    'yandex_uid': '111',
                    'notification_payload': {
                        'client_id': 'client1',
                        'service': 'go',
                        'locale': '',
                        'device_id': '',
                        'app_install_id': '',
                    },
                },
                {
                    'completions': 1,
                    'event_id': 'event_id2',
                    'event_type': 'EVENT_TYPE_ZAPRAVKI_ORDER',
                    'is_fully_completed': True,
                    'log_extra': {'_link': ''},
                    'stage_id': 'stage1',
                    'version': 1,
                    'task_description_id': 'task1_level1',
                    'yandex_uid': '222',
                    'notification_payload': {
                        'client_id': 'client1',
                        'service': 'go',
                        'locale': '',
                        'device_id': '',
                        'app_install_id': '',
                    },
                },
                {
                    'completions': 10,
                    'event_id': 'event_id4',
                    'event_type': 'EVENT_TYPE_TAXI_ORDER',
                    'is_fully_completed': True,
                    'log_extra': {'_link': ''},
                    'stage_id': 'stage1',
                    'version': 1,
                    'task_description_id': 'task1_level2',
                    'yandex_uid': '222',
                    'notification_payload': {
                        'client_id': 'client1',
                        'service': 'go',
                        'locale': '',
                        'device_id': '',
                        'app_install_id': '',
                    },
                },
                {
                    'completions': 5,
                    'event_id': 'event_id5',
                    'event_type': 'EVENT_TYPE_EDA_ORDER',
                    'is_fully_completed': False,
                    'log_extra': {'_link': ''},
                    'stage_id': 'stage1',
                    'version': 1,
                    'task_description_id': 'task1_level2',
                    'yandex_uid': '333',
                    'notification_payload': {
                        'client_id': 'client1',
                        'service': 'go',
                        'locale': '',
                        'device_id': '',
                        'app_install_id': '',
                    },
                },
                {
                    'completions': 1,
                    'event_id': 'event_id7',
                    'event_type': 'EVENT_TYPE_MARKET_ORDER',
                    'is_fully_completed': False,
                    'log_extra': {'_link': ''},
                    'stage_id': 'stage1',
                    'version': 1,
                    'task_description_id': 'task1_level3',
                    'yandex_uid': '444',
                    'notification_payload': {
                        'client_id': 'client1',
                        'service': 'market',
                        'locale': '',
                        'device_id': '',
                        'app_install_id': '',
                    },
                },
                {
                    'completions': 1,
                    'event_id': 'event_id9',
                    'event_type': 'EVENT_TYPE_MARKET_ORDER',
                    'is_fully_completed': True,
                    'log_extra': {'_link': ''},
                    'stage_id': 'stage1',
                    'version': 1,
                    'task_description_id': 'task1_level3',
                    'yandex_uid': '666',
                    'notification_payload': {
                        'client_id': 'client1',
                        'service': 'market',
                        'locale': '',
                        'device_id': '',
                        'app_install_id': '',
                    },
                },
                {
                    'completions': 1,
                    'event_id': 'event_id10',
                    'event_type': 'EVENT_TYPE_MARKET_ORDER',
                    'is_fully_completed': False,
                    'log_extra': {'_link': ''},
                    'stage_id': 'stage1',
                    'version': 1,
                    'task_description_id': 'task1_level3',
                    'yandex_uid': '777',
                    'notification_payload': {
                        'client_id': 'client1',
                        'service': 'market',
                        'locale': '',
                        'device_id': '',
                        'app_install_id': '',
                    },
                },
            ],
            id='any_change_of_completions_is_notified_no_matter_the_reward',
        ),
    ],
)
async def test_mission_completion_notify_stq_called(
        get_notification,
        send_message_to_logbroker,
        messages_to_b64_protoseq,
        testpoint,
        stq,
        notification_params,
        notify_stq_times_called,
        expected_stq_kwargs,
        compare_dct_lists,
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
        stq.cashback_levels_mission_completion_notify.times_called
        == notify_stq_times_called
    )
    actual_calls = []
    for _ in range(notify_stq_times_called):
        task = stq.cashback_levels_mission_completion_notify.next_call()
        actual_calls.append(task['kwargs'])

    compare_dct_lists(actual_calls, expected_stq_kwargs)


@pytest.mark.config(CASHBACK_LEVELS_MISSION_PROGRESS_CONSUMER_ENABLED=True)
@pytest.mark.now('2021-09-25T12:00:00+0000')
@pytest.mark.experiments3(filename='exp3_mission_completion_lbkx_enabled.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_offers.json')
@pytest.mark.experiments3(filename='exp3_trigger_promotion_enabled.json')
@pytest.mark.experiments3(filename='exp3_store_progress_enabled.json')
@pytest.mark.experiments3(
    filename='exp3_mission_completion_notify_enabled.json',
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
    (
        'initial_db_values',
        'stq_kwargs',
        'expected_db_values',
        'logbroker_calls',
    ),
    [
        pytest.param(
            [
                (
                    '111',
                    'stage1',
                    'task1_level1',
                    'completed',
                    0,
                    'event_id0',
                    1,
                ),
                ('222', 'stage1', 'task1_level1', 'assigned', 0, '', 0),
                (
                    '222',
                    'stage1',
                    'task1_level1',
                    'completed',
                    0,
                    'event_id00',
                    1,
                ),
            ],
            [
                {
                    'completions': 2,
                    'event_id': 'event_id1',
                    'event_type': 'EVENT_TYPE_TAXI_ORDER',
                    'is_fully_completed': False,
                    'log_extra': {'_link': ''},
                    'version': 1,
                    'stage_id': 'stage1',
                    'task_description_id': 'task1_level1',
                    'yandex_uid': '111',
                    'notification_payload': {'client_id': 'client1'},
                },
                {
                    'completions': 2,
                    'event_id': 'event_id2',
                    'event_type': 'EVENT_TYPE_KINOPOISK_VIEW',
                    'is_fully_completed': True,
                    'log_extra': {'_link': ''},
                    'version': 1,
                    'stage_id': 'stage1',
                    'task_description_id': 'task1_level1',
                    'yandex_uid': '222',
                    'notification_payload': {'client_id': 'client1'},
                },
                {
                    'completions': 1,
                    'event_id': 'event_id3',
                    'event_type': 'EVENT_TYPE_ZAPRAVKI_ORDER',
                    'is_fully_completed': True,
                    'log_extra': {'_link': ''},
                    'version': 1,
                    'stage_id': 'stage1',
                    'task_description_id': 'task1_level2',
                    'yandex_uid': '222',
                    'notification_payload': {'client_id': 'client1'},
                },
                {
                    'completions': 10,
                    'event_id': 'event_id4',
                    'event_type': 'EVENT_TYPE_EDA_ORDER',
                    'is_fully_completed': False,
                    'log_extra': {'_link': ''},
                    'version': 1,
                    'stage_id': 'stage1',
                    'task_description_id': 'task1_level3',
                    'yandex_uid': '333',
                    'notification_payload': {'client_id': 'client1'},
                },
                {
                    'completions': 10000,
                    'event_id': 'event_id5',
                    'event_type': 'EVENT_TYPE_MARKET_ORDER',
                    'is_fully_completed': False,
                    'log_extra': {'_link': ''},
                    'version': 1,
                    'stage_id': 'stage1',
                    'task_description_id': 'task1_level3',
                    'yandex_uid': '444',
                    'notification_payload': {
                        'client_id': 'client1',
                        'service': 'market',
                    },
                },
            ],
            [
                (
                    '111',
                    'stage1',
                    'task1_level1',
                    'completed',
                    0,
                    'event_id0',
                    1,
                ),
                (
                    '111',
                    'stage1',
                    'task1_level1',
                    'completed',
                    1,
                    'event_id1',
                    2,
                ),
                (
                    '222',
                    'stage1',
                    'task1_level1',
                    'completed',
                    0,
                    'event_id00',
                    1,
                ),
                ('222', 'stage1', 'task1_level1', 'assigned', 0, '', 0),
                (
                    '222',
                    'stage1',
                    'task1_level1',
                    'completed',
                    1,
                    'event_id2',
                    2,
                ),
                (
                    '222',
                    'stage1',
                    'task1_level2',
                    'completed',
                    1,
                    'event_id3',
                    1,
                ),
                (
                    '333',
                    'stage1',
                    'task1_level3',
                    'completed',
                    1,
                    'event_id4',
                    10,
                ),
                (
                    '444',
                    'stage1',
                    'task1_level3',
                    'completed',
                    1,
                    'event_id5',
                    10000,
                ),
            ],
            [
                {
                    'event_id': 'event_id2',
                    'notification_id': 'd7cbc04e-d459-44f8-820c-eeb0ddfb56f1',
                    'puid': '222',
                    'reward': '',
                    'timestamp': '1636658361',
                    'type': 'EVENT_TYPE_KINOPOISK_VIEW',
                    'task_description_id': 'task1_level1',
                    'service': 'taxi',
                },
                {
                    'event_id': 'event_id3',
                    'notification_id': '610ea911-dafa-40f4-9362-9997d52f28fe',
                    'puid': '222',
                    'reward': '100 баллов плюса',
                    'timestamp': '1636658361',
                    'type': 'EVENT_TYPE_ZAPRAVKI_ORDER',
                    'task_description_id': 'task1_level2',
                    'service': 'eda',
                },
            ],
            id='stq_result',
        ),
    ],
)
async def test_mission_completion_stq_work(
        taxi_cashback_levels,
        testpoint,
        stq_runner,
        pgsql,
        initial_db_values,
        stq_kwargs,
        expected_db_values,
        logbroker_calls,
        b64_protoseq_to_message,
        compare_dct_lists,
):
    committed_data = []

    @testpoint('logbroker_publish_b64')
    def commit(data):
        ntf = b64_protoseq_to_message(
            data['data'], MissionCompletionNotification,
        )
        proto_dict = google.protobuf.json_format.MessageToDict(
            ntf, **PROTO_JSON_FORMAT_KWARGS,
        )
        committed_data.append(proto_dict)

    await taxi_cashback_levels.enable_testpoints()

    cursor = pgsql['cashback_levels'].cursor()
    set_mission_notification_values(cursor, initial_db_values)
    for kwargs in stq_kwargs:
        task_id = f'{kwargs["task_description_id"]}/{kwargs["event_id"]}'
        await stq_runner.cashback_levels_mission_completion_notify.call(
            task_id=task_id, kwargs=kwargs,
        )

    result_values = get_mission_notification_values(cursor)
    assert sorted(result_values) == sorted(expected_db_values)

    assert commit.times_called == len(logbroker_calls)
    compare_dct_lists(
        committed_data,
        logbroker_calls,
        excluded_fields={'timestamp', 'notification_id'},
    )


@pytest.mark.config(CASHBACK_LEVELS_MISSION_PROGRESS_CONSUMER_ENABLED=True)
@pytest.mark.now('2021-09-25T12:00:00+0000')
@pytest.mark.experiments3(
    filename='exp3_mission_completion_lbkx_disabled.json',
)
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_offers.json')
@pytest.mark.experiments3(filename='exp3_trigger_promotion_enabled.json')
@pytest.mark.experiments3(filename='exp3_store_progress_enabled.json')
@pytest.mark.experiments3(
    filename='exp3_mission_completion_notify_enabled.json',
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
    (
        'initial_db_values',
        'stq_kwargs',
        'expected_db_values',
        'logbroker_calls',
    ),
    [
        pytest.param(
            [],
            [
                {
                    'completions': 2,
                    'event_id': 'event_id2',
                    'event_type': 'EVENT_TYPE_KINOPOISK_VIEW',
                    'is_fully_completed': True,
                    'log_extra': {'_link': ''},
                    'version': 1,
                    'stage_id': 'stage1',
                    'task_description_id': 'task1_level1',
                    'yandex_uid': '222',
                    'notification_payload': {'client_id': 'client1'},
                },
            ],
            [
                (
                    '222',
                    'stage1',
                    'task1_level1',
                    'completed',
                    1,
                    'event_id2',
                    2,
                ),
            ],
            [],
            id='stq_result',
        ),
    ],
)
async def test_mission_completion_stq_lbkx_exp_disabled(
        taxi_cashback_levels,
        testpoint,
        stq_runner,
        pgsql,
        initial_db_values,
        stq_kwargs,
        expected_db_values,
        logbroker_calls,
):
    @testpoint('logbroker_publish_b64')
    def commit(data):
        pass

    await taxi_cashback_levels.enable_testpoints()

    cursor = pgsql['cashback_levels'].cursor()
    set_mission_notification_values(cursor, initial_db_values)
    for kwargs in stq_kwargs:
        task_id = f'{kwargs["task_description_id"]}/{kwargs["event_id"]}'
        await stq_runner.cashback_levels_mission_completion_notify.call(
            task_id=task_id, kwargs=kwargs,
        )

    result_values = get_mission_notification_values(cursor)
    assert sorted(result_values) == sorted(expected_db_values)

    assert commit.times_called == 0
