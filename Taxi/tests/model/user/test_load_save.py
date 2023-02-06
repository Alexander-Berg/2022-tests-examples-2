from stall.model.user import User
from stall.model.role import Role


async def test_save(tap, uuid):
    with tap.plan(23, 'Операции сохранения/загрузки'):

        user_eid = uuid()

        user = User({'provider': 'yandex',
                     'provider_user_id': user_eid,
                     'role': 'authen_guest'})
        tap.ok(user, 'инстанцирован')

        tap.eq(user.user_id, None, 'идентификатора до сохранения нет')
        tap.ok(await user.save(), 'сохранен')
        tap.ok(user.user_id, 'идентификатор назначился')
        user_id = user.user_id

        tap.eq(user.nick, None, 'ника нет')
        user.nick = 'unera'

        tap.ok(await user.save(), 'сохранен еще раз')
        tap.eq(user.user_id, user_id, 'идентификатор не поменялся')
        tap.eq(user.nick, 'unera', 'ник')

        tap.isa_ok(user.role, Role, 'роль')
        tap.eq(user.role, 'authen_guest', 'по умолчанию - роль гостя')


        loaded = await User.load(user_id)
        tap.ok(loaded, 'загружено')
        tap.isa_ok(loaded, User, 'тип')
        tap.eq(loaded.nick, user.nick, 'ник')
        tap.eq(loaded.user_id, user.user_id, 'id')

        loaded = await User.load(('yandex', user_eid), by='provider')
        tap.ok(loaded, 'загружено')
        tap.isa_ok(loaded, User, 'тип')
        tap.eq(loaded.nick, user.nick, 'ник')
        tap.eq(loaded.user_id, user.user_id, 'id')

        user.device = [uuid()]
        tap.ok(await user.save(), 'сохранили device')
        tap.isa_ok(user.device, list, 'device')
        tap.ok(len(user.device), 'не пустой')

        tap.ok(await user.rm(), 'удалён')
        tap.ok(not await User.load(user_id), 'удалён в БД')

async def test_barcode_change(tap, dataset):
    with tap.plan(5, 'тесты на смену баркода'):
        user = await dataset.user()
        tap.ok(user, 'пользователь сгенерирован')
        serial = user.serial

        tap.ok(await user.save(), 'сохранён обычно')
        tap.eq(user.serial, serial, 'сериал у пользователя не поменялся')

        user.serial = None
        tap.ok(await user.save(), 'сохранён')

        tap.ne(user.serial, serial, 'сериал у пользователя поменялся')
