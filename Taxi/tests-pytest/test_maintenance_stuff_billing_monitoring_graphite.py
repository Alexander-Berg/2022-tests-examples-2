import pytest

import taxi.internal.billing_monitor
from taxi_maintenance.stuff import billing_monitoring_graphite
from taxi.conf import settings


@pytest.mark.now('2017-09-12 10:00:33.123+03')
@pytest.inline_callbacks
def test_do_stuff(patch):
    metrics_sent = {}

    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    def send_taxi_cluster_metric(metric, value, stamp):
        metrics_sent[metric] = stamp, value

    yield billing_monitoring_graphite.do_stuff()

    assert len(metrics_sent) == (
        len(taxi.internal.billing_monitor.METHODS) *
        len(taxi.internal.billing_monitor.STAT_TYPES) *
        len(settings.BILLINGS) +
        1  # pending_transactions
    )
    nonzero_metrics = {
        'billing.trust.services.card.methods.CreateBasket.rps.success': (
            1505199540.0, 0.1
        ),
        'billing.trust.services.card.methods.UpdateBasket.rps.limited': (
            1505199540.0, 0.05
        ),
        'billing.trust.services.card.methods.UpdateBasket.rps.success': (
            1505199540.0, 0.2
        ),
        'billing.trust.services.donate.methods.PayBasket.rps.limited': (
            1505199540.0, 0.05
        ),
        'billing.trust.services.donate.methods.PayBasket.rps.success': (
            1505199540.0, 0.3
        ),
        'billing.fallback.pending_transactions': (
            1505199633.0, 0
        ),
    }
    for metric, value in metrics_sent.iteritems():
        if metric in nonzero_metrics:
            assert value == nonzero_metrics[metric], metric
        else:
            assert value == (1505199540.0, 0.0), metric
