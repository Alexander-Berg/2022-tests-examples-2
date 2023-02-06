async def test_over_ok(tap, http_api, cfg):
    cfg.set('seregaapi', 'yes')
    t = await http_api()

    with tap:
        await t.post_ok(
            'api_developer_pretty_error',
            json={'bar': 1, 'baz': 'foo'},
        )
        t.status_is(200, diag=True)
        t.json_is('foo', 42)

        await t.post_ok(
            'api_developer_pretty_error',
            json={
                'bar': '1',
                'baz': 'foo',
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST', 'Correct code')
        t.json_like(
            'details.errors.0.message',
            "'1' is not of type 'integer'",
            'Correct message',
        )
        t.json_is(
            'details.errors.0.path',
            'body.bar',
            'Correct path',
        )

        await t.post_ok(
            'api_developer_pretty_error',
            json={
                'bar': 1,
                'baz': 'foo',
                'foo': {
                    'foo_string': '1',
                }
            },
        )
        t.status_is(200, diag=True)
        t.json_is('foo', 42)

        await t.post_ok(
            'api_developer_pretty_error',
            json={
                'bar': 1,
                'baz': 'foo',
                'foo': {
                    'foo_string': 1,
                }
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST', 'Correct code')
        t.json_is(
            'details.errors.0.path',
            'body.foo.foo_string',
            'Correct path',
        )

        await t.post_ok(
            'api_developer_pretty_error',
            json={
                'bar': 1,
                'baz': 'foo',
                'foo': {
                    'foo_string': '1',
                    'foo_array': [1, 2]
                }
            },
        )
        t.status_is(200, diag=True)
        t.json_is('foo', 42)

        await t.post_ok(
            'api_developer_pretty_error',
            json={
                'bar': 1,
                'baz': 'foo',
                'foo': {
                    'foo_string': '1',
                    'foo_array': ['1', 2]
                }
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST', 'Correct code')
        t.json_is(
            'details.errors.0.path',
            'body.foo.foo_array.0',
            'Correct path',
        )

        await t.post_ok(
            'api_developer_pretty_error',
            json={
                'bar': 1,
                'baz': 'foo',
                'foo': {
                    'foo_string': '1',
                    'foo_array': [1, '2']
                }
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST', 'Correct code')
        t.json_is(
            'details.errors.0.path',
            'body.foo.foo_array.1',
            'Correct path',
        )
