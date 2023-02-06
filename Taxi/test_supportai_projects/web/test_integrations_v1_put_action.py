import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_response_statuses(web_app_client):
    test_samples = [
        {
            'integration_id': 100500,
            'action_id': 1,
            'request_body': {'slug': 'test_action_1'},
            'response_status': 404,
        },
        {
            'integration_id': 1,
            'action_id': 100500,
            'request_body': {'slug': 'wrong_action'},
            'response_status': 404,
        },
        {
            'integration_id': 1,
            'action_id': 1,
            'request_body': {'slug': 'test_action_2'},
            'response_status': 400,
        },
        {
            'integration_id': 1,
            'action_id': 1,
            'request_body': {
                'slug': 'test_action_1',
                'is_ignored': True,
                'request_mapping': '{"text": "Oh my mapping!"}',
                'response_mapping': (
                    '{"text": "yet another awesome mapping!!!"}'
                ),
            },
            'response_status': 200,
        },
        {
            'integration_id': 1,
            'action_id': 2,
            'request_body': {'slug': 'yet_another_action'},
            'response_status': 200,
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.put(
            f'/v1/integrations/{test_sample["integration_id"]}'
            f'/actions/{test_sample["action_id"]}',
            json=test_sample['request_body'],
        )
        assert response.status == test_sample['response_status']


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_response_data(web_app_client):
    integration_id = 1
    test_samples = [
        {
            'integration_id': 1,
            'action_id': 1,
            'request_body': {
                'slug': 'test_action_1',
                'is_ignored': True,
                'request_mapping': '{"text": "Oh my mapping!"}',
                'response_mapping': (
                    '{"text": "yet another awesome mapping!!!"}'
                ),
            },
            'response_body': {
                'id': 1,
                'slug': 'test_action_1',
                'is_ignored': True,
                'request_mapping': '{"text": "Oh my mapping!"}',
                'response_mapping': (
                    '{"text": "yet another awesome mapping!!!"}'
                ),
            },
        },
        {
            'integration_id': 1,
            'action_id': 2,
            'request_body': {'slug': 'yet_another_action'},
            'response_body': {
                'id': 2,
                'slug': 'yet_another_action',
                'is_ignored': False,
                'request_mapping': '{}',
                'response_mapping': '{}',
            },
        },
    ]

    actions_list_response_before = {
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

    actions_list_response_after = {
        'actions': [
            {
                'id': 1,
                'slug': 'test_action_1',
                'is_ignored': True,
                'request_mapping': '{"text": "Oh my mapping!"}',
                'response_mapping': (
                    '{"text": "yet another awesome mapping!!!"}'
                ),
            },
            {
                'id': 2,
                'slug': 'yet_another_action',
                'is_ignored': False,
                'request_mapping': '{}',
                'response_mapping': '{}',
            },
        ],
    }

    response = await web_app_client.get(
        f'/v1/integrations/{integration_id}/actions',
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == actions_list_response_before

    for test_sample in test_samples:
        response = await web_app_client.put(
            f'/v1/integrations/{integration_id}'
            f'/actions/{test_sample["action_id"]}',
            json=test_sample['request_body'],
        )
        assert response.status == 200
        response_json = await response.json()
        assert response_json == test_sample['response_body']

    response = await web_app_client.get(
        f'/v1/integrations/{integration_id}/actions',
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == actions_list_response_after
