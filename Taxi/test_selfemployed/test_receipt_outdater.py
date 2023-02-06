import pytest

from selfemployed.db import dbreceipts
from selfemployed.scripts import run_script
from . import conftest


_EXPECTED_STATUSES = {
    1: {'order1': 'new', 'order2': 'outdated'},
    0: {'order3': 'new', 'order4': 'outdated'},
}


@pytest.mark.pgsql('selfemployed_orders@0', files=['receipts@0.sql'])
@pytest.mark.pgsql('selfemployed_orders@1', files=['receipts@1.sql'])
@pytest.mark.translations(taximeter_backend_selfemployed=conftest.TRANSLATIONS)
async def test_receipt_sync(
        se_cron_context, mock_token_update, patch, monkeypatch,
):

    await run_script.main(
        [
            'selfemployed.scripts.receipt_outdater',
            '-t',
            '0',
            '--to=2020-01-02T00:00',
        ],
    )

    pg_ = se_cron_context.pg

    for shard in dbreceipts.iterate_shard_nums(pg_):
        for rid, status in _EXPECTED_STATUSES[shard].items():
            receipt = await dbreceipts.get_receipt(pg_, shard, rid)
            assert receipt['status'] == status
