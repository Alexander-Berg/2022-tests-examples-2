# pylint: disable=redefined-outer-name
import pytest

from hiring_sf_loader.generated.cron import run_cron


@pytest.mark.config(HIRING_SF_LOADER_SYNC_DISABLED={'stop_sync': True})
@pytest.mark.parametrize(
    'cron_name',
    [
        'sf_sync_cars',
        'sf_sync_leads',
        'sf_sync_assets',
        'sf_sync_cancelled_tasks',
        'sf_sync_organizations',
        'sf_sync_tasks',
        'update_assets_in_zd',
        'update_leads_in_zd',
    ],
)
async def test_sync_disabled(
        load_json,
        mock_salesforce_deleted,
        mock_salesforce_make_query,
        cron_name,
        cron_context,
):
    mock_sf_deleted = mock_salesforce_deleted({})
    mock_sf_make_query = mock_salesforce_make_query({})

    await run_cron.main(['hiring_sf_loader.crontasks.' + cron_name, '-t', '0'])

    assert not mock_sf_deleted.has_calls
    assert not mock_sf_make_query.has_calls
