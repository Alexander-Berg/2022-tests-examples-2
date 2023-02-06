# pylint: disable=redefined-outer-name
import datetime
from unittest import mock

import pytest

from hiring_sf_loader.generated.cron import run_cron


CRON_NAME = 'hiring_sf_loader.crontasks.sf_sync_tasks'
# queries with * are better for unintended consequences of db migrations :(
DATES_QUERY = (
    'SELECT sync_name, last_updated, last_deleted '
    'FROM hiring_sf_loader.sync_dates'
)
TASKS_QUERY = (
    'SELECT '
    'id, document, lead_id, task_id, line_id, '
    'received_at, request_id, priority '
    'FROM hiring_sf_loader.lead_documents'
)
YT_FAILED_TASKS_TABLE = '//home/test/2021-07-25'


@pytest.mark.config(HIRING_SF_LOADER_FAILED_TASKS_TABLE_PATH='//home/test')
@pytest.mark.config(
    HIRING_SF_LOADER_SYNC_DISABLED={'stop_sync': True, 'except': ['tasks']},
)
@pytest.mark.config(HIRING_SF_LOADER_DOWNLOAD_TASKS_ENABLE=True)
@pytest.mark.config(HIRING_SF_LOADER_TASK_SYNC_DELETION_ENABLED=False)
@pytest.mark.now('2021-07-25T12:00:00+0000')
@pytest.mark.usefixtures(
    'mock_salesforce_auth', 'mock_territories_api', 'personal',
)
async def test_sync_update_no_deletion_save_to_pg(
        # caplog,
        load_json,
        match_sf_query,
        pgsql,
        taxi_config,
        yt_client,
        mock_salesforce_deleted,
        mock_salesforce_make_query,
        mock_upsert_tasks,
):
    # arrange
    upsert_tasks_mock = mock_upsert_tasks(
        load_json('upsert_tasks_response.json'),
    )
    sf_deleted_mock = mock_salesforce_deleted(
        load_json('deleted_records.json'),
    )
    sf_query_mock = mock_salesforce_make_query(
        load_json(f'normal_sf_response.json'),
    )

    # act
    await run_cron.main([CRON_NAME, '-t', '0'])

    # assert
    assert sf_query_mock.times_called == 1
    query_request = sf_query_mock.next_call()['request']
    assert query_request.method == 'GET'
    assert dict(query_request.query) == {'q': mock.ANY}
    sf_query = match_sf_query(query_request.query['q'])
    expected_sf_query = load_json('sf_query_update.json')
    assert sf_query == expected_sf_query

    assert sf_deleted_mock.times_called == 1
    deleted_request = sf_deleted_mock.next_call()['request']
    assert deleted_request.method == 'GET'
    assert dict(deleted_request.query) == {
        'start': '2021-07-20T03:00:00+03:00',
        'end': '2021-07-25T15:00:00+03:00',
    }

    cursor = pgsql['hiring_sf_loader'].cursor()

    cursor.execute(DATES_QUERY)
    data = cursor.fetchall()
    assert data == [
        (
            'tasks',
            datetime.datetime(2021, 7, 25, 11, 50),
            datetime.datetime(2021, 7, 23, 11, 5),
        ),
    ]

    assert upsert_tasks_mock.times_called == 1
    upsert_request = upsert_tasks_mock.next_call()['request']
    assert upsert_request.method == 'POST'
    assert upsert_request.json == load_json('upsert_tasks_request.json')

    # check that in direct sending mode we don't save anything to posgres
    cursor.execute(TASKS_QUERY)
    data = cursor.fetchall()
    assert data == []

    yt_rows = list(yt_client.read_table(YT_FAILED_TASKS_TABLE))
    assert yt_rows == load_json('yt_logs.json')


@pytest.mark.config(HIRING_SF_LOADER_FAILED_TASKS_TABLE_PATH='//home/test')
@pytest.mark.config(HIRING_SF_LOADER_TASK_SYNC_DELETION_ENABLED=True)
@pytest.mark.config(HIRING_SF_LOADER_SYNC_DISABLED={'stop_sync': False})
@pytest.mark.config(HIRING_SF_LOADER_DOWNLOAD_TASKS_ENABLE=True)
@pytest.mark.now('2021-07-25T12:00:00+0000')
@pytest.mark.usefixtures(
    'mock_salesforce_auth', 'mock_territories_api', 'personal',
)
async def test_sync_update_straight_sending_and_deletion_enabled(
        caplog,
        load_json,
        match_sf_query,
        pgsql,
        taxi_config,
        mock_hiring_telephony_oktell_callback,
        cron_context,
        yt_client,
        mock_bulk_cancel_tasks,
        mock_salesforce_deleted,
        mock_salesforce_make_query,
        mock_upsert_tasks,
):
    # arrange
    upsert_tasks_mock = mock_upsert_tasks(
        load_json('upsert_tasks_response.json'),
    )
    bulk_cancel_tasks_mock = mock_bulk_cancel_tasks(
        {'cancelled_tasks': ['deleted_id']},
    )
    sf_deleted_mock = mock_salesforce_deleted(
        load_json('deleted_records.json'),
    )
    sf_query_mock = mock_salesforce_make_query(
        load_json(f'normal_sf_response.json'),
    )

    # act
    await run_cron.main([CRON_NAME, '-t', '0'])

    # assert
    assert sf_query_mock.times_called == 1
    query_request = sf_query_mock.next_call()['request']
    assert query_request.method == 'GET'
    assert dict(query_request.query) == {'q': mock.ANY}
    sf_query = match_sf_query(query_request.query['q'])
    expected_sf_query = load_json('sf_query_update.json')
    assert sf_query == expected_sf_query

    assert sf_deleted_mock.times_called == 1
    deleted_request = sf_deleted_mock.next_call()['request']
    assert deleted_request.method == 'GET'
    assert dict(deleted_request.query) == {
        'start': '2021-07-20T03:00:00+03:00',
        'end': '2021-07-25T15:00:00+03:00',
    }

    assert upsert_tasks_mock.times_called == 1
    upsert_request = upsert_tasks_mock.next_call()['request']
    assert upsert_request.method == 'POST'
    assert upsert_request.json == load_json('upsert_tasks_request.json')

    assert bulk_cancel_tasks_mock.times_called == 1
    bulk_cancel_tasks_request = bulk_cancel_tasks_mock.next_call()['request']
    assert bulk_cancel_tasks_request.method == 'POST'
    assert bulk_cancel_tasks_request.json == {'task_ids': ['deleted_id']}

    cursor = pgsql['hiring_sf_loader'].cursor()

    cursor.execute(DATES_QUERY)
    data = cursor.fetchall()
    assert data == [
        (
            'tasks',
            datetime.datetime(2021, 7, 25, 11, 50),
            datetime.datetime(2021, 7, 23, 11, 5),
        ),
    ]

    cursor.execute(TASKS_QUERY)
    data = cursor.fetchall()
    assert data == []  # straight sending does not require database entry


@pytest.mark.config(HIRING_SF_LOADER_FAILED_TASKS_TABLE_PATH='//home/test')
@pytest.mark.config(HIRING_SF_LOADER_DOWNLOAD_TASKS_ENABLE=False)
async def test_sync_update_download_disabled_raises(taxi_config, caplog):
    # arrange
    # act & assert
    with pytest.raises(RuntimeError) as exc:
        await run_cron.main([CRON_NAME, '-t', '0'])
    assert str(exc.value) == 'Crontask is stopped by Safe Mode Config'
    assert 'Crontask is stopped by Safe Mode Config' in caplog.messages


@pytest.mark.config(HIRING_SF_LOADER_DOWNLOAD_TASKS_ENABLE=True)
@pytest.mark.parametrize(
    'sync_disabled',
    [{'stop_sync': True, 'except': ['not_that_tasks']}, {'stop_sync': True}],
)
async def test_sync_update_sync_stopped(
        taxi_config, pgsql, caplog, sync_disabled,
):
    # arrange
    taxi_config.set_values({'HIRING_SF_LOADER_SYNC_DISABLED': sync_disabled})

    # act & assert
    await run_cron.main([CRON_NAME, '-t', '0'])
    assert (
        'SF sync stopped by config '
        'HIRING_SF_LOADER_SYNC_DISABLED' in caplog.messages
    )

    # checking that we made no changes in database
    cursor = pgsql['hiring_sf_loader'].cursor()
    cursor.execute(TASKS_QUERY)
    data = cursor.fetchall()
    assert data == []
