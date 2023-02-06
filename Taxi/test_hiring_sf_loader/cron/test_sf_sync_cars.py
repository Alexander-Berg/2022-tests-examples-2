# pylint: disable=redefined-outer-name
from unittest import mock

import pytest


DATES_QUERY = (
    'SELECT sync_name, last_updated, last_deleted '
    'FROM hiring_sf_loader.sync_dates'
)


@pytest.mark.parametrize(
    'sync_enabled_config',
    [{'stop_sync': True, 'except': ['cars']}, {'stop_sync': False}],
)
@pytest.mark.now('2021-07-25T12:00:00+0000')
@pytest.mark.usefixtures(
    'mock_salesforce_auth', 'mock_territories_api', 'personal',
)
async def test_sf_sync_cars_delete_and_upsert(
        load_json,
        match_sf_query,
        pgsql,
        mock_salesforce_deleted,
        mock_salesforce_make_query,
        mock_bulk_delete_cars,
        mock_upsert_cars,
        taxi_config,
        sync_enabled_config,
        cron_runner,
):
    # arrange
    taxi_config.set_values(
        {'HIRING_SF_LOADER_SYNC_DISABLED': sync_enabled_config},
    )
    sf_deleted_mock = mock_salesforce_deleted(
        load_json('deleted_records.json'),
    )
    sf_query_mock = mock_salesforce_make_query(load_json('sf_response.json'))
    bulk_delete_cars_mock = mock_bulk_delete_cars(
        load_json('delete_cars_response.json'),
    )
    upsert_cars_mock = mock_upsert_cars(load_json('upsert_cars_response.json'))
    expected_sf_query = load_json('expected_sf_query.json')
    expected_upsert_request = load_json('expected_upsert_request.json')
    expected_sync_dates = load_json('expected_sync_dates.json')
    expected_deleted_request = load_json('expected_deleted_request.json')

    # act
    await cron_runner.sf_sync_cars()

    # assert
    assert sf_query_mock.times_called == 1
    query_request = sf_query_mock.next_call()['request']
    assert query_request.method == 'GET'
    assert dict(query_request.query) == {'q': mock.ANY}
    sf_query = match_sf_query(query_request.query['q'])
    assert sf_query == expected_sf_query

    assert sf_deleted_mock.times_called == 1
    deleted_request = sf_deleted_mock.next_call()['request']
    assert deleted_request.method == 'GET'
    assert dict(deleted_request.query) == expected_deleted_request

    bulk_delete_cars_request = bulk_delete_cars_mock.next_call()['request']
    assert bulk_delete_cars_request.method == 'POST'
    assert bulk_delete_cars_request.json == {'ids': ['deleted_id']}

    upsert_cars_request = upsert_cars_mock.next_call()['request']
    assert upsert_cars_request.method == 'POST'
    assert upsert_cars_request.json == expected_upsert_request

    cursor = pgsql['hiring_sf_loader'].cursor()

    cursor.execute(DATES_QUERY)
    sync_name, last_updated, last_deleted = cursor.fetchone()
    assert [
        sync_name,
        str(last_updated),
        str(last_deleted),
    ] == expected_sync_dates


@pytest.mark.now('2021-07-25T12:00:00+0000')
@pytest.mark.usefixtures(
    'mock_salesforce_auth', 'mock_territories_api', 'personal',
)
async def test_sf_sync_cars_empty(
        load_json,
        match_sf_query,
        pgsql,
        mock_salesforce_deleted,
        mock_salesforce_make_query,
        mock_bulk_delete_cars,
        mock_upsert_cars,
        caplog,
        cron_runner,
):
    # arrange
    sf_deleted_mock = mock_salesforce_deleted(
        load_json('deleted_records.json'),
    )
    sf_query_mock = mock_salesforce_make_query(load_json('sf_response.json'))
    bulk_delete_cars_mock = mock_bulk_delete_cars({})
    upsert_cars_mock = mock_upsert_cars({})
    expected_sf_query = load_json('expected_sf_query.json')
    expected_sync_dates = load_json('expected_sync_dates.json')
    expected_deleted_request = load_json('expected_deleted_request.json')

    # act
    await cron_runner.sf_sync_cars()

    # assert
    assert sf_query_mock.times_called == 1
    query_request = sf_query_mock.next_call()['request']
    assert query_request.method == 'GET'
    assert dict(query_request.query) == {'q': mock.ANY}
    sf_query = match_sf_query(query_request.query['q'])
    assert sf_query == expected_sf_query

    assert sf_deleted_mock.times_called == 1
    deleted_request = sf_deleted_mock.next_call()['request']
    assert deleted_request.method == 'GET'
    assert dict(deleted_request.query) == expected_deleted_request

    assert bulk_delete_cars_mock.times_called == 0
    assert upsert_cars_mock.times_called == 0

    cursor = pgsql['hiring_sf_loader'].cursor()

    cursor.execute(DATES_QUERY)
    sync_name, last_updated, last_deleted = cursor.fetchone()
    assert [
        sync_name,
        str(last_updated),
        str(last_deleted),
    ] == expected_sync_dates
