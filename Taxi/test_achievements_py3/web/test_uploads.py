import pytest

from achievements_py3 import consts


@pytest.mark.xfail(reason='temporary disabled')
async def test_upload_add(web_app_client):
    data = {
        'yql_text': 'Test YQL',
        'reward_id': 666,
        'upload_type': 'set_unlocked',
        'initiator': {'yandex_login': 'test'},
    }
    response = await web_app_client.post(
        '/admin/v1/reward-upload/add',
        json=data,
        headers={'X-Idempotency-Token': '1'},
    )
    assert response.status == 200

    result = await response.json()
    assert result.get('id')
    assert result.get('updated_at')
    assert result.get('status') == consts.Status.NEW.value
    assert result.get('yql', {}).get('text') == data['yql_text']
    assert result.get('initiator', {}).pop('created_at')
    assert result.get('initiator') == data['initiator']


@pytest.mark.xfail(reason='temporary disabled')
async def test_upload_list(web_app_client):
    data = {
        'yql_text': 'Test YQL',
        'reward_id': 666,
        'upload_type': 'set_unlocked',
        'initiator': {'yandex_login': 'test'},
    }
    for i in range(3):
        response = await web_app_client.post(
            '/admin/v1/reward-upload/add',
            json=data,
            headers={'X-Idempotency-Token': f'{i}'},
        )
        assert response.status == 200

    response = await web_app_client.get(
        '/admin/v1/reward-upload/list', params={'limit': 2},
    )
    assert response.status == 200
    result = await response.json()
    assert len(result['items']) == 2
    assert result.get('has_more') is True
    assert result.get('cursor')

    next_response = await web_app_client.get(
        '/admin/v1/reward-upload/list',
        params={'limit': 2, 'cursor': result.get('cursor')},
    )
    assert next_response.status == 200
    next_result = await next_response.json()
    assert len(next_result['items']) == 1
    assert next_result.get('has_more') is False
    assert next_result.get('cursor')

    last_response = await web_app_client.get(
        '/admin/v1/reward-upload/list',
        params={'limit': 2, 'cursor': next_result.get('cursor')},
    )
    assert last_response.status == 200
    last_result = await last_response.json()
    assert not last_result['items']
    assert last_result.get('has_more') is False
    assert last_result.get('cursor') is None


@pytest.mark.xfail(reason='temporary disabled')
async def test_upload_idempotency(taxi_achievements_py3_web):
    data = {
        'yql_text': 'Test YQL',
        'reward_id': 666,
        'upload_type': 'set_unlocked',
        'initiator': {'yandex_login': 'test'},
    }
    response = await taxi_achievements_py3_web.post(
        '/admin/v1/reward-upload/add',
        json=data,
        headers={'X-Idempotency-Token': '1'},
    )
    assert response.status == 200
    upload_1 = await response.json()

    response = await taxi_achievements_py3_web.post(
        '/admin/v1/reward-upload/add',
        json=data,
        headers={'X-Idempotency-Token': '1'},
    )
    assert response.status == 200
    upload_2 = await response.json()
    assert upload_1 == upload_2

    list_response = await taxi_achievements_py3_web.get(
        '/admin/v1/reward-upload/list', params={'limit': 2},
    )
    assert list_response.status == 200
    list_result = await list_response.json()
    assert len(list_result['items']) == 1
    assert list_result.get('has_more') is False
