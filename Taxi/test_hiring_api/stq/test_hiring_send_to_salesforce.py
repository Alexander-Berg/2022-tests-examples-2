import pytest


@pytest.mark.parametrize('case', ['201', '400'])
async def test_salesforce(
        load_json,
        stq_runner,
        stq3_context,
        simple_secdist,
        mock_salesforce_auth,
        mock_salesforce_create,
        case,
):
    request = load_json('ticket_data.json')[case]
    handler_salesforce = mock_salesforce_create(
        int(case), request['success'], request['errors'],
    )
    await stq_runner.hiring_send_to_salesforce.call(
        task_id='1',
        args=(),
        kwargs={'external_id': 'ID1', 'body': request['data']},
    )
    assert handler_salesforce.has_calls


@pytest.mark.now('2020-10-17T10:05:00+03:00')
@pytest.mark.config(HIRING_API_FAILED_SF_LEADS_TABLE_PATH='//home/test')
@pytest.mark.parametrize('case', ['400', '409', '422'])
async def test_sending_failed_lead_to_yt(
        load_json,
        stq_runner,
        stq3_context,
        simple_secdist,
        mock_salesforce_auth,
        mock_salesforce_error,
        yt_apply,
        case,
        yt_client,
):
    request = load_json('bad_ticket_data.json')[case]
    handler_salesforce = mock_salesforce_error(int(case), request['errors'])

    await stq_runner.hiring_send_to_salesforce.call(
        task_id='1',
        args=(),
        kwargs={'external_id': 'ID1', 'body': request['data']},
    )
    assert handler_salesforce.has_calls

    expected_data = load_json('expected_result_yt_data.json')[case]
    rows = list(yt_client.read_table('//home/test/2020-10-17'))
    assert rows == expected_data


@pytest.mark.now('2020-10-18T10:05:00+03:00')
@pytest.mark.config(HIRING_API_POSTPONED_SF_LEADS_TABLE_PATH='//home/test')
@pytest.mark.config(HIRING_API_CREATE_LEADS_IN_SALESFORCE=False)
@pytest.mark.parametrize('case', ['201'])
async def test_sending_postponed_lead_to_yt(
        load_json, stq_runner, case, yt_client,
):
    request = load_json('ticket_data.json')[case]
    await stq_runner.hiring_send_to_salesforce.call(
        task_id='1',
        args=(),
        kwargs={'external_id': 'ID1', 'body': request['data']},
    )
    expected_data = load_json('expected_result_yt_data.json')[case]
    rows = list(yt_client.read_table('//home/test/2020-10-18'))
    assert rows == expected_data
