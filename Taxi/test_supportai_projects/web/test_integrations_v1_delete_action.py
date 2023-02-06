import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_response_statuses(web_app_client):
    test_samples = [
        {'integration_id': 100500, 'action_id': 1, 'response_status': 404},
        {'integration_id': 1, 'action_id': 100500, 'response_status': 404},
        {'integration_id': 1, 'action_id': 1, 'response_status': 204},
    ]

    for test_sample in test_samples:
        response = await web_app_client.delete(
            f'/v1/integrations/{test_sample["integration_id"]}'
            f'/actions/{test_sample["action_id"]}',
        )
        assert response.status == test_sample['response_status']


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_response_data(web_app_client):
    integration_id = 1
    action_id = 1

    list_actions_response_before = {
        'actions': [
            {
                'id': 1,
                'slug': 'test_action_1',
                'is_ignored': False,
                'request_mapping': '{"key": "value"}',
                'response_mapping': '{}',
            },
            {
                'id': 2,
                'slug': 'test_action_2',
                'is_ignored': True,
                'request_mapping': '{}',
                'response_mapping': '{"response": "some awesome mapping!!!"}',
            },
        ],
    }

    list_actions_response_after = {
        'actions': [
            {
                'id': 2,
                'slug': 'test_action_2',
                'is_ignored': True,
                'request_mapping': '{}',
                'response_mapping': '{"response": "some awesome mapping!!!"}',
            },
        ],
    }

    response = await web_app_client.get(
        f'/v1/integrations/{integration_id}/actions',
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == list_actions_response_before

    response = await web_app_client.delete(
        f'/v1/integrations/{integration_id}/actions/{action_id}',
    )
    assert response.status == 204

    response = await web_app_client.get(
        f'/v1/integrations/{integration_id}/actions',
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == list_actions_response_after
