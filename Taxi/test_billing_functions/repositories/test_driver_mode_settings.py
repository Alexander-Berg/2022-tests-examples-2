import datetime as dt

import pytest


def test_raises_if_no_key(stq3_context):
    timestamp = dt.datetime(2021, 4, 23, tzinfo=dt.timezone.utc)
    repo = stq3_context.driver_mode_settings
    with pytest.raises(KeyError):
        repo.fetch_tags('non_existing_mode_rule', timestamp)


def test_raises_if_no_settings_for_ts(stq3_context):
    timestamp = dt.datetime(2021, 4, 19, tzinfo=dt.timezone.utc)
    with pytest.raises(KeyError):
        stq3_context.driver_mode_settings.fetch_tags('mode_rule1', timestamp)


def test_chooses_correct_value(stq3_context):
    timestamp = dt.datetime(2021, 4, 21, tzinfo=dt.timezone.utc)
    repo = stq3_context.driver_mode_settings
    assert repo.fetch_tags('mode_rule1', timestamp) == ['t2']
