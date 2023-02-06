import pytest


from tests_subvention_schedule import utils


@pytest.mark.parametrize(
    'db_before,should_work',
    [
        ('db_empty_affected_schedules.json', True),
        ('db_not_empty_affected_schedules.json', False),
    ],
)
@pytest.mark.config(
    PREFETCH_JOB_SETTINGS_V2={
        'do_prefetech_stored_requests': True,
        'prefetech_stored_requests_before_midnight_minutes': 24 * 7,
    },
)
@pytest.mark.now('2021-02-01T12:10:00+0300')
@pytest.mark.suspend_periodic_tasks('prefetch-job-sharded-0')
async def test_dont_work_if_there_are_affected_schedules(
        taxi_subvention_schedule,
        pgsql,
        bsx,
        testpoint,
        load_json,
        db_before,
        should_work,
):
    utils.load_db(pgsql, load_json(db_before))

    @testpoint('testpoint::prefetch_job_started')
    def prefetch_job_started(data):
        pass

    await taxi_subvention_schedule.run_periodic_task('prefetch-job-sharded-0')
    assert bool(prefetch_job_started.times_called) == should_work
