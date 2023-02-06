import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_get_projects(web_app_client):
    expected_response = {
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
        ],
    }

    response = await web_app_client.get('/v1/projects')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == expected_response


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_get_projects_preset_filter(web_app_client):
    test_samples = [
        {
            'preset_slug': 'test_preset_1',
            'expected_response': {
                'projects': [
                    {
                        'id': 1,
                        'slug': 'test_project',
                        'title': 'Test Project',
                        'is_chatterbox': False,
                        'validation_instance_id': '',
                        'preset': 'test_preset_1',
                    },
                ],
            },
        },
        {
            'preset_slug': 'test_preset_2',
            'expected_response': {
                'projects': [
                    {
                        'id': 2,
                        'slug': 'test_project_2',
                        'title': 'Test Project 2',
                        'is_chatterbox': False,
                        'validation_instance_id': '',
                        'preset': 'test_preset_2',
                    },
                ],
            },
        },
        {
            'preset_slug': 'test_preset_3',
            'expected_response': {
                'projects': [
                    {
                        'id': 3,
                        'slug': 'test_project_3',
                        'title': 'Test Project 3',
                        'is_chatterbox': False,
                        'validation_instance_id': '',
                        'preset': 'test_preset_3',
                    },
                ],
            },
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.get(
            f'/v1/projects?preset={test_sample["preset_slug"]}',
        )
        assert response.status == 200
        response_json = await response.json()
        assert response_json == test_sample['expected_response']
