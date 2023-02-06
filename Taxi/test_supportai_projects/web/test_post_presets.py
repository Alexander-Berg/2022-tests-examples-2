import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_post_presets(web_app_client):
    test_samples = [
        {
            'request_body': {'slug': 'test_preset_1', 'title': 'Unique Title'},
            'response_status': 400,
        },
        {
            'request_body': {
                'slug': 'unique_preset',
                'title': 'Test Preset 1',
            },
            'response_status': 400,
        },
        {
            'request_body': {'slug': 'unique_preset', 'title': 'Unique Title'},
            'response_status': 200,
            'response_body': {
                'id': 7,
                'slug': 'unique_preset',
                'title': 'Unique Title',
            },
        },
        {
            'request_body': {
                'slug': 'unique_preset_2',
                'title': 'Unique Title 2',
            },
            'response_status': 200,
            'response_body': {
                'id': 8,
                'slug': 'unique_preset_2',
                'title': 'Unique Title 2',
            },
        },
        {
            'request_body': {
                'slug': 'unique_preset_3',
                'title': 'Unique Title 3',
            },
            'response_status': 200,
            'response_body': {
                'id': 9,
                'slug': 'unique_preset_3',
                'title': 'Unique Title 3',
            },
        },
        {
            'request_body': {
                'slug': 'unique_preset_4',
                'title': 'Unique Title 4',
            },
            'response_status': 200,
            'response_body': {
                'id': 10,
                'slug': 'unique_preset_4',
                'title': 'Unique Title 4',
            },
        },
    ]

    expected_list_response = {
        'presets': [
            {'id': 1, 'slug': 'test_preset_1', 'title': 'Test Preset 1'},
            {'id': 2, 'slug': 'test_preset_2', 'title': 'Test Preset 2'},
            {'id': 3, 'slug': 'test_preset_3', 'title': 'Test Preset 3'},
            {'id': 4, 'slug': 'test_preset_4', 'title': 'Test Preset 4'},
            {'id': 7, 'slug': 'unique_preset', 'title': 'Unique Title'},
            {'id': 8, 'slug': 'unique_preset_2', 'title': 'Unique Title 2'},
            {'id': 9, 'slug': 'unique_preset_3', 'title': 'Unique Title 3'},
            {'id': 10, 'slug': 'unique_preset_4', 'title': 'Unique Title 4'},
        ],
    }

    for test_sample in test_samples:
        response = await web_app_client.post(
            '/v1/presets', json=test_sample['request_body'],
        )
        assert response.status == test_sample['response_status']
        if response.status == 200:
            response_json = await response.json()
            assert response_json == test_sample['response_body']

    response = await web_app_client.get('/v1/presets')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == expected_list_response
