from atlas.service_utils.anomalies.downtime_info import (
    scan_timeline,
    DowntimeEvent,
    EventType
)


class TestScanTimeline(object):
    def test_empty_events(self):
        confirmed_time_sec, total_time_sec = scan_timeline([])
        assert confirmed_time_sec == 0
        assert total_time_sec == 0

    def test_anomaly_starts_before_requested_interval(self):
        events = [
            DowntimeEvent(0, EventType.ANOMALY_START),
            DowntimeEvent(10, EventType.REQUEST_START),
            DowntimeEvent(15, EventType.ANOMALY_END),
            DowntimeEvent(20, EventType.REQUEST_END)
        ]

        confirmed_time_sec, total_time_sec = scan_timeline(events)
        assert confirmed_time_sec == 5
        assert total_time_sec == 10

    def test_anomaly_ends_after_requested_interval(self):
        events = [
            DowntimeEvent(0, EventType.REQUEST_START),
            DowntimeEvent(10, EventType.ANOMALY_START),
            DowntimeEvent(15, EventType.REQUEST_END),
            DowntimeEvent(20, EventType.ANOMALY_END)
        ]

        confirmed_time_sec, total_time_sec = scan_timeline(events)
        assert confirmed_time_sec == 5
        assert total_time_sec == 15

    def test_multiple_nonoverlapping_anomalies(self):
        events = [
            DowntimeEvent(0, EventType.REQUEST_START),
            DowntimeEvent(12, EventType.ANOMALY_START),
            DowntimeEvent(19, EventType.ANOMALY_END),
            DowntimeEvent(21, EventType.ANOMALY_START),
            DowntimeEvent(24, EventType.ANOMALY_END),
            DowntimeEvent(36, EventType.ANOMALY_START),
            DowntimeEvent(59, EventType.ANOMALY_END),
            DowntimeEvent(77, EventType.ANOMALY_START),
            DowntimeEvent(88, EventType.ANOMALY_END),
            DowntimeEvent(100, EventType.REQUEST_END),
        ]

        confirmed_time_sec, total_time_sec = scan_timeline(events)
        assert confirmed_time_sec == 44
        assert total_time_sec == 100

    def test_overlapping_anomalies(self):
        events = [
            DowntimeEvent(0, EventType.REQUEST_START),
            DowntimeEvent(10, EventType.ANOMALY_START),  # 1
            DowntimeEvent(20, EventType.ANOMALY_START),  # 2
            DowntimeEvent(30, EventType.ANOMALY_START),  # 3
            DowntimeEvent(40, EventType.ANOMALY_END),  # 2
            DowntimeEvent(50, EventType.ANOMALY_END),  # 1
            DowntimeEvent(70, EventType.ANOMALY_END),  # 3
            DowntimeEvent(70, EventType.ANOMALY_START),  # 4
            DowntimeEvent(80, EventType.ANOMALY_END),  # 4
            DowntimeEvent(100, EventType.REQUEST_END)
        ]

        confirmed_time_sec, total_time_sec = scan_timeline(events)
        assert confirmed_time_sec == 70
        assert total_time_sec == 100
