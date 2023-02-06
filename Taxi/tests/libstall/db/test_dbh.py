async def test_ping(tap, dbh):
    tap.plan(4)
    async with dbh() as conn:
        tap.ok(conn, 'Коннекшен создан')
        tap.eq(conn.mode, 'master', 'master')
        tap.eq(conn.name, 'main', 'имя соответствует имени БД')
        tap.eq(await conn.fetchval('SELECT $1::INTEGER', 123), 123, 'ping')


    tap()
