# pylint: disable=redefined-outer-name
import datetime

import pytest

from corp_scoring.generated.cron import run_cron
from test_corp_scoring import conftest

BEGIN = datetime.datetime(2019, 7, 29, 12)
LONG_CONTRACT = '333/33aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'

RECORDS = [
    ['111/11', 111.11, (BEGIN + datetime.timedelta(days=2)).date()],
    ['222/22', 222.22, (BEGIN + datetime.timedelta(days=1)).date()],
    [LONG_CONTRACT, 333.33, (BEGIN + datetime.timedelta(days=5)).date()],
    ['111/11', 444.44, (BEGIN + datetime.timedelta(days=3)).date()],
    ['555/55', 555.55, (BEGIN + datetime.timedelta(days=3)).date()],
    ['444/44', 444.44, (BEGIN + datetime.timedelta(days=3)).date()],
]


@pytest.fixture
def mock_corp_clients(mockserver):
    class MockCorpClients:
        @staticmethod
        @mockserver.json_handler('/corp-clients/v1/contracts/by-external-ids')
        async def get_contracts(request):
            ext_contract_ids = request.json['contract_external_ids']
            contract_list = []
            for ext_contract_id in ext_contract_ids:
                contract_list.extend(
                    conftest.CONTRACTS.get(ext_contract_id, []),
                )
            return mockserver.make_response(
                json={'contracts': contract_list}, status=200,
            )

        @staticmethod
        @mockserver.json_handler('/corp-clients/v1/contracts/threshold/update')
        async def update_thresholds(request):
            if request.json['contract_id'] != 4:
                return mockserver.make_response(json={}, status=200)

            return mockserver.make_response(
                json={'message': 'Not Found'}, status=400,
            )

    return MockCorpClients()


async def _get_synced_contracts(context):
    contracts_synced = {}
    async with context.pg.master_pool.acquire(log_extra=None) as conn:
        async with conn.transaction():
            query = context.postgres_queries['local_pg/search_thresholds.sqlt']
            cursor = conn.cursor(query=query)
            async for record in cursor:
                contract_id = record['contract_id']
                if contract_id not in contracts_synced:
                    contracts_synced.update({contract_id: record})

    return contracts_synced


@pytest.mark.config(
    TVM_RULES=[{'dst': 'corp-clients', 'src': 'corp-scoring'}],
    CORP_SCORING_SYNC_CONTRACTS_CHUNK_SIZE=3,
)
async def test_sync_client_thresholds(cron_context, mock_corp_clients):
    async with cron_context.greenplum.get_connection() as greenplum_conn:
        await greenplum_conn.execute(
            f"""
        CREATE SCHEMA IF NOT EXISTS snb_b2b;""",
        )

        create_query = f"""
        CREATE TABLE  IF NOT EXISTS
        snb_b2b.ankozik_limit_recalculation_fin_changes(
        corp_contract_id VARCHAR,
        final_limit float,
        record_date DATE
        );
        """

        await greenplum_conn.execute(create_query)

        await greenplum_conn.copy_records_to_table(
            table_name='ankozik_limit_recalculation_fin_changes',
            schema_name='snb_b2b',
            records=RECORDS,
            columns=['corp_contract_id', 'final_limit', 'record_date'],
        )

    await run_cron.main(
        ['corp_scoring.crontasks.sync_client_thresholds', '-t', '0'],
    )

    assert mock_corp_clients.update_thresholds.has_calls
    call = mock_corp_clients.update_thresholds.next_call()['request'].json
    assert call['contract_id'] == 3

    rows = await _get_synced_contracts(cron_context)
    assert len(rows) == 1
    assert 3 in rows

    await run_cron.main(
        ['corp_scoring.crontasks.sync_client_thresholds', '-t', '0'],
    )

    assert not mock_corp_clients.update_thresholds.times_called == 1
