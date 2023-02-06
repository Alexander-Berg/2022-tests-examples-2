async def test_fetch_row(
        hiring_forms_mockserver, wait_until_ready, web_context,
):

    await wait_until_ready()
    query = 'SELECT $1 AS a, $2 AS b'
    binds = ('hello', 'world')

    async with web_context.postgresql() as conn:
        row = await conn.fetch_row(query, *binds)
        assert dict(row) == {'a': 'hello', 'b': 'world'}


async def test_fetch_row_empty_resp(
        hiring_forms_mockserver, wait_until_ready, web_context,
):

    await wait_until_ready()
    query = 'SELECT $1 AS a, $2 AS b WHERE FALSE'
    binds = ('hello', 'world')

    async with web_context.postgresql() as conn:
        row = await conn.fetch_row(query, *binds)
        assert row is None
