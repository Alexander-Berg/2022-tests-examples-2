HEADERS = {
    'X-B2B-Client-Id': '12345678912345678912345678912345',
    'Accept-Language': 'ru',
}


async def create_comments(taxi_cargo_misc):
    ids = list()
    response = await taxi_cargo_misc.post(
        '/api/b2b/cargo-misc/v1/claims/comments/create',
        params={'idempotency_token': 'a'},
        json={'name': 'some name1', 'comment': 'some comment1'},
        headers=HEADERS,
    )
    assert response.status_code == 200
    ids.append(response.json()['id'])
    response = await taxi_cargo_misc.post(
        '/api/b2b/cargo-misc/v1/claims/comments/create',
        params={'idempotency_token': 'b'},
        json={'name': 'some name2', 'comment': 'some comment2'},
        headers=HEADERS,
    )
    assert response.status_code == 200
    ids.append(response.json()['id'])
    response = await taxi_cargo_misc.post(
        '/api/b2b/cargo-misc/v1/claims/comments/create',
        params={'idempotency_token': 'c'},
        json={
            'name': 'some name3',
            'comment': 'some comment3',
            'tariff': 'cargo',
        },
        headers=HEADERS,
    )
    assert response.status_code == 200
    ids.append(response.json()['id'])
    return ids


async def test_create(taxi_cargo_misc, pgsql):
    response = await taxi_cargo_misc.post(
        '/api/b2b/cargo-misc/v1/claims/comments/create',
        params={'idempotency_token': 'b'},
        json={
            'name': 'some name1',
            'comment': 'some comment1',
            'tariff': 'cargo',
        },
        headers=HEADERS,
    )
    assert response.status_code == 200
    response_json1 = response.json()

    response = await taxi_cargo_misc.post(
        '/api/b2b/cargo-misc/v1/claims/comments/create',
        params={'idempotency_token': 'a'},
        json={
            'name': 'some name2',
            'comment': 'some comment2',
            'tariff': 'econom',
        },
        headers=HEADERS,
    )
    assert response.status_code == 200
    response_json2 = response.json()
    response = await taxi_cargo_misc.post(
        '/api/b2b/cargo-misc/v1/claims/comments/create',
        params={'idempotency_token': 'a'},
        json={
            'name': 'some name2',
            'comment': 'some comment2',
            'tariff': 'econom',
        },
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response_json2 == response.json()

    cursor = pgsql['cargo_misc'].conn.cursor()
    cursor.execute(
        """
        SELECT id, name, comment, tariff
        FROM cargo_misc.cargo_comments
        """,
    )
    assert list(cursor) == [
        (response_json1['id'], 'some name1', 'some comment1', 'cargo'),
        (response_json2['id'], 'some name2', 'some comment2', 'econom'),
    ]


async def test_create_rewrite_default(taxi_cargo_misc, pgsql):
    await create_comments(taxi_cargo_misc)

    response = await taxi_cargo_misc.post(
        '/api/b2b/cargo-misc/v1/claims/comments/create',
        params={'idempotency_token': 'd'},
        json={
            'name': 'some name2',
            'comment': 'some comment2',
            'tariff': 'cargo',
        },
        headers=HEADERS,
    )
    assert response.status_code == 200
    comment_id = response.json()['id']

    cursor = pgsql['cargo_misc'].conn.cursor()
    cursor.execute(
        """
        SELECT id
        FROM cargo_misc.cargo_comments
        WHERE tariff = 'cargo'
        """,
    )
    assert list(cursor) == [(comment_id,)]


async def test_edit(taxi_cargo_misc, pgsql):
    ids = await create_comments(taxi_cargo_misc)

    response = await taxi_cargo_misc.post(
        '/api/b2b/cargo-misc/v1/claims/comments/edit',
        json={
            'id': ids[2],
            'name': 'some name4',
            'comment': 'some comment4',
            'tariff': 'cargo',
        },
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': ids[2],
        'name': 'some name4',
        'comment': 'some comment4',
        'tariff': 'cargo',
    }
    cursor = pgsql['cargo_misc'].conn.cursor()
    cursor.execute(
        f"""
        SELECT id, name, comment, tariff
        FROM cargo_misc.cargo_comments
        WHERE id = '{ids[2]}'
        """,
    )
    assert list(cursor) == [(ids[2], 'some name4', 'some comment4', 'cargo')]


async def test_edit_404(taxi_cargo_misc):
    await create_comments(taxi_cargo_misc)

    response = await taxi_cargo_misc.post(
        '/api/b2b/cargo-misc/v1/claims/comments/edit',
        json={
            'id': 'abacaba',
            'name': 'some name4',
            'comment': 'some comment4',
            'tariff': 'cargo',
        },
        headers=HEADERS,
    )
    assert response.status_code == 404


async def test_edit_rewrite_default(taxi_cargo_misc, pgsql):
    ids = await create_comments(taxi_cargo_misc)

    response = await taxi_cargo_misc.post(
        '/api/b2b/cargo-misc/v1/claims/comments/edit',
        json={
            'id': ids[1],
            'name': 'some name4',
            'comment': 'some comment4',
            'tariff': 'cargo',
        },
        headers=HEADERS,
    )
    assert response.status_code == 200

    cursor = pgsql['cargo_misc'].conn.cursor()
    cursor.execute(
        """
        SELECT id
        FROM cargo_misc.cargo_comments
        WHERE tariff = 'cargo'
        """,
    )
    assert list(cursor) == [(ids[1],)]


async def test_delete(taxi_cargo_misc, pgsql):
    ids = await create_comments(taxi_cargo_misc)

    for comment_id in ids:
        response = await taxi_cargo_misc.delete(
            '/api/b2b/cargo-misc/v1/claims/comments/delete',
            params={'id': comment_id},
            headers=HEADERS,
        )
        assert response.status_code == 200

    cursor = pgsql['cargo_misc'].conn.cursor()
    cursor.execute(
        """
        SELECT id, name, comment, tariff
        FROM cargo_misc.cargo_comments
        """,
    )
    assert not list(cursor)


async def test_get(taxi_cargo_misc):
    ids = await create_comments(taxi_cargo_misc)

    response = await taxi_cargo_misc.get(
        '/api/b2b/cargo-misc/v1/claims/comments/get',
        params={'id': ids[2]},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': ids[2],
        'name': 'some name3',
        'comment': 'some comment3',
        'tariff': 'cargo',
    }


async def test_get_404(taxi_cargo_misc):
    await create_comments(taxi_cargo_misc)

    response = await taxi_cargo_misc.get(
        '/api/b2b/cargo-misc/v1/claims/comments/get',
        params={'id': 'abacaba'},
        headers=HEADERS,
    )
    assert response.status_code == 404


async def test_list(taxi_cargo_misc):
    ids = await create_comments(taxi_cargo_misc)

    response = await taxi_cargo_misc.get(
        '/api/b2b/cargo-misc/v1/claims/comments/list', headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'comments': [
            {'id': ids[0], 'name': 'some name1', 'comment': 'some comment1'},
            {'id': ids[1], 'name': 'some name2', 'comment': 'some comment2'},
            {
                'id': ids[2],
                'name': 'some name3',
                'comment': 'some comment3',
                'tariff': 'cargo',
            },
        ],
    }


async def test_get_default(taxi_cargo_misc):
    ids = await create_comments(taxi_cargo_misc)

    response = await taxi_cargo_misc.get(
        '/api/b2b/cargo-misc/v1/claims/comments/default',
        params={'tariff': 'cargo'},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': ids[2],
        'name': 'some name3',
        'comment': 'some comment3',
        'tariff': 'cargo',
    }


async def test_get_default_404(taxi_cargo_misc):
    await create_comments(taxi_cargo_misc)

    response = await taxi_cargo_misc.get(
        '/api/b2b/cargo-misc/v1/claims/comments/default',
        params={'tariff': 'econom'},
        headers=HEADERS,
    )
    assert response.status_code == 404
