# pylint: disable=invalid-name
import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_post_project_capabilities_from_preset_responses(web_app_client):
    test_samples = [
        {
            'project_slug': 'non_existing_project',
            'preset_slug': 'test_preset_1',
            'response_status': 404,
        },
        {
            'project_slug': 'test_project',
            'preset_slug': 'non_existing_preset',
            'response_status': 400,
        },
        {
            'project_slug': 'test_project',
            'preset_slug': 'test_preset_1',
            'response_status': 204,
        },
    ]

    for test_sample in test_samples:
        response = await web_app_client.post(
            f'/v1/projects/{test_sample["project_slug"]}'
            f'/from-preset/add-capabilities'
            f'?preset={test_sample["preset_slug"]}',
        )
        assert response.status == test_sample['response_status']


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_post_project_capabilities_from_preset_data(web_app_client):
    project_slug = 'test_project'
    preset_slug = 'test_preset_1'
    expected_response_status = 204

    get_project_capabilities_response_before = {
        'capabilities': [
            {'slug': 'project_capability_1', 'type': 'allowed'},
            {'slug': 'project_capability_2', 'type': 'blocked'},
            {'slug': 'project_capability_3', 'type': 'allowed'},
        ],
    }
    get_project_capabilities_response_after = {
        'capabilities': [
            {'slug': 'project_capability_1', 'type': 'allowed'},
            {'slug': 'project_capability_2', 'type': 'blocked'},
            {'slug': 'project_capability_3', 'type': 'allowed'},
            {'slug': 'test_capability', 'type': 'allowed'},
            {'slug': 'test_capability_3', 'type': 'allowed'},
        ],
    }

    response = await web_app_client.get(
        f'/v1/capabilities/project/{project_slug}',
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == get_project_capabilities_response_before

    response = await web_app_client.post(
        f'/v1/projects/{project_slug}'
        f'/from-preset/add-capabilities'
        f'?preset={preset_slug}',
    )
    assert response.status == expected_response_status

    response = await web_app_client.get(
        f'/v1/capabilities/project/{project_slug}',
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == get_project_capabilities_response_after
