import pytest


@pytest.mark.config(HIRING_API_ENABLE_REQUEST_LIMIT=True)
async def test_external_leads_create(
        hiring_rate_calculate,
        hiring_rate_update,
        taxi_hiring_api_web,
        mock_personal_api,
        mock_territories_api,
        mock_stq_queue,
        mock_hiring_data_markup_by_flow,
        mock_hiring_data_markup,
        load_json,
):
    # arrange
    hiring_data_markup_mock = mock_hiring_data_markup_by_flow(
        responses_by_flows={
            None: load_json('markup_responses/default_flow.json'),
        },
    )

    # act
    response = await taxi_hiring_api_web.post(
        '/external/v2/leads/create',
        json=load_json('request.json'),
        headers={'X-Delivery-Id': 'some_delivery_id'},
        params={'endpoint': 'some_endpoint', 'creator_meta_role': 'scout'},
    )

    # assert
    assert response.status == 200
    assert await response.json() == load_json('response.json')

    assert hiring_data_markup_mock.times_called == 1
    hiring_partners_app_markup_call = hiring_data_markup_mock.next_call()[
        'request'
    ].json
    assert hiring_partners_app_markup_call == load_json(
        'data_markup_request.json',
    )

    assert mock_stq_queue.times_called == 3
    # SF stq call
    stq_call_request = mock_stq_queue.next_call()['request'].json
    assert stq_call_request == load_json('stq_calls/salesforce.json')
    # Candidates stq call
    stq_call_request = mock_stq_queue.next_call()['request'].json
    assert stq_call_request == load_json('stq_calls/candidates.json')
    # Infranaim stq call
    stq_call_request = mock_stq_queue.next_call()['request'].json
    assert stq_call_request == load_json('stq_calls/infranaim.json')
