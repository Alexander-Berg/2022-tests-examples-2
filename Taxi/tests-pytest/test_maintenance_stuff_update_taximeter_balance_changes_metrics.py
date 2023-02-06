import datetime

import pytest

from taxi.core import async
from taxi_maintenance.stuff import update_taximeter_balance_changes_metrics


CRON_START_TIME = datetime.datetime(2018, 4, 26, 10, 52, 12, 638)
EXPECTED_METRIC_TIMESTAMP = 1524739860.0


@pytest.mark.parametrize(
    'expected_send_taxi_cluster_metric_calls',
    [
            [
                {
                    'args': (),
                    'kwargs': {
                        'stamp': EXPECTED_METRIC_TIMESTAMP,
                        'metric': (
                            'taximeter_balance_changes.payment_counts.refund'
                        ),
                        'value': 0
                    }
                },
                {
                    'args': (),
                    'kwargs': {
                        'stamp': EXPECTED_METRIC_TIMESTAMP,
                        'metric': (
                            'taximeter_balance_changes.payment_counts.applepay'
                        ),
                        'value': 45
                    }
                },
                {
                    'args': (),
                    'kwargs': {
                        'stamp': EXPECTED_METRIC_TIMESTAMP,
                        'metric': (
                            'taximeter_balance_changes.payment_counts.googlepay'
                        ),
                        'value': 45
                    }
                },
                {
                    'args': (),
                    'kwargs': {
                        'stamp': EXPECTED_METRIC_TIMESTAMP,
                        'metric': (
                            'taximeter_balance_changes.payment_counts.'
                            'compensation'
                        ),
                        'value': 7
                    }
                },
                {
                    'args': (),
                    'kwargs': {
                        'stamp': EXPECTED_METRIC_TIMESTAMP,
                        'metric': (
                            'taximeter_balance_changes.payment_counts.'
                            'compensation_refund'
                        ),
                        'value': 0
                    }
                },
                {
                    'args': (),
                    'kwargs': {
                        'stamp': EXPECTED_METRIC_TIMESTAMP,
                        'metric': (
                            'taximeter_balance_changes.payment_counts.resize'
                        ),
                        'value': 9
                    }
                },
                {
                    'args': (),
                    'kwargs': {
                        'stamp': EXPECTED_METRIC_TIMESTAMP,
                        'metric': (
                            'taximeter_balance_changes.payment_counts.corp'
                        ),
                        'value': 21
                    }
                },
                {
                    'args': (),
                    'kwargs': {
                        'stamp': EXPECTED_METRIC_TIMESTAMP,
                        'metric': (
                            'taximeter_balance_changes.payment_counts.card'
                        ),
                        'value': 719
                    }
                },
                {
                    'args': (),
                    'kwargs': {
                        'stamp': EXPECTED_METRIC_TIMESTAMP,
                        'metric': (
                            'taximeter_balance_changes.payment_counts.__total__'
                        ),
                        'value': 846
                    }
                },
                {
                    'args': (),
                    'kwargs': {
                        'stamp': EXPECTED_METRIC_TIMESTAMP,
                        'metric': (
                            'taximeter_balance_changes.error_counts.'
                            'currency_mismatch'
                        ),
                        'value': 2
                    }
                },
                {
                    'args': (),
                    'kwargs': {
                        'stamp': EXPECTED_METRIC_TIMESTAMP,
                        'metric': (
                            'taximeter_balance_changes.error_counts.'
                            'multiple_changes'
                        ),
                        'value': 3
                    }
                },
                {
                    'args': (),
                    'kwargs': {
                        'stamp': EXPECTED_METRIC_TIMESTAMP,
                        'metric': (
                            'taximeter_balance_changes.error_counts.__total__'
                        ),
                        'value': 5
                    }
                },
            ],
    ]
)
@pytest.inline_callbacks
def test_do_stuff(patch, expected_send_taxi_cluster_metric_calls):
    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    @async.inline_callbacks
    def send_taxi_cluster_metric(*args, **kwargs):
        yield async.return_value()

    yield update_taximeter_balance_changes_metrics.do_stuff(
        cron_start_time=CRON_START_TIME
    )
    _check_calls(
        send_taxi_cluster_metric.calls,
        expected_send_taxi_cluster_metric_calls
    )


def _check_calls(calls, expected_calls):
    def sort_key(call):
        return call['kwargs']['metric']
    assert sorted(calls, key=sort_key) == sorted(expected_calls, key=sort_key)
