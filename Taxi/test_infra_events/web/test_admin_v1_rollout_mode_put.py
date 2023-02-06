import pytest


INFRA_EVENTS_VIEWS = {'rolling_view': {'release_schedule': 'default'}}


@pytest.mark.config(INFRA_EVENTS_VIEWS=INFRA_EVENTS_VIEWS)
async def test_admin_v1_rollout_mode_put(web_app_client):
    response = await web_app_client.put(
        '/admin/v1/rollout-mode',
        headers={'X-Yandex-Login': 'tester1'},
        json={'view': 'rolling_view', 'can_deploy': False},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'view': 'rolling_view', 'can_deploy': False}

    response = await web_app_client.put(
        '/admin/v1/rollout-mode',
        headers={'X-Yandex-Login': 'tester1'},
        json={'view': 'not_existing_view', 'can_deploy': False},
    )
    assert response.status == 404
    content = await response.json()
    assert content == {
        'code': 'view_not_found',
        'message': 'Specified view does not exists',
    }
