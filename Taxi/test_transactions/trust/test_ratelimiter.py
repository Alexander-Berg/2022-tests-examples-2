# pylint: disable=redefined-outer-name
import pytest

from transactions.clients.trust import ratelimiter


class DummyMetrics:
    def __init__(self, rps=None):
        self._rps = {}
        if rps is not None:
            for key, value in rps.items():
                self._rps[key.replace('.', '_')] = value

    def calc_rps_for(self, metric, period):
        assert period == 60
        metric = metric.replace('.', '_')
        return self._rps.get(metric, 0.0)


@pytest.fixture
def config():
    class Config:
        TRANSACTIONS_TRUST_RATELIMIT_RULES = {
            'testsuite_methods_foo': 10,
            'testsuite_methods_maurice': 30,
        }

    return Config


@pytest.mark.nofilldb
def test_get_ratelimit_for(config):
    limiter = ratelimiter.RateLimiter(DummyMetrics(), config)
    assert limiter.get_ratelimit_for('testsuite.methods.foo') == 10
    assert limiter.get_ratelimit_for('testsuite.methods_maurice') == 30
    assert limiter.get_ratelimit_for('testsuite.methods.bar') is None


@pytest.mark.nofilldb
def test_ratelimit(config):
    metrics = DummyMetrics(
        {'testsuite.methods.foo': 1, 'testsuite.methods.maurice': 30},
    )
    limiter = ratelimiter.RateLimiter(metrics, config)
    assert limiter.ratelimit('testsuite.methods.foo') is True
    assert limiter.ratelimit('testsuite.methods.maurice') is False
    assert limiter.ratelimit('testsuite.methods.bar') is True
