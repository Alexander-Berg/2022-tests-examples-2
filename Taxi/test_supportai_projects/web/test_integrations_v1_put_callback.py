import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_response_statuses(web_app_client):
    test_samples = [
        {
            'integration_id': 100500,
            'action_id': 1,
            'callback_id': 1,
            'request_body': {
                'condition': 'tag',
                'uri': '/slugiwe',
                'request_method': 'PUT',
                'request_mapping': '{"message": "Never gonna give you up"}',
            },
            'response_status': 404,
        },
        {
            'integration_id': 1,
            'action_id': 100500,
            'callback_id': 1,
            'request_body': {
                'condition': 'tag',
                'uri': '/slugiwe',
                'request_method': 'PUT',
                'request_mapping': '{"message": "Never gonna give you up"}',
            },
            'response_status': 404,
        },
        {
            'integration_id': 1,
            'action_id': 1,
            'callback_id': 4,
            'request_body': {
                'condition': 'tag',
                'uri': '/slugiwe',
                'request_method': 'PUT',
                'request_mapping': '{"message": "Never gonna give you up"}',
            },
            'response_status': 404,
        },
        {
            'integration_id': 1,
            'action_id': 1,
            'callback_id': 1,
            'request_body': {
                'uri': '/slugiwe',
                'request_method': 'PUT',
                'request_mapping': '{"message": "Never gonna give you up"}',
            },
            'response_status': 400,
        },
        {
            'integration_id': 1,
            'action_id': 1,
            'callback_id': 1,
            'request_body': {
                'condition': 'tag',
                'request_method': 'PUT',
                'request_mapping': '{"message": "Never gonna give you up"}',
            },
            'response_status': 400,
        },
        {
            'integration_id': 1,
            'action_id': 1,
            'callback_id': 1,
            'request_body': {
                'condition': 'tag',
                'uri': '/slugiwe',
                'request_mapping': '{"message": "Never gonna give you up"}',
            },
            'response_status': 400,
        },
        {
            'integration_id': 1,
            'action_id': 1,
            'callback_id': 1,
            'request_body': {
                'condition': 'wrong_condition',
                'uri': '/slugiwe',
                'request_method': 'PUT',
                'request_mapping': '{"message": "Never gonna give you up"}',
            },
            'response_status': 400,
        },
        {
            'integration_id': 1,
            'action_id': 1,
            'callback_id': 1,
            'request_body': {
                'condition': 'forward',
                'uri': '/slugiwe',
                'request_method': 'PUT',
                'request_mapping': '{"message": "Never gonna give you up"}',
            },
            'response_status': 200,
        },
        {
            'integration_id': 1,
            'action_id': 1,
            'callback_id': 2,
            'request_body': {
                'condition': 'reply',
                'uri': '/slugiwe',
                'request_method': 'GET',
            },
            'response_status': 200,
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.put(
            f'/v1/integrations/{test_sample["integration_id"]}'
            f'/actions/{test_sample["action_id"]}'
            f'/callbacks/{test_sample["callback_id"]}',
            json=test_sample['request_body'],
        )
        assert response.status == test_sample['response_status']


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_response_data(web_app_client):
    integration_id = 1
    action_id = 1

    test_samples = [
        {
            'callback_id': 1,
            'request_body': {
                'condition': 'forward',
                'uri': '/slugiwe',
                'request_method': 'PUT',
                'request_mapping': '{"message": "Never gonna give you up"}',
            },
            'response_body': {
                'id': 1,
                'condition': 'forward',
                'uri': '/slugiwe',
                'request_method': 'PUT',
                'request_mapping': '{"message": "Never gonna give you up"}',
            },
        },
        {
            'callback_id': 2,
            'request_body': {
                'condition': 'reply',
                'uri': '/slugiwe',
                'request_method': 'GET',
            },
            'response_body': {
                'id': 2,
                'condition': 'reply',
                'uri': '/slugiwe',
                'request_method': 'GET',
                'request_mapping': '{}',
            },
        },
    ]

    list_callbacks_response_before = {
        'callbacks': [
            {
                'id': 1,
                'condition': 'reply',
                'uri': '/',
                'request_method': 'GET',
                'request_mapping': '{}',
            },
            {
                'id': 2,
                'condition': 'tag',
                'uri': '/some_slug',
                'request_method': 'POST',
                'request_mapping': (
                    '{"message": "Awwww, infinite loops, my pleasure"}'
                ),
            },
            {
                'id': 3,
                'condition': 'tag',
                'uri': '/another_slug',
                'request_method': 'DELETE',
                'request_mapping': '{}',
            },
        ],
    }

    list_callbacks_response_after = {
        'callbacks': [
            {
                'id': 1,
                'condition': 'forward',
                'uri': '/slugiwe',
                'request_method': 'PUT',
                'request_mapping': '{"message": "Never gonna give you up"}',
            },
            {
                'id': 2,
                'condition': 'reply',
                'uri': '/slugiwe',
                'request_method': 'GET',
                'request_mapping': '{}',
            },
            {
                'id': 3,
                'condition': 'tag',
                'uri': '/another_slug',
                'request_method': 'DELETE',
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
        response = await web_app_client.put(
            f'/v1/integrations/{integration_id}'
            f'/actions/{action_id}'
            f'/callbacks/{test_sample["callback_id"]}',
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
