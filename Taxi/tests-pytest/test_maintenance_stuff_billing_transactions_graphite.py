import pytest

import taxi.internal.billing_transactions
from taxi_maintenance.stuff import billing_transactions_graphite
from taxi.conf import settings


@pytest.mark.now('2017-09-12 10:00:33.123+03')
@pytest.inline_callbacks
def test_do_stuff(patch):
    metrics_sent = {}

    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    def send_taxi_cluster_metric(metric, value, stamp):
        metrics_sent[metric] = stamp, value

    yield billing_transactions_graphite.do_stuff()

    assert len(metrics_sent) == (
        len(taxi.internal.billing_transactions.STAT_TYPES) *
        len(settings.BILLINGS) +
        3  # arbitrary resp_codes from fixtures
    )

    nonzero_metrics = {
        'billing.trust.services.card.transactions.rps.success': (
            1505199540.0, 0.3
        ),
        'billing.trust.services.card.transactions.rps.technical_error': (
            1505199540.0, 0.1
        ),
        'billing.trust.services.card.transactions.rps.hold_fail': (
            1505199540.0, 0.2
        ),
        'billing.trust.services.donate.transactions.rps.success': (
            1505199540.0, 0.1
        ),
        'billing.trust.services.card.transactions.resp_codes.payment_gateway_technical_error': (
            1505199540.0, 0.1
        ),
        'billing.trust.services.card.transactions.resp_codes.expired_card': (
            1505199540.0, 0.15
        ),
        'billing.trust.services.card.transactions.resp_codes.unknown_error': (
            1505199540.0, 0.05
        ),
    }

    for metric, value in metrics_sent.iteritems():
        if metric in nonzero_metrics:
            assert value == nonzero_metrics[metric], metric
        else:
            assert value == (1505199540.0, 0.0), metric
