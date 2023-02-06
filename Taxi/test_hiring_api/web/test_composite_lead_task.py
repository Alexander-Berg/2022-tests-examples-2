import pytest


@pytest.mark.parametrize(
    ('request_name',), [('with_task',), ('without_task',)],
)
@pytest.mark.usefixtures(
    'mock_personal_api',
    'mock_territories_api',
    'mock_hiring_data_markup',
    'salesforce',
)
@pytest.mark.now('2022-01-01T16:00:00.0')
async def test_composite_lead_task(
        taxi_hiring_api_web,
        load_json,
        request_name,
        mock_salesforce_composite,
):
    # arrange
    mock_salesforce_composite = mock_salesforce_composite()
    request = load_json('requests.json')[request_name]
    expected = load_json('expected.json')[request_name]

    # act
    response = await taxi_hiring_api_web.post(
        '/v2/composite/lead-task', **request,
    )

    # assert
    assert response.status == expected['status_code']
    assert await response.json() == expected['response']
