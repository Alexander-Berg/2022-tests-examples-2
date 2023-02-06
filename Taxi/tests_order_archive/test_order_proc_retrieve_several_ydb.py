import pytest


@pytest.mark.parametrize(
    'order_ids, logs',
    [
        (
            ['id1', 'id2', 'id3', 'id4', 'id5', 'id6'],
            [
                '[ydb.order_proc] 6 doc(s) was requested, '
                'num of found doc(s): 3',
                '[ydb.order_proc] not found 3 doc(s)',
                '[ydb.order_proc] found 3/6 ids',
            ],
        ),
        (
            ['id1', 'id2', 'id3'],
            [
                '[ydb.order_proc] 3 doc(s) was requested, '
                'num of found doc(s): 3',
                '[ydb.order_proc] found 3/3 ids',
            ],
        ),
    ],
)
@pytest.mark.config(
    ORDER_ARCHIVE_YDB={'ydb_read_only': ['v1_order_proc_bulk_retrieve']},
)
@pytest.mark.ydb(
    files=[
        'fill_orders.sql',
        'fill_order_id_index.sql',
        'fill_created_index.sql',
    ],
)
async def test_order_proc_ydb_read_only(taxi_order_archive, order_ids, logs):
    async with taxi_order_archive.capture_logs() as capture:
        await taxi_order_archive.post(
            'v1/order_proc/bulk-retrieve', json={'ids': order_ids},
        )
    all_logs = [log['text'] for log in capture.select()]
    ydb_logs = [log for log in all_logs if log.startswith('[ydb.order_proc]')]
    assert ydb_logs == logs
