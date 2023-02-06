import datetime
import json

import pytest

from tests_driver_mode_index import utils

MOCK_NOW = datetime.datetime(
    2016, 6, 13, 12, 0, 0, tzinfo=datetime.timezone.utc,
)
TIME_DELTA = datetime.timedelta(hours=1)


def get_unix_time(time):
    return (
        time - datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
    ).total_seconds()


@pytest.fixture(name='replication')
def mock_replication(mockserver):
    class ReplicationContext:
        def __init__(self):
            self.data = []

        def put_data(self, doc):
            for item in doc['items']:
                self.data.append(item['data'])

    ctx = ReplicationContext()

    @mockserver.json_handler('/replication/data/dmi_documents')
    def _put_data(request):
        doc = request.json
        ctx.put_data(doc)
        ids = [item['id'] for item in doc['items']]
        resp_items = [{'id': id, 'status': 'ok'} for id in ids]
        return {'items': resp_items}

    return ctx


@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.config(
    DRIVER_MODE_INDEX_CONFIG=utils.get_config(
        cleanup_job={
            'enabled': True,
            'delete_after': 1000,
            'batch_size': 100,
            'delete_limit': 10,
        },
        replication_job={
            'enabled': True,
            'batch_size': 100,
            'replication_batch_size': 100,
        },
    ),
)
@pytest.mark.suspend_periodic_tasks('replication-job')
@pytest.mark.suspend_periodic_tasks('cleanup-job')
async def test_replication(taxi_driver_mode_index, pgsql, replication):
    utils.TestData.id_ = 1
    ext_ref = 1
    should_be_replicated = []
    should_be_replicated_ids = []
    try:
        event_at = MOCK_NOW
        for [db, uid] in [
                ['u1', 'd1'],
                ['u2', 'd2'],
                ['u3', 'd3'],
                ['u4', 'd4'],
        ]:
            for sync in [True, True, False, False]:
                print('creating doc!')
                doc = utils.TestData(
                    db,
                    uid,
                    event_at,
                    event_at,
                    event_at,
                    event_at if sync else None,
                    'ext_{}'.format(ext_ref),
                    'df',
                    json.dumps({'settings': 'some'}),
                    billing_mode='not_used_billing_mode',
                    billing_mode_rule='not_used_billing_mode_rule',
                    is_active=False,
                )
                doc.add_to_pgsql(pgsql)

                if sync:
                    should_be_replicated.append(doc)
                    should_be_replicated_ids.append(ext_ref)
                ext_ref = ext_ref + 1
                event_at = event_at + TIME_DELTA

    except Exception as exc:  # pylint: disable=W0703
        print('Failed to sql: \'{}\''.format(exc))

    db = utils.get_items_count_in_db_with_id(16, pgsql)
    await taxi_driver_mode_index.run_periodic_task('replication-job')

    for (doc, replicated_doc) in zip(should_be_replicated, replication.data):
        assert doc.id_ == replicated_doc['id']
        assert doc.park_id == replicated_doc['park_id']
        assert doc.driver_id == replicated_doc['driver_profile_id']
        assert get_unix_time(doc.event_at) == replicated_doc['event_at']
        assert get_unix_time(doc.updated_at) == replicated_doc['updated']
        assert (
            get_unix_time(doc.billing_synced_at)
            == replicated_doc['billing_synced_at']
        )
        assert doc.external_ref == replicated_doc['external_ref']
        assert doc.work_mode == replicated_doc['driver_mode']
        assert doc.is_active == replicated_doc['is_active']


@pytest.mark.now('2019-05-01T12:00:00+0300')
@pytest.mark.config(
    DRIVER_MODE_INDEX_CONFIG=utils.get_config(
        cleanup_job={
            'enabled': True,
            'delete_after': 1000,
            'batch_size': 100,
            'delete_limit': 10,
        },
        replication_job={
            'enabled': True,
            'batch_size': 100,
            'replication_batch_size': 100,
        },
    ),
)
@pytest.mark.suspend_periodic_tasks('replication-job')
@pytest.mark.suspend_periodic_tasks('cleanup-job')
async def test_replication_with_cleanup(
        taxi_driver_mode_index, pgsql, replication,
):
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
                    False,
                )
                if not sync:
                    should_keep_ids.append(ext_ref)
                ext_ref = ext_ref + 1
                event_at = event_at + TIME_DELTA

    except Exception as exc:  # pylint: disable=W0703
        print('Failed to sql: \'{}\''.format(exc))

    db = utils.get_items_count_in_db_with_id(16, pgsql)
    await taxi_driver_mode_index.run_periodic_task('cleanup-job')
    utils.get_items_count_in_db_with_id(16, pgsql)

    await taxi_driver_mode_index.run_periodic_task('replication-job')
    await taxi_driver_mode_index.run_periodic_task('cleanup-job')
    db = utils.get_items_count_in_db_with_id(8, pgsql)
    assert sorted([x[0] for x in db]) == sorted(should_keep_ids)
