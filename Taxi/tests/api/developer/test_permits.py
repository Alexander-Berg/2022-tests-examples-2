from http.cookies import SimpleCookie

from stall import cfg
from libstall.util import token


async def test_permits(api, tap, dataset):

    tap.plan(18)

    t = await api()
    await t.get_ok('api_developer_permits')
    t.status_is(401, diag=True)
    t.json_is('code', 'ER_AUTH', 'code')
    t.json_is('message', 'Authorization required', 'message')

    t.header_has('Set-Cookie', 'куки установлены')


    res_cookie = t.res['headers'].get('Set-Cookie')
    tap.ok(res_cookie, 'кука установлена')

    cookie = SimpleCookie()
    cookie.load(res_cookie)

    value = cookie[cfg('web.cookie.device.name')].value
    tap.ok(value, 'Значение куки есть')

    payload = token.unpack(cfg('web.cookie.device.secret'), value)
    tap.isa_ok(payload, dict, 'упаковано с секретом конфига')
    tap.ok('device' in payload, 'device есть')
    tap.like(payload['device'], r'^[a-fA-F0-9]{32}$', 'формат id device')


    await t.get_ok('api_developer_permits')
    t.status_is(401, diag=True)
    t.header_hasnt('Set-Cookie', 'Повторно device-куку не даём')

    user = await dataset.user(role='admin')
    t.tap.ok(user, 'пользователь создан')
    t.set_user(user)

    await t.get_ok('api_developer_permits')
    t.status_is(200, diag=True)

    t.json_is('code', 'OK')
    t.json_is('message', f'cur_user,{user.user_id}')


    tap()

