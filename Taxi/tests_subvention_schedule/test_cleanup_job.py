import datetime


import dateutil.parser
import pytest

from testsuite import utils as tutils

from tests_subvention_schedule import utils


@pytest.mark.config(
    CRON_SCHEDULER_SETTINGS={
        'update_job': {'enabled': False, 'update_period': 100},
        'db_cleanup_statistics_store_job': {
            'enabled': True,
            'update_period': 100,
        },
        'db_cleanup_by_uses_job': {'enabled': True, 'update_period': 100},
        'db_cleanup_by_time_job': {'enabled': True, 'update_period': 100},
        'db_cleanup_by_uses_and_time_job': {
            'enabled': True,
            'update_period': 100,
        },
        'db_cleanup_by_no_stats': {'enabled': True, 'update_period': 100},
    },
    DELETE_OLD_JOB_SETTINGS={
        'delete_if_not_used_for': 86400,  # 1 day
        'delete_if_used_less_than': 1,
        'batch_size': 1,
        'min_lifetime': 86400,  # 1 day
    },
)
@pytest.mark.parametrize(
    'method, original_db, idx, uses, used_at, expected_db',
    [
        (
            'db-cleanup-time',
            'simple_rule_db.json',
            1,
            1,
            '2021-01-31 21:00:00',
            'simple_rule_db.json',
        ),
        (
            'db-cleanup-time',
            'simple_rule_db.json',
            1,
            1,
            '2021-01-31 00:00:00',
            'empty_db.json',
        ),
        (
            'db-cleanup-uses',
            'simple_rule_db.json',
            1,
            1,
            '2021-01-31 21:00:00',
            'simple_rule_db.json',
        ),
        (
            'db-cleanup-uses',
            'simple_rule_db.json',
            1,
            0,
            '2021-01-31 21:00:00',
            'empty_db.json',
        ),
        (
            'db-cleanup-uses-time',
            'simple_rule_db.json',
            1,
            0,
            '2021-01-31 21:00:00',
            'simple_rule_db.json',
        ),
        (
            'db-cleanup-uses-time',
            'simple_rule_db.json',
            1,
            1,
            '2021-01-31 21:00:00',
            'simple_rule_db.json',
        ),
        (
            'db-cleanup-uses-time',
            'simple_rule_db.json',
            1,
            0,
            '2021-01-30 21:00:00',
            'empty_db.json',
        ),
        (
            'db-cleanup-uses-time',
            'simple_rule_db.json',
            1,
            1,
            '2021-01-30 21:00:00',
            'simple_rule_db.json',
        ),
        (
            'db-cleanup-no-stats',
            'simple_rule_db_2.json',
            1,
            1,
            '2021-01-30 21:00:00',
            'simple_rule_db.json',
        ),
        (
            'db-cleanup-no-stats',
            'simple_rule_db_2.json',
            None,
            None,
            None,
            'simple_rule_db_3.json',
        ),
    ],
)
@pytest.mark.now('2021-02-01T12:10:00+0300')
@pytest.mark.xfail(reason='flaky test, will be fixed in EFFICIENCYDEV-18359')
async def test_cleanup(
        taxi_subvention_schedule,
        pgsql,
        mocked_time,
        load_json,
        bsx,
        method,
        original_db,
        idx,
        uses,
        used_at,
        expected_db,
):
    mocked_time.set(
        tutils.to_utc(dateutil.parser.parse('2021-01-29T12:00:00+0300')),
    )
    utils.load_db(pgsql, load_json(original_db), mocked_time)
    mocked_time.set(
        tutils.to_utc(dateutil.parser.parse('2021-02-01T12:10:00+0300')),
    )

    if idx is not None:
        utils.insert_use_statistics(pgsql, idx, uses, used_at)

    assert (
        await taxi_subvention_schedule.post(
            '/service/cron', json={'task_name': method},
        )
    ).status_code == 200

    assert utils.get_schedules(pgsql) == load_json(expected_db)


@pytest.mark.config(
    CRON_SCHEDULER_SETTINGS={
        'update_job': {'enabled': True, 'update_period': 100},
        'db_cleanup_statistics_store_job': {
            'enabled': True,
            'update_period': 100,
        },
        'db_cleanup_by_uses_job': {'enabled': True, 'update_period': 100},
        'db_cleanup_by_time_job': {'enabled': True, 'update_period': 100},
        'db_cleanup_by_uses_and_time_job': {
            'enabled': True,
            'update_period': 100,
        },
        'db_cleanup_by_no_stats': {'enabled': True, 'update_period': 100},
    },
    DELETE_OLD_JOB_SETTINGS={
        'delete_if_not_used_for': 86400,  # 1 day
        'delete_if_used_less_than': 1,
        'batch_size': 1,
        'min_lifetime': 86400,  # 1 day
        'min_worktime': 3600,  # 1 hour
    },
)
@pytest.mark.parametrize(
    'method,use_stats',
    [
        ('db-cleanup-time', True),
        ('db-cleanup-uses', True),
        ('db-cleanup-uses-time', True),
        ('db-cleanup-no-stats', False),
    ],
)
@pytest.mark.parametrize(
    'now,active_range,should_delete',
    [
        pytest.param(
            # now
            '2021-02-01T12:10:00+0000',
            # active_range
            ('2021-02-01 21:00:00', '2021-02-08 21:00:00'),
            # should_delete
            False,
            id='future_descriptor',
        ),
        pytest.param(
            # now
            '2021-02-01T21:10:00+0000',
            # active_range
            ('2021-02-01 21:00:00', '2021-02-08 21:00:00'),
            # should_delete
            False,
            id='past_descriptor_worktime_isnt_expired',
        ),
        pytest.param(
            # now
            '2021-02-01T23:10:00+0000',
            # active_range
            ('2021-02-01 21:00:00', '2021-02-08 21:00:00'),
            # should_delete
            True,
            id='past_descriptor_worktime_expired',
        ),
    ],
)
async def test_cleanup_respects_active_range(
        taxi_subvention_schedule,
        pgsql,
        mocked_time,
        bsx,
        method,
        use_stats,
        now,
        active_range,
        should_delete,
):
    mocked_time.set(
        tutils.to_utc(dateutil.parser.parse('2021-01-29T12:00:00+0300')),
    )
    db = {
        'descriptors': [
            [
                'moscow',
                'eco',
                'single_ride',
                0,
                100,
                '{activity}',
                True,
                True,
                ['t1', 't2'],
                active_range[0],
                active_range[1],
                '2021-01-15 21:00:00',  # last_rule_updated_at
            ],
        ],
        'items': [],
    }
    utils.load_db(pgsql, db, mocked_time)
    if use_stats:
        utils.insert_use_statistics(
            pgsql, idx=1, count=0, used_at='1970-01-01 00:00:00',
        )
    mocked_time.set(tutils.to_utc(dateutil.parser.parse(now)))

    assert (
        await taxi_subvention_schedule.post(
            '/service/cron', json={'task_name': method},
        )
    ).status_code == 200

    descriptors_left = utils.get_schedules(pgsql)['descriptors']

    assert bool(descriptors_left) == (not should_delete)


@pytest.mark.config(
    CRON_SCHEDULER_SETTINGS={
        'update_job': {'enabled': True, 'update_period': 100},
        'db_cleanup_statistics_store_job': {
            'enabled': True,
            'update_period': 100,
        },
        'db_cleanup_by_uses_job': {'enabled': True, 'update_period': 100},
        'db_cleanup_by_time_job': {'enabled': True, 'update_period': 100},
        'db_cleanup_by_uses_and_time_job': {
            'enabled': True,
            'update_period': 100,
        },
    },
    DELETE_OLD_JOB_SETTINGS={
        'delete_if_not_used_for': 86400,  # 1 day
        'delete_if_used_less_than': 1,
        'batch_size': 1,
    },
    STORE_DESCRIPTOR_USAGE_STATISTIC=True,
)
@pytest.mark.parametrize(
    'original_db, original_stats, expected_stats',
    [
        (
            'simple_rule_db.json',
            None,
            [(1, 1, datetime.datetime(2021, 2, 1, 9, 10))],
        ),
        (
            'simple_rule_db.json',
            None,
            [(1, 2, datetime.datetime(2021, 2, 1, 9, 10))],
        ),
        (
            'simple_rule_db.json',
            (1, 0, datetime.datetime(2007, 2, 1, 9, 10)),
            [(1, 1, datetime.datetime(2021, 2, 1, 9, 10))],
        ),
    ],
)
@pytest.mark.now('2021-02-01T12:10:00+0300')
async def test_statistics(
        taxi_subvention_schedule,
        pgsql,
        load_json,
        bsx,
        original_db,
        original_stats,
        expected_stats,
):
    utils.load_db(pgsql, load_json(original_db))

    if original_stats:
        utils.insert_use_statistics(pgsql, *original_stats)

    request = {
        'types': ['single_ride'],
        'ignored_restrictions': ['activity'],
        'time_range': {
            'from': '2021-02-01T12:00:00+0300',
            'to': '2021-02-07T12:00:00+0300',
        },
        'activity_points': 20,
        'branding': {'has_lightbox': True, 'has_sticker': True},
        'tags': ['t1', 't2'],
        'tariff_classes': ['eco'],
        'zones': ['moscow'],
    }

    for _ in range(expected_stats[0][1]):
        response = await taxi_subvention_schedule.post(
            '/internal/subvention-schedule/v1/schedule', json=request,
        )

        assert response.status_code == 200
        assert utils.get_use_statistics(pgsql) == (
            [original_stats] if original_stats else []
        )

    assert (
        await taxi_subvention_schedule.post(
            '/service/cron', json={'task_name': 'db-cleanup-statistics'},
        )
    ).status_code == 200

    assert utils.get_use_statistics(pgsql) == expected_stats


@pytest.mark.config(
    CRON_SCHEDULER_SETTINGS={
        'update_job': {'enabled': True, 'update_period': 100},
        'db_cleanup_statistics_store_job': {
            'enabled': True,
            'update_period': 100,
        },
        'db_cleanup_by_uses_job': {'enabled': True, 'update_period': 100},
        'db_cleanup_by_time_job': {'enabled': True, 'update_period': 100},
        'db_cleanup_by_uses_and_time_job': {
            'enabled': True,
            'update_period': 100,
        },
    },
    DELETE_OLD_JOB_SETTINGS={
        'delete_if_not_used_for': 86400,  # 1 day
        'delete_if_used_less_than': 1,
        'batch_size': 10,
    },
    STORE_DESCRIPTOR_USAGE_STATISTIC=True,
)
@pytest.mark.now('2021-02-01T12:10:00+0300')
async def test_store_deleted_statistics(
        taxi_subvention_schedule, pgsql, load_json, bsx,
):
    utils.load_db(pgsql, load_json('simple_rule_db.json'))

    request = {
        'types': ['single_ride'],
        'ignored_restrictions': ['activity'],
        'time_range': {
            'from': '2021-02-01T12:00:00+0300',
            'to': '2021-02-07T12:00:00+0300',
        },
        'activity_points': 20,
        'branding': {'has_lightbox': True, 'has_sticker': True},
        'tags': ['t1', 't2'],
        'tariff_classes': ['eco'],
        'zones': ['moscow'],
    }

    response = await taxi_subvention_schedule.post(
        '/internal/subvention-schedule/v1/schedule', json=request,
    )

    assert response.status_code == 200
    assert utils.get_use_statistics(pgsql) == []

    utils.execute('TRUNCATE TABLE sch.schedule_descriptiors CASCADE;', pgsql)

    assert (
        await taxi_subvention_schedule.post(
            '/service/cron', json={'task_name': 'db-cleanup-statistics'},
        )
    ).status_code == 200

    assert utils.get_use_statistics(pgsql) == []


@pytest.mark.config(
    CRON_SCHEDULER_SETTINGS={
        'update_job': {'enabled': True, 'update_period': 100},
        'db_cleanup_statistics_store_job': {
            'enabled': True,
            'update_period': 100,
        },
        'db_cleanup_by_uses_job': {'enabled': True, 'update_period': 100},
        'db_cleanup_by_time_job': {'enabled': True, 'update_period': 100},
        'db_cleanup_by_uses_and_time_job': {
            'enabled': True,
            'update_period': 100,
        },
    },
    DELETE_OLD_JOB_SETTINGS={
        'delete_if_not_used_for': 86400,  # 1 day
        'delete_if_used_less_than': 1,
        'batch_size': 1,
    },
    STORE_DESCRIPTOR_USAGE_STATISTIC=True,
)
@pytest.mark.now('2021-02-01T12:10:00+0300')
async def test_insert_deleted_statistics(
        taxi_subvention_schedule, pgsql, load_json, bsx,
):
    utils.load_db(pgsql, load_json('simple_rule_db.json'))

    request = {
        'types': ['single_ride'],
        'ignored_restrictions': ['activity'],
        'time_range': {
            'from': '2021-02-01T12:00:00+0300',
            'to': '2021-02-07T12:00:00+0300',
        },
        'activity_points': 20,
        'branding': {'has_lightbox': True, 'has_sticker': True},
        'tags': ['t1', 't2'],
        'tariff_classes': ['eco'],
        'zones': ['moscow'],
    }
    response = await taxi_subvention_schedule.post(
        '/internal/subvention-schedule/v1/schedule', json=request,
    )

    assert response.status_code == 200
    assert utils.get_use_statistics(pgsql) == []

    utils.execute('TRUNCATE TABLE sch.schedule_descriptiors CASCADE;', pgsql)

    assert (
        await taxi_subvention_schedule.post(
            '/service/cron', json={'task_name': 'db-cleanup-statistics'},
        )
    ).status_code == 200

    assert utils.get_use_statistics(pgsql) == []


@pytest.mark.config(
    CRON_SCHEDULER_SETTINGS={
        'update_job': {'enabled': False, 'update_period': 100},
        'db_delete_outdated': {'enabled': True, 'update_period': 100},
    },
    DELETE_OLD_JOB_SETTINGS={
        'delete_if_not_used_for': 86400,  # 1 day
        'delete_if_used_less_than': 1,
        'batch_size': 10,
    },
)
@pytest.mark.now('2021-02-01T12:10:00+0300')
async def test_deleted_outdated(
        taxi_subvention_schedule, pgsql, load_json, bsx,
):
    utils.load_db(pgsql, load_json('outdated_db.json'))

    assert (
        await taxi_subvention_schedule.post(
            '/service/cron', json={'task_name': 'db-delete-outdated'},
        )
    ).status_code == 200

    assert utils.get_schedules(pgsql) == load_json('outdated_db_expected.json')
