import datetime
import logging
import pytest

from taxi.core import db
from taxi.core import devreplica

from taxi_maintenance.stuff.order_proc_statistics.metrics import created
from taxi_maintenance.stuff.order_proc_statistics.metrics import active
from taxi_maintenance.stuff.order_proc_statistics.metrics import finished


logging.basicConfig(level=logging.INFO)


@pytest.mark.now('2019-01-01T10:09:08')
@pytest.inline_callbacks
@pytest.mark.config(
    CREATED_ORDERS_METRICS_CLASSES_ENABLED=['vip', 'econom', 'express'],
    CREATED_ORDERS_METRICS_SOURCES_ENABLED=['alice', 'call_center'],
    CREATED_ORDERS_METRICS_PRICE_MODIFIERS_SOURCES=['alice'],
    ORDERS_METRICS_APPLICATIONS_ENABLED=['turboapp'],
)
def test_created_do_stuff(monkeypatch, patch):
    test_metrics = []

    monkeypatch.setattr(devreplica, 'order_proc', db.order_proc)

    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    def send_cluster_metric(metric, value, stamp):
        test_metrics.append((metric, value, stamp))

    # to be sure, that anyone who added new collector - knows about tests here
    assert len(created.graphite._REGISTERED_COLLECTORS) == 9

    yield created.do_stuff(datetime.datetime.utcnow())

    ts = 1546337348
    assert set(test_metrics) == {
        # multiorder metrics
        ('orders.astana.by_multiorder_order_number.num_1', 1, ts),
        ('orders.astana.by_multiorder_order_number.num_3', 1, ts),
        ('orders.moscow.by_multiorder_order_number.num_0', 1, ts),
        ('orders.moscow.by_multiorder_order_number.num_1', 1, ts),
        ('orders.moscow.by_multiorder_order_number.num_2', 2, ts),
        ('orders.allcities.by_multiorder_order_number.num_1', 2, ts),
        ('orders.allcities.by_multiorder_order_number.num_0', 1, ts),
        ('orders.allcities.by_multiorder_order_number.num_2', 2, ts),
        ('orders.allcities.by_multiorder_order_number.num_3', 1, ts),
        # multiclass metrics
        ('orders.astana.multiclass_selected_classes_count.num_2', 1, ts),
        ('orders.astana.multiclass_selected_classes_count.num_3', 1, ts),
        ('orders.moscow.multiclass_selected_classes_count.num_2', 1, ts),
        ('orders.moscow.multiclass_selected_classes_count.num_3', 1, ts),
        ('orders.moscow.multiclass_selected_classes_count.num_4', 1, ts),
        ('orders.moscow.multiclass_selected_classes_count.num_5', 1, ts),
        ('orders.allcities.multiclass_selected_classes_count.num_2', 2, ts),
        ('orders.allcities.multiclass_selected_classes_count.num_3', 2, ts),
        ('orders.allcities.multiclass_selected_classes_count.num_4', 1, ts),
        ('orders.allcities.multiclass_selected_classes_count.num_5', 1, ts),
        # delayed metrics
        ('orders.astana.created_delayed_count.num_exacturgent', 1, ts),
        ('orders.allcities.created_delayed_count.num_exacturgent', 1, ts),
        # coop_account metrics
        ('orders.coop_account.created.allcities.count', 1, ts),
        ('orders.coop_account.created.astana.count', 1, ts),
        # all orders metrics
        ('orders.created.count', 21, ts),
        # by classes metrics
        ('orders.moscow.econom', 3, ts),
        ('orders.moscow.vip', 2, ts),
        ('orders.astana.econom', 2, ts),
        ('orders.allcities.vip', 2, ts),
        ('orders.allcities.econom', 5, ts),
        # by source metrics
        ('orders.moscow.source.alice', 2, ts),
        ('orders.astana.source.alice', 1, ts),
        ('orders.astana.source.call_center', 1, ts),
        ('orders.allcities.source.alice', 3, ts),
        ('orders.allcities.source.call_center', 1, ts),
        ('orders.moscow.price_modifier.ya_plus.source.alice', 1, ts),
        ('orders.moscow.price_modifier.mastercard.source.alice', 1, ts),
        ('orders.allcities.price_modifier.ya_plus.source.alice', 1, ts),
        ('orders.allcities.price_modifier.mastercard.source.alice', 1, ts),
        # by application metrics
        ('orders.allcities.application.turboapp.class.express', 1, ts),
    }


@pytest.mark.now('2019-01-01T10:09:08')
@pytest.inline_callbacks
@pytest.mark.config(
    ACTIVE_ORDERS_METRICS_CLASSES_ENABLED=['vip', 'econom'],
    ACTIVE_ORDERS_METRICS_SOURCES_ENABLED=['alice', 'call_center'],
    ACTIVE_ORDERS_METRICS_REQUIREMENTS_ENABLED=['hourly_rental'],
    ORDERS_METRICS_APPLICATIONS_ENABLED=['turboapp'],
)
def test_active_do_stuff(monkeypatch, patch):
    test_metrics = []

    monkeypatch.setattr(devreplica, 'order_proc', db.order_proc)

    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    def send_cluster_metric(metric, value, stamp):
        test_metrics.append((metric, value, stamp))

    # to be sure, that anyone who added new collector - knows about tests here
    assert len(active.graphite._REGISTERED_COLLECTORS) == 7

    yield active.do_stuff(datetime.datetime.utcnow())

    ts = 1546337348
    assert set(test_metrics) == {
        # multiorder metrics
        ('multiorder.active_devices_count', 3, ts),
        # multiclass metrics
        ('multiclass.active_orders', 7, ts),
        ('multiclass.assigned.comfort', 1, ts),
        ('multiclass.assigned.econom', 6, ts),
        # coop_account metrics
        ('orders.coop_account.active.all.count', 2, ts),
        ('orders.coop_account.active.debt.count', 1, ts),
        # by classes metrics
        ('by_class.assigned.econom', 6, ts),
        ('by_class.assigned.vip', 1, 1546337348),
        # by source
        ('by_source.assigned.alice', 1, ts),
        ('by_source.assigned.call_center', 1, ts),
        # by requirements
        ('by_requirements.assigned.vip.hourly_rental.1_hours', 1, 1546337348),
        # by applications
        ('by_application.assigned.turboapp', 1, ts),
    }


@pytest.mark.now('2019-01-01T10:09:08')
@pytest.inline_callbacks
def test_finished_do_stuff(monkeypatch, patch):
    test_metrics = []

    monkeypatch.setattr(devreplica, 'order_proc', db.order_proc)

    @patch('taxi.util.graphite.send_taxi_cluster_metric')
    def send_cluster_metric(metric, value, stamp):
        test_metrics.append((metric, value, stamp))

    # to be sure, that anyone who added new collector - knows about tests here
    assert len(finished.graphite._REGISTERED_COLLECTORS) == 1

    yield finished.do_stuff(datetime.datetime.utcnow())

    ts = 1546337348
    assert set(test_metrics) == {
        # delayed metrics
        ('orders.moscow.expired_delayed_count.num_exacturgent', 1, ts),
        ('orders.astana.expired_delayed_count.num_exacturgent', 1, ts),
        ('orders.allcities.expired_delayed_count.num_exacturgent', 2, ts),
    }
