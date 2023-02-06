import pytest

from taxi.conf import settings
from taxi.external import yt_wrapper
from taxi_maintenance.stuff import (
    antifraud_replicate_personal_guarantee_fraud_checks as
    personal_guarantee_fraud_checks
)


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


_YT_PERSONAL_GUARANTEE_FRAUD_CHECKS_ROWS = [
    {
        "license": "36BB016083",
        "total_rides_count": 3,
        "due_period_days": 1,
        "checked": False,
        "frauder": False,
        "frauder_rules": [],
        "frauder_test_rules": [],
    },
    {
        "license": "AK000012769",
        "total_rides_count": 5,
        "due_period_days": 15,
        "checked": True,
        "frauder": True,
        "frauder_rules": ["simple", "complicated"],
        "frauder_test_rules": [],
    },
]


@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2016-07-01T12:33:44')
@pytest.mark.filldb(cron_jobs='empty')
@pytest.inline_callbacks
def test_replicate_personal_guarantee_fraud_checks_raise(monkeypatch):
    monkeypatch.setattr(
        'taxi.external.yt_wrapper.hahn_fraud',
        DummyYtClient(
            '{}/logs/personal_guarantee_fraud_checks/2016-07-01'.format(
                settings.YT_CONFIG_ENV_PREFIX,
            ),
            _YT_PERSONAL_GUARANTEE_FRAUD_CHECKS_ROWS,
        )
    )
    try:
        yield (personal_guarantee_fraud_checks
               .replicate_personal_guarantee_fraud_checks())
    except personal_guarantee_fraud_checks.EarlyStartError:
        pass
    else:
        assert False, (
            'exception must be raised if update_day_ride not '
            'found in cron_jobs for current day'
        )


@pytest.mark.asyncenv('blocking')
@pytest.mark.now('2016-07-01T12:33:44')
@pytest.inline_callbacks
def test_replicate_personal_guarantee_fraud_checks(monkeypatch):
    monkeypatch.setattr(
        'taxi.external.yt_wrapper.hahn_fraud',
        DummyYtClient(
            '{}/logs/personal_guarantee_fraud_checks/2016-07-01'.format(
                settings.YT_CONFIG_ENV_PREFIX,
            ),
            _YT_PERSONAL_GUARANTEE_FRAUD_CHECKS_ROWS,
        )
    )
    yield (personal_guarantee_fraud_checks
           .replicate_personal_guarantee_fraud_checks())
