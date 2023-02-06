import datetime

import pytest

from taxi.core import async
from taxi.internal import dbh
from taxi.internal import event_monitor
from taxi_maintenance.stuff import (
    update_day_ride_count_subventions_watcher as watcher
)

_NOW = datetime.datetime(2018, 8, 10, 0, 1, 2)


@pytest.mark.filldb(
    cron_jobs='for_test_do_stuff',
)
@pytest.mark.now(_NOW.isoformat())
@pytest.inline_callbacks
def test_do_stuff():
    yield watcher.do_stuff()
    event = yield event_monitor.full_udrcs_event.get_recent()
    assert event['date_string'] == '2018-08-09'
    jobs = yield dbh.cron_jobs.Doc.get_recent_jobs_by_name(
        'update_day_ride_count_subventions'
    )
    assert len(jobs) == 1


@pytest.mark.filldb(
    cron_jobs='for_test_do_stuff_do_nothing_because_dependency',
)
@pytest.mark.now(_NOW.isoformat())
@pytest.inline_callbacks
def test_do_stuff_do_nothing_because_dependency():
    yield _check_watcher_does_nothing()


@pytest.mark.filldb(
    cron_jobs='for_test_do_stuff_do_nothing_because_already_run',
)
@pytest.mark.now(_NOW.isoformat())
@pytest.inline_callbacks
def test_do_stuff_do_nothing_because_already_run():
    yield _check_watcher_does_nothing()


@async.inline_callbacks
def _check_watcher_does_nothing():
    num_jobs_before = yield _get_num_jobs()
    yield watcher.do_stuff()
    event = yield event_monitor.full_udrcs_event.get_recent()
    assert event is None

    num_jobs_after = yield _get_num_jobs()
    assert num_jobs_before == num_jobs_after


@async.inline_callbacks
def _get_num_jobs():
    jobs = yield dbh.cron_jobs.Doc.get_recent_jobs_by_name(
        'update_day_ride_count_subventions'
    )
    async.return_value(len(jobs))
