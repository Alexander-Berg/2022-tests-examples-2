import pytest


@pytest.mark.config(HIRING_API_ZD_ACTIVES_YT_TABLE='//home/test/zd_tickets')
@pytest.mark.usefixtures('mock_salesforce_auth')
@pytest.mark.yt(static_table_data=['yt_zd_tickets.yaml'])
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
    expected_data = load_json('expected_data.json')
    sf_mock_create_bulk = mock_salesforce_create_bulk_job(
        {'id': 'test_job_id'},
    )

    await cron_runner.send_zd_actives_to_sf()

    assert sf_mock_create_bulk.has_calls
    call = sf_mock_create_bulk.next_call()
    request = call['request']
    assert request.json == expected_data['create_bulk']

    assert mock_salesforce_upload_data.has_calls

    expected_sf_upload = expected_data['sf_upload']

    call = mock_salesforce_upload_data.next_call()
    assert call['job_id'] == expected_sf_upload['job_id']

    request = call['request']
    assert request.method == expected_sf_upload['method']
    assert request.content_type == expected_sf_upload['content_type']

    body = request.get_data().decode()
    assert body == expected_sf_upload['body']

    assert mock_salesforce_close_bulk_job.has_calls

    task = stq.hiring_ensure_bulk_update_sent.next_call()
    assert task == expected_data['task']
    assert stq.is_empty


@pytest.mark.config(HIRING_API_ZD_ACTIVES_YT_TABLE='//not/existing/table')
async def test_not_existing_table(cron_runner, yt_apply):
    with pytest.raises(RuntimeError):
        await cron_runner.send_zd_actives_to_sf()


async def test_empty_config(cron_runner, yt_apply):
    with pytest.raises(RuntimeError):
        await cron_runner.send_zd_actives_to_sf()
