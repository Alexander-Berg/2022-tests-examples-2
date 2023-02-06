# pylint: disable=redefined-outer-name
import pytest

from clowny_quotas.generated.cron import run_cron


@pytest.mark.config(CLOWNY_QUOTAS_DATA_TTL_HOURS={'ttl': 24 * 7 * 2})
@pytest.mark.usefixtures('taxi_clowny_quotas_mocks')
async def test_quotas_db_cleanup(web_context):

    await run_cron.main(
        ['clowny_quotas.crontasks.quotas_db_cleanup', '-t', '0'],
    )

    pool = web_context.postgresql.clowny_quotas[0]
    db_resp = await pool.primary_fetch('SELECT COUNT(*) FROM quotas.quotas;')
    print(db_resp)
    assert db_resp[0]['count'] == 3
