# pylint: disable=redefined-outer-name
import pytest

from taxi.stq.async_worker_ng import TaskInfo

from taxi_driver_metrics.stq.client import task as client_task

NULL_DP_UDID = '5b05621ee6c22ea2654849c0'


@pytest.fixture
async def patched_processing(patch):
    @patch(
        'taxi_driver_metrics.common.models.'
        'ItemBasedEntityProcessor.process_unblocking',
    )
    async def process(*args, **kwargs):
        pass

    return process


@pytest.mark.now('2020-04-16T12:00:00Z')
async def test_task_client(stq3_context, stq):

    await client_task.task(
        stq3_context,
        TaskInfo(
            id='task_id',
            exec_tries=1,
            reschedule_counter=1,
            queue='driver_metrics_client',
        ),
        1,
        'test',
    )
    assert not stq.driver_metrics_processing.times_called

    await client_task.task(
        stq3_context,
        TaskInfo(
            id='rates_calc_finished1234',
            exec_tries=1,
            reschedule_counter=1,
            queue='driver_metrics_client',
        ),
        1,
        'test',
        log_extra={'extdict': {'task_id': 'rates_calc_finished1234'}},
    )
    assert not stq.driver_metrics_processing.times_called

    await client_task.task(
        stq3_context,
        TaskInfo(
            id='order_event/123/1234',
            exec_tries=1,
            reschedule_counter=1,
            queue='driver_metrics_client',
        ),
        {
            'v': 1,
            'timestamp': '2020-04-16T12:00:00Z',
            'handler': 'driving_handler',
            'order_id': '123',
            'reason_code': 'code',
            'update_index': 'some_index',
            'udid': 'awesome_udid',
            'candidate_index': 4,
            'zone': 'spb',
        },
    )
    assert not stq.driver_metrics_processing.times_called
    assert stq.driver_metrics_client.times_called

    assert (
        stq.driver_metrics_client.next_call()['id'] == 'order_event/123/1234'
    )

    await client_task.task(
        stq3_context,
        TaskInfo(
            id='order_event/123/processing',
            exec_tries=1,
            reschedule_counter=1,
            queue='driver_metrics_client',
        ),
        {
            'timestamp': '2020-04-16T12:00:00Z',
            'handler': 'unset_unconfirmed_performer',
            'order_id': '123',
            'reason_code': 'code',
            'update_index': 'some_index',
            'udid': None,
            'candidate_index': 4,
            'zone': 'spb',
        },
    )
    assert not stq.driver_metrics_processing.times_called
    assert stq.driver_metrics_client.times_called

    assert (
        stq.driver_metrics_client.next_call()['id']
        == 'order_event/123/processing'
    )


@pytest.mark.filldb()
@pytest.mark.now('2020-05-28T15:48:50.840Z')
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                USE_ORDER_CORE_PY3={'driver-metrics': {'enabled': True}},
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                USE_ORDER_CORE_PY3={'driver-metrics': {'enabled': False}},
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'task_id,task_kwargs,expected_data,expected_tags',
    [
        pytest.param(
            'order_event/68ea827b26503c8c931c3f20095d323a/processing',
            {
                'timestamp': '2020-05-27T15:48:57.882Z',
                'handler': 'unset_unconfirmed_performer',
                'order_id': '123',
                'reason_code': 'code',
                'update_index': 2,
                'udid': None,
                'candidate_index': 1000230,  # look for candidate index in proc
                'zone': 'spb',
            },
            {
                'type': 'order',
                'unique_driver_id': '5d8cf2d6b8e3f8796887b21d',
                'created': '2020-05-27T15:48:57.882000+00:00',
                'idempotency_token': 'o/68ea827b26503c8c931c3f20095d323a/2',
                'order_id': '123',
                'tariff_zone': 'spb',
                'descriptor': {'type': 'unset_unconfirmed_performer'},
                'park_driver_profile_id': (
                    '7ad36bc7560449998acbe2c57a75c293_'
                    '870fbf758122ac002c302cff682d3488'
                ),
                'extra_data': {
                    'activity_value': 100,
                    'driver_id': '100500_870fbf758122ac002c302cff682d3488',
                    'time_to_a': 100000,
                    'distance_to_a': 1,
                    'tariff_class': 'econom',
                    'dtags': None,
                    'rtags': None,
                    'sp': None,
                    'dispatch_id': '5ece8be684f802986fd32b50',
                    'sp_alpha': None,
                    'replace_activity_with_priority': False,
                    'calculate_priority': False,
                },
            },
            ['tariff_econom', 'dispatch_long'],
            id='0',
        ),
        pytest.param(
            'order_event/68ea827b26503c8c931c3f20095d323b/processing',
            {
                'timestamp': '2020-05-27T15:48:57.882Z',
                'handler': 'auto_reorder',
                'order_id': '68ea827b26503c8c931c3f20095d323b',
                'reason_code': 'code',
                'update_index': 5,
                'udid': None,
                'candidate_index': 0,
                'zone': 'spb',
            },
            {
                'created': '2020-05-27T15:48:57.882000+00:00',
                'descriptor': {'type': 'auto_reorder'},
                'park_driver_profile_id': (
                    '7ad36bc7560449998acbe2c57a75c293_'
                    '870fbf758122ac002c302cff682d3488'
                ),
                'extra_data': {
                    'activity_value': 100,
                    'dispatch_id': '5ece8be684f802986fd32b50',
                    'distance_to_a': 1,
                    'driver_id': '100500_870fbf758122ac002c302cff682d3488',
                    'dtags': None,
                    'rtags': None,
                    'sp': None,
                    'sp_alpha': None,
                    'tariff_class': 'econom',
                    'time_to_a': 100000,
                    'replace_activity_with_priority': False,
                    'calculate_priority': False,
                },
                'idempotency_token': 'o/68ea827b26503c8c931c3f20095d323b/5',
                'order_id': '68ea827b26503c8c931c3f20095d323b',
                'tariff_zone': 'spb',
                'type': 'order',
                'unique_driver_id': '5d8cf2d6b8e3f8796887b21d',
            },
            [
                'cancel_during_waiting',
                'tariff_econom',
                'multiple_destination',
                'dispatch_long',
            ],
            id='1',
        ),
        pytest.param(
            'order_event/0a8c6a355903147ea39cca6634633a99/processing',
            {
                'timestamp': '2020-05-27T15:48:57.882Z',
                'handler': 'user_cancel',
                'order_id': '0a8c6a355903147ea39cca6634633a99',
                'reason_code': 'code',
                'update_index': 6,
                'udid': None,
                'candidate_index': 0,
                'zone': 'spb',
            },
            {
                'created': '2020-05-27T15:48:57.882000+00:00',
                'descriptor': {'type': 'user_cancel'},
                'extra_data': {
                    'activity_value': 22,
                    'calculate_priority': False,
                    'dispatch_id': '629dffd3319b750052b7eb85',
                    'distance_passed_rel': 0.98,
                    'distance_to_a': 1050,
                    'driver_id': (
                        '400000112879_ecc43a49b10ccacd34b9ff29526ee974'
                    ),
                    'dtags': [],
                    'replace_activity_with_priority': False,
                    'rtags': None,
                    'sp': 1,
                    'sp_alpha': 0,
                    'tariff_class': 'start',
                    'time_passed_rel': 0.86,
                    'time_to_a': 128,
                    'user_cancel_reasons': ['drove_away', 'some_other_reason'],
                    'payment_type': 'cash',
                    'user_total_price': 100,
                },
                'idempotency_token': 'o/0a8c6a355903147ea39cca6634633a99/6',
                'order_alias': 'f2bc90908a931e7381cc3651d2800549',
                'order_id': '0a8c6a355903147ea39cca6634633a99',
                'park_driver_profile_id': (
                    '6a2cdccff4854097a3c4455707a51c00'
                    '_ecc43a49b10ccacd34b9ff29526ee974'
                ),
                'tariff_zone': 'spb',
                'type': 'order',
                'unique_driver_id': '60f053898fe28d5ce42cb3e0',
            },
            ['dispatch_medium', 'lookup_mode_direct', 'tariff_start'],
            id='user_cancel_extra_features',
        ),
        pytest.param(
            'amnesty_event/68ea827b26503c8c931c3f20095d323b/processing',
            {
                'idempotency_token': 'blabla',
                'value': 5,
                'unique_driver_id': '5d8cf2d6b8e3f8796887b21d',
                'operation': 'set_activity_value',
            },
            {
                'created': '2020-05-28T15:48:50.840000+00:00',
                'descriptor': {'type': 'set_activity_value'},
                'extra_data': {
                    'mode': 'additive',
                    'operation': 'set_activity_value',
                    'reason': None,
                    'value': 5,
                },
                'idempotency_token': 'blabla',
                'type': 'dm_service_manual',
                'unique_driver_id': '5d8cf2d6b8e3f8796887b21d',
            },
            ['auto_amnesty'],
            id='amnesty_event_creation',
        ),
    ],
)
async def test_with_order_proc(
        stq3_context,
        stq,
        dms_mockserver,
        task_id,
        task_kwargs,
        expected_data,
        expected_tags,
        order_core_mock,
):
    await client_task.task(
        stq3_context,
        TaskInfo(
            id=task_id,
            exec_tries=1,
            reschedule_counter=1,
            queue='driver_metrics_client',
        ),
        task_kwargs,
    )

    assert dms_mockserver.event_new.times_called == 1
    event_new_call = dms_mockserver.event_new.next_call()['request'].json

    tags = event_new_call['descriptor'].pop('tags')
    assert sorted(tags) == sorted(expected_tags)

    assert event_new_call == expected_data
