# pylint: disable=redefined-outer-name
import pytest

from hiring_sf_loader.generated.cron import run_cron

CRON_NAME = 'hiring_sf_loader.crontasks.update_assets_in_zd'
DATES_QUERY = (
    'SELECT last_updated, last_deleted FROM hiring_sf_loader.sync_dates '
    'WHERE sync_name = \'update_assets_in_zd\''
)


@pytest.mark.parametrize(
    'sync_enabled_config',
    [
        {'stop_sync': True, 'except': ['update_assets_in_zd']},
        {'stop_sync': False},
    ],
)
@pytest.mark.now('2021-07-25T12:00:00+0000')
@pytest.mark.config(HIRING_SF_LOADER_UPDATE_ZD_ENABLE=True)
@pytest.mark.usefixtures('mock_salesforce_auth', 'mock_territories_api')
async def test_sync_update_assets(
        load_json,
        mock_salesforce_deleted,
        mock_salesforce_make_query,
        mock_api_sync_update,
        match_sf_query,
        get_mock_calls_json,
        pgsql,
        taxi_config,
        sync_enabled_config,
        cron_context,
):
    taxi_config.set_values(
        {'HIRING_SF_LOADER_SYNC_DISABLED': sync_enabled_config},
    )

    # initialize
    sf_responses = load_json('sf_responses.json')
    mock_salesforce_deleted(sf_responses['deleted'])
    sf_query_mock = mock_salesforce_make_query(sf_responses['query'])
    expected_data = load_json('expected_data.json')

    # run
    await run_cron.main([CRON_NAME, '-t', '0'])

    # check
    assert sf_query_mock.has_calls
    query_call = sf_query_mock.next_call()
    request = query_call['request']
    sf_query = match_sf_query(request.query['q'])
    assert sf_query == expected_data['sf_query_update']

    assert mock_api_sync_update.has_calls
    upsert_call = mock_api_sync_update.next_call()
    request = upsert_call['request']
    data = request.json
    assert data == expected_data['cabinets_upsert']

    cursor = pgsql['hiring_sf_loader'].cursor()
    cursor.execute(DATES_QUERY)
    row = list(next(cursor))
    assert row == expected_data['new_dates_update']


@pytest.mark.now('2021-07-25T12:00:00+0000')
@pytest.mark.config(HIRING_SF_LOADER_UPDATE_ZD_ENABLE=False)
async def test_update_zd_fallback(mock_api_sync_update):
    await run_cron.main([CRON_NAME, '-t', '0'])
    assert not mock_api_sync_update.has_calls
