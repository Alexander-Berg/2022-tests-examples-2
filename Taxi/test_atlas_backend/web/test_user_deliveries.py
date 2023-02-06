import datetime

import pytest

NOW = datetime.datetime(2020, 10, 20, 0, 0, 0)


@pytest.mark.now(NOW.isoformat())
async def test_create_delivery(
        user_deliveries_mock,
        web_app_client,
        db,
        load_json,
        patch,
        atlas_blackbox_mock,
):
    delivery_example = load_json('user_delivery_example.json')
    create_delivery_params = {
        'yt_proxy': delivery_example['yt_proxy'],
        'query': delivery_example['query'],
        'id': delivery_example['id'],
        'name': delivery_example['name'],
        'run_every': delivery_example['run_every'],
        'last_ts_1_min': delivery_example['last_ts_1_min'],
        'description': delivery_example['description'],
    }

    response = await web_app_client.post(
        '/api/delivery/create_delivery', json=create_delivery_params,
    )

    assert response.status == 200

    new_delivery = await db.atlas_data_delivery_tst.find(
        {'id': delivery_example['id']},
    ).to_list(None)

    assert len(new_delivery) == 1
    assert 'def latlon2quadkey' in new_delivery[0]['query_full']

    response = await web_app_client.post(
        '/api/delivery/create_delivery', json=create_delivery_params,
    )
    assert response.status == 400

    content = await response.json()

    assert content == {
        'code': 1,
        'desc': 'Delivery with id \'test\' already exists',
    }


@pytest.mark.parametrize('username', ['eugenest'])
async def test_get_actual_deliveries(
        user_deliveries_mock,
        web_app_client,
        db,
        atlas_blackbox_mock,
        username,
):
    response = await web_app_client.get('/api/delivery/get_actual_deliveries')
    assert response.status == 200
    content = await response.json()

    ids = [
        'test_order_count',
        'test_migrate_delivery',
        'test_order_count_2',
        'test_1',
    ]

    assert len(content['desc']) == 4
    # First should go user deliveries
    assert content['desc'][0]['author'] == username
    for delivery in content['desc']:
        assert delivery['id'] in ids


async def test_get_deliveries_to_process(
        user_deliveries_mock, web_app_client, db, patch,
):
    response = await web_app_client.get(
        '/api/delivery/get_deliveries_to_process',
    )

    ids = ['test_order_count', 'test_1']

    assert response.status == 200
    content = await response.json()
    assert len(content['desc']) == 2
    for delivery in content['desc']:
        assert delivery['id'] in ids


async def test_get_delivery_config(user_deliveries_mock, web_app_client, db):
    response = await web_app_client.get('/api/delivery/get_config')

    assert response.status == 200

    content = await response.json()

    assert content == {'code': 0, 'desc': {'database': 'data_delivery_tst'}}


async def test_get_delivery_data(user_deliveries_mock, web_app_client, db):
    # Test get nonexistent delivery
    response = await web_app_client.get(
        '/api/delivery/data/5c4120c7-9000-4c64-ba72-b935197e9aea',
    )

    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 1,
        'desc': (
            'Delivery was not found: {'
            '\'uuid\': \'5c4120c7-9000-4c64-ba72-b935197e9aea\', '
            '\'state\': {\'$ne\': \'deprecated\'}}'
        ),
    }

    response = await web_app_client.get(
        '/api/delivery/data/a5023b9a-8589-4219-8f97-5aca1ac209fb',
    )

    assert response.status == 200
    content = await response.json()
    assert content['desc']['uuid'] == 'a5023b9a-8589-4219-8f97-5aca1ac209fb'
    assert (
        content['desc']['description']
        == 'Тестовая поставка с количеством заказов в минуту'
    )

    # Test limiting by fields param
    response = await web_app_client.get(
        '/api/delivery/data/a5023b9a-8589-4219-8f97-5aca1ac209fb',
        params={'fields': 'state'},
    )
    assert response.status == 200
    content = await response.json()
    assert content['desc'] == {'state': 'active'}


@pytest.mark.now(NOW.isoformat())
async def test_get_running_deliveries(
        user_deliveries_mock, web_app_client, db,
):
    response = await web_app_client.get('/api/delivery/get_running_deliveries')

    assert response.status == 200
    content = await response.json()
    assert len(content['desc']) == 1
    assert content['desc'][0]['id'] == 'test_order_count_2'

    # Test delta param
    response = await web_app_client.get(
        '/api/delivery/get_running_deliveries', params={'delta': 1800},
    )
    assert response.status == 200
    content = await response.json()
    assert not content['desc']


@pytest.mark.parametrize('username', ['eugenest'])
async def test_update_delivery_data(
        user_deliveries_mock,
        web_app_client,
        db,
        patch,
        atlas_blackbox_mock,
        username,
):
    delivery_id = 'a5023b9a-8589-4219-8f97-5aca1ac209fb'
    update_delivery_data = {
        'description': 'ololo2',
        'autorestart': True,
        'run_every': 10,
    }
    response = await web_app_client.post(
        f'/api/delivery/data/{delivery_id}', json=update_delivery_data,
    )
    assert response.status == 200
    delivery_data = await db.atlas_data_delivery_tst.find_one(
        {'uuid': delivery_id},
    )
    fields = update_delivery_data.keys()
    for field in fields:
        assert delivery_data[field] == update_delivery_data[field]

    # Test changed query
    update_delivery_data['query'] = delivery_data['query'] + ' '
    update_delivery_data['last_ts_1_min'] = (
        delivery_data['last_ts_1_min'] + 1800
    )
    response = await web_app_client.post(
        f'api/delivery/data/{delivery_id}', json=update_delivery_data,
    )
    assert response.status == 200

    old_delivery = await db.atlas_data_delivery_tst.find_one(
        {'uuid': delivery_id},
    )
    assert old_delivery['state'] == 'deprecated'

    new_delivery = await db.atlas_data_delivery_tst.find_one(
        {'id': 'test_order_count', 'uuid': {'$ne': delivery_id}},
    )
    assert new_delivery['query'] == update_delivery_data['query']
    assert (
        new_delivery['last_ts_1_min'] == update_delivery_data['last_ts_1_min']
    )


@pytest.mark.now(NOW.isoformat())
async def test_update_delivery_state(
        user_deliveries_mock, web_app_client, db, patch,
):
    # Test update_state running->running
    update_state_json = {
        'delivery_uuid': '1734b03b-6cf3-4ade-9c2f-de2f835f222d',
        'state': 'running',
    }
    delivery_before = await db.atlas_data_delivery_tst.find_one(
        {'uuid': '1734b03b-6cf3-4ade-9c2f-de2f835f222d'},
    )
    assert delivery_before['state'] == 'running'

    response = await web_app_client.post(
        '/api/delivery/update_state', json=update_state_json,
    )
    assert response.status == 200

    delivery = await db.atlas_data_delivery_tst.find_one(
        {'uuid': '1734b03b-6cf3-4ade-9c2f-de2f835f222d'},
    )

    assert delivery['state'] == 'running'

    # Test deprecating
    update_state_json = {
        'delivery_uuid': 'a5023b9a-8589-4219-8f97-5aca1ac209fb',
        'state': 'deprecated',
    }
    response = await web_app_client.post(
        '/api/delivery/update_state', json=update_state_json,
    )
    assert response.status == 200

    deprecated_delivery = await db.atlas_data_delivery_tst.find_one(
        {'uuid': 'a5023b9a-8589-4219-8f97-5aca1ac209fb'}, {'state': 1},
    )

    assert deprecated_delivery['state'] == 'deprecated'

    # Test finishing delivery
    finish_running_json = {
        'delivery_uuid': '1734b03b-6cf3-4ade-9c2f-de2f835f222d',
        'state': 'active',
    }

    response = await web_app_client.post(
        '/api/delivery/update_state', json=finish_running_json,
    )
    assert response.status == 200
    delivery = await db.atlas_data_delivery_tst.find_one(
        {'uuid': '1734b03b-6cf3-4ade-9c2f-de2f835f222d'},
        {'state': 1, 'last_end_run_ts': 1, 'last_ts_1_min': 1, '_id': 0},
    )
    assert delivery == {
        'last_end_run_ts': 1603152000,
        'last_ts_1_min': 1559225390,
        'state': 'active',
    }

    running_log = await db.atlas_delivery_logs.find_one(
        {'uuid': '1734b03b-6cf3-4ade-9c2f-de2f835f222d'}, {'_id': 0},
    )
    assert running_log == {
        'uuid': '1734b03b-6cf3-4ade-9c2f-de2f835f222d',
        'id': 'test_order_count_2',
        'state': 'active',
        'start_ts': 1603151000,
        'end_ts': 1603152000,
        'details': (
            'https://yql.yandex-team.ru/Operations/'
            'XO_rU2im9UVcTrOQWjjn34GZLEiHlNQYu6GwdltVxTo='
        ),
    }

    # Test start running delivery
    start_running_json = {
        'delivery_uuid': '178f5264-611d-4d67-a887-02e9dd4bf4a1',
        'state': 'running',
        'workflow_id': 'a7c0a3a7-3439-4016-a240-41dbe0261776',
        'instance_id': '7ff5f644-f71d-4164-8c51-0d8cfc2beda2',
        'details': 'ololo',
    }

    response = await web_app_client.post(
        '/api/delivery/update_state', json=start_running_json,
    )
    assert response.status == 200

    delivery = await db.atlas_data_delivery_tst.find_one(
        {'uuid': '178f5264-611d-4d67-a887-02e9dd4bf4a1'},
    )
    changed_fields = [
        'workflow_id',
        'instance_id',
        'details',
        'state',
        'last_start_run_ts',
    ]
    start_running_json['last_start_run_ts'] = 1603152000
    for field in changed_fields:
        assert delivery[field] == start_running_json[field]
