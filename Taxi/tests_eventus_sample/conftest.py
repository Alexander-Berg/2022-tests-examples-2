import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eventus_sample_plugins import *  # noqa: F403 F401


@pytest.fixture(name='metrics_snapshot', autouse=True)
def _metrics_snapshot(taxi_eventus_sample_monitor):
    class Metrics:
        def __init__(self):
            self._snapshot_metrics = None

        async def take_snapshot(self):
            self._snapshot_metrics = (
                await taxi_eventus_sample_monitor.get_metrics()
            )

        async def get_metrics_diff(self):
            assert self._snapshot_metrics, (
                'You should call metrics_snapshot.take_snapshot() in '
                'your test before get_metrics_diff call'
            )

            metrics = await taxi_eventus_sample_monitor.get_metrics()

            class MetricsDiff:
                def __init__(self, old_metrics, new_metrics):
                    self._old_metrics = old_metrics
                    self._new_metrics = new_metrics

                def __getitem__(self, arg):
                    assert arg in self._new_metrics
                    return MetricsDiff(
                        self._old_metrics.get(arg, {})
                        if self._old_metrics is not None
                        else {},
                        self._new_metrics[arg],
                    )

                def get_diff(self):
                    if isinstance(self._new_metrics, dict):
                        res = {}
                        for key, value in self._new_metrics.items():
                            if key.startswith('$'):
                                continue
                            res[key] = MetricsDiff(
                                self._old_metrics.get(key, {}), value,
                            ).get_diff()
                        return res
                    return self._new_metrics - (self._old_metrics or 0)

            return MetricsDiff(self._snapshot_metrics, metrics)

    return Metrics()
