import pytest


@pytest.mark.yt(static_table_data=['yt_carsharing_transactions.yaml'])
async def test_fetch_carsharing_transactions(
        yt_apply,
        load_json,
        cron_runner,
        mock_salesforce_auth,
        mock_salesforce_create_bulk_job,
        mock_salesforce_upload_data,
        mock_salesforce_close_bulk_job,
):
    sf_response = load_json('salesforce_response.json')
    sf_mock_create_bulk = mock_salesforce_create_bulk_job({'id': '123'})

    await cron_runner.fetch_carsharing_transactions()

    assert sf_mock_create_bulk.times_called == 1

    call = sf_mock_create_bulk.next_call()
    request = call['request']
    assert request.json == sf_response['create']

    assert mock_salesforce_upload_data.times_called == 1

    call = mock_salesforce_upload_data.next_call()
    request = call['request']
    body = request.get_data().decode()
    assert body == sf_response['upload']
    assert call['job_id'] == sf_response['job_id']

    assert mock_salesforce_close_bulk_job.times_called == 1
