import pytest

EXPECTED_STQ_REQUEST = 'expected_stq_request.json'
EXPECTED_YT_DATA_TABLE = 'expected_yt_data.json'
SF_RESPONSES_FILE = 'sf_responses.json'
YT_STQ_TABLE = '//home/test/stq_table'
STQ_KWARGS = 'stq_kwargs.json'
LEAD_ID = 'ID1'


@pytest.mark.now('2022-09-15T10:00:00Z')
@pytest.mark.usefixtures('mock_salesforce_auth')
@pytest.mark.config(
    HIRING_FAILED_STQ_CRM_UPSERT_LEAD_WITH_ASSET_PATH=YT_STQ_TABLE,
)
@pytest.mark.parametrize('status', [200, 400, 404, 405, 409])
@pytest.mark.parametrize('case', ['simple', 'custom_asset_fields'])
async def test_create_lead_and_create_asset(
        stq_runner,
        mock_salesforce_composite,
        mock_salesforce_find_lead,
        mock_personal_api,
        load_json,
        yt_client,
        case,
        status,
        mock_stq_queue,
):
    kwargs = load_json(STQ_KWARGS)[case]
    mock_salesforce_composite = mock_salesforce_composite(status)
    mock_salesforce_find_lead = mock_salesforce_find_lead()

    await stq_runner.hiring_crm_upsert_lead_with_asset.call(
        args=(), kwargs=kwargs,
    )
    assert mock_stq_queue.times_called == 1
    stq_call = mock_stq_queue.next_call()
    stq_call_request = stq_call['request']
    stq_call_json = stq_call_request.json
    expected_stq_request = load_json(EXPECTED_STQ_REQUEST)[case]
    expected_stq_request['args'].append(expected_stq_request['task_id'])
    assert stq_call_json == expected_stq_request

    assert mock_salesforce_composite.has_calls
    assert mock_salesforce_find_lead.times_called == 1

    if status >= 400:
        expected_yt_data = load_json(EXPECTED_YT_DATA_TABLE)[case]
        rows = list(yt_client.read_table(YT_STQ_TABLE))
        assert rows[-1] == expected_yt_data


@pytest.mark.now('2022-09-15T10:00:00Z')
@pytest.mark.usefixtures('mock_salesforce_auth')
@pytest.mark.config(
    HIRING_FAILED_STQ_CRM_UPSERT_LEAD_WITH_ASSET_PATH=YT_STQ_TABLE,
)
@pytest.mark.parametrize(
    'status, sf_resp',
    [(201, '2xx'), (400, '4xx'), (405, '4xx'), (409, '4xx')],
)
async def test_create_lead(
        mock_salesforce_auth,
        mock_salesforce_create,
        mock_salesforce_find_lead,
        mock_territories_api,
        load_json,
        stq_runner,
        stq3_context,
        simple_secdist,
        mock_stq_queue,
        yt_client,
        status,
        sf_resp,
):
    kwargs = load_json(STQ_KWARGS)['single_lead']
    request = load_json(SF_RESPONSES_FILE)[sf_resp]
    handler_salesforce = mock_salesforce_create(
        status, request['success'], request['errors'],
    )
    mock_salesforce_find_lead = mock_salesforce_find_lead()
    await stq_runner.hiring_crm_upsert_lead_with_asset.call(
        args=(), kwargs=kwargs,
    )

    assert mock_salesforce_find_lead.has_calls
    assert handler_salesforce.has_calls
    assert mock_stq_queue.times_called == 1
    stq_call = mock_stq_queue.next_call()
    stq_call_request = stq_call['request']
    stq_call_json = stq_call_request.json
    expected_stq_request = load_json(EXPECTED_STQ_REQUEST)['single_lead']
    expected_stq_request['args'].append(expected_stq_request['task_id'])
    assert stq_call_json == expected_stq_request

    if status >= 400:
        expected_yt_data = load_json(EXPECTED_YT_DATA_TABLE)['single_lead']
        rows = list(yt_client.read_table(YT_STQ_TABLE))
        assert rows[-1] == expected_yt_data


@pytest.mark.usefixtures('mock_salesforce_auth')
async def test_create_empty_lead(
        mock_salesforce_auth,
        mock_salesforce_create,
        mock_salesforce_find_lead,
        mock_territories_api,
        load_json,
        stq_runner,
        stq3_context,
        simple_secdist,
        mock_stq_queue,
):
    kwargs = load_json(STQ_KWARGS)['empty_lead']
    request = load_json(SF_RESPONSES_FILE)['4xx']
    handler_salesforce = mock_salesforce_create(
        400, request['success'], request['errors'],
    )
    mock_salesforce_find_lead = mock_salesforce_find_lead()
    await stq_runner.hiring_crm_upsert_lead_with_asset.call(
        args=(), kwargs=kwargs,
    )

    assert mock_stq_queue.times_called == 0
    assert not mock_salesforce_find_lead.has_calls
    assert not handler_salesforce.has_calls


@pytest.mark.now('2022-09-15T10:00:00Z')
@pytest.mark.usefixtures('mock_salesforce_auth')
@pytest.mark.config(
    HIRING_FAILED_STQ_CRM_UPSERT_LEAD_WITH_ASSET_PATH=YT_STQ_TABLE,
)
@pytest.mark.parametrize(
    'status, sf_resp',
    [(204, '2xx'), (400, '4xx'), (405, '4xx'), (409, '4xx')],
)
async def test_update_lead(
        mock_salesforce_auth,
        mock_salesforce_update,
        mock_salesforce_find_lead,
        mock_territories_api,
        mock_stq_queue,
        load_json,
        stq_runner,
        status,
        sf_resp,
        stq3_context,
        simple_secdist,
        yt_client,
):
    kwargs = load_json(STQ_KWARGS)['single_lead']
    request = load_json(SF_RESPONSES_FILE)[sf_resp]
    handler_salesforce = mock_salesforce_update(
        LEAD_ID, status, request['success'], request['errors'],
    )
    mock_salesforce_find_lead = mock_salesforce_find_lead(LEAD_ID)
    await stq_runner.hiring_crm_upsert_lead_with_asset.call(
        args=(), kwargs=kwargs,
    )
    assert mock_stq_queue.times_called == 1
    stq_call = mock_stq_queue.next_call()
    assert mock_salesforce_find_lead.has_calls
    assert handler_salesforce.has_calls
    stq_call_request = stq_call['request']
    stq_call_json = stq_call_request.json
    expected_stq_request = load_json(EXPECTED_STQ_REQUEST)['single_lead']
    expected_stq_request['args'].append(expected_stq_request['task_id'])
    assert stq_call_json == expected_stq_request

    if status >= 400:
        expected_yt_data = load_json(EXPECTED_YT_DATA_TABLE)['single_lead_upd']
        rows = list(yt_client.read_table(YT_STQ_TABLE))
        assert rows[-1] == expected_yt_data


@pytest.mark.parametrize('found_asset', ['not_exist', 'car', 'not_car'])
@pytest.mark.now('2022-09-15T10:00:00Z')
@pytest.mark.usefixtures('mock_salesforce_auth')
@pytest.mark.config(
    HIRING_FAILED_STQ_CRM_UPSERT_LEAD_WITH_ASSET_PATH=YT_STQ_TABLE,
)
@pytest.mark.parametrize('status', [200, 400, 405, 409])
async def test_update_lead_and_upsert_asset(
        mock_salesforce_auth,
        mock_salesforce_find_lead,
        mock_territories_api,
        mock_stq_queue,
        mock_salesforce_make_query,
        mock_salesforce_composite,
        mock_personal_api,
        load_json,
        stq_runner,
        stq3_context,
        simple_secdist,
        found_asset,
        status,
        yt_client,
):
    kwargs = load_json(STQ_KWARGS)['custom_asset_fields']
    sf_response = load_json(SF_RESPONSES_FILE)
    mock_salesforce_find_lead = mock_salesforce_find_lead(LEAD_ID)
    mock_salesforce_composite = mock_salesforce_composite(status)
    mock_salesforce_make_query = mock_salesforce_make_query(
        sf_response[found_asset],
    )
    await stq_runner.hiring_crm_upsert_lead_with_asset.call(
        args=(), kwargs=kwargs,
    )
    assert mock_salesforce_composite.has_calls
    assert mock_stq_queue.times_called == 1
    stq_call = mock_stq_queue.next_call()
    assert mock_salesforce_find_lead.has_calls
    assert mock_salesforce_make_query.has_calls
    stq_call_request = stq_call['request']
    stq_call_json = stq_call_request.json
    expected_stq_request = load_json(EXPECTED_STQ_REQUEST)[
        'custom_asset_fields'
    ]
    expected_stq_request['args'].append(expected_stq_request['task_id'])
    assert stq_call_json == expected_stq_request

    if status >= 400:
        expected_yt_data = load_json(EXPECTED_YT_DATA_TABLE)[
            'custom_asset_fields_upd'
        ]
        rows = list(yt_client.read_table(YT_STQ_TABLE))
        if found_asset in ('not_exist', 'not_car'):
            expected_yt_data['data']['car_id'] = None
        assert rows[-1] == expected_yt_data


@pytest.mark.now('2022-09-15T10:00:00Z')
@pytest.mark.usefixtures('mock_salesforce_auth')
async def test_composite_limit_exceeded(
        stq_runner,
        mock_salesforce_composite,
        mock_salesforce_find_lead,
        mock_personal_api,
        load_json,
        yt_client,
        mock_stq_queue,
):
    kwargs = load_json(STQ_KWARGS)['simple']
    mock_salesforce_composite = mock_salesforce_composite(403)
    mock_salesforce_find_lead = mock_salesforce_find_lead()
    with pytest.raises(Exception):
        await stq_runner.hiring_crm_upsert_lead_with_asset.call(
            args=(), kwargs=kwargs,
        )
    assert mock_salesforce_find_lead.has_calls
    assert mock_salesforce_composite.has_calls
