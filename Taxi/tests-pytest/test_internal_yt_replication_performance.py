import pytest

from taxi.internal.data_manager import performance


@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb(_fill=False)
def test_timer(sleep):
    with performance.Timer() as timer:
        sleep(1)
    assert timer.result == 1.0


@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb(_fill=False)
def test_timeit_iter(sleep):
    times_to_sleep = [1, 2, 3]

    def sleeper(times):
        for time in times:
            sleep(time)
            yield time

    actual_times = []
    for time, expected_time in performance.timeit_iter(
            sleeper(times_to_sleep)
    ):
        actual_times.append(time)
        assert time == expected_time
    assert actual_times == times_to_sleep


@pytest.mark.asyncenv('blocking')
@pytest.mark.filldb(_fill=False)
def test_performance_monitor():
    monitor = performance.PerformanceMonitor('taxi')
    monitor.add('foo', 1.0, 10)
    monitor.add('bar', 5.0, 100)
    monitor.add('foo', 0.1, 1)

    assert sorted(monitor.items()) == [
        ('taxi.bar.count', 100),
        ('taxi.bar.time', 5.0),
        ('taxi.foo.count', 11),
        ('taxi.foo.time', 1.1),
    ]
