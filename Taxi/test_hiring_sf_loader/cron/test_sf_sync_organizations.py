# pylint: disable=redefined-outer-name
import pytest

from hiring_sf_loader.generated.cron import run_cron


CRON_NAME = 'hiring_sf_loader.crontasks.sf_sync_organizations'
DATES_QUERY = (
    'SELECT last_updated, last_deleted FROM hiring_sf_loader.sync_dates '
    'WHERE sync_name = \'organization\''
)


@pytest.mark.parametrize(
    'sync_enabled_config',
    [{'stop_sync': True, 'except': ['organization']}, {'stop_sync': False}],
)
@pytest.mark.now('2021-07-25T12:00:00+0000')
@pytest.mark.usefixtures('mock_salesforce_auth')
async def test_sync_expired(
        load_json,
        mock_salesforce_deleted,
        mock_salesforce_make_query,
        mock_partners_app_sync_delete,
        mock_partners_app_sync_upsert,
        match_sf_query,
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
    sf_deleted_mock = mock_salesforce_deleted(sf_responses['deleted'])
    sf_query_mock = mock_salesforce_make_query(sf_responses['query'])
    expected_data = load_json('expected_data.json')

    # run
    await run_cron.main([CRON_NAME, '-t', '0'])

    # check
    assert sf_deleted_mock.has_calls
    deleted_call = sf_deleted_mock.next_call()
    assert deleted_call['sobject'] == 'Account'
    request = deleted_call['request']
    assert request.query['start'] == '2021-07-11T15:00:00+03:00'

    assert sf_query_mock.has_calls
    query_call = sf_query_mock.next_call()
    request = query_call['request']
    sf_query = match_sf_query(request.query['q'])
    assert sf_query == expected_data['sf_query_expired']

    assert mock_partners_app_sync_upsert.has_calls
    upsert_call = mock_partners_app_sync_upsert.next_call()
    request = upsert_call['request']
    data = request.json
    assert data == expected_data['partners_app_upsert']

    cursor = pgsql['hiring_sf_loader'].cursor()
    cursor.execute(DATES_QUERY)
    row = list(next(cursor))
    assert row == expected_data['new_dates_update']


@pytest.mark.now('2021-07-25T12:00:00+0000')
@pytest.mark.usefixtures('mock_salesforce_auth')
async def test_sync_update(
        load_json,
        mock_salesforce_deleted,
        mock_salesforce_make_query,
        mock_partners_app_sync_delete,
        mock_partners_app_sync_upsert,
        match_sf_query,
        pgsql,
):
    # initialize
    sf_responses = load_json('sf_responses.json')
    sf_deleted_mock = mock_salesforce_deleted(sf_responses['deleted'])
    sf_query_mock = mock_salesforce_make_query(sf_responses['query'])
    expected_data = load_json('expected_data.json')

    # run
    await run_cron.main([CRON_NAME, '-t', '0'])

    # check
    assert sf_deleted_mock.has_calls
    deleted_call = sf_deleted_mock.next_call()
    assert deleted_call['sobject'] == 'Account'

    assert sf_query_mock.has_calls
    query_call = sf_query_mock.next_call()
    request = query_call['request']
    sf_query = match_sf_query(request.query['q'])
    assert sf_query == expected_data['sf_query_update']

    assert mock_partners_app_sync_delete.has_calls
    delete_call = mock_partners_app_sync_delete.next_call()
    request = delete_call['request']
    data = request.json
    assert data == expected_data['partners_app_delete']

    assert mock_partners_app_sync_upsert.has_calls
    upsert_call = mock_partners_app_sync_upsert.next_call()
    request = upsert_call['request']
    data = request.json
    assert data == expected_data['partners_app_upsert']

    cursor = pgsql['hiring_sf_loader'].cursor()
    cursor.execute(DATES_QUERY)
    row = list(next(cursor))
    assert row == expected_data['new_dates_update']
