# pylint: disable=redefined-outer-name
import asyncio
import datetime

import pytest

from taxi_corp.notifier import notices_queue


@pytest.fixture()
def queue(db):
    return notices_queue.NoticesQueue(db)


@pytest.mark.parametrize(
    ['entity_id', 'notice_names', 'send_times'],
    [
        (
            'entity_id3',
            ['notice1'],
            [datetime.datetime(2019, 10, 5, 23, 00, 00)],
        ),
        (
            'entity_id3',
            ['notice1', 'notice2'],
            [
                datetime.datetime(2019, 10, 5, 23, 00, 00),
                datetime.datetime(2019, 10, 10, 23, 00, 00),
            ],
        ),
    ],
)
async def test_notices_queue(db, queue, entity_id, notice_names, send_times):
    rows_cnt = await db.corp_notices_queue.find({}).count()
    await asyncio.gather(
        *[
            queue.enqueue_notice(entity_id, notice_name, send_at, {})
            for notice_name, send_at in zip(notice_names, send_times)
        ],
    )
    rows_cnt_now = await db.corp_notices_queue.find({}).count()
    assert rows_cnt + len(notice_names) == rows_cnt_now


@pytest.mark.parametrize(
    ['entity_id', 'notice_name'], [('entity_id2', 'notice_name1')],
)
async def test_dequeue_notice(db, queue, entity_id, notice_name):
    rows_cnt = await db.corp_notices_queue.find({}).count()
    await queue.dequeue_notice(entity_id, notice_name)
    rows_cnt_now = await db.corp_notices_queue.find({}).count()
    assert rows_cnt - 1 == rows_cnt_now


@pytest.mark.parametrize(
    ['queued_ids'], [(['id_notice1'],), (['id_notice1', 'id_notice2'],)],
)
async def test_clean_queue(db, queue, queued_ids):
    rows_cnt = await db.corp_notices_queue.find({}).count()
    await queue.clean_queue(queued_ids)
    rows_cnt_now = await db.corp_notices_queue.find({}).count()
    assert rows_cnt - len(queued_ids) == rows_cnt_now
