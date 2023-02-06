import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_response_statuses(web_app_client):
    test_samples = [
        {
            'integration_id': 100500,
            'request_body': {'slug': 'yet_another_integration'},
            'response_status': 404,
        },
        {
            'integration_id': 1,
            'request_body': {'slug': 'test_action_1'},
            'response_status': 400,
        },
        {
            'integration_id': 2,
            'request_body': {'slug': 'test_action_1'},
            'response_status': 200,
        },
        {
            'integration_id': 5,
            'request_body': {'slug': 'yet_another_action_1'},
            'response_status': 200,
        },
        {
            'integration_id': 5,
            'request_body': {
                'slug': 'yet_another_action_2',
                'is_ignored': True,
                'request_mapping': '{"text": "blahblah-blahblahblah"}',
                'response_mapping': (
                    '{"text": "yet another awesome mapping!!!"}'
                ),
            },
            'response_status': 200,
        },
        {
            'integration_id': 5,
            'request_body': {
                'slug': 'yet_another_action_3',
                'is_ignored': False,
                'request_mapping': '',
                'response_mapping': '',
            },
            'response_status': 200,
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.post(
            f'/v1/integrations/{test_sample["integration_id"]}/actions',
            json=test_sample['request_body'],
        )
        assert response.status == test_sample['response_status']


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_response_data(web_app_client):
    integration_id = 5
    test_samples = [
        {
            'request_body': {'slug': 'yet_another_action_1'},
            'response_body': {
                'id': 7,
                'slug': 'yet_another_action_1',
                'is_ignored': False,
                'request_mapping': '{}',
                'response_mapping': '{}',
            },
        },
        {
            'request_body': {
                'slug': 'yet_another_action_2',
                'is_ignored': True,
                'request_mapping': '{"text": "blahblah-blahblahblah"}',
                'response_mapping': (
                    '{"text": "yet another awesome mapping!!!"}'
                ),
            },
            'response_body': {
                'id': 8,
                'slug': 'yet_another_action_2',
                'is_ignored': True,
                'request_mapping': '{"text": "blahblah-blahblahblah"}',
                'response_mapping': (
                    '{"text": "yet another awesome mapping!!!"}'
                ),
            },
        },
        {
            'request_body': {
                'slug': 'yet_another_action_3',
                'is_ignored': False,
                'request_mapping': '',
                'response_mapping': '',
            },
            'response_body': {
                'id': 9,
                'slug': 'yet_another_action_3',
                'is_ignored': False,
                'request_mapping': '{}',
                'response_mapping': '{}',
            },
        },
    ]

    list_actions_response_before = {'actions': []}

    list_actions_response_after = {
        'actions': [
            {
                'id': 7,
                'slug': 'yet_another_action_1',
                'is_ignored': False,
                'request_mapping': '{}',
                'response_mapping': '{}',
            },
            {
                'id': 8,
                'slug': 'yet_another_action_2',
                'is_ignored': True,
                'request_mapping': '{"text": "blahblah-blahblahblah"}',
                'response_mapping': (
                    '{"text": "yet another awesome mapping!!!"}'
                ),
            },
            {
                'id': 9,
                'slug': 'yet_another_action_3',
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
    assert response_json == list_actions_response_before

    for test_sample in test_samples:
        response = await web_app_client.post(
            f'/v1/integrations/{integration_id}/actions',
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
    assert response_json == list_actions_response_after
