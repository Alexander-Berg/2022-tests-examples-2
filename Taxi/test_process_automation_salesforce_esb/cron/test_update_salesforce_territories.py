import pytest


@pytest.mark.yt(static_table_data=['yt_salesforce_territories.yaml'])
async def test_update_salesforce_territories(
        yt_apply,
        load_json,
        cron_runner,
        mock_salesforce_auth,
        mock_salesforce_create_bulk_job,
        mock_salesforce_upload_data,
        mock_salesforce_close_bulk_job,
        stq,
):
    # arrange
    expected_data = load_json('expected_data.json')
    sf_mock_create_bulk = mock_salesforce_create_bulk_job({'id': '123'})

    # act
    await cron_runner.update_salesforce_territories()

    # assert
    assert sf_mock_create_bulk.times_called == 2

    call = sf_mock_create_bulk.next_call()
    request = call['request']
    assert request.json == expected_data['first_create']

    call = sf_mock_create_bulk.next_call()
    request = call['request']
    assert request.json == expected_data['second_create']

    assert mock_salesforce_upload_data.times_called == 2

    call = mock_salesforce_upload_data.next_call()
    request = call['request']
    body = request.get_data().decode()
    assert body == expected_data['upload']
    assert call['job_id'] == expected_data['job_id']

    assert mock_salesforce_close_bulk_job.times_called == 2

    task = stq.hiring_ensure_bulk_update_sent.next_call()
    assert task == expected_data['task']

    task = stq.hiring_ensure_bulk_update_sent.next_call()
    assert task == expected_data['task']

    assert stq.is_empty
