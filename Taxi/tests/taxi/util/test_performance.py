import pytest

from taxi.util import performance


@pytest.mark.parametrize('times_to_sleep', [list(range(3)), []])
@pytest.mark.nofilldb()
async def test_timeit_iter(monkeypatch, times_to_sleep):
    class FakeTimer(performance.Timer):
        results = iter(times_to_sleep)

        @property
        def result(self):
            return next(self.results)

    monkeypatch.setattr(performance, 'Timer', FakeTimer)

    async def simple_aiter():
        for _time in times_to_sleep:
            yield 'item %s' % _time

    actual_times = []
    async for time, item in performance.timeit_aiter(simple_aiter()):
        actual_times.append(time)
        assert 'item %s' % time == item
    assert actual_times == times_to_sleep


@pytest.mark.nofilldb()
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
