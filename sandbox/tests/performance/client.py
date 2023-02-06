import pytest

from sandbox.serviceq.tests.performance import common as perf_common

from sandbox.serviceq.tests.client import utils


@pytest.mark.serviceq_perf
class TestPerformance(perf_common.BaseTestPerformance):
    @staticmethod
    def _collect_garbage(qapi):
        pass

    def test__performance_client(self, serviceq):
        super(TestPerformance, self).run_test(serviceq, utils)
