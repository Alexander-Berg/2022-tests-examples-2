import json

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from driver_metrics_storage_plugins import *  # noqa: F403 F401
# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest


@pytest.fixture(scope='function')
def clear_range_partitions(pgsql):
    yield
    cursor = pgsql['drivermetrics'].conn.cursor()
    cursor.execute(
        """
        DO $$
        DECLARE
          rec record;
        BEGIN
          FOR rec IN SELECT table_name FROM common.range_partitions_metadata
            LOOP
              execute format ('DROP TABLE data.%s;', rec.table_name);
            END LOOP;
        END $$;
    """,
    )
    cursor.execute(
        """
        DELETE FROM common.range_partitions_metadata;
    """,
    )


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

    def __str__(self):
        if self._old_metrics is None:
            return json.dumps(self._new_metrics)
        if isinstance(self._new_metrics, str):
            return str(
                {
                    '$strdiff': [
                        json.dumps(self._old_metrics),
                        json.dumps(self._new_metrics),
                    ],
                },
            )
        if isinstance(self._new_metrics, dict):
            res = {}
            for key, value in self._new_metrics.items():
                if key.startswith('$') or value is None:
                    continue
                if (
                        isinstance(self._old_metrics, dict)
                        and self._old_metrics.get(key, None) == value
                ):
                    continue
                vdiff = MetricsDiff(
                    self._old_metrics.get(key, {}), value,
                ).get_diff()
                res[key] = vdiff
            return json.dumps(res)
        return str(self._new_metrics - (self._old_metrics or 0))

    def get_diff(self):
        if isinstance(self._new_metrics, dict):
            res = {}
            for key, value in self._new_metrics.items():
                if key.startswith('$'):
                    continue
                if self._old_metrics.get(key, {}) == value:
                    continue
                res[key] = MetricsDiff(
                    self._old_metrics.get(key, {}), value,
                ).get_diff()
            return res
        return (self._new_metrics or 0) - (self._old_metrics or 0)


class MetricsMonitor:
    def __init__(self, service_monitor):
        self._service_monitor = service_monitor
        self._snapshot_metrics = None

    async def take_snapshot(self):
        self._snapshot_metrics = await self._service_monitor.get_metrics()

    async def get_metrics_diff(self):
        assert self._snapshot_metrics, (
            'You should call metrics_snapshot.take_snapshot() in '
            'your test before get_metrics_diff call'
        )

        metrics = await self._service_monitor.get_metrics()

        return MetricsDiff(self._snapshot_metrics, metrics)


@pytest.fixture(name='metrics_snapshot', autouse=True)
def _metrics_snapshot(taxi_driver_metrics_storage_monitor):
    return MetricsMonitor(taxi_driver_metrics_storage_monitor)
