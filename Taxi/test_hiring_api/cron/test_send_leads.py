import pytest


@pytest.mark.usefixtures('mock_salesforce_auth')
@pytest.mark.yt(static_table_data=['yt_to_send.yaml'])
async def test_send_leads(
        cron_runner,
        simple_secdist,
        load_json,
        yt_apply,
        mock_salesforce_upload_data,
        mock_salesforce_create_bulk_job,
        mock_salesforce_close_bulk_job,
        mockserver,
):
    # arrange
    sf_mock_create_bulk = mock_salesforce_create_bulk_job(
        {'id': 'test_job_id'},
    )
    expected_data = load_json('leads.json')
    expected_data['sf_upload']['body'] = (
        '\r\n'.join(expected_data['sf_upload']['body']) + '\r\n'
    )  # array is more readable but it must be a string
    expected_sf_upload = expected_data['sf_upload']

    # act
    await cron_runner.send_leads()

    # assert

    assert sf_mock_create_bulk.has_calls
    create_bulk_call = sf_mock_create_bulk.next_call()
    create_bulk_request = create_bulk_call['request']
    assert create_bulk_request.json == expected_data['create_bulk']

    assert mock_salesforce_upload_data.has_calls

    salesforce_call = mock_salesforce_upload_data.next_call()
    assert salesforce_call['job_id'] == expected_sf_upload['job_id']

    salesforce_request = salesforce_call['request']
    assert salesforce_request.method == expected_sf_upload['method']
    assert (
        salesforce_request.content_type == expected_sf_upload['content_type']
    )

    salesforce_body = salesforce_request.get_data().decode()
    assert salesforce_body == expected_sf_upload['body']

    assert mock_salesforce_close_bulk_job.has_calls
