import json

import pytest

FIND_CLIENT_ROUTE = '/v1/billing/client/find'


@pytest.mark.parametrize(
    'content_type, request_name',
    [('client_id', 'by_client_id'), ('email', 'by_email'), ('404', '404')],
)
async def test_find_client(
        taxi_process_automation_salesforce_esb_web,
        mock_balance,
        load_json,
        content_type,
        request_name,
):
    method_response = {'Balance2.FindClient': f'{content_type}_response.xml'}
    mock_balance(method_response)

    data = load_json('requests.json')[request_name]
    response = await taxi_process_automation_salesforce_esb_web.get(
        FIND_CLIENT_ROUTE, params=data['params'],
    )

    assert response.status == data['status']
    if data['status'] == 200:
        content = await response.content.read()
        assert json.loads(content) == data['expected_result']
