import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_response_statuses(web_app_client):
    test_samples = [
        {
            'integration_id': 100500,
            'action_id': 1,
            'callback_id': 1,
            'response_status': 404,
        },
        {
            'integration_id': 1,
            'action_id': 100500,
            'callback_id': 1,
            'response_status': 404,
        },
        {
            'integration_id': 1,
            'action_id': 1,
            'callback_id': 1,
            'response_status': 204,
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.delete(
            f'/v1/integrations/{test_sample["integration_id"]}'
            f'/actions/{test_sample["action_id"]}'
            f'/callbacks/{test_sample["callback_id"]}',
        )
        assert response.status == test_sample['response_status']


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_data(web_app_client):
    integration_id = 1
    action_id = 1
    callback_id = 1

    response_body_before = {
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

    response_body_after = {
        'callbacks': [
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

    response = await web_app_client.get(
        f'/v1/integrations/{integration_id}' f'/actions/{action_id}/callbacks',
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == response_body_before

    response = await web_app_client.delete(
        f'/v1/integrations/{integration_id}'
        f'/actions/{action_id}'
        f'/callbacks/{callback_id}',
    )
    assert response.status == 204

    response = await web_app_client.get(
        f'/v1/integrations/{integration_id}' f'/actions/{action_id}/callbacks',
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == response_body_after
