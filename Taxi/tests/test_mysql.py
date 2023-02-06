from stall.mysql import eda_mysql


async def test_mysql(tap):
    with tap.plan(2, 'Доступ к mysql'):
        tap.ok(eda_mysql, 'синглтон инстанцирован')

        async with eda_mysql() as cursor:
            await cursor.execute('SELECT %s AS `ping`', (1,))
            r = await cursor.fetchall()
            tap.eq(r, [{'ping': 1}], 'pong')
