async def test_ping(api):
    t = await api()
    t.tap.plan(5)
    await t.get_ok('api_developer_ping')
    t.status_is(200, diag=True)

    t.content_type_like(r'^application/json')

    t.json_is('code', 'OK')
    t.json_is('message', 'PONG')

    t.tap()


async def test_validator_ok(api):
    """Правильные параметры"""
    t = await api()
    t.tap.plan(4)

    await t.post_ok(
        'api_developer_test_request',
        json={'bar': 123, 'baz': 'abc'},
    )

    t.status_is(200, diag=True)
    t.content_type_like(r'^application/json')
    t.json_is('foo', 123)

    t.tap()


async def test_validator_ok_unknown(api):
    """Неизвествые параметры игнорируются"""
    t = await api()
    t.tap.plan(4)

    await t.post_ok(
        'api_developer_test_request',
        json={'bar': 123, 'baz': 'abc', 'unknown': 789},
    )

    t.status_is(200)
    t.content_type_like(r'^application/json')
    t.json_is('foo', 123)

    t.tap()


async def test_validator_fail_request(api):
    """Ошибка в запросе"""
    t = await api()
    t.tap.plan(15)

    await t.post_ok(
        'api_developer_test_request',
        json={'bar': 'abc', 'baz': 'abc'},
    )

    t.status_is(400)
    t.content_type_like(r'^application/json')
    t.json_is('code', 'BAD_REQUEST')
    t.json_is(
        'details.errors.0.message',
        "'abc' is not of type 'integer'",
    )

    await t.post_ok(
        'api_developer_test_request',
        json={'bar': 123},
    )

    t.status_is(400)
    t.content_type_like(r'^application/json')
    t.json_is('code', 'BAD_REQUEST')
    t.json_is(
        'details.errors.0.message',
        "'baz' is a required property",
    )

    await t.post_ok(
        'api_developer_test_request',
        json={},
    )

    t.status_is(400)
    t.content_type_like(r'^application/json')
    t.json_is('code', 'BAD_REQUEST')
    t.json_is(
        'details.errors.0.message',
        "'bar' is a required property",
    )

    t.tap()


async def test_validator_fail_response(api):
    """Ошибка в ответе"""
    t = await api()
    t.tap.plan(5)

    await t.get_ok('api_developer_test_response')

    t.status_is(500)
    t.content_type_like(r'^application/json')
    t.json_is('code', 'BAD_RESPONSE')
    t.json_is(
        'details.errors.0.message',
        "'foo' is a required property",
    )

    t.tap()


async def test_validator_not_found(api):
    """Роут не найден"""
    t = await api()
    t.tap.plan(4)

    await t.post_ok('/unknown_route', json={'foo': 123})

    t.status_is(404, diag=True)
    t.content_type_like(r'^application/json')
    t.json_is('code', 'ROUTE_NOT_FOUND')

    t.tap()
