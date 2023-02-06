import pytest

EXPECTED_YT_DATA_TABLE = 'expected_yt_data.json'
YT_STQ_TABLE = '//home/test/stq_table'


@pytest.mark.usefixtures('mock_salesforce_auth')
@pytest.mark.now('2021-09-15T10:00:00Z')
async def test_reschedule_task(
        stq_runner, mock_salesforce_job_info, stq, load_json,
):
    input_data = load_json('input_data.json')['reschedule']
    job_info_mock = mock_salesforce_job_info(input_data['job_info_mock'])
    await stq_runner.hiring_ensure_bulk_update_sent.call(
        **input_data['stq_args'],
    )

    assert job_info_mock.has_calls

    expected_data = load_json('expected_data.json')['reschedule']
    task = stq.hiring_ensure_bulk_update_sent.next_call()
    assert task == expected_data['stq_task']
    assert stq.is_empty


@pytest.mark.usefixtures('mock_salesforce_auth')
@pytest.mark.now('2021-09-15T10:00:00Z')
async def test_successful_task(
        stq_runner,
        mock_salesforce_job_info,
        mock_salesforce_successful,
        load_json,
):
    input_data = load_json('input_data.json')['success']
    job_info_mock = mock_salesforce_job_info(input_data['job_info_mock'])
    successful_results_mock = mock_salesforce_successful(
        input_data['successful_results'],
    )

    await stq_runner.hiring_ensure_bulk_update_sent.call(
        **input_data['stq_args'],
    )

    assert job_info_mock.has_calls
    assert successful_results_mock.has_calls


@pytest.mark.usefixtures('mock_salesforce_auth')
@pytest.mark.now('2021-09-15T10:00:00Z')
@pytest.mark.config(HIRING_API_FAILED_SF_LEADS_TABLE_PATH='//home/test/')
async def test_failed_task(
        stq_runner,
        mock_salesforce_job_info,
        mock_salesforce_successful,
        mock_salesforce_failed,
        mock_salesforce_unprocessed,
        yt_apply,
        yt_client,
        load_json,
):
    input_data = load_json('input_data.json')['failed']
    job_info_mock = mock_salesforce_job_info(input_data['job_info_mock'])
    successful_results_mock = mock_salesforce_successful(
        input_data['successful_results'],
    )
    failed_results_mock = mock_salesforce_failed(input_data['failed_results'])
    unprocessed_records_mock = mock_salesforce_unprocessed(
        input_data['unprocessed_records'],
    )

    await stq_runner.hiring_ensure_bulk_update_sent.call(
        **input_data['stq_args'],
    )

    assert job_info_mock.has_calls
    assert successful_results_mock.has_calls
    assert failed_results_mock.has_calls
    assert unprocessed_records_mock.has_calls

    expected_data = load_json('expected_data.json')['failed']['yt_results']
    rows = list(yt_client.read_table('//home/test/2021-09-15'))
    assert rows == expected_data


@pytest.mark.config(HIRING_FAILED_STQ_TABLE_PATH=YT_STQ_TABLE)
@pytest.mark.usefixtures('mock_salesforce_auth')
@pytest.mark.now('2022-09-15T10:00:00Z')
async def test_failed_joba_task(
        mock_salesforce_jobs_error, stq_runner, load_json, yt_client,
):
    input_data = load_json('input_data.json')['failed']
    mock_salesforce_jobs_error = mock_salesforce_jobs_error(
        404, ['SOME_ERROR_1'],
    )

    await stq_runner.hiring_ensure_bulk_update_sent.call(
        **input_data['stq_args'],
    )

    assert mock_salesforce_jobs_error.has_calls

    expected_yt_data = load_json(EXPECTED_YT_DATA_TABLE)
    rows = list(yt_client.read_table(YT_STQ_TABLE))
    assert rows[-1] == expected_yt_data
