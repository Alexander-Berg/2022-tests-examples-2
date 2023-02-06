import pytest


@pytest.mark.parametrize(
    'order_id, indexes, logs',
    [
        (
            'id1',
            [],
            [
                '[ydb.order_proc] id id1 is located in partition 2022-03',
                '[ydb.order_proc] id id1 found',
            ],
        ),
        (
            'id2',
            [],
            [
                '[ydb.order_proc] id id2 is located in partition 2022-03',
                '[ydb.order_proc] id id2 found',
            ],
        ),
        (
            'id3',
            [],
            [
                '[ydb.order_proc] id id3 is located in partition 2022-03',
                '[ydb.order_proc] id id3 not found',
            ],
        ),
        ('id4', [], ['[ydb.order_proc] not found any partition for id id4']),
        (
            'id5',
            ['alias'],
            [
                '[ydb.order_proc] id id5 is located in partition 2022-03',
                '[ydb.order_proc] id id5 found',
            ],
        ),
        (
            'id5',
            ['reorder'],
            ['[ydb.order_proc] not found any partition for id id5'],
        ),
    ],
)
@pytest.mark.ydb(
    files=[
        'fill_orders.sql',
        'fill_order_id_index.sql',
        'fill_created_index.sql',
    ],
)
async def test_order_proc_ydb_read_only(
        taxi_order_archive, order_id, indexes, logs,
):
    async with taxi_order_archive.capture_logs() as capture:
        request_json_data = {'id': order_id}
        if indexes:
            request_json_data['indexes'] = indexes
        await taxi_order_archive.post(
            'v1/order_proc/retrieve', json=request_json_data,
        )
    all_logs = [
        log['text']
        for log in capture.select()
        if log['text'].startswith('[ydb.order_proc]')
    ]
    assert all_logs == logs
