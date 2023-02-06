# coding: utf-8
from __future__ import unicode_literals

import pytest

from taxi.external import yt_wrapper
from taxi_maintenance.stuff import (
    antifraud_replicate_subvention_frauders as
    subvention_frauders
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


_YT_SUBVENTION_FRAUDER_ROWS = [
    {
        'order_id': '90deecdda3bc4c0f8542e26ef2074d0a',
        'license': '0712066735',
        'rule_id': 'subv_ratio_ban_rule',
        'hold': False,
        'found': True,
        'frauder': True,
        'confidence': 10111,
        'rule_ids': [
            'subv_ratio_ban_rule',
        ],
        'test_rule_ids': [],
    },
    {
        'order_id': 'b92da458d7d24896be1284edba1c7954',
        'license': '07KБ309143',
        'rule_id': 'rule1',
        'hold': True,
        'found': True,
        'frauder': False,
        'confidence': 0,
        'rule_ids': [
            'rule1',
            'rule2',
        ],
        'test_rule_ids': [
            'test_rule1',
        ],
    },
]


@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2016-07-01T12:33:44')
@pytest.mark.filldb(cron_jobs='empty')
@pytest.inline_callbacks
def test_replicate_subvention_frauders_raise(monkeypatch):
    monkeypatch.setattr(
        'taxi.external.yt_wrapper.hahn_fraud',
        DummyYtClient(
            'logs/{}/subvention_frauders/2016-07-01'.format(
                settings.YT_CONFIG_ENV_PREFIX
            ),
            _YT_SUBVENTION_FRAUDER_ROWS,
        )
    )
    try:
        yield subvention_frauders.replicate_subvention_frauders()
    except subvention_frauders.EarlyStartError:
        pass
    else:
        assert False, (
            'exception must be raised if depends jobs not '
            'found in cron_jobs for current day'
        )


@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2016-07-01T12:33:44')
@pytest.inline_callbacks
def test_replicate_subvention_frauders(monkeypatch):
    monkeypatch.setattr(
        'taxi.external.yt_wrapper.hahn_fraud',
        DummyYtClient(
            'logs/{}/subvention_frauders/2016-07-01'.format(
                settings.YT_CONFIG_ENV_PREFIX
            ),
            _YT_SUBVENTION_FRAUDER_ROWS,
        )
    )
    yield subvention_frauders.replicate_subvention_frauders()
