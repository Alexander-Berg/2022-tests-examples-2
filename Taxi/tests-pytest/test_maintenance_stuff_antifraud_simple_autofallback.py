import datetime
import pytest

from taxi.core import async
from taxi.core import db
from taxi_maintenance.stuff import antifraud_simple_autofallback

_RULES = ['bad_rule1', 'bad_rule2', 'bad_rule3']


def _make_rules(updated_rules=None, rules=None):
    now = datetime.datetime.utcnow()
    return sorted([
        {
            '_id': rule,
            'enabled': False,
            'updated': now,
        }
        for rule in (updated_rules if updated_rules else [])
    ] + [
        {
            '_id': rule,
            'enabled': True,
        }
        for rule in (rules if rules else [])
    ])


@pytest.inline_callbacks
def _rules_from_db():
    async.return_value(
        sorted(
            (yield db.antifraud_rules.find().run())
        )
    )


@pytest.inline_callbacks
def _all_off():
    yield _simple_test(updated_rules=_RULES)


@pytest.inline_callbacks
def _all_on():
    yield _simple_test(rules=_RULES)


@pytest.inline_callbacks
def _simple_test(updated_rules=None, rules=None):
    yield antifraud_simple_autofallback._autofallback()
    assert _make_rules(updated_rules, rules) == (yield _rules_from_db())


@pytest.mark.now('2019-10-01T09:25:37')
@pytest.mark.config(
    AFS_SIMPLE_AUTOFALLBACK_ENABLED=True,
    AFS_SIMPLE_AUTOFALLBACK_SETTINGS={
        '__default__': 0.15,
        'antifake': 0.05,
    },
)
@pytest.inline_callbacks
def test_replicate_subvention_frauders_base1():
    yield _all_off()


@pytest.mark.now('2019-10-01T09:25:37')
@pytest.mark.config(
    AFS_SIMPLE_AUTOFALLBACK_ENABLED=False,
    AFS_SIMPLE_AUTOFALLBACK_SETTINGS={
        '__default__': 0.15,
        'antifake': 0.05,
    },
)
@pytest.inline_callbacks
def test_replicate_subvention_frauders_disabled():
    yield _all_on


@pytest.mark.now('2019-10-01T09:25:37')
@pytest.mark.config(
    AFS_SIMPLE_AUTOFALLBACK_ENABLED=True,
    AFS_SIMPLE_AUTOFALLBACK_SETTINGS={
        '__default__': 0.15,
        'antifake': 0.057,
    },
)
@pytest.inline_callbacks
def test_replicate_subvention_frauders_base2():
    yield _simple_test(['bad_rule2', 'bad_rule3'], ['bad_rule1'])


@pytest.mark.now('2019-10-01T09:25:37')
@pytest.mark.config(
    AFS_SIMPLE_AUTOFALLBACK_ENABLED=True,
    AFS_SIMPLE_AUTOFALLBACK_SETTINGS={
        '__default__': 0.15,
    },
)
@pytest.inline_callbacks
def test_replicate_subvention_frauders_default():
    yield _simple_test(['bad_rule3'], ['bad_rule1', 'bad_rule2'])


@pytest.mark.now('2019-10-01T09:26:00')
@pytest.mark.config(
    AFS_SIMPLE_AUTOFALLBACK_ENABLED=True,
    AFS_SIMPLE_AUTOFALLBACK_SETTINGS={
        '__default__': 0.15,
        'antifake': 0.05,
    },
)
@pytest.inline_callbacks
def test_replicate_subvention_frauders_no_rule_ids():
    yield _all_on()


@pytest.mark.now('2019-10-01T09:27:00')
@pytest.mark.config(
    AFS_SIMPLE_AUTOFALLBACK_ENABLED=True,
    AFS_SIMPLE_AUTOFALLBACK_SETTINGS={
        '__default__': 0.15,
        'antifake': 0.05,
    },
)
@pytest.inline_callbacks
def test_replicate_subvention_frauders_small_triggered1():
    yield _simple_test(['bad_rule1'], ['bad_rule2', 'bad_rule3'])


@pytest.mark.now('2019-10-01T09:28:00')
@pytest.mark.config(
    AFS_SIMPLE_AUTOFALLBACK_ENABLED=True,
    AFS_SIMPLE_AUTOFALLBACK_SETTINGS={
        '__default__': 0.15,
        'antifake': 0.05,
    },
)
@pytest.inline_callbacks
def test_replicate_subvention_frauders_small_triggered2():
    yield _all_on()
