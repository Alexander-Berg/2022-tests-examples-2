import pytest

from taxi_maintenance.stuff import graphite_yt_errors


@pytest.mark.now('2018-01-31T08:21:00')
@pytest.mark.config(YT_REPLICATION_CLUSTERS=['hahn', 'arnold'])
@pytest.mark.config(YT_REPLICATION_RUNTIME_CLUSTERS=['seneca-man'])
@pytest.inline_callbacks
def test_do_stuff(monkeypatch, patch):
    calls = []

    monkeypatch.setattr(
        graphite_yt_errors, 'STATS_INTERVAL', 60
    )

    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    def send_taxi_cluster_metric(*args, **kwargs):
        calls.append((args, kwargs))

    @patch('taxi.internal.yt_tools.meta.errors.get_all_errors_keys')
    def get_all_errors_keys():
        return (
            'yt_no_such_tablet',
            'yt_proxy_unavailable',
            'other_yt_response_error',
        )

    created_ts = 1517386740.0

    yield graphite_yt_errors.do_stuff()

    expected = [
        (
            ('yt_replication_errors.arnold.other_yt_response_error', 0,
             created_ts),
            {},
        ),
        (('yt_replication_errors.arnold.total', 3, created_ts), {}),
        (
            ('yt_replication_errors.arnold.yt_no_such_tablet', 3, created_ts),
            {},
        ),
        (
            (
                'yt_replication_errors.arnold.yt_proxy_unavailable',
                0,
                created_ts,
            ),
            {},
        ),
        (
            ('yt_replication_errors.hahn.other_yt_response_error', 1,
             created_ts),
            {},
        ),
        (('yt_replication_errors.hahn.total', 4, created_ts), {}),
        (
            ('yt_replication_errors.hahn.yt_no_such_tablet', 0, created_ts),
            {},
        ),
        (
            ('yt_replication_errors.hahn.yt_proxy_unavailable', 3, created_ts),
            {},
        ),
        (
            ('yt_replication_errors.seneca-man.other_yt_response_error', 0,
             created_ts),
            {},
        ),
        (('yt_replication_errors.seneca-man.total', 0, created_ts), {}),
        (
            ('yt_replication_errors.seneca-man.yt_no_such_tablet', 0,
             created_ts),
            {},
        ),
        (
            ('yt_replication_errors.seneca-man.yt_proxy_unavailable', 0,
             created_ts),
            {},
        ),
    ]

    assert sorted(calls) == expected
