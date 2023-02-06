from django import test
from l3abc import models as abc_models
from .. import metrics
from ... import models as mgr_models


class MetricsGauge:
    def __init__(self):
        self.store = {}

    def __call__(self, key):
        self.key = key
        self.store[self.key] = 0
        return self

    def set(self, value):
        self.store[self.key] = value

    def validate(self, key, value):
        return key in self.store and self.store[key] == value

    def metrics_count(self):
        return len(self.store.keys())


class MissingABCMetricsTest(test.TransactionTestCase):
    def setUp(self) -> None:
        self.mg = MetricsGauge()
        abc_models.ABCService.objects.create(abc_slug="abcA", abc_id=1)
        abc_models.ABCService.objects.create(abc_slug="abcB", abc_id=2)

        mgr_models.Service.objects.create(fqdn="lb-1a.abc.yandex.test", abc="abcA")
        mgr_models.Service.objects.create(fqdn="lb-1b.abc.yandex.test", abc="abcB")

    def test_metrics_stub(self) -> None:
        self.mg("key").set(33)
        self.assertTrue(self.mg.validate("key", value=33), "Metrics are not stored")
        self.assertFalse(self.mg.validate("key", value=34), "Wrong value is stored for metric")
        self.assertFalse(self.mg.validate("key2", value=33), "Any non-existent metric seems to be stored")

    def test_no_missing_abc(self) -> None:
        metrics._services_missing_abc(self.mg)
        self.assertEqual(self.mg.metrics_count(), 0, "Found wrong missing abc slugs, there should be none")

    def test_missing_abc(self) -> None:
        mgr_models.Service.objects.create(fqdn="lb-1c.abc.yandex.test", abc="abcC")
        metrics._services_missing_abc(self.mg)
        self.assertTrue(self.mg.validate("abcC", 1), "Failed to find that only one service with missing abc found")
        self.assertEqual(self.mg.metrics_count(), 1, "Not only missing abc found")

    def test_archived_services(self) -> None:
        mgr_models.Service.objects.create(fqdn="lb-1c.abc.yandex.test", archive=True, abc="abcC")
        metrics._services_missing_abc(self.mg)
        self.assertEqual(self.mg.metrics_count(), 0, "Found wrong missing abc slugs, there should be none")

    def test_complex_states_services(self) -> None:
        mgr_models.Service.objects.create(fqdn="lb-1c.abc.yandex.test", archive=True, abc="abcC")
        mgr_models.Service.objects.create(fqdn="lb-2c.abc.yandex.test", abc="abcC")
        mgr_models.Service.objects.create(fqdn="lb-3c.abc.yandex.test", abc="abcC")
        mgr_models.Service.objects.create(fqdn="lb-1d.abc.yandex.test", abc="abcD")
        metrics._services_missing_abc(self.mg)
        self.assertEqual(self.mg.metrics_count(), 2, "Found wrong missing abc slugs, there should be two")
        self.assertTrue(self.mg.validate("abcC", 2), "Should be two services, as one abcC is archived")
        self.assertTrue(self.mg.validate("abcD", 1), "Should be one abcD service")
