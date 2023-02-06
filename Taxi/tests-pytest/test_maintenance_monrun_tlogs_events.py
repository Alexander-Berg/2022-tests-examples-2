import pytest

from taxi.core import async
from taxi_maintenance.monrun import main


_CONFIG = {
    '__default__': {
        'warning': 600,  # 10 minutes
        'critical': 3600  # 1 hour
    }
}

_CONFIG_WARN_ONLY = {
    '__default__': {
        'warning': 0,
        'critical': 307584000  # 10 years
    }
}

_CONFIG_CRIT_ONLY = {
    '__default__': {
        'warning': 0,
        'critical': 0
    }
}

_CONFIG_CUSTOMIZED = {
    '__default__': {
        'warning': 600,
        'critical': 3600
    },
    'taximeter_balance_changes': {
        'warning': 10,
        'critical': 307584000  # 10 years
    },
}


@pytest.inline_callbacks
def _get_stats():
    result = yield main.run(['tlogs_events'])
    async.return_value(result)


@pytest.mark.config(TLOGS_EVENTS_DELAY_THRESHOLDS=_CONFIG)
@pytest.mark.now('2018-11-11 00:00:00.000')
@pytest.mark.filldb(event_monitor='empty')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_no_data():
    result = yield _get_stats()
    assert result == '0; OK'


@pytest.mark.config(TLOGS_EVENTS_DELAY_THRESHOLDS=_CONFIG)
@pytest.mark.now('2018-11-11 00:00:00.000')
@pytest.mark.filldb(event_monitor='allok')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_allok_gmt():
    result = yield _get_stats()
    assert result == '0; OK'


@pytest.mark.config(TLOGS_EVENTS_DELAY_THRESHOLDS=_CONFIG)
@pytest.mark.now('2018-11-11 03:00:00.000+03')
@pytest.mark.filldb(event_monitor='allok')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_allok_msk():
    result = yield _get_stats()
    assert result == '0; OK'


@pytest.mark.config(TLOGS_EVENTS_DELAY_THRESHOLDS=_CONFIG)
@pytest.mark.now('2018-11-11 00:10:00.000')
@pytest.mark.filldb(event_monitor='allok')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_allwarn():
    result = yield _get_stats()
    assert result == '1; WARN (4 problems): ' \
                     'taximeter_balance_changes[0/4]:630, ' \
                     'taximeter_balance_changes[1/4]:630, ' \
                     'taximeter_balance_changes[2/4]:630, ' \
                     'taximeter_balance_changes[3/4]:630'


@pytest.mark.config(TLOGS_EVENTS_DELAY_THRESHOLDS=_CONFIG)
@pytest.mark.now('2018-11-11 01:00:00.000')
@pytest.mark.filldb(event_monitor='allok')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_allcrit():
    result = yield _get_stats()
    assert result == '2; CRIT (4 problems): ' \
                     'taximeter_balance_changes[0/4]:3630, ' \
                     'taximeter_balance_changes[1/4]:3630, ' \
                     'taximeter_balance_changes[2/4]:3630, ' \
                     'taximeter_balance_changes[3/4]:3630'


@pytest.mark.config(TLOGS_EVENTS_DELAY_THRESHOLDS=_CONFIG)
@pytest.mark.now('2018-11-11 00:00:00.000')
@pytest.mark.filldb(event_monitor='mixed')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_mixed():
    result = yield _get_stats()
    assert result == '2; CRIT (2 problems): ' \
                     'taximeter_balance_changes[0/4]:7200, ' \
                     'taximeter_balance_changes[1/4]:3600; ' \
                     'WARN (1 problems): ' \
                     'taximeter_balance_changes[2/4]:1800'


@pytest.mark.config(TLOGS_EVENTS_DELAY_THRESHOLDS=_CONFIG_WARN_ONLY)
@pytest.mark.now('2018-11-11 00:00:00.000')
@pytest.mark.filldb(event_monitor='allok')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_config_default_warn_only():
    result = yield _get_stats()
    assert result == '1; WARN (4 problems): ' \
                     'taximeter_balance_changes[0/4]:30, ' \
                     'taximeter_balance_changes[1/4]:30, ' \
                     'taximeter_balance_changes[2/4]:30, ' \
                     'taximeter_balance_changes[3/4]:30'


@pytest.mark.config(TLOGS_EVENTS_DELAY_THRESHOLDS=_CONFIG_CRIT_ONLY)
@pytest.mark.now('2018-11-11 00:00:00.000')
@pytest.mark.filldb(event_monitor='allok')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_config_default_crit_only():
    result = yield _get_stats()
    assert result == '2; CRIT (4 problems): ' \
                     'taximeter_balance_changes[0/4]:30, ' \
                     'taximeter_balance_changes[1/4]:30, ' \
                     'taximeter_balance_changes[2/4]:30, ' \
                     'taximeter_balance_changes[3/4]:30'


@pytest.mark.config(TLOGS_EVENTS_DELAY_THRESHOLDS=_CONFIG_CUSTOMIZED)
@pytest.mark.now('2018-11-11 00:00:00.000')
@pytest.mark.filldb(event_monitor='allok')
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_config_custom_mix():
    result = yield _get_stats()
    assert result == '1; WARN (4 problems): ' \
                     'taximeter_balance_changes[0/4]:30, ' \
                     'taximeter_balance_changes[1/4]:30, ' \
                     'taximeter_balance_changes[2/4]:30, ' \
                     'taximeter_balance_changes[3/4]:30'
