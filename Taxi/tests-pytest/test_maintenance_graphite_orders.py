import datetime
import logging
import pytest

from taxi.core import async
from taxi.core import db
from taxi.core import devreplica
from taxi.core.arequests._common import Response

from taxi_maintenance.stuff import graphite_orders


logging.basicConfig(level=logging.INFO)


APPLICATION_MAP_BRAND_DEFAULT = {
    '__default__': 'yataxi',
    'android': 'yataxi',
    'iphone': 'yataxi',
    'uber_android': 'yauber',
    'uber_iphone': 'yauber',
    'yango_android': 'yango',
    'yango_iphone': 'yango',
    'vezet_android': 'vezet',
    'vezet_iphone': 'vezet',
    'rutaxi_android': 'rutaxi',
    'rutaxi_iphone': 'rutaxi',
    'callcenter': 'yataxi',
    'vezet_call_center': 'vezet',
}


METRICS_TIMESTAMP = ts = 1546337220
CORRECT_METRICS_VALUES = set([
    # global metrics
    ('orders.drafts', 1, ts),
    ('orders.fallbacks', 1, ts),
    # all orders
    ('orders.allcities.exact.total', 1, ts),
    ('orders.allcities.urgent.total', 1, ts),
    ('orders.allcities.soon.total', 10, ts),
    ('orders.allcities.soon.found', 2, ts),
    ('orders.allcities.soon.found_percent', 20.0, ts),
    ('orders.allcities.soon.user_fraud', 1, ts),
    ('orders.allcities.soon.user_fraud_percent', 10.0, ts),
    # by source
    ('orders.yandex.allcities.exact.total', 1, ts),
    ('orders.yandex.allcities.urgent.total', 1, ts),
    ('orders.yandex.allcities.soon.total', 8, ts),
    ('orders.yandex.allcities.soon.found', 2, ts),
    ('orders.yandex.allcities.soon.found_percent', 25.0, ts),
    ('orders.yandex.allcities.soon.user_fraud', 1, ts),
    ('orders.yandex.allcities.soon.user_fraud_percent', 13.0, ts),
    #
    ('orders.yauber.allcities.soon.total', 2, ts),
    # by brand
    ('orders.brand_yataxi.allcities.exact.total', 1, ts),
    ('orders.brand_yataxi.allcities.urgent.total', 1, ts),
    ('orders.brand_yataxi.allcities.soon.total', 5, ts),
    ('orders.brand_yataxi.allcities.soon.found', 1, ts),
    ('orders.brand_yataxi.allcities.soon.found_percent', 20.0, ts),
    ('orders.brand_yataxi.allcities.soon.user_fraud', 1, ts),
    ('orders.brand_yataxi.allcities.soon.user_fraud_percent', 20.0, ts),
    #
    ('orders.brand_yauber.allcities.soon.total', 1, ts),
    #
    ('orders.brand_yango.allcities.soon.total', 1, ts),
    ('orders.brand_yango.allcities.soon.found', 1, ts),
    ('orders.brand_yango.allcities.soon.found_percent', 100.0, ts),
    #
    ('orders.brand_vezet.allcities.soon.total', 2, ts),
    ('orders.brand_rutaxi.allcities.soon.total', 1, ts),
    # detailed apps
    ('orders.callcenter.allcities.soon.total', 1, ts),
    ('orders.vezet_call_center.allcities.soon.total', 1, ts),
])


@pytest.mark.now('2019-01-01T10:09:08')
@pytest.mark.config(
    APPLICATION_MAP_BRAND=APPLICATION_MAP_BRAND_DEFAULT,
    ORDERS_METRICS_DETAILED_APPS=[
        'callcenter',
        'vezet_call_center',
    ],
)
@pytest.inline_callbacks
def test_created_do_stuff_graphite(monkeypatch, patch):
    test_metrics = []

    monkeypatch.setattr(devreplica, 'order_proc', db.order_proc)

    @patch('taxi.util.graphite.send_cluster_metric')
    def send_cluster_metric(metric, value, stamp):
        # percent metrics are difficult to compare in test
        # since they are decimal numbers, so we just round them
        if metric.endswith('_percent'):
            value = round(value)
        test_metrics.append((metric, value, stamp))

    yield graphite_orders.do_stuff(datetime.datetime.utcnow())

    assert set(test_metrics) == CORRECT_METRICS_VALUES


def _solomon_labels_to_graphite_metric_name(labels):
    graphite_metric_name = 'orders'

    labels_order = [
        'source', 'brand', 'order_application', 'city', 'order_type', 'sensor',
    ]

    for label in labels_order:
        if label in labels:
            label_value = labels[label]

            if label == 'brand':
                label_value = 'brand_' + label_value
            elif label == 'sensor':
                value_start = len('orders_')
                label_value = label_value[value_start:]

            graphite_metric_name += '.%s' % label_value

    return graphite_metric_name


@pytest.mark.parametrize('solomon_labels, graphite_metric_name', [
    (
        {'sensor': 'orders_drafts'},
        'orders.drafts',
    ),
    (
        {
            'sensor': 'orders_total',
            'source': 'yauber',
        },
        'orders.yauber.total',
    ),
    (
        {
            'sensor': 'orders_total',
            'brand': 'yataxi',
        },
        'orders.brand_yataxi.total',
    ),
    (
        {
            'sensor': 'orders_total',
            'order_application': 'callcenter',
        },
        'orders.callcenter.total',
    ),
    (
        {
            'sensor': 'orders_total',
            'brand': 'yataxi',
            'city': 'allcities',
        },
        'orders.brand_yataxi.allcities.total',
    ),
    (
        {
            'sensor': 'orders_total',
            'brand': 'yataxi',
            'city': 'allcities',
            'order_type': 'soon',
        },
        'orders.brand_yataxi.allcities.soon.total',
    ),
])
def test_solomon_labels_to_graphite_metric_name(solomon_labels,
                                                graphite_metric_name):
    assert (
        _solomon_labels_to_graphite_metric_name(solomon_labels) ==
        graphite_metric_name
    )


@pytest.mark.now('2019-01-01T10:09:08')
@pytest.mark.config(
    APPLICATION_MAP_BRAND=APPLICATION_MAP_BRAND_DEFAULT,
    ORDERS_METRICS_DETAILED_APPS=[
        'callcenter',
        'vezet_call_center',
    ],
    ORDERS_METRICS_SEND_TO_SOLOMON_ENABLED=True,
    ORDERS_METRICS_SOLOMON_SERVICE_NAME='order_stats',
)
@pytest.inline_callbacks
def test_created_do_stuff_solomon(monkeypatch, patch):
    test_metrics = []

    monkeypatch.setattr(devreplica, 'order_proc', db.order_proc)

    @patch('taxi.core.arequests.post')
    @async.inline_callbacks
    def post_request(
        url=None, json=None, **kwargs
    ):
        yield
        assert url == 'http://127.0.0.1:4400/order_stats'

        assert 'sensors' in json

        for sensor in json['sensors']:
            labels = sensor['labels']
            value = sensor['value']
            ts = sensor['ts']

            # percent metrics are difficult to compare in test
            # since they are decimal numbers, so we just round them
            if labels['sensor'].endswith('_percent'):
                value = round(value)

            graphite_metric_name = _solomon_labels_to_graphite_metric_name(
                labels
            )

            test_metrics.append((graphite_metric_name, value, ts))

        async.return_value(Response(status_code=200))

    yield graphite_orders.do_stuff(datetime.datetime.utcnow())

    assert set(test_metrics) == CORRECT_METRICS_VALUES
