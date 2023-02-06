# coding: utf-8
from __future__ import unicode_literals

import pytest

from taxi.external import yt_wrapper
from taxi_maintenance.stuff import (
    antifraud_replicate_personal_subvention_frauders as
    personal_subvention_frauders
)
from taxi.conf import settings


class DummyYtClient(object):
    def __init__(self, path, rows=None):
        if rows is None:
            rows = []
        self.path = path
        self.rows = rows

    def remove(self, path, recursive=False, force=False):
        assert recursive is False
        assert force is True
        assert path == self.path
        return True

    def create_table(self, path, recursive=None, attributes=None):
        assert path == self.path
        assert recursive is True
        assert 'schema' in attributes
        return True

    def write_table(self, path, input_stream, format=None, raw=None):
        assert path == self.path
        assert format == yt_wrapper.YSON
        assert raw is False
        input_rows = list(input_stream)
        assert sorted(input_rows) == sorted(self.rows)
        return True


_YT_PERSONAL_SUBVENTION_FRAUDER_ROWS = [
    {
        "license": "36BB016083",
        "day_ride_count": [1, 2, 3],
        "day_ride_count_days": 1,
        "rule_id": "",
        "found": False,
        "frauder": False,
        "rule_ids": [],
        "test_rule_ids": [],
    },
    {
        "license": "AK000012769",
        "day_ride_count": [5, 6, 7, 8],
        "day_ride_count_days": 15,
        "rule_id": "simple",
        "found": True,
        "frauder": True,
        "rule_ids": ["simple", "complicated"],
        "test_rule_ids": [],
    },
]


@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2016-07-01T12:33:44')
@pytest.mark.filldb(cron_jobs='empty')
@pytest.inline_callbacks
def test_replicate_personal_subvention_frauders_raise(monkeypatch):
    monkeypatch.setattr(
        'taxi.external.yt_wrapper.hahn_fraud',
        DummyYtClient(
            'logs/{}/personal_subvention_frauders/2016-07-01'.format(
                settings.YT_CONFIG_ENV_PREFIX
            ),
            _YT_PERSONAL_SUBVENTION_FRAUDER_ROWS,
        )
    )
    try:
        yield personal_subvention_frauders.replicate_personal_subvention_frauders()
    except personal_subvention_frauders.EarlyStartError:
        pass
    else:
        assert False, (
            'exception must be raised if update_day_ride not '
            'found in cron_jobs for current day'
        )


@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2016-07-01T12:33:44')
@pytest.inline_callbacks
def test_replicate_personal_subvention_frauders(monkeypatch):
    monkeypatch.setattr(
        'taxi.external.yt_wrapper.hahn_fraud',
        DummyYtClient(
            'logs/{}/personal_subvention_frauders/2016-07-01'.format(
                settings.YT_CONFIG_ENV_PREFIX
            ),
            _YT_PERSONAL_SUBVENTION_FRAUDER_ROWS,
        )
    )
    yield personal_subvention_frauders.replicate_personal_subvention_frauders()
