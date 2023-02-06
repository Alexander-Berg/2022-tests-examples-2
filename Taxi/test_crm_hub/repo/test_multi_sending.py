import datetime

import pytest

from crm_hub.repositories import multi_sending


@pytest.mark.parametrize(
    'multi_sending_id, batch_sending_id',
    [
        (
            '00000000-0000-0000-0000-000000000001',
            '00000000-0000-0000-0000-000000000011',
        ),
        (
            '00000000-0000-0000-0000-000000000001',
            '00000000-0000-0000-0000-000000000012',
        ),
        (
            '00000000-0000-0000-0000-000000000001',
            '00000000-0000-0000-0000-000000000013',
        ),
        (
            '00000000-0000-0000-0000-000000000002',
            '00000000-0000-0000-0000-000000000011',
        ),
        (
            '00000000-0000-0000-0000-000000000002',
            '00000000-0000-0000-0000-000000000015',
        ),
        (
            '00000000-0000-0000-0000-000000000003',
            '00000000-0000-0000-0000-000000000016',
        ),
        (
            '00000000-0000-0000-0000-000000000004',
            '00000000-0000-0000-0000-000000000017',
        ),
    ],
)
@pytest.mark.pgsql('crm_hub', files=['init_batch_sending.sql'])
async def test_multi_sending_storage_create_part(
        web_context, multi_sending_id, batch_sending_id,
):

    storage = multi_sending.MultiSendingStorage(web_context)
    await storage.create_part(
        multi_sending_id=multi_sending_id, batch_sending_id=batch_sending_id,
    )

    async with web_context.pg.master_pool.acquire() as conn:
        multi_sending_records = await conn.fetch(
            'SELECT * FROM crm_hub.multi_sending_parts;',
        )
        assert len(multi_sending_records) == 1
        record = multi_sending_records[0]
        assert multi_sending_id == str(record['multi_sending_id'])
        assert batch_sending_id == str(record['batch_sending_id'])
        minute = datetime.timedelta(minutes=1)
        assert record['created_at'] - datetime.datetime.utcnow() < minute


@pytest.mark.parametrize(
    'multi_sending_id, batch_sending_list',
    [
        (
            '00000000-0000-0000-0000-000000000001',
            [
                '00000000-0000-0000-0000-000000000011',
                '00000000-0000-0000-0000-000000000012',
                '00000000-0000-0000-0000-000000000013',
            ],
        ),
        (
            '00000000-0000-0000-0000-000000000002',
            [
                '00000000-0000-0000-0000-000000000014',
                '00000000-0000-0000-0000-000000000015',
            ],
        ),
        (
            '00000000-0000-0000-0000-000000000003',
            ['00000000-0000-0000-0000-000000000016'],
        ),
        (
            '00000000-0000-0000-0000-000000000004',
            ['00000000-0000-0000-0000-000000000017'],
        ),
    ],
)
@pytest.mark.pgsql(
    'crm_hub', files=['init_batch_sending.sql', 'init_multi_sending.sql'],
)
async def test_multi_sending_storage_fetch_all_parts(
        web_context, multi_sending_id, batch_sending_list,
):
    storage = multi_sending.MultiSendingStorage(web_context)
    parts = await storage.fetch_all_parts(multi_sending_id=multi_sending_id)
    expected = set(batch_sending_list)
    computed = {str(part['batch_sending_id']) for part in parts}
    assert expected == computed
