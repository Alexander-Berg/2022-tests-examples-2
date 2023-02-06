import pytest


@pytest.mark.pgsql('supportai_projects', files=['db_sample.sql'])
async def test_get_capabilities(web_app_client):
    expected_response = {
        'capabilities': [
            {'slug': 'admin_capability'},
            {'slug': 'admin_capability_2'},
            {'slug': 'admin_capability_3'},
            {'slug': 'project_capability_1'},
            {'slug': 'project_capability_2'},
            {'slug': 'project_capability_3'},
            {'slug': 'test_capability'},
            {'slug': 'test_capability_2'},
            {'slug': 'test_capability_3'},
            {'slug': 'test_capability_4'},
            {'slug': 'test_capability_5'},
        ],
    }

    response = await web_app_client.get('/v1/capabilities')
    assert response.status == 200
    response_json = await response.json()
    assert response_json == expected_response
