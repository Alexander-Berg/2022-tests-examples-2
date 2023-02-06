# pylint: disable=redefined-outer-name
import pytest

from hiring_sf_loader.generated.cron import run_cron


CRON_NAME = 'hiring_sf_loader.crontasks.sf_sync_cancelled_tasks'


@pytest.mark.now('2021-07-25T12:00:00+0000')
@pytest.mark.usefixtures(
    'mock_salesforce_auth', 'mock_territories_api', 'personal',
)
async def test_sync_cancelled_tasks(
        load_json,
        match_sf_query,
        mock_bulk_cancel_tasks,
        mock_salesforce_deleted,
        mock_salesforce_make_query,
        mock_hiring_telephony_oktell_callback,
):
    # arrange
    sf_deleted_mock = mock_salesforce_deleted(
        load_json('deleted_records.json'),
    )
    bulk_cancel_tasks_mock = mock_bulk_cancel_tasks(
        {
            'cancelled_tasks': [
                '00T7Y00000EOdWzUAL',
                '00T7Y00011EOdWzUAL',
                '00T7Y00010EOdWzUAL',
                '00T7Y00510EOdWzUAL',
            ],
        },
    )
    sf_query_mock = mock_salesforce_make_query(
        load_json('normal_sf_response.json'),
    )

    # act
    await run_cron.main([CRON_NAME, '-t', '0'])

    # assert
    assert sf_query_mock.times_called == 1
    query_call = sf_query_mock.next_call()
    request = query_call['request']
    sf_query = match_sf_query(request.query['q'])
    assert sf_query == load_json('sf_query_cancel.json')

    assert bulk_cancel_tasks_mock.times_called == 1
    assert bulk_cancel_tasks_mock.next_call()['request'].json == {
        'task_ids': [
            '00T7Y00000EOdWzUAL',
            '00T7Y00011EOdWzUAL',
            '00T7Y00010EOdWzUAL',
            '00T7Y00510EOdWzUAL',
        ],
    }

    assert sf_deleted_mock.times_called == 1
    deleted_query_call = sf_deleted_mock.next_call()['request']
    assert deleted_query_call.method == 'GET'
    assert dict(deleted_query_call.query) == {
        'start': '2021-07-20T03:00:00+03:00',
        'end': '2021-07-25T15:00:00+03:00',
    }


@pytest.mark.now('2021-07-25T12:00:00+0000')
@pytest.mark.usefixtures(
    'mock_salesforce_auth', 'mock_territories_api', 'personal',
)
async def test_sync_cancelled_tasks_empty_response_not_called(
        load_json,
        match_sf_query,
        yt_client,
        mock_bulk_cancel_tasks,
        mock_salesforce_deleted,
        mock_salesforce_make_query,
        mock_hiring_telephony_oktell_callback,
):
    # arrange
    sf_deleted_mock = mock_salesforce_deleted(
        load_json('deleted_records.json'),
    )
    bulk_cancel_tasks_mock = mock_bulk_cancel_tasks(
        {
            'cancelled_tasks': [
                'some_non_existent_task_id_1',
                'some_non_existent_task_id_2',
            ],
        },
    )
    sf_query_mock = mock_salesforce_make_query(
        load_json('empty_sf_response.json'),
    )

    # act
    await run_cron.main([CRON_NAME, '-t', '0'])

    # assert
    assert sf_query_mock.times_called == 1
    query_call = sf_query_mock.next_call()['request']
    sf_query = match_sf_query(query_call.query['q'])
    assert sf_query == load_json('sf_query_cancel.json')

    # cancellation in telephony should not be called
    assert bulk_cancel_tasks_mock.times_called == 0

    assert sf_deleted_mock.times_called == 1
    deleted_query_call = sf_deleted_mock.next_call()['request']
    assert deleted_query_call.method == 'GET'
    assert dict(deleted_query_call.query) == {
        'start': '2021-07-20T03:00:00+03:00',
        'end': '2021-07-25T15:00:00+03:00',
    }


@pytest.mark.now('2022-02-22T12:00:00+0000')
@pytest.mark.usefixtures(
    'mock_salesforce_auth', 'mock_territories_api', 'personal',
)
async def test_sync_cancelled_tasks_some_not_cancelled_send_to_yt(
        load_json,
        match_sf_query,
        mock_bulk_cancel_tasks,
        mock_salesforce_deleted,
        mock_salesforce_make_query,
        mock_hiring_telephony_oktell_callback,
):
    # arrange
    sf_deleted_mock = mock_salesforce_deleted(
        load_json('deleted_records.json'),
    )
    bulk_cancel_tasks_mock = mock_bulk_cancel_tasks(
        {'cancelled_tasks': ['00T7Y00000EOdWzUAL', '00T7Y00010EOdWzUAL']},
    )
    sf_query_mock = mock_salesforce_make_query(
        load_json('normal_sf_response.json'),
    )

    # act
    await run_cron.main([CRON_NAME, '-t', '0'])

    # assert
    assert sf_query_mock.times_called == 1
    query_call = sf_query_mock.next_call()
    request = query_call['request']
    sf_query = match_sf_query(request.query['q'])
    assert sf_query == load_json('sf_query_cancel.json')

    assert bulk_cancel_tasks_mock.times_called == 1
    bulk_cancel_tasks_request = bulk_cancel_tasks_mock.next_call()['request']
    assert bulk_cancel_tasks_request.method == 'POST'
    assert bulk_cancel_tasks_request.json == {
        'task_ids': [
            '00T7Y00000EOdWzUAL',
            '00T7Y00011EOdWzUAL',
            '00T7Y00010EOdWzUAL',
            '00T7Y00510EOdWzUAL',
        ],
    }

    assert sf_deleted_mock.times_called == 1
    deleted_query_call = sf_deleted_mock.next_call()['request']
    assert deleted_query_call.method == 'GET'
    assert dict(deleted_query_call.query) == {
        'start': '2022-02-08T15:00:00+03:00',
        'end': '2022-02-22T15:00:00+03:00',
    }
