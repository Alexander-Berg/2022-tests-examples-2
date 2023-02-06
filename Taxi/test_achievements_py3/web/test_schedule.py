import pytest


@pytest.mark.xfail(reason='temporary disabled')
async def test_schedule_add(web_app_client):
    data = {
        'yql_text': 'Test YQL',
        'reward_id': 666,
        'upload_type': 'set_unlocked',
        'initiator': {'yandex_login': 'test'},
        'period_minutes': 1,
        'is_active': True,
    }
    response = await web_app_client.post(
        '/admin/v1/reward-schedule/add', json=data,
    )
    assert response.status == 200

    result_add = await response.json()
    response = await web_app_client.get(
        '/admin/v1/reward-schedule/retrieve', params={'id': result_add['id']},
    )
    assert response.status == 200
    result_retrieve = await response.json()
    assert result_add == result_retrieve

    assert result_add.get('id')
    assert result_add.get('updated_at')
    assert result_add.get('is_active') == data['is_active']
    assert result_add.get('period_minutes') == data['period_minutes']
    assert result_add.get('yql_text') == data['yql_text']
    assert result_add.get('initiator', {}).pop('created_at')
    assert result_add.get('initiator') == data['initiator']


@pytest.mark.xfail(reason='temporary disabled')
async def test_schedule_not_found(web_app_client):
    response = await web_app_client.get(
        '/admin/v1/reward-schedule/retrieve', params={'id': '1'},
    )
    assert response.status == 404


@pytest.mark.xfail(reason='temporary disabled')
async def test_schedule_set(web_app_client):
    data = {
        'yql_text': 'Test YQL',
        'reward_id': 666,
        'upload_type': 'set_unlocked',
        'initiator': {'yandex_login': 'test'},
        'period_minutes': 1,
        'is_active': True,
    }
    response = await web_app_client.post(
        '/admin/v1/reward-schedule/add', json=data,
    )
    assert response.status == 200
    result_add = await response.json()
    assert result_add['id'] == '1'
    assert result_add['is_active'] is True
    assert result_add['period_minutes'] == 1

    new_data = {
        'id': result_add['id'],
        'updated_at': result_add['updated_at'],
        'period_minutes': 2,
        'is_active': False,
    }
    response = await web_app_client.post(
        '/admin/v1/reward-schedule/store', json=new_data,
    )
    assert response.status == 200
    result_store_1 = await response.json()

    assert result_store_1['id'] == '1'
    assert result_store_1['is_active'] is False
    assert result_store_1['period_minutes'] == 2

    new_data['period_minutes'] = 4
    new_data['updated_at'] = result_store_1['updated_at']
    response = await web_app_client.post(
        '/admin/v1/reward-schedule/store', json=new_data,
    )
    assert response.status == 200
    result_store = await response.json()

    assert result_store['id'] == result_add['id']
    assert result_store['updated_at'] != result_add['updated_at']
    assert result_store['period_minutes'] == new_data['period_minutes']
    assert result_store['is_active'] == new_data['is_active']

    response = await web_app_client.get(
        '/admin/v1/reward-schedule/retrieve', params={'id': result_add['id']},
    )
    assert response.status == 200
    result_retrieve = await response.json()
    assert result_store == result_retrieve


@pytest.mark.xfail(reason='temporary disabled')
async def test_schedule_list(web_app_client):
    data = {
        'yql_text': 'Test YQL',
        'upload_type': 'set_unlocked',
        'initiator': {'yandex_login': 'test'},
        'period_minutes': 1,
        'is_active': True,
    }
    rewards = {0: 666, 1: 777, 2: 888}
    for i in range(3):
        data['reward_id'] = rewards[i]
        response = await web_app_client.post(
            '/admin/v1/reward-schedule/add', json=data,
        )
        assert response.status == 200

    response = await web_app_client.get(
        '/admin/v1/reward-schedule/list', params={'limit': 2},
    )
    assert response.status == 200
    result = await response.json()
    assert len(result['items']) == 2
    assert result.get('has_more') is True
    assert result.get('cursor')

    next_response = await web_app_client.get(
        '/admin/v1/reward-schedule/list',
        params={'limit': 2, 'cursor': result.get('cursor')},
    )
    assert next_response.status == 200
    next_result = await next_response.json()
    assert len(next_result['items']) == 1
    assert next_result.get('has_more') is False
    assert next_result.get('cursor')

    last_response = await web_app_client.get(
        '/admin/v1/reward-schedule/list',
        params={'limit': 2, 'cursor': next_result.get('cursor')},
    )
    assert last_response.status == 200
    last_result = await last_response.json()
    assert not last_result['items']
    assert last_result.get('has_more') is False
    assert last_result.get('cursor') is None


@pytest.mark.xfail(reason='temporary disabled')
async def test_schedule_add_idempotency(web_app_client):
    data = {
        'yql_text': 'Test YQL',
        'reward_id': 666,
        'upload_type': 'set_unlocked',
        'initiator': {'yandex_login': 'test'},
        'period_minutes': 1,
        'is_active': True,
    }
    response = await web_app_client.post(
        '/admin/v1/reward-schedule/add',
        json=data,
        headers={'X-Idempotency-Token': '1'},
    )
    assert response.status == 200
    upload_1 = await response.json()

    response = await web_app_client.post(
        '/admin/v1/reward-schedule/add',
        json=data,
        headers={'X-Idempotency-Token': '1'},
    )
    assert response.status == 200
    upload_2 = await response.json()
    assert upload_1 == upload_2

    list_response = await web_app_client.get(
        '/admin/v1/reward-schedule/list', params={'limit': 2},
    )
    assert list_response.status == 200
    list_result = await list_response.json()
    assert len(list_result['items']) == 1
    assert list_result.get('has_more') is False


@pytest.mark.xfail(reason='temporary disabled')
async def test_schedule_set_idempotency(web_app_client):
    data = {
        'yql_text': 'Test YQL',
        'reward_id': 666,
        'upload_type': 'set_unlocked',
        'initiator': {'yandex_login': 'test'},
        'period_minutes': 1,
        'is_active': True,
    }
    response = await web_app_client.post(
        '/admin/v1/reward-schedule/add',
        json=data,
        headers={'X-Idempotency-Token': '1'},
    )
    assert response.status == 200
    result_add = await response.json()

    new_data = {
        'id': result_add['id'],
        'updated_at': result_add['updated_at'],
        'period_minutes': 2,
        'is_active': False,
    }
    response = await web_app_client.post(
        '/admin/v1/reward-schedule/store',
        json=new_data,
        headers={'X-Idempotency-Token': '2'},
    )
    assert response.status == 200
    set_1 = await response.json()

    response = await web_app_client.post(
        '/admin/v1/reward-schedule/store',
        json=new_data,
        headers={'X-Idempotency-Token': '2'},
    )
    assert response.status == 200
    set_2 = await response.json()
    assert set_1 == set_2

    # после предыдущего апдейта поменялся updated_at
    response = await web_app_client.post(
        '/admin/v1/reward-schedule/store',
        json=new_data,
        headers={'X-Idempotency-Token': '3'},
    )
    assert response.status == 409
