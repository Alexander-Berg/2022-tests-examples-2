import datetime
import signal
import threading

import pymongo
import pytest

from taxi.internal import distlock
from taxi.internal import maintenance
from taxi_maintenance import autoprolong

PID = 100500


@pytest.mark.parametrize(
    'max_count,prolongation_frequency,error,max_errors,'
    'marker_time_gap,start_last_mark,alive', [
        (
            3, 10, pymongo.errors.NetworkTimeout, 2, None, None, True,
        ),
        (
            2, 10, distlock.ProlongationError, 2, None, None, False,
        ),
        (
            5, 10, None, 0, None, None, True,
        ),
        (
            2, 10, None, 0, datetime.timedelta(hours=1),
            datetime.datetime(2019, 4, 3, 0), False,
        ),
        (
            2, 10, None, 0, datetime.timedelta(hours=1), None, True,
        ),
    ]
)
@pytest.mark.now('2019-04-04 10:00:00 +03')
@pytest.mark.asyncenv('blocking')
def test_autoprolong(monkeypatch, max_count, prolongation_frequency, error,
                     max_errors, marker_time_gap, start_last_mark, alive):

    def get_pid():
        return PID

    tasks = {PID: True}

    def kill(pid, sig):
        assert sig == signal.SIGINT
        tasks[pid] = False

    test_event = threading.Event()

    class _DummyTaskLock(maintenance.DummyLock):
        def __init__(self):
            super(_DummyTaskLock, self).__init__()
            if start_last_mark:
                self.marker._last_mark = start_last_mark
            self.count = 0
            self.max_count = max_count
            self.errors = 0
            self.max_errors = max_errors

        def prolong(self, timeout):
            if self.count < self.max_count:
                self.count += 1
                return
            elif error:
                if self.errors < self.max_errors:
                    self.errors += 1
                    raise error
            test_event.set()

    monkeypatch.setattr('os.getpid', get_pid)
    monkeypatch.setattr('os.kill', kill)

    task_lock = _DummyTaskLock()
    with autoprolong.thread(task_lock, 0.05, prolongation_frequency,
                            marker_time_gap=marker_time_gap):
        assert test_event.wait(10)

    assert task_lock.count == max_count
    assert task_lock.errors == max_errors
    assert tasks[PID] == alive
