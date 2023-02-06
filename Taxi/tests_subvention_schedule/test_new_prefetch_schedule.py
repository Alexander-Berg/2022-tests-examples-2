import datetime

import pytest

from tests_subvention_schedule import utils


def make_request(
        start,
        end,
        classes,
        zones,
        activity,
        tags,
        has_lightbox,
        has_sticker,
        ignored_restrictions,
):
    return {
        'types': ['single_ride'],
        'ignored_restrictions': ignored_restrictions,
        'time_range': {'from': start, 'to': end},
        'activity_points': activity,
        'branding': {'has_lightbox': has_lightbox, 'has_sticker': has_sticker},
        'tags': tags,
        'tariff_classes': classes,
        'zones': zones,
    }


@pytest.mark.parametrize('apply_fix', [False, True])
@pytest.mark.parametrize(
    'requests,expected_db',
    [
        (
            [
                {
                    'start': '2021-02-01T12:00:00+0300',
                    'end': '2021-02-06T12:00:00+0300',
                    'classes': ['eco'],
                    'zones': ['moscow'],
                    'activity': 50,
                    'tags': ['t1', 't2'],
                    'has_lightbox': True,
                    'has_sticker': True,
                    'ignored_restrictions': ['activity'],
                },
            ],
            'expected',
        ),
        (
            [
                {
                    'start': '2021-02-01T12:00:00+0300',
                    'end': '2021-02-06T12:00:00+0300',
                    'classes': ['eco'],
                    'zones': ['moscow'],
                    'activity': 50,
                    'tags': ['t1', 't2'],
                    'has_lightbox': True,
                    'has_sticker': True,
                    'ignored_restrictions': ['activity'],
                },
                {
                    'start': '2021-02-01T12:00:00+0300',
                    'end': '2021-02-06T12:00:00+0300',
                    'classes': ['eco'],
                    'zones': ['moscow'],
                    'activity': 60,
                    'tags': ['t1', 't2'],
                    'has_lightbox': True,
                    'has_sticker': True,
                    'ignored_restrictions': ['activity'],
                },
            ],
            'expected_merged',
        ),
        (
            [
                {
                    'start': '2021-02-01T12:00:00+0300',
                    'end': '2021-02-06T12:00:00+0300',
                    'classes': ['eco'],
                    'zones': ['moscow'],
                    'activity': 60,
                    'tags': ['t1', 't2'],
                    'has_lightbox': True,
                    'has_sticker': True,
                    'ignored_restrictions': ['activity'],
                },
                {
                    'start': '2021-02-01T12:00:00+0300',
                    'end': '2021-02-06T12:00:00+0300',
                    'classes': ['eco'],
                    'zones': ['moscow'],
                    'activity': 50,
                    'tags': ['t1', 't2'],
                    'has_lightbox': True,
                    'has_sticker': True,
                    'ignored_restrictions': ['activity'],
                },
            ],
            'expected_merged',
        ),
        (
            [
                {
                    'start': '2021-02-01T12:00:00+0300',
                    'end': '2021-02-06T12:00:00+0300',
                    'classes': ['eco'],
                    'zones': ['moscow'],
                    'activity': 50,
                    'tags': ['t1', 't2'],
                    'has_lightbox': True,
                    'has_sticker': True,
                    'ignored_restrictions': ['activity'],
                },
                {
                    'start': '2021-02-01T12:00:00+0300',
                    'end': '2021-02-07T12:00:00+0300',
                    'classes': ['eco'],
                    'zones': ['moscow'],
                    'activity': 50,
                    'tags': ['t1', 't2'],
                    'has_lightbox': True,
                    'has_sticker': True,
                    'ignored_restrictions': ['activity'],
                },
            ],
            'expected_merged_date',
        ),
    ],
)
@pytest.mark.parametrize('save_each_request', [True, False])
@pytest.mark.config(
    PREFETCH_JOB_SETTINGS_V2={
        'save_user_requests': True,
        'save_user_requests_before_midnight_minutes': 60 * 24,
    },
    CRON_SCHEDULER_SETTINGS={
        'update_job': {'enabled': False, 'update_period': 100},
        'db_store_postponed_requests': {'enabled': True, 'update_period': 100},
    },
)
@pytest.mark.now('2021-02-01T12:10:01+0300')
@pytest.mark.suspend_periodic_tasks('prefetch-job-sharded-0')
@pytest.mark.suspend_periodic_tasks('db-store-postponed-requests')
async def test_use_request_store(
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
        taxi_config,
        requests,
        expected_db,
        save_each_request,
        apply_fix,
):
    taxi_config.set_values(
        {'SUBVENTION_SCHEDULE_APPLY_PREFETCH_FIX': apply_fix},
    )
    await taxi_subvention_schedule.invalidate_caches()

    async def save_request():
        assert (
            await taxi_subvention_schedule.post(
                '/service/cron',
                json={'task_name': 'db-store-postponed-requests'},
            )
        ).status_code == 200

    for request in requests:
        await taxi_subvention_schedule.post(
            '/internal/subvention-schedule/v1/schedule',
            json=make_request(**request),
        )
        if save_each_request:
            await save_request()

    if not save_each_request:
        await save_request()

    if apply_fix:
        expected_db += '_shifted'
    assert utils.get_prostponed_user_requests(pgsql) == load_json(
        expected_db + '.json',
    )


@pytest.mark.parametrize(
    'apply_fix, now, initial_db, expected_db',
    [
        (
            True,
            datetime.datetime(2021, 2, 1, 18, 0),
            'to_prefetch.json',
            'to_prefetch.json',
        ),
        (
            True,
            datetime.datetime(2021, 2, 1, 20, 0),
            'to_prefetch.json',
            'prefetched.json',
        ),
        (
            True,
            datetime.datetime(2021, 2, 1, 22, 0),
            'to_prefetch.json',
            'to_prefetch.json',
        ),
        (
            False,
            datetime.datetime(2021, 2, 1, 18, 0),
            'to_prefetch.json',
            'prefetched.json',
        ),
        (
            False,
            datetime.datetime(2021, 2, 1, 20, 0),
            'to_prefetch.json',
            'prefetched.json',
        ),
        (
            False,
            datetime.datetime(2021, 2, 1, 22, 0),
            'to_prefetch.json',
            'to_prefetch.json',
        ),
        # ('to_prefetch_partialy.json', 'prefetched_partialy.json')
        # Failing, fix in next PR (see last @miktor commit)
    ],
)
@pytest.mark.config(
    PREFETCH_JOB_SETTINGS_V2={
        'do_prefetech_stored_requests': True,
        'prefetech_stored_requests_before_midnight_minutes': 60 * 2,
    },
)
@pytest.mark.suspend_periodic_tasks('prefetch-job-sharded-0')
async def test_fetch_postponed_requests(
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
        mocked_time,
        taxi_config,
        apply_fix,
        now,
        initial_db,
        expected_db,
):
    taxi_config.set_values(
        {'SUBVENTION_SCHEDULE_APPLY_PREFETCH_FIX': apply_fix},
    )
    await taxi_subvention_schedule.invalidate_caches()

    mocked_time.set(now)

    utils.load_db(pgsql, load_json(initial_db))
    await taxi_subvention_schedule.run_periodic_task('prefetch-job-sharded-0')

    assert utils.get_schedules(pgsql) == load_json(expected_db)


@pytest.mark.config(
    CRON_SCHEDULER_SETTINGS={
        'update_job': {'enabled': False, 'update_period': 100},
        'db_delete_postponed_requests': {
            'enabled': True,
            'update_period': 100,
        },
    },
    DELETE_OUTDATED_POSTPONED_REQUESTS={
        'delete_older_than_minutes': 60,  # 1 hour
        'batch_size': 1,
    },
)
@pytest.mark.parametrize(
    'original_db, expected_db',
    [
        ('expired.json', 'expected_expired.json'),
        ('mixed_expired.json', 'expected_mixed_expired.json'),
    ],
)
@pytest.mark.now('2021-02-02T12:00:00+0300')
async def test_cleanup(
        taxi_subvention_schedule, pgsql, load_json, original_db, expected_db,
):
    utils.load_db(pgsql, load_json(original_db))

    assert (
        await taxi_subvention_schedule.post(
            '/service/cron',
            json={'task_name': 'db-delete-postponed-requests'},
        )
    ).status_code == 200

    assert utils.get_schedules(pgsql) == load_json(expected_db)
