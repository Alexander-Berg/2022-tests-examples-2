import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_post_projects(web_app_client):
    test_samples = [
        {
            'request_body': {
                'slug': 'test_project',
                'title': 'Unique Title',
                'preset': 'test_preset_1',
            },
            'response_status': 400,
        },
        {
            'request_body': {
                'slug': 'unique_slug',
                'title': 'Test Project',
                'preset': 'test_preset_1',
            },
            'response_status': 400,
        },
        {
            'request_body': {'slug': 'unique_slug', 'title': 'Test Project'},
            'response_status': 400,
        },
        {
            'request_body': {
                'slug': 'unique_slug',
                'title': 'Unique Title',
                'preset': 'test_preset_1',
            },
            'response_status': 200,
            'response_body': {
                'id': 6,
                'slug': 'unique_slug',
                'title': 'Unique Title',
                'is_chatterbox': False,
                'validation_instance_id': '',
                'preset': 'test_preset_1',
            },
        },
        {
            'request_body': {
                'slug': 'unique_slug_2',
                'title': 'Unique Title 2',
                'preset': 'test_preset_2',
                'is_chatterbox': True,
                'validation_instance_id': '12345',
                'new_config_schema': True,
            },
            'response_status': 200,
            'response_body': {
                'id': 7,
                'slug': 'unique_slug_2',
                'title': 'Unique Title 2',
                'is_chatterbox': True,
                'validation_instance_id': '12345',
                'preset': 'test_preset_2',
            },
        },
    ]

    expected_list_response = {
        'projects': [
            {
                'id': 1,
                'slug': 'test_project',
                'title': 'Test Project',
                'is_chatterbox': False,
                'validation_instance_id': '',
                'preset': 'test_preset_1',
            },
            {
                'id': 2,
                'slug': 'test_project_2',
                'title': 'Test Project 2',
                'is_chatterbox': False,
                'validation_instance_id': '',
                'preset': 'test_preset_2',
            },
            {
                'id': 3,
                'slug': 'test_project_3',
                'title': 'Test Project 3',
                'is_chatterbox': False,
                'validation_instance_id': '',
                'preset': 'test_preset_3',
            },
            {
                'id': 6,
                'slug': 'unique_slug',
                'title': 'Unique Title',
                'is_chatterbox': False,
                'validation_instance_id': '',
                'preset': 'test_preset_1',
            },
            {
                'id': 7,
                'slug': 'unique_slug_2',
                'title': 'Unique Title 2',
                'is_chatterbox': True,
                'validation_instance_id': '12345',
                'preset': 'test_preset_2',
            },
        ],
    }

    for test_sample in test_samples:
        response = await web_app_client.post(
            '/v1/projects', json=test_sample['request_body'],
        )
        assert response.status == test_sample['response_status']
        if response.status == 200:
            response_json = await response.json()
            assert response_json == test_sample['response_body']

    response = await web_app_client.get('/v1/projects')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == expected_list_response
