async def test_find_simple(taxi_blocklist, add_request, headers):
    # Добавляем блокировку по park_id и car_number, потом ищем
    # только по car_number, проверяем, что блокировок нет
    # потом ищем по park_id и car_number, проверяем, что блокировки есть
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/add', json=add_request, headers=headers,
    )
    assert res.status_code == 200

    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/find',
        json=dict(kwargs=dict(car_number=add_request['kwargs']['car_number'])),
        headers=headers,
    )

    assert res.status_code == 200

    assert not res.json()['blocks']

    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/find',
        json=dict(kwargs=add_request['kwargs']),
        headers=headers,
    )

    assert len(res.json()['blocks']) == 1


async def test_find_admin_designation(taxi_blocklist, add_request, headers):
    # Добавляем блокировку по park_id и car_number, потом
    # находим её и провериям designation предиката
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/add', json=add_request, headers=headers,
    )
    assert res.status_code == 200

    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/find',
        json=dict(kwargs=add_request['kwargs']),
        headers=headers,
    )

    assert len(res.json()['blocks']) == 1
    assert res.json()['blocks'][0]['designation'] == 'park_car_number'


async def test_find_internal_designation(taxi_blocklist, add_request, headers):
    # Добавляем блокировку по park_id и car_number, потом
    # не находим designation предиката, потому что
    # designation должено быть только в admin ручке
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/add', json=add_request, headers=headers,
    )
    assert res.status_code == 200

    res = await taxi_blocklist.post(
        '/internal/blocklist/v1/find',
        json=dict(kwargs=add_request['kwargs']),
        headers=headers,
    )

    assert len(res.json()['blocks']) == 1
    assert 'designation' not in res.json()['blocks'][0]


async def test_find_many(
        pgsql, load_json, taxi_blocklist, add_request, headers,
):
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/add', json=add_request, headers=headers,
    )
    assert res.status_code == 200

    park_id = add_request['kwargs']['park_id']
    del add_request['kwargs']['park_id']
    add_request['predicate_id'] = '11111111-1111-1111-1111-111111111111'
    headers['X-Idempotency-Token'] = headers['X-Idempotency-Token'] + '1'
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/add', json=add_request, headers=headers,
    )
    assert res.status_code == 200

    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/find',
        json={'kwargs': {'car_number': add_request['kwargs']['car_number']}},
        headers=headers,
    )

    assert len(res.json()['blocks']) == 1

    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/find',
        json={
            'kwargs': {
                'car_number': add_request['kwargs']['car_number'],
                'park_id': park_id,
            },
        },
        headers=headers,
    )

    assert len(res.json()['blocks']) == 2


async def test_find_meta(taxi_blocklist, add_request, headers):
    add_request['meta'] = {
        'meta_key_1': 'meta_val_1',
        'meta_key_2': 'meta_val_2',
        'meta_key_3': 'meta_val_3',
    }
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/add', json=add_request, headers=headers,
    )
    assert res.status_code == 200

    # Проверяем, что отдается мета целиком
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/find',
        json={'kwargs': add_request['kwargs']},
        headers=headers,
    )
    assert res.status_code == 200
    assert res.json()['blocks'][0]['meta'] == add_request['meta']

    # Проверяем проекцию
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/find',
        json=dict(
            kwargs=add_request['kwargs'], meta_projection=['meta_key_2'],
        ),
        headers=headers,
    )
    assert res.status_code == 200
    assert res.json()['blocks'][0]['meta'] == dict(meta_key_2='meta_val_2')

    # Проверяем, что можно запросить без меты совсем (другой запрос в базу)
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/find',
        json=dict(kwargs=add_request['kwargs'], meta_projection=[]),
        headers=headers,
    )
    assert res.status_code == 200
    assert 'meta' not in res.json()['blocks'][0]


async def test_find_active_only(
        load_json, taxi_blocklist, add_request, headers,
):
    # Добавляем блокировку
    predicate_id = add_request['predicate_id']
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/add', json=add_request, headers=headers,
    )
    assert res.status_code == 200

    # Удаляем только что добавленную блокировку
    delete_request = dict(
        block=dict(block_id=res.json()['block_id'], comment='test'),
        predicate_id=predicate_id,
    )
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/delete', json=delete_request, headers=headers,
    )
    assert res.status_code == 200

    # Проверяем, что блокировка находится и что она неактивна
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/find',
        json=dict(kwargs=add_request['kwargs']),
        headers=headers,
    )
    assert res.status_code == 200
    blocks = res.json()['blocks']
    assert len(blocks) == 1
    assert blocks[0]['status'] == 'inactive'

    # Проверяем, что блокировка не находится, если запросить только активные
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/find',
        json=dict(kwargs=add_request['kwargs'], status='active'),
        headers=headers,
    )
    assert res.status_code == 200
    blocks = res.json()['blocks']
    assert not blocks


async def test_find_without_history(
        load_json, taxi_blocklist, add_request, headers,
):
    # Добавляем блокировку
    predicate_id = add_request['predicate_id']
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/add', json=add_request, headers=headers,
    )
    assert res.status_code == 200

    # Удаляем только что добавленную блокировку
    block_id = res.json()['block_id']
    delete_request = dict(
        block=dict(block_id=block_id, comment='test'),
        predicate_id=predicate_id,
    )
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/delete', json=delete_request, headers=headers,
    )
    assert res.status_code == 200

    # Проверяем загрузку с историей
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/find',
        json=dict(kwargs=add_request['kwargs'], load_history=True),
        headers=headers,
    )
    assert res.status_code == 200
    history = res.json()['history']
    assert len(history.get(block_id)) == 2  # добавление и удаление

    # Проверяем загрузку без истории
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/find',
        json=dict(kwargs=add_request['kwargs'], load_history=False),
        headers=headers,
    )
    assert res.status_code == 200
    history = res.json()['history']
    assert not history
