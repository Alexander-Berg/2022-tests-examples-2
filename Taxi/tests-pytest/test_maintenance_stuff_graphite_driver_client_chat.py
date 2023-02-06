import datetime
import pytest

from taxi.internal import event_monitor
from taxi_maintenance.stuff import graphite_driver_client_chat


@pytest.mark.now('2018-01-31T08:21:00')
@pytest.inline_callbacks
def test_do_stuff(monkeypatch, patch):
    calls = []

    @patch('taxi.util.graphite.send_cluster_metric')
    def send_cluster_metric(*args, **kwargs):
        calls.append((args, kwargs))

    yield event_monitor.driver_client_chat_event_stats(
        closed_with_client_error=1
    )

    now = datetime.datetime.utcnow()
    start_time = now + datetime.timedelta(
        seconds=graphite_driver_client_chat.UPDATE_TIME + 1
    )
    yield graphite_driver_client_chat.do_stuff(start_time)

    created_ts = calls[0][0][2]

    expected = [(
        (
            'driver_client_chat.closed_with_client_error',
            1,
            created_ts
        ),
        {}
    )]

    assert sorted(calls) == expected
