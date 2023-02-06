import datetime

import pytest

from crm_hub.repositories import efficiency_sending


@pytest.mark.parametrize(
    'efficiency_sending_id, table_path, expected_error',
    [
        ('00000000-0000-0000-0000-000000000001', '//home/taxi-crm/1/', True),
        ('00000000-0000-0000-0000-000000000002', '//home/taxi-crm/2/', False),
        ('00000000-0000-0000-0000-000000000003', '//home/taxi-crm/3/', False),
    ],
)
@pytest.mark.pgsql('crm_hub', files=['init_efficiency_sending.sql'])
async def test_efficiency_sending_storage_create(
        web_context, efficiency_sending_id, table_path, expected_error,
):
    storage = efficiency_sending.EfficiencySendingStorage(web_context)

    if not expected_error:
        await storage.create(
            sending_id=efficiency_sending_id, table_path=table_path,
        )

        async with web_context.pg.master_pool.acquire() as conn:
            query = 'SELECT * FROM crm_hub.efficiency_sending '
            query += f'WHERE id = \'{efficiency_sending_id}\';'

            efficiency_sending_records = await conn.fetch(query)
            assert len(efficiency_sending_records) == 1
            record = efficiency_sending_records[0]
            assert efficiency_sending_id == str(record['id'])
            assert record['state'] == 'new'
            assert table_path == record['table_path']
            minute = datetime.timedelta(minutes=1)
            assert record['created_at'] - datetime.datetime.utcnow() < minute
    else:
        with pytest.raises(efficiency_sending.EfficiencySendingAlreayExists):
            await storage.create(
                sending_id=efficiency_sending_id, table_path=table_path,
            )


@pytest.mark.parametrize(
    'efficiency_sending_id, exists',
    [
        ('00000000000000000000000000000001', True),
        ('00000000000000000000000000000011', True),
        ('00000000000000000000000000000012', True),
        ('00000000000000000000000000000100', False),
    ],
)
@pytest.mark.pgsql('crm_hub', files=['init_efficiency_sending.sql'])
async def test_efficiency_sending_storage_fetch(
        web_context, load_json, efficiency_sending_id, exists,
):
    storage = efficiency_sending.EfficiencySendingStorage(web_context)
    if exists:
        computed = await storage.fetch(sending_id=efficiency_sending_id)
        expected = load_json('efficiency_sending.json')[efficiency_sending_id]

        assert str(computed.id) == expected['id']
        assert computed.state == expected['state']
        assert computed.table_path == expected['table_path']
    else:
        with pytest.raises(efficiency_sending.EfficiencySendingNotFound):
            await storage.fetch(sending_id=efficiency_sending_id)
