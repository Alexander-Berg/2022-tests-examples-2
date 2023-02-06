import json

import pytest

from billing_fin_payouts import db
from billing_fin_payouts.generated.cron import run_cron


@pytest.mark.now('2022-05-30T00:00:00.000000+00:00')
@pytest.mark.config(
    BILLING_FIN_PAYOUTS_UPLOAD_ENABLED=True,
    BILLING_FIN_PAYOUTS_LB_UPLOAD_SETTINGS_V2={
        '__default__': {
            'enabled': True,
            'pg_read_size': 10_000,
            'pg_overlap_offset': 0,
            'iterations': 1,
            'sleep_between_iterations': 0,
            'max_inflight': 1,
        },
    },
)
@pytest.mark.parametrize(
    'cron_name, expected_data_json',
    [
        pytest.param(
            'billing_fin_payouts.crontasks.upload_cpf_to_lb',
            'cash_payment_fact_expected_data.json',
            marks=[
                pytest.mark.pgsql(
                    dbname='billing_fin_payouts',
                    files=('cash_payment_fact_data.psql',),
                ),
            ],
        ),
        pytest.param(
            'billing_fin_payouts.crontasks.upload_accruals_to_lb',
            'accruals_expected_data.json',
            marks=[
                pytest.mark.pgsql(
                    dbname='billing_fin_payouts',
                    files=('accruals_data.psql',),
                ),
            ],
        ),
        pytest.param(
            'billing_fin_payouts.crontasks.upload_accruals_to_lb',
            'accruals_dry_expected_data.json',
            marks=[
                pytest.mark.pgsql(
                    dbname='billing_fin_payouts',
                    files=('accruals_dry_data.psql',),
                ),
            ],
        ),
    ],
)
async def test_upload_to_lb(
        patch, cron_context, load_json, cron_name, expected_data_json,
):
    expected_data = load_json(expected_data_json)
    expected_entries = expected_data['logbroker_entries']
    consumer_id = expected_data['consumer_id']

    data_chunk_sent = []

    @patch('billing_fin_payouts.logbroker.wrapper.LogbrokerWrapper.write')
    async def _write(data_chunk, topic, source_id, partition_group=None):
        assert topic == expected_data['topic']
        assert source_id == consumer_id
        assert partition_group is None
        json_chunks = [json.loads(event.data) for event in data_chunk]
        data_chunk_sent.append(json_chunks)

    cursor = await db.DBExportConsumerCursor.get_cursor(
        cron_context, [consumer_id],
    )
    assert cursor == expected_data['cursor_at_the_beginning']

    await run_cron.main([cron_name, '-t', '0'])

    assert data_chunk_sent == expected_entries

    cursor = await db.DBExportConsumerCursor.get_cursor(
        cron_context, [consumer_id],
    )
    assert cursor == expected_data['cursor_at_the_end']
