from stall import cfg
from stall.model.user import User
from libstall.util import token


async def test_save(tap, uuid):
    with tap.plan(9):
        idstr = uuid()

        user = User({'provider': 'yandex',
                     'provider_user_id': idstr,
                     'role': 'executer'})
        tap.ok(await user.save(), 'пользователь сохранен')

        device = uuid()
        gtoken = user.token(device)
        tap.ok(gtoken, 'токен сгенерирован')
        tap.isa_ok(gtoken, str, 'токен - строка')
        tap.like(gtoken, r'^[a-zA-Z0-9\.+/=]+$', 'символы токена')

        payload = token.unpack(cfg('web.auth.secret'), gtoken)
        tap.isa_ok(payload, dict, 'payload распакован')


        tap.ok(not await User.load(gtoken, by='token'), 'пользователя ещё нет')

        user.device = [device]
        tap.ok(await user.save(), 'пользователь сохранён')
        tap.eq(user.device, [device], 'значение device')

        loaded = await User.load(gtoken, by='token')
        tap.ok(loaded, 'загружен по токену')
