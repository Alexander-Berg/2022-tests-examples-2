import datetime as dt

import pytest

from taxi.util import monrun

from taxi_billing_audit.monrun_checks import (
    tlog_payment_requests_check as check,
)

WINDOW = check.Config('05:00', '06:00', 60)

NOW_BEFORE_WINDOW = dt.datetime(2020, 12, 2, 2, tzinfo=check.MSK_TZ)
NOW_INSIDE_WINDOW = dt.datetime(2020, 12, 2, 5, 30, tzinfo=check.MSK_TZ)
NOW_AFTER_WINDOW = dt.datetime(2020, 12, 2, 6, 30, tzinfo=check.MSK_TZ)
NOW_AFTER_CRIT_THRESHOLD = dt.datetime(2020, 12, 2, 7, 30, tzinfo=check.MSK_TZ)

EARLY_REQUESTS = check.Row(dt.datetime(2020, 12, 2, 1, tzinfo=check.MSK_TZ), 1)
NORMAL_REQUESTS = check.Row(
    dt.datetime(2020, 12, 2, 5, tzinfo=check.MSK_TZ), 1,
)
LATE_REQUESTS = check.Row(
    dt.datetime(2020, 12, 2, 6, 10, tzinfo=check.MSK_TZ), 1,
)
VERY_LATE_REQUESTS = check.Row(
    dt.datetime(2020, 12, 2, 7, 10, tzinfo=check.MSK_TZ), 1,
)


@pytest.mark.parametrize(
    'rows, now, expected_level',
    [
        ([], NOW_BEFORE_WINDOW, monrun.LEVEL_NORMAL),
        ([], NOW_INSIDE_WINDOW, monrun.LEVEL_NORMAL),
        ([], NOW_AFTER_WINDOW, monrun.LEVEL_WARNING),
        ([], NOW_AFTER_CRIT_THRESHOLD, monrun.LEVEL_CRITICAL),
        ([EARLY_REQUESTS], NOW_BEFORE_WINDOW, monrun.LEVEL_WARNING),
        ([EARLY_REQUESTS], NOW_INSIDE_WINDOW, monrun.LEVEL_WARNING),
        ([EARLY_REQUESTS], NOW_AFTER_WINDOW, monrun.LEVEL_WARNING),
        ([EARLY_REQUESTS], NOW_AFTER_CRIT_THRESHOLD, monrun.LEVEL_WARNING),
        ([NORMAL_REQUESTS], NOW_BEFORE_WINDOW, monrun.LEVEL_NORMAL),
        ([NORMAL_REQUESTS], NOW_INSIDE_WINDOW, monrun.LEVEL_NORMAL),
        ([NORMAL_REQUESTS], NOW_AFTER_WINDOW, monrun.LEVEL_NORMAL),
        ([NORMAL_REQUESTS], NOW_AFTER_CRIT_THRESHOLD, monrun.LEVEL_NORMAL),
        (
            [EARLY_REQUESTS, NORMAL_REQUESTS],
            NOW_AFTER_WINDOW,
            monrun.LEVEL_WARNING,
        ),
        (
            [NORMAL_REQUESTS, VERY_LATE_REQUESTS],
            NOW_AFTER_CRIT_THRESHOLD,
            monrun.LEVEL_CRITICAL,
        ),
        ([LATE_REQUESTS], NOW_AFTER_WINDOW, monrun.LEVEL_WARNING),
        ([LATE_REQUESTS], NOW_AFTER_CRIT_THRESHOLD, monrun.LEVEL_WARNING),
        (
            [VERY_LATE_REQUESTS],
            NOW_AFTER_CRIT_THRESHOLD,
            monrun.LEVEL_CRITICAL,
        ),
    ],
)
def test_get_level_and_info(rows, now, expected_level):
    actual_level, _ = check.get_level_and_info(rows, now, WINDOW)
    assert actual_level == expected_level
