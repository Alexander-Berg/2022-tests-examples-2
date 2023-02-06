from datetime import datetime, timedelta

import pytest

from sandbox.projects.yabs.qa.tasks.YabsServerUploadShootResultToYt import get_ttl_with_respect_to_weekends


@pytest.mark.parametrize(
    ('now', 'ttl_days', 'expected_ttl_days'), (
        pytest.param(datetime(year=2022, month=4, day=15, hour=1), 0, 0, id='Friday, expires immediately'),
        pytest.param(datetime(year=2022, month=4, day=15, hour=1), 1, 3, id='Friday, expires on Saturday, should prolongate ttl'),
        pytest.param(datetime(year=2022, month=4, day=11, hour=1), 4, 4, id='Monday, expires on Friday, shouldn\'t prolongate ttl'),
        pytest.param(datetime(year=2022, month=4, day=13, hour=1), 5, 7, id='Wednesday, expires on next Monday, should prolongate ttl'),
        pytest.param(datetime(year=2022, month=4, day=16, hour=1), 4, 5, id='Saturday, expires on next Wednesday, should prolongate ttl'),
    ),
)
def test_get_ttl_with_respect_to_weekends(now, ttl_days, expected_ttl_days):
    assert timedelta(days=expected_ttl_days) == timedelta(seconds=get_ttl_with_respect_to_weekends(now, ttl_days))
