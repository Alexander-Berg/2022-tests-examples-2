import pytest


@pytest.mark.usefixtures('mock_salesforce_auth', 'mock_personal_api')
@pytest.mark.yt(static_table_data=['yt_driver_journeys.yaml'])
async def test_sending_failed_lead_to_yt(
        cron_runner,
        simple_secdist,
        load_json,
        yt_apply,
        mock_salesforce_upload_data,
        mock_salesforce_create_bulk_job,
        mock_salesforce_close_bulk_job,
        stq,
):
    # arrange
    expected_data = load_json('expected_data.json')
    expected_sf_upload = expected_data['sf_upload']

    sf_mock_create_bulk = mock_salesforce_create_bulk_job(
        {'id': 'test_job_id'},
    )

    # act
    await cron_runner.send_driver_journeys()

    # assert
    call = sf_mock_create_bulk.next_call()
    request = call['request']
    assert request.json == expected_data['create_bulk']

    request = sf_mock_create_bulk.next_call()['request']
    assert request.json == expected_data['create_bulk']

    call = mock_salesforce_upload_data.next_call()
    assert call['job_id'] == expected_sf_upload['job_id']

    request = call['request']
    assert request.method == expected_sf_upload['method']
    assert request.content_type == expected_sf_upload['content_type']

    body = request.get_data().decode()
    assert body == expected_sf_upload['body_first']

    request = mock_salesforce_upload_data.next_call()['request']
    assert request.get_data().decode() == expected_sf_upload['body_second']

    assert mock_salesforce_close_bulk_job.has_calls

    task = stq.hiring_ensure_bulk_update_sent.next_call()
    assert task == expected_data['task']
    task = stq.hiring_ensure_bulk_update_sent.next_call()
    assert task == expected_data['task']
    assert stq.is_empty


@pytest.mark.config(
    HIRING_API_ARRAY_DRIVER_JOURNEYS_SETTINGS=[
        {'path_to_yt_table': '//not/existing/table'},
    ],
)
async def test_not_existing_table(
        cron_runner, mock_salesforce_create_bulk_job,
):
    # arrange
    sf_mock_create_bulk = mock_salesforce_create_bulk_job({})

    # act
    await cron_runner.send_driver_journeys()

    # assert
    assert not sf_mock_create_bulk.has_calls


@pytest.mark.config(HIRING_API_ARRAY_DRIVER_JOURNEYS_SETTINGS=[])
async def test_empty_config(cron_runner, mock_salesforce_create_bulk_job):
    # arrange
    sf_mock_create_bulk = mock_salesforce_create_bulk_job({})

    # act
    await cron_runner.send_driver_journeys()

    # assert
    assert not sf_mock_create_bulk.has_calls
