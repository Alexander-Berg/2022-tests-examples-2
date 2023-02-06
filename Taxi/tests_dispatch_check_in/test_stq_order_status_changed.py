import copy
import datetime

import pytest

import tests_dispatch_check_in.utils as utils

SOME_DATETIME = datetime.datetime(
    2021, 6, 4, 13, 37, 2, 85130, tzinfo=datetime.timezone.utc,
)
CHECK_IN_TIME = datetime.datetime(
    2021, 6, 4, 13, 40, 0, 0, tzinfo=datetime.timezone.utc,
)
TRANSPORTING_TIME = datetime.datetime(
    2021, 6, 4, 13, 45, 0, 0, tzinfo=datetime.timezone.utc,
)
CHECK_IN_TIME_STR = CHECK_IN_TIME.isoformat()
TRANSPORTING_TIME_STR = TRANSPORTING_TIME.isoformat()
NOW = datetime.datetime(2021, 6, 4, 15, 0, 0, 0, tzinfo=datetime.timezone.utc)

INIT_ETALON = {
    'order_id1': {
        'updated_ts': SOME_DATETIME,
        'created_ts': SOME_DATETIME,
        'check_in_ts': None,
        'terminal_id': 'terminal_id1',
        'pickup_line': None,
        'tariff_zone': 'some_tariff_zone',
        'user_id': 'some_user',
        'user_locale': 'some_locale',
        'classes': ['econom', 'comfortplus'],
    },
    'order_id2': {
        'updated_ts': CHECK_IN_TIME,
        'created_ts': SOME_DATETIME,
        'check_in_ts': CHECK_IN_TIME,
        'terminal_id': 'terminal_id2',
        'pickup_line': 'pickup_line1',
        'tariff_zone': 'some_tariff_zone',
        'user_id': 'some_user',
        'user_locale': 'some_locale',
        'classes': ['business'],
    },
}


async def test_stq_order_status_changed_check_in_empty_db(pgsql, stq_runner):
    await stq_runner.dispatch_check_in_order_status_changed.call(
        task_id='task_id1',
        kwargs={
            'order_id': 'order_id1',
            'user_id': 'some_user',
            'new_status_type': 'start-dispatch-check-in',
            'check_in_info': {
                'check_in_time': CHECK_IN_TIME_STR,
                'pickup_line': 'pickup_line1',
            },
        },
    )

    db = pgsql['dispatch_check_in']
    assert utils.get_all_orders(db) == {}


@pytest.mark.parametrize(
    'status_type',
    ['start-dispatch-check-in', 'handle_finish', 'handle_transporting'],
)
async def test_stq_order_status_changed_check_in_missed_parameter(
        pgsql, stq_runner, status_type,
):
    await stq_runner.dispatch_check_in_order_status_changed.call(
        task_id='task_id1',
        kwargs={
            'order_id': 'order_id1',
            'user_id': 'some_user',
            'new_status_type': status_type,
        },
        # if args validation failed, task is marked as finished
        expect_fail=False,
    )

    db = pgsql['dispatch_check_in']
    assert utils.get_all_orders(db) == {}


# order_id3 not exist => no change in db
@pytest.mark.parametrize('order_id', ['order_id1', 'order_id3'])
@pytest.mark.pgsql('dispatch_check_in', files=['check_in_orders.sql'])
async def test_stq_order_status_changed_check_in(
        pgsql, stq_runner, mocked_time, order_id,
):
    mocked_time.set(NOW)

    etalon = copy.deepcopy(INIT_ETALON)

    db = pgsql['dispatch_check_in']

    assert utils.get_all_orders(db) == etalon

    await stq_runner.dispatch_check_in_order_status_changed.call(
        task_id='task_id1',
        kwargs={
            'order_id': order_id,
            'user_id': 'some_user',
            'new_status_type': 'start-dispatch-check-in',
            'check_in_info': {
                'check_in_time': CHECK_IN_TIME_STR,
                'pickup_line': 'pickup_line1',
            },
        },
    )

    # Check checked_in handler idempotency. This call must not change db
    await stq_runner.dispatch_check_in_order_status_changed.call(
        task_id='task_id2',
        kwargs={
            'order_id': 'order_id2',
            'user_id': 'some_user',
            'new_status_type': 'start-dispatch-check-in',
            'check_in_info': {
                'check_in_time': CHECK_IN_TIME_STR,
                'pickup_line': 'pickup_line3',
            },
        },
    )

    if order_id in etalon:
        etalon[order_id]['check_in_ts'] = CHECK_IN_TIME
        etalon[order_id]['pickup_line'] = 'pickup_line1'
        etalon[order_id]['updated_ts'] = NOW

    assert utils.get_all_orders(db) == etalon


# order_id1 is not checked in
# order_id2 is already checked in
# order_id3 not exist => no change in db
@pytest.mark.pgsql('dispatch_check_in', files=['check_in_orders.sql'])
@pytest.mark.parametrize(
    'new_status_type,finish_reason',
    [
        ('handle_finish', 'expired'),
        ('handle_finish', 'cancelled_by_user'),
        ('handle_finish', 'cancelled_by_park'),
        ('handle_finish', 'other'),
        ('handle_transporting', None),
    ],
)
@pytest.mark.parametrize('order_id', ['order_id1', 'order_id2', 'order_id3'])
async def test_stq_order_status_changed_remove_from_db(
        pgsql, stq_runner, new_status_type, finish_reason, order_id,
):
    etalon = copy.deepcopy(INIT_ETALON)

    db = pgsql['dispatch_check_in']

    assert utils.get_all_orders(db) == etalon

    kwargs = {
        'order_id': order_id,
        'user_id': 'some_user',
        'new_status_type': new_status_type,
        'finish_info': {'reason': finish_reason},
    }
    if new_status_type == 'handle_transporting':
        del kwargs['finish_info']
        kwargs['transporting_info'] = {
            'transporting_ts': TRANSPORTING_TIME_STR,
            'performer': {'dbid': 'dbid1', 'uuid': 'uuid1'},
        }
    await stq_runner.dispatch_check_in_order_status_changed.call(
        task_id='task_id1', kwargs=kwargs,
    )

    if order_id in etalon:
        del etalon[order_id]

    assert utils.get_all_orders(db) == etalon


@pytest.mark.config(DISPATCH_CHECK_IN_ORDER_STATUS_CHANGED_MAX_ATTEMPTS=3)
async def test_stq_order_status_changed_max_attempts(
        taxi_dispatch_check_in, stq_runner, testpoint,
):
    @testpoint('dispatch_check_in_order_status_changed')
    def testpoint_call(_):
        return {'inject_error': True}

    await taxi_dispatch_check_in.enable_testpoints()

    kwargs = {
        'order_id': 'order_id1',
        'user_id': 'some_user',
        'new_status_type': 'handle_transporting',
        'transporting_info': {
            'transporting_ts': TRANSPORTING_TIME_STR,
            'performer': {'dbid': 'dbid1', 'uuid': 'uuid1'},
        },
    }

    await stq_runner.dispatch_check_in_order_status_changed.call(
        task_id='task_id1', kwargs=kwargs, expect_fail=True,
    )
    await stq_runner.dispatch_check_in_order_status_changed.call(
        task_id='task_id1', kwargs=kwargs, expect_fail=False, exec_tries=3,
    )

    assert testpoint_call.times_called == 2


@pytest.mark.parametrize('order_id', ['order_id1', 'order_id2', 'order_id3'])
@pytest.mark.pgsql('dispatch_check_in', files=['check_in_orders.sql'])
async def test_stq_order_status_changed_checked_in_metrics(
        taxi_dispatch_check_in,
        taxi_dispatch_check_in_monitor,
        stq_runner,
        mocked_time,
        order_id,
):
    mocked_time.set(NOW)

    await stq_runner.dispatch_check_in_order_status_changed.call(
        task_id='task_id1',
        kwargs={
            'order_id': order_id,
            'user_id': 'some_user',
            'new_status_type': 'start-dispatch-check-in',
            'check_in_info': {
                'check_in_time': CHECK_IN_TIME_STR,
                'pickup_line': 'pickup_line1',
            },
        },
    )

    if order_id == 'order_id1':
        mocked_time.set(NOW + datetime.timedelta(seconds=15))
        await taxi_dispatch_check_in.tests_control(invalidate_caches=False)
        await utils.check_metric(
            taxi_dispatch_check_in_monitor,
            'checked_in_orders',
            1,
            ['terminal_id1', 'econom', 'pickup_line1'],
        )
        await utils.check_metric(
            taxi_dispatch_check_in_monitor,
            'transporting_orders',
            None,
            ['terminal_id1', 'econom', 'pickup_line1'],
        )
        await utils.check_metric(
            taxi_dispatch_check_in_monitor,
            'from_created_to_check_in_time',
            (CHECK_IN_TIME - SOME_DATETIME).seconds,
            ['terminal_id1', 'econom', 'pickup_line1', 'p100'],
        )
    else:
        await utils.check_no_metrics(taxi_dispatch_check_in_monitor)


# order_id1 - not checked-in order => finished_before_check_in
# order_id2 - checked-in order => finished_after_check_in
# order_id3 - not exist order => no metrics
@pytest.mark.pgsql('dispatch_check_in', files=['check_in_orders.sql'])
@pytest.mark.parametrize(
    'finish_reason',
    ['expired', 'cancelled_by_user', 'cancelled_by_park', 'other'],
)
@pytest.mark.parametrize('order_id', ['order_id1', 'order_id2', 'order_id3'])
async def test_stq_order_status_changed_finished_metrics(
        taxi_dispatch_check_in,
        taxi_dispatch_check_in_monitor,
        stq_runner,
        mocked_time,
        finish_reason,
        order_id,
):
    mocked_time.set(NOW)

    kwargs = {
        'order_id': order_id,
        'user_id': 'some_user',
        'new_status_type': 'handle_finish',
        'finish_info': {'reason': finish_reason},
    }
    await stq_runner.dispatch_check_in_order_status_changed.call(
        task_id='task_id1', kwargs=kwargs,
    )

    mocked_time.set(NOW + datetime.timedelta(seconds=10))
    await taxi_dispatch_check_in.tests_control(invalidate_caches=False)
    if order_id == 'order_id1':
        await utils.check_metric(
            taxi_dispatch_check_in_monitor,
            'finished_before_check_in_orders',
            1,
            ['terminal_id1', 'econom', finish_reason],
        )
    elif order_id == 'order_id2':
        await utils.check_metric(
            taxi_dispatch_check_in_monitor,
            'finished_after_check_in_orders',
            1,
            ['terminal_id2', 'business', 'pickup_line1', finish_reason],
        )
    else:
        await utils.check_no_metrics(taxi_dispatch_check_in_monitor)


# order_id2 - checked-in order in db => has metrics
# order_id3 - not exist in db => has no metrics

# dbid1_uuid10 - queued driver => by_check_in_flow
# dbid1_uuid11 - not exist in cache driver => by_fallback
# dbid2_uuid20 - filtered by holded reason driver => by_check_in_flow
# dbid2_uuid21 - filtered by not holded reason driver => by_fallback
# dbid3_uuid30 - filtered by holded reason driver
#                but not pickup_line => by_fallback
# dbid3_uuid31 - filtered by not holded reason
#                and not pickup_line => by_fallback
# dbid3_uuid32 - queued driver but not pickup_line => by_fallback
@pytest.mark.parametrize('order_id', ['order_id2', 'order_id3'])
@pytest.mark.parametrize(
    'dbid,uuid,dispatch_result',
    [
        ('dbid1', 'uuid10', 'by_check_in_flow'),
        ('dbid1', 'uuid11', 'by_fallback'),
        ('dbid2', 'uuid20', 'by_check_in_flow'),
        ('dbid2', 'uuid21', 'by_fallback'),
        ('dbid3', 'uuid30', 'by_fallback'),
        ('dbid3', 'uuid31', 'by_fallback'),
        ('dbid3', 'uuid32', 'by_fallback'),
    ],
)
@pytest.mark.pgsql('dispatch_check_in', files=['check_in_orders.sql'])
async def test_stq_order_status_changed_transporting_metrics(
        taxi_dispatch_check_in,
        taxi_dispatch_check_in_monitor,
        mockserver,
        stq_runner,
        mocked_time,
        order_id,
        dbid,
        uuid,
        dispatch_result,
):
    mocked_time.set(NOW)

    @mockserver.json_handler('/dispatch-airport/v1/active-drivers-queues')
    def _active_drivers_queues(request):
        assert request.query['with_filtered'] == 'true'
        if request.query['airport'] == 'pickup_line1':
            return {
                'queues': [
                    {
                        'tariff': 'business',
                        'active_drivers': [
                            {
                                'dbid_uuid': 'dbid1_uuid10',
                                'queued': '2019-06-10T13:02:20Z',
                            },
                        ],
                    },
                ],
                'filtered': [
                    {'dbid_uuid': 'dbid2_uuid20', 'reason': 'holded'},
                    {'dbid_uuid': 'dbid2_uuid21', 'reason': 'some_reason'},
                ],
            }
        if request.query['airport'] == 'svo':
            return {
                'queues': [
                    {
                        'tariff': 'business',
                        'active_drivers': [
                            {
                                'dbid_uuid': 'dbid3_uuid32',
                                'queued': '2019-06-10T13:02:20Z',
                            },
                        ],
                    },
                ],
                'filtered': [
                    {'dbid_uuid': 'dbid3_uuid30', 'reason': 'holded'},
                    {'dbid_uuid': 'dbid3_uuid31', 'reason': 'some-reason'},
                ],
            }
        return {'queues': []}

    await stq_runner.dispatch_check_in_order_status_changed.call(
        task_id='task_id1',
        kwargs={
            'order_id': order_id,
            'user_id': 'some_user',
            'new_status_type': 'handle_transporting',
            'transporting_info': {
                'transporting_ts': TRANSPORTING_TIME_STR,
                'performer': {'dbid': dbid, 'uuid': uuid},
            },
        },
    )

    if order_id == 'order_id2':
        mocked_time.set(NOW + datetime.timedelta(seconds=15))
        await taxi_dispatch_check_in.tests_control(invalidate_caches=False)
        await utils.check_metric(
            taxi_dispatch_check_in_monitor,
            'checked_in_orders',
            None,
            ['terminal_id2', 'business', 'pickup_line1'],
        )
        await utils.check_metric(
            taxi_dispatch_check_in_monitor,
            'transporting_orders',
            1,
            ['terminal_id2', 'business', 'pickup_line1', dispatch_result],
        )
        await utils.check_metric(
            taxi_dispatch_check_in_monitor,
            'from_check_in_to_transporting_time',
            (TRANSPORTING_TIME - CHECK_IN_TIME).seconds,
            [
                'terminal_id2',
                'business',
                'pickup_line1',
                dispatch_result,
                'p100',
            ],
        )
    else:
        await utils.check_no_metrics(taxi_dispatch_check_in_monitor)


@pytest.mark.parametrize('force_totw', [True, False])
@pytest.mark.parametrize('stq_status', ['handle_driving', 'handle_waiting'])
async def test_stq_order_status_changed_force_totw(
        taxi_config, mockserver, stq_runner, force_totw, stq_status,
):
    @mockserver.json_handler('/client-notify/v2/push')
    def _v2_push(request):
        assert (
            request.headers['X-Idempotency-Token']
            == f'{stq_status}_force_totw_order_id1_0'
        )
        assert request.json == {
            'client_id': 'some_user',
            'intent': 'force_totw',
            'service': 'go',
            'data': {'order_id': 'order_id1'},
        }
        return {'notification_id': '1'}

    taxi_config.set_values(
        {
            'DISPATCH_CHECK_IN_FORCE_TOTW_PUSH_SETTINGS': {
                'enabled': force_totw,
            },
        },
    )

    task_kwargs = {
        'order_id': 'order_id1',
        'user_id': 'some_user',
        'new_status_type': stq_status,
    }

    if stq_status == 'handle_driving':
        task_kwargs['driving_info'] = {
            'performer': {'dbid': 'dbid1', 'uuid': 'uuid1'},
            'order_alias_id': 'order_alias_id1',
        }

    await stq_runner.dispatch_check_in_order_status_changed.call(
        task_id='task_id1', kwargs=task_kwargs,
    )

    if force_totw:
        await _v2_push.wait_call()
    else:
        assert _v2_push.times_called == 0


@pytest.mark.parametrize(
    'auto_waiting_enabled, driver_uuid, order_status_change_call_expected',
    [
        # driver is in check-in queue -> call change status
        (True, 'uuid0', True),
        # driver is in check-in queue, change status is disabled by config
        (False, 'uuid0', False),
        # driver is in non check-in queue -> don't call change status
        (True, 'uuid1', False),
        # driver is not queued -> don't call change status
        (True, 'uuid2', False),
    ],
)
async def test_stq_order_status_changed_auto_waiting(
        taxi_config,
        mockserver,
        stq_runner,
        auto_waiting_enabled,
        driver_uuid,
        order_status_change_call_expected,
):
    @mockserver.json_handler('/dispatch-airport/v1/active-drivers-queues')
    def _active_drivers_queues(request):
        assert request.query['with_filtered'] == 'true'
        if request.query['airport'] == 'pickup_line1':
            return {
                'queues': [
                    {
                        'tariff': 'business',
                        'active_drivers': [
                            {
                                'dbid_uuid': 'dbid0_uuid0',
                                'queued': '2019-06-10T13:02:20Z',
                            },
                        ],
                    },
                ],
                'filtered': [],
            }
        if request.query['airport'] == 'svo':
            return {
                'queues': [
                    {
                        'tariff': 'business',
                        'active_drivers': [
                            {
                                'dbid_uuid': 'dbid0_uuid1',
                                'queued': '2019-06-10T13:02:20Z',
                            },
                        ],
                    },
                ],
                'filtered': [],
            }
        return {'queues': []}

    @mockserver.json_handler(
        '/driver-orders-app-api/internal/v1/order/status/waiting',
    )
    def _order_status_change(request):
        assert request.json == {
            'driver_profile_id': driver_uuid,
            'park_id': 'dbid0',
            'setcar_id': 'order_alias_id1',
            'origin': 'yandex_dispatch',
            'should_notify': True,
        }

        return {'status': 'ok'}

    taxi_config.set_values(
        {'DISPATCH_CHECK_IN_AUTO_WAITING_ENABLED': auto_waiting_enabled},
    )

    task_kwargs = {
        'order_id': 'order_id1',
        'user_id': 'some_user',
        'new_status_type': 'handle_driving',
        'driving_info': {
            'performer': {'dbid': 'dbid0', 'uuid': driver_uuid},
            'order_alias_id': 'order_alias_id1',
        },
    }

    await stq_runner.dispatch_check_in_order_status_changed.call(
        task_id='task_id1', kwargs=task_kwargs,
    )

    if order_status_change_call_expected:
        await _order_status_change.wait_call()
    else:
        assert _order_status_change.times_called == 0
