import pytest

from hiring_taxiparks_gambling.internal.salesforce import db


async def test_db_fetch_for_taximeter(cron_context, load_json):
    expected_parks = load_json('expected_db_result.json')
    result = await db.fetch_for_taximeter(cron_context)
    assert expected_parks == list(result)


@pytest.mark.config(ENABLE_TAXIMETER_SF_PARKS_SYNC=False)
async def test_run_disabled_cron(cron_runner):
    await cron_runner.sf_sync_with_taximeter()


@pytest.mark.usefixtures('mock_taximeter_parks')
@pytest.mark.config(ENABLE_TAXIMETER_SF_PARKS_SYNC=True)
async def test_run_cron(cron_runner, mock_taximeter_parks):
    await cron_runner.sf_sync_with_taximeter()
