import pytest

from taxi.internal.dbh import trustable_tlogs


@pytest.mark.config(BILLING_USE_TLOG_FOR_DONATIONS={})
@pytest.inline_callbacks
def test_use_tlog_use_trust_with_default_config():
    result = yield trustable_tlogs.use_tlog('1')
    assert result is False


@pytest.mark.config(BILLING_USE_TLOG_FOR_DONATIONS={
    'park_id_regex': '^1$'
})
@pytest.inline_callbacks
def test_use_tlog_regex():
    result = yield trustable_tlogs.use_tlog('1')
    assert result is True
    result = yield trustable_tlogs.use_tlog('2')
    assert result is False


@pytest.mark.config(BILLING_USE_TLOG_FOR_DONATIONS={
    'rollout_percentage': 100
})
@pytest.inline_callbacks
def test_use_tlog_percentage_100():
    for i in xrange(0, 1000):
        result = yield trustable_tlogs.use_tlog(str(i))
        assert result is True


@pytest.mark.config(BILLING_USE_TLOG_FOR_DONATIONS={
    'rollout_percentage': 99
})
@pytest.inline_callbacks
def test_use_tlog_percentage_99():
    counter = 0
    for i in xrange(0, 1000):
        result = yield trustable_tlogs.use_tlog(str(i))
        if not result:
            counter += 1
    assert 0 < counter < 15


@pytest.mark.config(BILLING_USE_TLOG_FOR_DONATIONS={
    'rollout_percentage': 0
})
@pytest.inline_callbacks
def test_use_tlog_percentage_0():
    for i in xrange(0, 1000):
        result = yield trustable_tlogs.use_tlog(str(i))
        assert result is False


@pytest.mark.config(BILLING_USE_TLOG_FOR_DONATIONS={
    'rollout_percentage': 1
})
@pytest.inline_callbacks
def test_use_tlog_percentage_1():
    counter = 0
    for i in xrange(0, 1000):
        result = yield trustable_tlogs.use_tlog(str(i))
        if result:
            counter += 1
    assert 0 < counter < 15


@pytest.mark.config(BILLING_USE_TLOG_FOR_DONATIONS={
    'rollout_percentage': 50
})
@pytest.inline_callbacks
def test_use_tlog_percentage_50():
    counter = 0
    for i in xrange(0, 1000):
        result = yield trustable_tlogs.use_tlog(str(i))
        if result:
            counter += 1
    assert 450 < counter < 550


@pytest.mark.config(BILLING_USE_TLOG_FOR_DONATIONS={
    'park_id_regex': '.*',
    'rollout_percentage': 0
})
@pytest.inline_callbacks
def test_use_tlog_percentage_has_higher_priority():
    result = yield trustable_tlogs.use_tlog('1')
    assert result is False
