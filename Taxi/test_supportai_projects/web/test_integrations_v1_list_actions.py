import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_response_statuses(web_app_client):
    test_samples = [
        {'integration_id': 100500, 'response_status': 404},
        {'integration_id': 1, 'response_status': 200},
    ]

    for test_sample in test_samples:
        response = await web_app_client.get(
            f'/v1/integrations/{test_sample["integration_id"]}/actions',
        )
        assert response.status == test_sample['response_status']


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_data(web_app_client):
    test_samples = [
        {
            'integration_id': 1,
            'response_body': {
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
                        'response_mapping': (
                            '{"response": "some awesome mapping!!!"}'
                        ),
                    },
                ],
            },
        },
        {'integration_id': 2, 'response_body': {'actions': []}},
        {
            'integration_id': 3,
            'response_body': {
                'actions': [
                    {
                        'id': 3,
                        'slug': 'test_action_3',
                        'is_ignored': True,
                        'request_mapping': (
                            '{"key_1": "value_1", "key_2": "value_2"}'
                        ),
                        'response_mapping': '{}',
                    },
                    {
                        'id': 4,
                        'slug': 'test_action_4',
                        'is_ignored': True,
                        'request_mapping': '{"key": "value"}',
                        'response_mapping': '{}',
                    },
                    {
                        'id': 5,
                        'slug': 'test_action_5',
                        'is_ignored': False,
                        'request_mapping': '{}',
                        'response_mapping': '{}',
                    },
                ],
            },
        },
        {
            'integration_id': 4,
            'response_body': {
                'actions': [
                    {
                        'id': 6,
                        'slug': 'test_action_6',
                        'is_ignored': False,
                        'request_mapping': '{}',
                        'response_mapping': '{}',
                    },
                ],
            },
        },
        {'integration_id': 5, 'response_body': {'actions': []}},
    ]

    for test_sample in test_samples:
        response = await web_app_client.get(
            f'/v1/integrations/{test_sample["integration_id"]}/actions',
        )
        assert response.status == 200
        response_json = await response.json()
        assert response_json == test_sample['response_body']
