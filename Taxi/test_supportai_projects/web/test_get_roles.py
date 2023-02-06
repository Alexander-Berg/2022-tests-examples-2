import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_get_roles(web_app_client):
    expected_response = {
        'roles': [
            {'id': 1, 'slug': 'super_admin', 'permissions': []},
            {
                'id': 2,
                'slug': 'admin',
                'permissions': ['read', 'write', 'modify'],
            },
            {'id': 3, 'slug': 'editor', 'permissions': ['read', 'write']},
            {'id': 4, 'slug': 'reader', 'permissions': ['read']},
            {
                'id': 5,
                'slug': 'read_modifier',
                'permissions': ['read', 'modify'],
            },
            {
                'id': 6,
                'slug': 'write_modifier',
                'permissions': ['write', 'modify'],
            },
            {'id': 7, 'slug': 'writer', 'permissions': ['write']},
            {'id': 8, 'slug': 'modifier', 'permissions': ['modify']},
            {'id': 9, 'slug': 'not_allowed', 'permissions': []},
        ],
    }

    response = await web_app_client.get('/v1/roles')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == expected_response
