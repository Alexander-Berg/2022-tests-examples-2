import gc

import pytest

from sandbox.common import context

from sandbox.serviceq.tests.server import utils
from sandbox.serviceq.tests.performance import common as perf_common


@pytest.mark.serviceq_perf
class TestPerformance(perf_common.BaseTestPerformance):
    def test__performance_server(self, qserver_with_quotas):
        gc.collect()
        with context.disabled_gc():
            super(TestPerformance, self).run_test(
                qserver_with_quotas, utils, test_snapshot=True, test_encode_decode=True
            )
