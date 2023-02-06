from unittest import SkipTest
from unittest.mock import patch, Mock
from django.test import SimpleTestCase
from l3metrics.tvm.reporter import _TvmReporter


class MockTVM:
    code = 2
    last_error = "Error"

    @property
    def client_state(self):
        return self


class MockMetric:
    stored = None

    def set(self, value):
        self.stored = value


class EndWhileLoop(Exception):
    pass


_TvmReporter.LOCK_FILE = "/home/ttmgmt/test-tvm-metrics-reporter.lock"


@SkipTest
class TestTvmMetricsThinner(SimpleTestCase):
    @patch("l3metrics.tvm.reporter.sleep", Mock(side_effect=[True, EndWhileLoop("Stop test")]))
    @patch("l3metrics.tvm.reporter.TvmAuthenticator", new_callable=lambda *args: MockTVM)
    def test_metric_collected(self, mock_tvm):
        with self.assertRaises(EndWhileLoop):
            reporter = _TvmReporter()
            metric = MockMetric()
            reporter.run(metric)

            self.assertEqual(MockTVM.code, metric.stored)

    @patch("l3metrics.tvm.reporter.sleep", Mock(side_effect=[True, EndWhileLoop("Stop test")]))
    @patch("l3metrics.tvm.reporter.TvmAuthenticator", Mock(side_effect=Exception("Exception test case")))
    def test_tvm_exception(self):
        with self.assertRaises(EndWhileLoop):
            reporter = _TvmReporter()
            metric = MockMetric()
            reporter.run(metric)

            self.assertEqual(_TvmReporter.STATUS_NOT_AVAILABLE, metric.stored)
