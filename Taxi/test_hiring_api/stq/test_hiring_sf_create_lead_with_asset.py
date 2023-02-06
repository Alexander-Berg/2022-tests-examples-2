import pytest

EXPECTED_YT_DATA_TABLE = 'expected_yt_data.json'
YT_STQ_TABLE = '//home/test/stq_table'


@pytest.mark.usefixtures('mock_salesforce_auth')
@pytest.mark.parametrize(
    ('stq_args_name', 'expected_name'),
    [
        ('simple', 'simple'),
        ('no_asset_name', 'no_asset_name'),
        ('custom_asset_fields', 'custom_asset_fields'),
    ],
)
async def test_salesforce_composite(
        stq_runner,
        mock_salesforce_composite,
        mock_hiring_candidates_region,
        load_json,
        stq_args_name,
        expected_name,
):
    mock_salesforce_composite = mock_salesforce_composite()
    # arrange
    kwargs = load_json('stq_kwargs.json')[stq_args_name]
    expected_sf_request = load_json('sf_composite_request.json')[expected_name]

    # act
    await stq_runner.hiring_sf_create_lead_with_asset.call(
        args=(), kwargs=kwargs,
    )

    # assert
    assert mock_salesforce_composite.times_called == 1
    sf_call = mock_salesforce_composite.next_call()
    request = sf_call['request']
    data = request.json
    assert data == expected_sf_request


@pytest.mark.now('2022-09-15T10:00:00Z')
@pytest.mark.usefixtures('mock_salesforce_auth')
@pytest.mark.config(HIRING_FAILED_STQ_TABLE_PATH=YT_STQ_TABLE)
@pytest.mark.parametrize('case', [400, 404, 405, 409, 422])
async def test_fail_salesforce_composite(
        stq_runner,
        mock_salesforce_composite_error,
        load_json,
        yt_client,
        case,
):
    kwargs = load_json('stq_kwargs.json')['simple']
    mock_salesforce_composite_error = mock_salesforce_composite_error(
        int(case), ['SOME_ERROR_1'],
    )

    await stq_runner.hiring_sf_create_lead_with_asset.call(
        args=(), kwargs=kwargs,
    )

    assert mock_salesforce_composite_error.has_calls

    expected_yt_data = load_json(EXPECTED_YT_DATA_TABLE)
    rows = list(yt_client.read_table(YT_STQ_TABLE))
    assert rows[-1] == expected_yt_data
