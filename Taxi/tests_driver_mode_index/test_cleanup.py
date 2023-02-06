import datetime
import json

import pytest

from tests_driver_mode_index import utils


MOCK_NOW = datetime.datetime(
    2016, 6, 13, 12, 0, 0, tzinfo=datetime.timezone.utc,
)
TIME_DELTA = datetime.timedelta(hours=1)


@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.config(
    DRIVER_MODE_INDEX_CONFIG=utils.get_config(
        cleanup_job={
            'enabled': True,
            'delete_after': 1000,
            'batch_size': 100,
            'delete_limit': 10,
        },
    ),
)
@pytest.mark.suspend_periodic_tasks('cleanup-job')
async def test_clean_old(taxi_driver_mode_index, pgsql):
    should_keep_ids = []
    ext_ref = 1
    try:
        event_at = MOCK_NOW
        for [db, uid] in [
                ['u1', 'd1'],
                ['u2', 'd2'],
                ['u3', 'd3'],
                ['u4', 'd4'],
        ]:
            for sync in [True, True, False, False]:
                utils.insert_values(
                    pgsql,
                    db,
                    uid,
                    'ext_{}'.format(ext_ref),
                    'df',
                    json.dumps({'settings': 'some'}),
                    'mock_billing_mode',
                    'mock_billing_mode_rule',
                    event_at.strftime('%Y-%m-%d %H:%M:%S'),
                    event_at.strftime('\'%Y-%m-%d %H:%M:%S\'')
                    if sync
                    else None,
                    event_at.strftime('%Y-%m-%d %H:%M:%S'),
                    True,
                )
                if not sync:
                    should_keep_ids.append(ext_ref)
                ext_ref = ext_ref + 1
                event_at = event_at + TIME_DELTA

    except Exception as exc:  # pylint: disable=W0703
        print('Failed to sql: \'{}\''.format(exc))

    db = utils.get_items_count_in_db_with_id(16, pgsql)
    await taxi_driver_mode_index.run_periodic_task('cleanup-job')
    db = utils.get_items_count_in_db_with_id(8, pgsql)
    assert sorted([x[0] for x in db]) == sorted(should_keep_ids)


@pytest.mark.now('2019-05-01T09:00:00+0000')
@pytest.mark.config(
    DRIVER_MODE_INDEX_CONFIG=utils.get_config(
        cleanup_job={
            'enabled': True,
            'delete_after': 3600,
            'batch_size': 5,
            'delete_limit': 10,
        },
    ),
)
@pytest.mark.suspend_periodic_tasks('cleanup-job')
async def test_dont_delete_new(taxi_driver_mode_index, pgsql):
    should_keep_ids = []
    ext_ref = 1
    try:
        for [db, uid] in [
                ['u1', 'd1'],
                ['u2', 'd2'],
                ['u3', 'd3'],
                ['u4', 'd4'],
        ]:
            for sync in [
                    '2019-05-01 07:00:00',
                    '2019-05-01 08:00:00',
                    '2019-05-01 09:00:00',
            ]:
                utils.insert_values(
                    pgsql,
                    db,
                    uid,
                    'ext_{}'.format(ext_ref),
                    'df',
                    json.dumps({'settings': 'some'}),
                    'mock_billing_mode',
                    'mock_billing_mode_rule',
                    sync,
                    '\'{}\''.format(sync),
                    sync,
                    True,
                )
                if sync == '2019-05-01 09:00:00':
                    should_keep_ids.append(ext_ref)
                ext_ref = ext_ref + 1

    except Exception as exc:  # pylint: disable=W0703
        print('Failed to sql: \'{}\''.format(exc))

    db = utils.get_items_count_in_db_with_id(12, pgsql)
    await taxi_driver_mode_index.run_periodic_task('cleanup-job')
    db = utils.get_items_count_in_db_with_id(4, pgsql)
    assert [x[0] for x in db] == should_keep_ids


@pytest.mark.now('2019-05-01T09:00:00+0000')
@pytest.mark.config(
    DRIVER_MODE_INDEX_CONFIG=utils.get_config(
        cleanup_job={
            'enabled': True,
            'delete_after': 3600,
            'batch_size': 3,
            'delete_limit': 4,
        },
    ),
)
@pytest.mark.suspend_periodic_tasks('cleanup-job')
async def test_dont_delete_limit(taxi_driver_mode_index, pgsql):
    ext_ref = 1
    try:
        for [db, uid] in [
                ['u1', 'd1'],
                ['u2', 'd2'],
                ['u3', 'd3'],
                ['u4', 'd4'],
        ]:
            for sync in [
                    '2019-05-01 07:00:00',
                    '2019-05-01 08:00:00',
                    '2019-05-01 09:00:00',
            ]:
                utils.insert_values(
                    pgsql,
                    db,
                    uid,
                    'ext_{}'.format(ext_ref),
                    'df',
                    json.dumps({'settings': 'some'}),
                    'mock_billing_mode',
                    'mock_billing_mode_rule',
                    sync,
                    '\'{}\''.format(sync),
                    sync,
                    True,
                )
                ext_ref = ext_ref + 1

    except Exception as exc:  # pylint: disable=W0703
        print('Failed to sql: \'{}\''.format(exc))

    db = utils.get_items_count_in_db_with_id(12, pgsql)
    await taxi_driver_mode_index.run_periodic_task('cleanup-job')
    db = utils.get_items_count_in_db_with_id(8, pgsql)
