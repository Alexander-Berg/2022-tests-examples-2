import pytest


async def test_services_get(web_app_client):
    response = await web_app_client.get(
        '/v1/services', params={'client_id': 'client_id_1'},
    )
    response_json = await response.json()

    assert response.status == 200, response_json
    assert response_json == {
        'cargo': {
            'is_active': True,
            'is_visible': True,
            'next_day_delivery': True,
        },
        'drive': {'is_active': True, 'is_visible': True, 'parent_id': 12345},
        'eats': {'is_active': True, 'is_visible': True},
        'eats2': {'is_active': True, 'is_visible': True},
        'market': {'is_active': True, 'is_visible': True},
        'taxi': {
            'is_active': True,
            'is_visible': True,
            'categories': [{'name': 'econom'}, {'name': 'vip'}],
            'default_category': 'econom',
            'comment': 'Держи дверь, стой у входа!',
        },
        'tanker': {'is_active': True, 'is_visible': True},
    }


@pytest.mark.parametrize('service', ['taxi', 'cargo', 'drive', 'eats2'])
async def test_inactive_set_visible_400(web_app_client, service):
    data = {'is_visible': True}

    response = await web_app_client.patch(
        f'/v1/services/{service}',
        params={'client_id': 'client_id_2'},
        json=data,
    )
    response_json = await response.json()
    assert response.status == 400, response_json
    assert response_json == {
        'code': 'REQUEST_ERROR',
        'details': {'reason': 'Inactive service can not be visible'},
        'message': 'Request error',
    }
