from stall.model.user import User
from stall.config import cfg


async def test_seek(tap, dataset, uuid):

    tap.plan(35)
    store = await dataset.store()
    tap.ok(store, 'склад создан')

    users = []

    for _ in range(5):
        user = await dataset.user(role='store_admin',
                                  nick=uuid(),
                                  email='%s@mail.ru' % uuid(),
                                  store=store)
        tap.ok(user, 'Пользователь создан')
        tap.ok(user.email, 'мыло есть')
        tap.ok(user.nick, 'ник есть')
        tap.eq(user.role, 'store_admin', 'Роль')
        tap.eq(user.store_id, store.store_id, 'Склад')
        users.append(user)

    uids = set(map(lambda x: x.user_id, users))

    loaded = []

    cursor = await User.list(by='look', limit=3, store_id=store.store_id)
    tap.ok(cursor, 'список получен')
    tap.eq(len(cursor.list), 3, 'Число записей')
    tap.ok(cursor.cursor_str, 'Можно еще делать запросы')

    loaded.extend(cursor.list)

    cursor2 = await user.list(by='look', store_id=store.store_id,
                              cursor_str=cursor.cursor_str)
    tap.ok(cursor2, 'второй список получен')
    tap.eq(len(cursor2.list), 2, 'Число записей')
    tap.ok(not cursor2.cursor_str, 'Запросы больше делать нельзя')

    loaded.extend(cursor2.list)
    loaded_uids = set(map(lambda x: x.user_id, loaded))

    tap.eq(loaded_uids, uids, 'все пользователи загружены')

    print('nick:', users[0].nick)
    cursor = await User.list(by='look', nick=users[0].nick)
    tap.ok(cursor, 'список получен')
    tap.eq(len(cursor.list), 1, 'Один пользователь только найден')

    tap()


async def test_seek_pagination(tap, dataset, uuid):
    limit = cfg('cursor.limit')
    users_number = int(limit * 2.43)
    with tap.plan(3):
        store = await dataset.store()
        tap.ok(store, 'склад создан')
        ids = []
        for _ in range(users_number):
            user = await dataset.user(role='store_admin',
                                      nick=uuid(),
                                      email='%s@mail.ru' % uuid(),
                                      store=store)
            ids += [user.user_id]
        ret_ids = []
        with tap.subtest(None, 'Дочитываем до конца') as taps:
            cursor = await User.list(by='look', store_id=store.store_id)
            taps.ok(cursor.list, 'Получены пользователи')
            taps.ok(cursor.cursor_str, 'Прочитано еще не все')
            ret_ids += [user.user_id for user in cursor.list]
            while cursor.cursor_str:
                cursor = await User.list(by='look', store_id=store.store_id,
                                         cursor_str=cursor.cursor_str)
                ret_ids += [user.user_id for user in cursor.list]

        tap.eq_ok(
            sorted(ret_ids),
            sorted(ids),
            'Пользователи прочитаны правильно'
        )
