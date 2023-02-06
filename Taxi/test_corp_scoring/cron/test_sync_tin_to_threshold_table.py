# pylint: disable=redefined-outer-name
import dataclasses
import decimal

import pytest

from corp_scoring.generated.cron import run_cron


async def _get_synced_tins(context) -> dict:
    query_tins = (
        'SELECT tin, threshold_val FROM corp_scoring.tins_to_thresholds'
    )

    table = {}
    async with context.pg.master_pool.acquire(log_extra=None) as conn:
        async with conn.transaction():
            cursor = conn.cursor(query=query_tins)
            async for record in cursor:
                table[record['tin']] = record['threshold_val']

    return table


@pytest.fixture
def yt_mock(patch, load_json):
    class MockYt:
        @dataclasses.dataclass
        class YtData:
            count: int

        data = YtData(count=0)

        @staticmethod
        @patch(
            'corp_scoring.generated.cron.yt_wrapper.plugin.'
            'AsyncYTClient.read_table',
        )
        async def _read_table(*args, **kwargs):
            MockYt.data.count = MockYt.data.count + 1

            if MockYt.data.count == 1:
                return load_json('yt_data1.json')

            return load_json('yt_data2.json')

    return MockYt()


async def test_main(cron_context, mock_corp_clients, yt_mock):
    await run_cron.main(
        ['corp_scoring.crontasks.sync_tin_to_threshold_table', '-t', '0'],
    )

    table = await _get_synced_tins(cron_context)
    assert table['12345678'] == decimal.Decimal('-7777.12')
    assert table['22222222'] == decimal.Decimal('-6666.12')

    await run_cron.main(
        ['corp_scoring.crontasks.sync_tin_to_threshold_table', '-t', '0'],
    )

    table = await _get_synced_tins(cron_context)
    assert table['12345678'] == decimal.Decimal('-6666.12')
