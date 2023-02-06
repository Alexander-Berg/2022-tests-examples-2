import datetime

import freezegun
import pytest

from taxi.core import async
from taxi.internal import cron_manager
from taxi.internal import dbh
from taxi.util import dates

ADD_JOB = 'add'
SUB_JOB = 'sub'


# fixtures are:
#   * add: 2016-06-02, 2016-06-03
#   * sub: 2016-06-03, 2016-06-04
@pytest.mark.filldb()
@pytest.mark.parametrize('name,utcnow,expected_num_calls', [
    # didn't run at 2016-06-01: 1 call
    (ADD_JOB, datetime.datetime(2016, 6, 1), 1),
    # run at 2016-06-02: 0 calls
    (ADD_JOB, datetime.datetime(2016, 6, 2), 0),
    # didn't run at 2016-06-04: 1 call
    (ADD_JOB, datetime.datetime(2016, 6, 4), 1),
])
@pytest.inline_callbacks
def test_job_decorator(name, utcnow, expected_num_calls):
    calls = []
    num_jobs_before = yield _get_num_cron_jobs()

    @cron_manager.job(name, cron_manager.MOSCOW_DAILY_CONDITION)
    @async.inline_callbacks
    def add_job(x, y):
        calls.append(x + y)
        yield

    with freezegun.freeze_time(utcnow, ignore=['']):
        yield add_job(1, 2)
    num_jobs_after = yield _get_num_cron_jobs()
    assert len(calls) == expected_num_calls
    if expected_num_calls:
        query = {
            dbh.cron_jobs.Doc.name: name,
            dbh.cron_jobs.Doc.started_at: utcnow
        }
        # just checking that it found it
        yield dbh.cron_jobs.Doc.find_one_or_not_found(query)
        assert num_jobs_after == num_jobs_before + 1
    else:
        assert num_jobs_after == num_jobs_before


@async.inline_callbacks
def _get_num_cron_jobs():
    num_cron_jobs = yield dbh.cron_jobs.Doc._get_db_collection().count()
    async.return_value(num_cron_jobs)


def _msk_datetime(year, month, day, hour):
    tz = 'Europe/Moscow'
    naive_msk_datetime = datetime.datetime(year, month, day, hour)
    naive_utc = dates.naive_tz_to_naive_utc(
        naive_msk_datetime, tz
    )
    return dates.localize(naive_utc, tz)
