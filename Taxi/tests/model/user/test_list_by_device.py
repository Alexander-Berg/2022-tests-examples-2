from stall.model.user import User


async def test_load_by_device(dataset, tap, uuid):
    with tap.plan(6):
        uid1 = uuid()
        uid2 = uuid()
        user = await dataset.user(device=[uid1, uid2])
        tap.ok(user, 'пользователь создан')

        cursor = await User.list(devices=uid1, by='device', full=True)
        with cursor:
            tap.ok(cursor.list, 'список получен')
            tap.eq(len(cursor.list), 1, 'в нем один элемент')

            loaded = cursor.list[0]

            tap.isa_ok(loaded, User, 'пользователь')
            tap.eq(loaded.user_id, user.user_id, 'идентификатор')

        cursor = await User.list(devices=[], by='device', full=True)
        with cursor:
            tap.eq(len(cursor.list), 0, 'нет выборки')


