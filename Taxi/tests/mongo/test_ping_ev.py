async def test_ping_ev(tap, uuid, mongo):   # pylint: disable=unused-argument
    tap.plan(7)
    tap.ok(mongo, 'инстанцирован')
    tap.eq(mongo.cache, {}, 'нет записей')

    async with mongo('ev') as conn:
        tap.ok(conn, 'соединение создано')


        _id = uuid()
        res = await conn.test.insert_one({'hello': _id})

        tap.like(res.inserted_id, r'^[0-9a-fA-F]+$', 'inserted_id')

        inserted_id = res.inserted_id

        res2 = await conn.test.find_one({'_id': inserted_id})

        tap.ok(res2, 'результат получен')
        tap.eq(res2['_id'], inserted_id, 'inserted_id')
        tap.eq(res2['hello'], _id, 'id')

    tap()
