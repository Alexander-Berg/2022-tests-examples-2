from datetime import datetime, timedelta

import mock
import pytest

from dmp_suite.decorators import try_except
from dmp_suite.postgresql.decorators import SolomonMetricReporterThread, retry_metric_reporter, Status


@pytest.mark.parametrize('start_datetime, stop_datetime, expected', [
    (
        None,
        datetime(1997, 5, 31),
        [datetime(1997, 5, 31)]
    ),
    (
        datetime(1997, 5, 31),
        datetime(1997, 5, 31),
        []
    ),
    (
        datetime(1997, 5, 31) - timedelta(seconds=9),
        datetime(1997, 5, 31),
        []
    ),
    (
        datetime(1997, 5, 31) - timedelta(seconds=10),
        datetime(1997, 5, 31),
        [datetime(1997, 5, 31)]
    ),
    (
        datetime(1997, 5, 31) - timedelta(seconds=40),
        datetime(1997, 5, 31),
        [datetime(1997, 5, 31) + timedelta(seconds=sec) for sec in range(-30, 1, 10)]
    ),
])
def test_get_datetime_range(start_datetime, stop_datetime, expected):
    solomon_client = mock.Mock()
    t = SolomonMetricReporterThread(solomon_client, timeout_sec=10)

    stop_datetime = datetime(1997, 5, 31)
    actual = list(t.get_datetime_range(start=start_datetime, stop=stop_datetime))

    assert actual == expected


def test_working_loop_just_work_if_success():
    solomon_client = mock.MagicMock()
    solomon_client.send = mock.Mock()
    t = SolomonMetricReporterThread(solomon_client, timeout_sec=10)
    t.update_state(status=Status.waiting, attempt=0)

    bool_sequence = iter([False, False, True])
    time_sequence = iter([datetime(1997, 5, 31) + timedelta(seconds=sec) for sec in range(0, 60, 10)])

    def status_changer(is_stopped: bool):
        if is_stopped:
            t.update_state(status=Status.success)
        return is_stopped

    with mock.patch(
        'dmp_suite.postgresql.decorators.get_current_rounded_utc_datetime',
        side_effect=lambda *_: next(time_sequence)
    ):
        t.wait = mock.Mock()
        t.is_stopped = lambda *_: status_changer(next(bool_sequence))

        # Все ради того, чтобы запустить это:
        t.working_loop()

    assert solomon_client.send.call_count == 3 * 2
    for i in range(2):
        assert solomon_client.send.call_args_list[-1 - i][1]['sensor'].startswith('retry.success.')


def test_working_loop_just_work_if_fail():
    solomon_client = mock.MagicMock()
    solomon_client.send = mock.Mock()

    attempt = 0

    t = SolomonMetricReporterThread(solomon_client, timeout_sec=10)

    t.update_state(status=Status.waiting, attempt=0)

    def mock_wait_callback():
        nonlocal attempt
        attempt += 1
        t.update_state(status=Status.waiting, attempt=attempt)

    bool_sequence = iter([False, False, False, True])
    time_sequence = iter([datetime(1997, 5, 31) + timedelta(seconds=sec) for sec in range(0, 60, 10)])

    def status_changer(is_stopped: bool):
        if is_stopped:
            t.update_state(status=Status.fail)
        return is_stopped

    with mock.patch(
        'dmp_suite.postgresql.decorators.get_current_rounded_utc_datetime',
        side_effect=lambda *_: next(time_sequence)
    ):
        t.wait = mock_wait_callback
        t.is_stopped = lambda *_: status_changer(next(bool_sequence))

        # Все ради того, чтобы запустить это:
        t.working_loop()

    assert solomon_client.send.call_count == 4 * 2
    for i in range(2):
        assert solomon_client.send.call_args_list[-1 - i][1]['sensor'].startswith('retry.fail.')


def test_working_loop_work_in_critical_scenario():
    solomon_client = mock.MagicMock()
    solomon_client.send = mock.Mock()
    t = SolomonMetricReporterThread(solomon_client, timeout_sec=10)
    t.update_state(status=Status.waiting, attempt=0)

    # Произошло слипание моментов времени с отправкой
    bool_sequence = iter([False, False, False, False, False, True])
    time_sequence = iter(
        [
            datetime(1997, 5, 31, 0, 0, 0),
            datetime(1997, 5, 31, 0, 0, 0),
            datetime(1997, 5, 31, 0, 0, 20),
            datetime(1997, 5, 31, 0, 0, 20),
            datetime(1997, 5, 31, 0, 0, 40),
            datetime(1997, 5, 31, 0, 0, 50),
         ]
    )

    with mock.patch(
        'dmp_suite.postgresql.decorators.get_current_rounded_utc_datetime',
        side_effect=lambda *_: next(time_sequence)
    ):
        t.wait = mock.Mock()
        t.is_stopped = lambda *_: next(bool_sequence)

        # Все ради того, чтобы запустить это:
        t.working_loop()

    assert solomon_client.send.call_count == 2 * 6
    assert solomon_client.send.call_args_list
    expected_time_sequence = iter([
        dttm
        for dttms in [2 * [datetime(1997, 5, 31, 0, 0, 0) + timedelta(seconds=sec)] for sec in range(0, 60, 10)]
        for dttm in dttms
    ])
    for call in solomon_client.send.call_args_list:
        assert call[1]['dttm'] == next(expected_time_sequence)


def test_decorator_can_be_used_without_task():
    inner_mock = mock.Mock()

    with mock.patch('dmp_suite.postgresql.decorators.get_solomon_client'):
        my_decorator = retry_metric_reporter(
            'my_database_type',
            'my_database_name',
            'my_user_name',
            attempt_limit=15,
        )

        @my_decorator
        def foo():
            inner_mock()
            return 'Hello world!'

        assert foo() == 'Hello world!'
        assert inner_mock.call_count == 1


def test_decorator_can_be_used_without_task_with_retry():
    rep_thread_obj = mock.MagicMock()
    inner_mock = mock.Mock()

    solomon = mock.MagicMock()
    with mock.patch(
        'dmp_suite.postgresql.decorators.get_solomon_client',
        return_value=solomon
    ) as get_solomon, \
        mock.patch(
            'dmp_suite.postgresql.decorators.SolomonMetricReporterThread',
            return_value=rep_thread_obj
    ) as rep_thread_cls:
        my_decorator = retry_metric_reporter(
            'my_database_type',
            'my_database_name',
            'my_user_name',
            attempt_limit=15,
        )
        my_retry = try_except(
            times=5,
            sleep=0
        )

        @my_retry
        @my_decorator
        def foo():
            inner_mock()
            raise Exception()

        try:
            foo()
        except:
            pass

        assert get_solomon.call_count == 1
        assert rep_thread_cls.call_count == 1

        start_call = 0
        update_metrics_call = 0

        for method_call in rep_thread_obj.method_calls:
            if method_call[0] == 'update_state':
                update_metrics_call += 1
            elif method_call[0] == 'start':
                start_call += 1

        assert start_call == 1
        assert update_metrics_call == 5
