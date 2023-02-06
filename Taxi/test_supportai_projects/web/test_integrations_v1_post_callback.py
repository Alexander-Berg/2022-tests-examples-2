import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_response_statuses(web_app_client):
    test_samples = [
        {
            'integration_id': 100500,
            'action_id': 1,
            'request_body': {
                'condition': 'tag',
                'uri': '/',
                'request_method': 'GET',
                'request_mapping': '{}',
            },
            'response_status': 404,
        },
        {
            'integration_id': 1,
            'action_id': 100500,
            'request_body': {
                'condition': 'tag',
                'uri': '/',
                'request_method': 'GET',
                'request_mapping': '{}',
            },
            'response_status': 404,
        },
        {
            'integration_id': 3,
            'action_id': 4,
            'request_body': {
                'uri': '/',
                'request_method': 'GET',
                'request_mapping': '{}',
            },
            'response_status': 400,
        },
        {
            'integration_id': 3,
            'action_id': 4,
            'request_body': {
                'condition': 'tag',
                'request_method': 'GET',
                'request_mapping': '{}',
            },
            'response_status': 400,
        },
        {
            'integration_id': 3,
            'action_id': 4,
            'request_body': {
                'condition': 'tag',
                'uri': '/',
                'request_mapping': '{}',
            },
            'response_status': 400,
        },
        {
            'integration_id': 3,
            'action_id': 4,
            'request_body': {
                'condition': 'tag',
                'uri': '/',
                'request_method': 'WRONG_METHOD',
                'request_mapping': '{}',
            },
            'response_status': 400,
        },
        {
            'integration_id': 3,
            'action_id': 4,
            'request_body': {
                'condition': 'wrong_condition',
                'uri': '/',
                'request_method': 'POST',
                'request_mapping': '{"message": "Brand new post"}',
            },
            'response_status': 400,
        },
        {
            'integration_id': 3,
            'action_id': 4,
            'request_body': {
                'condition': 'tag',
                'uri': '/',
                'request_method': 'POST',
                'request_mapping': '{"message": "Brand new post"}',
            },
            'response_status': 200,
        },
        {
            'integration_id': 3,
            'action_id': 4,
            'request_body': {
                'condition': 'forward',
                'uri': '/',
                'request_method': 'GET',
            },
            'response_status': 200,
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.post(
            f'/v1/integrations/{test_sample["integration_id"]}'
            f'/actions/{test_sample["action_id"]}'
            f'/callbacks',
            json=test_sample['request_body'],
        )
        assert response.status == test_sample['response_status']


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_response_data(web_app_client):
    integration_id = 3
    action_id = 4

    test_samples = [
        {
            'request_body': {
                'condition': 'tag',
                'uri': '/',
                'request_method': 'POST',
                'request_mapping': '{"message": "Brand new post"}',
            },
            'response_body': {
                'id': 9,
                'condition': 'tag',
                'uri': '/',
                'request_method': 'POST',
                'request_mapping': '{"message": "Brand new post"}',
            },
        },
        {
            'integration_id': 'test_integration_3',
            'action_id': 'test_action_4',
            'request_body': {
                'condition': 'forward',
                'uri': '/',
                'request_method': 'GET',
            },
            'response_body': {
                'id': 10,
                'condition': 'forward',
                'uri': '/',
                'request_method': 'GET',
                'request_mapping': '{}',
            },
        },
    ]

    list_callbacks_response_before = {'callbacks': []}

    list_callbacks_response_after = {
        'callbacks': [
            {
                'id': 9,
                'condition': 'tag',
                'uri': '/',
                'request_method': 'POST',
                'request_mapping': '{"message": "Brand new post"}',
            },
            {
                'id': 10,
                'condition': 'forward',
                'uri': '/',
                'request_method': 'GET',
                'request_mapping': '{}',
            },
        ],
    }

    response = await web_app_client.get(
        f'/v1/integrations/{integration_id}'
        f'/actions/{action_id}'
        f'/callbacks',
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == list_callbacks_response_before

    for test_sample in test_samples:
        response = await web_app_client.post(
            f'/v1/integrations/{integration_id}'
            f'/actions/{action_id}'
            f'/callbacks',
            json=test_sample['request_body'],
        )
        assert response.status == 200
        response_json = await response.json()
        assert response_json == test_sample['response_body']

    response = await web_app_client.get(
        f'/v1/integrations/{integration_id}'
        f'/actions/{action_id}'
        f'/callbacks',
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == list_callbacks_response_after
