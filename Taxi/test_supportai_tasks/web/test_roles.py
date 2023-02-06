import pytest


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_get_all_roles(web_app_client):
    permitted_user_ids = [34, 35, '000000', '007']

    for user_id in permitted_user_ids:
        response = await web_app_client.get(f'/v1/roles' f'?user_id={user_id}')
        assert response.status == 200
        response_json = await response.json()
        assert len(response_json['roles']) == 4
        assert {'id': 1, 'title': 'Super Admin'} in response_json['roles']
        assert {'id': 2, 'title': 'Project Admin'} in response_json['roles']
        assert {'id': 3, 'title': 'Project Editor'} in response_json['roles']
        assert {'id': 4, 'title': 'Project Reader'} in response_json['roles']
