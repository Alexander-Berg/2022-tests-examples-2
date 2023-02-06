import math

from yanetagent.metrics.base import Metrics, InfluxDBLineProtocolMetricsAdapter


class TestMetrics:
    def test_update_build_timings(self) -> None:
        metrics = Metrics("name")
        metrics._update_build_timings(0.0)

        expected = [
            [0.0, 0],
            [1.0, 1],
            [2.0, 0],
            [4.0, 0],
            [8.0, 0],
            [16.0, 0],
            [32.0, 0],
            [64.0, 0],
            [128.0, 0],
            [256.0, 0],
            [512.0, 0],
            [1024.0, 0],
            [2048.0, 0],
            [math.inf, 0],
        ]
        assert expected == metrics.build_timings()

    def test_update_build_timings_upper_bound(self) -> None:
        metrics = Metrics("name")
        metrics._update_build_timings(1.0)

        expected = [
            [0.0, 0],
            [1.0, 0],
            [2.0, 1],
            [4.0, 0],
            [8.0, 0],
            [16.0, 0],
            [32.0, 0],
            [64.0, 0],
            [128.0, 0],
            [256.0, 0],
            [512.0, 0],
            [1024.0, 0],
            [2048.0, 0],
            [math.inf, 0],
        ]
        assert expected == metrics.build_timings()

    def test_update_build_timings_middle(self) -> None:
        metrics = Metrics("name")
        metrics._update_build_timings(40.0)

        expected = [
            [0.0, 0],
            [1.0, 0],
            [2.0, 0],
            [4.0, 0],
            [8.0, 0],
            [16.0, 0],
            [32.0, 0],
            [64.0, 1],
            [128.0, 0],
            [256.0, 0],
            [512.0, 0],
            [1024.0, 0],
            [2048.0, 0],
            [math.inf, 0],
        ]
        assert expected == metrics.build_timings()

    def test_update_build_timings_huge(self) -> None:
        metrics = Metrics("name")
        metrics._update_build_timings(100500.0)

        expected = [
            [0.0, 0],
            [1.0, 0],
            [2.0, 0],
            [4.0, 0],
            [8.0, 0],
            [16.0, 0],
            [32.0, 0],
            [64.0, 0],
            [128.0, 0],
            [256.0, 0],
            [512.0, 0],
            [1024.0, 0],
            [2048.0, 0],
            [math.inf, 1],
        ]
        assert metrics.build_timings() == expected

    def test_influxdb_dump(self) -> None:
        metrics = Metrics("name", tags={"a": "b"})
        metrics._inc_errors()

        expected = "name,a=b errors=1i,errors_update_controlplane=0i,last_snapshot_timestamp=0i,last_status=0i,state=0i,uptime=0i"
        assert expected == InfluxDBLineProtocolMetricsAdapter(metrics).dump()
