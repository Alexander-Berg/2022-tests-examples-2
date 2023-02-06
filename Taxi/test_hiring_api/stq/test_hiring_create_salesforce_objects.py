import pytest

EXP3_RESPONSES = 'exp3_responses.json'
EXPECTED_OBJECTS = 'expected_objects.json'
EXPECTED_YT_DATA_TABLE = 'expected_yt_data.json'
OBJECTS = 'objects.json'
YT_STQ_TABLE = '//home/test/stq_table'


@pytest.mark.config(HIRING_FAILED_STQ_TABLE_PATH=YT_STQ_TABLE)
@pytest.mark.parametrize(
    'case, objects_flow',
    [
        (201, 'ONE_OBJECT'),
        (201, 'TWO_OBJECTS'),
        (400, 'ERROR'),
        (201, 'TWO_OBJECTS_WITH_UPDATE'),
    ],
)
async def test_salesforce_objects(
        mock_salesforce_auth,
        mock_sf_objects_lead,
        mock_sf_objects_lead_update,
        mock_sf_objects_asset,
        mock_sf_objects_account_update,
        mock_territories_api,
        load_json,
        stq_runner,
        stq3_context,
        simple_secdist,
        case,
        objects_flow,
):
    handler_sf_lead = mock_sf_objects_lead(
        load_json(EXPECTED_OBJECTS)[objects_flow], case,
    )
    handler_sf_asset = mock_sf_objects_asset(
        load_json(EXPECTED_OBJECTS)[objects_flow], case,
    )
    handler_sf_lead_update = mock_sf_objects_lead_update(
        load_json(EXPECTED_OBJECTS)[objects_flow], 204,
    )
    handler_sf_acc_update = mock_sf_objects_account_update(
        load_json(EXPECTED_OBJECTS)[objects_flow], 204,
    )
    await stq_runner.hiring_create_salesforce_objects.call(
        args=(),
        kwargs={
            'external_id': 'ID',
            'objects': load_json(OBJECTS)[objects_flow],
            'dynamic_flow': load_json(EXP3_RESPONSES)[objects_flow],
        },
    )
    assert handler_sf_lead.has_calls
    if objects_flow.startswith('TWO_OBJECTS'):
        assert handler_sf_asset.has_calls
    if objects_flow == 'TWO_OBJECTS_WITH_UPDATE':
        assert handler_sf_lead_update.has_calls
        assert handler_sf_acc_update.has_calls


@pytest.mark.now('2022-09-15T10:00:00Z')
@pytest.mark.config(HIRING_FAILED_STQ_TABLE_PATH=YT_STQ_TABLE)
async def test_salesforce_error(
        mock_salesforce_auth,
        mock_sf_objects_lead,
        mock_territories_api,
        load_json,
        stq_runner,
        stq3_context,
        yt_client,
):
    handler_sf_lead = mock_sf_objects_lead(
        load_json(EXPECTED_OBJECTS)['ONE_OBJECT'], 404, False,
    )
    await stq_runner.hiring_create_salesforce_objects.call(
        args=(),
        kwargs={
            'external_id': 'ID',
            'objects': load_json(OBJECTS)['ONE_OBJECT'],
            'dynamic_flow': load_json(EXP3_RESPONSES)['ONE_OBJECT'],
        },
    )
    assert handler_sf_lead.has_calls
    expected_yt_data = load_json(EXPECTED_YT_DATA_TABLE)
    rows = list(yt_client.read_table(YT_STQ_TABLE))
    assert rows[-1] == expected_yt_data
