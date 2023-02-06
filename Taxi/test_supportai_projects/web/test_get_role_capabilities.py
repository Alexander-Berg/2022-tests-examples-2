import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_get_role_capabilities(web_app_client):
    test_samples = [
        {
            'role_slug': 'super_admin',
            'response_status': 200,
            'response_body': {
                'capabilities': [
                    {'slug': 'admin_capability', 'type': 'allowed'},
                    {'slug': 'admin_capability_2', 'type': 'blocked'},
                    {'slug': 'admin_capability_3', 'type': 'allowed'},
                ],
            },
        },
        {
            'role_slug': 'editor',
            'response_status': 200,
            'response_body': {
                'capabilities': [
                    {'slug': 'test_capability_4', 'type': 'allowed'},
                    {'slug': 'test_capability_5', 'type': 'allowed'},
                ],
            },
        },
        {
            'role_slug': 'reader',
            'response_status': 200,
            'response_body': {'capabilities': []},
        },
        {'role_slug': 'unknown_role', 'response_status': 404},
    ]

    for test_sample in test_samples:
        response = await web_app_client.get(
            f'/v1/capabilities/role/{test_sample["role_slug"]}',
        )
        assert response.status == test_sample['response_status']
        if response.status == 200:
            response_body = await response.json()
            assert response_body == test_sample['response_body']
