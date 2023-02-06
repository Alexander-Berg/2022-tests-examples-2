# pylint: disable=redefined-outer-name
import pytest

from taxi_corp import cron_run
from taxi_corp import settings
from taxi_corp.api.common import distlock


TEST_LOCK_OWNER = 'process_notices_queue'


@pytest.fixture
def stq_exceptions(request):
    return request.param if hasattr(request, 'param') else {}


@pytest.fixture
def stq_call_mock(stq_exceptions, patch):
    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        entity_id = kwargs['kwargs']['entity_id']
        if entity_id in stq_exceptions:
            raise stq_exceptions[entity_id].pop()

    return _put


@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.parametrize(
    ['locked_notices', 'succeed_notices', 'stq_exceptions'],
    [(['id_notice3'], ['id_notice2'], {'entity_id4': [ValueError]})],
    indirect=['stq_exceptions'],
)
async def test_cron_notice_queue(
        db, stq_call_mock, locked_notices, succeed_notices, stq_exceptions,
):
    for lock_id in locked_notices:
        lock = distlock.DistributedLock(
            lock_id,
            settings.CORP_CRON_NOTICE_LOCK_TIME,
            db,
            TEST_LOCK_OWNER,
            lock_collection_name=settings.CORP_LOCK_COLLECTION,
        )
        locked = await lock.acquire()
        assert locked

    module = 'taxi_corp.stuff.process_notices_queue'
    await cron_run.main([module, '-t', '0'])

    calls = stq_call_mock.calls
    assert len(calls) == 2

    enqueued = await db.corp_notices_queue.find(
        {'_id': {'%in': succeed_notices}},
    ).to_list(None)
    assert not enqueued

    left_entities = {
        notice['_id']: notice['entity_id']
        for notice in await db.corp_notices_queue.find().to_list(None)
    }

    # failed notices still in db
    failed_entities = set(stq_exceptions.keys())
    assert failed_entities.issubset(set(left_entities.values()))

    # left notices are not locked
    lock_collection = getattr(db, settings.CORP_LOCK_COLLECTION)
    locked_ids = {
        locked['_id'] for locked in await lock_collection.find().to_list(None)
    }
    failed_ids = {
        notice_id
        for notice_id, entity_id in left_entities.items()
        if entity_id in failed_entities
    }
    assert not failed_ids & locked_ids
