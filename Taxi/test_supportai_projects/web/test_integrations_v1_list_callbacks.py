import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_response_statuses(web_app_client):
    test_samples = [
        {'integration_id': 100500, 'action_id': 1, 'response_status': 404},
        {'integration_id': 1, 'action_id': 100500, 'response_status': 404},
        {'integration_id': 1, 'action_id': 1, 'response_status': 200},
        {'integration_id': 3, 'action_id': 4, 'response_status': 200},
    ]

    for test_sample in test_samples:
        response = await web_app_client.get(
            f'/v1/integrations/{test_sample["integration_id"]}'
            f'/actions/{test_sample["action_id"]}'
            f'/callbacks',
        )
        assert response.status == test_sample['response_status']


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_data(web_app_client):
    test_samples = [
        {
            'integration_id': 1,
            'action_id': 1,
            'response_body': {
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
            },
        },
        {
            'integration_id': 1,
            'action_id': 2,
            'response_body': {
                'callbacks': [
                    {
                        'id': 4,
                        'condition': 'close',
                        'uri': '/',
                        'request_method': 'DELETE',
                        'request_mapping': (
                            '{"message": "Do not delete anything"}'
                        ),
                    },
                ],
            },
        },
        {
            'integration_id': 3,
            'action_id': 3,
            'response_body': {
                'callbacks': [
                    {
                        'id': 5,
                        'condition': 'forward',
                        'uri': '/sluggy_slug',
                        'request_method': 'GET',
                        'request_mapping': '{}',
                    },
                ],
            },
        },
        {
            'integration_id': 3,
            'action_id': 4,
            'response_body': {'callbacks': []},
        },
        {
            'integration_id': 3,
            'action_id': 5,
            'response_body': {
                'callbacks': [
                    {
                        'id': 6,
                        'condition': 'reply_iterable',
                        'uri': '/',
                        'request_method': 'GET',
                        'request_mapping': '{}',
                    },
                    {
                        'id': 7,
                        'condition': 'forward',
                        'uri': '/',
                        'request_method': 'POST',
                        'request_mapping': (
                            '{"message": "Awesome POST session"}'
                        ),
                    },
                ],
            },
        },
        {
            'integration_id': 4,
            'action_id': 6,
            'response_body': {
                'callbacks': [
                    {
                        'id': 8,
                        'condition': 'tag',
                        'uri': '/',
                        'request_method': 'GET',
                        'request_mapping': '{}',
                    },
                ],
            },
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.get(
            f'/v1/integrations/{test_sample["integration_id"]}'
            f'/actions/{test_sample["action_id"]}'
            f'/callbacks',
        )
        assert response.status == 200
        response_json = await response.json()
        assert response_json == test_sample['response_body']
