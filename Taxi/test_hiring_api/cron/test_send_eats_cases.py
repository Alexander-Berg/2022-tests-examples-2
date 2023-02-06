import pytest


@pytest.mark.usefixtures('mock_salesforce_auth')
@pytest.mark.yt(static_table_data=['yt_to_call.yaml'])
async def test_send_eats_cases(
        cron_runner,
        simple_secdist,
        load_json,
        yt_apply,
        mock_salesforce_upload_data,
        mock_salesforce_create_bulk_job,
        mock_salesforce_close_bulk_job,
        mockserver,
):
    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _retrieve_phone(pd_request):
        result = []
        for item in pd_request.json['items']:
            pd_marker, phone = item['id'].split(':', 1)
            assert pd_marker == 'pd'
            result.append(dict(id=item['id'], value=phone))
        return dict(items=result)

    sf_mock_create_bulk = mock_salesforce_create_bulk_job(
        {'id': 'test_job_id'},
    )

    await cron_runner.send_eats_cases()

    expected_data = load_json('to_call.json')
    # array is more readable but it must be a string
    expected_data['sf_upload']['body'] = (
        '\r\n'.join(expected_data['sf_upload']['body']) + '\r\n'
    )

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
