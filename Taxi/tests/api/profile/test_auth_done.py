# pylint: disable=too-many-locals,too-many-statements
from http.cookies import SimpleCookie

import pytest
import yarl

from libstall.util import token
from stall import cfg
from stall.model.user import User


@pytest.mark.parametrize('set_cookie', [0, 1])
async def test_done(tap, api, set_cookie):
    t = await api()

    tap.plan(22)
    await t.post_ok('api_profile_auth_prepare',
                    json={'provider': 'test'})
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_has('url', 'урл есть в ответе')

    url = yarl.URL(t.res['json']['url'])
    tap.eq(url.host, 'test.domain', 'тестовый хост')

    state = url.query.get('state')

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

    device = payload['device']

    await t.post_ok('api_profile_auth_done',
                    json={'code': 123, 'state': state, 'cookie': set_cookie})
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_has('token', 'токен есть')
    t.json_has('device', 'device есть')
    t.json_has('store_id', 'store_id есть')
    if set_cookie:
        t.header_has('Set-Cookie', 'Установка кук есть')
    else:
        t.header_hasnt('Set-Cookie', 'Установки кук нет')

    user = await User.load(t.res['json']['token'], by='token')

    tap.ok(user, 'пользователь создался в БД')
    tap.eq(user.provider, 'test', 'тестовый провайдер')
    tap.eq(user.role, 'authen_guest', 'Роль пользователя')
    tap.ok(device in user.device, 'Девайс прописан в профиль пользователя')

    tap()


@pytest.mark.skip(reason="no way of currently testing this")
async def test_yandex(tap, api):
    with tap.plan(13):
        t = await api()

        await t.post_ok('api_profile_auth_prepare',
                        json={'provider': 'yandex'})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('url', 'урл есть в ответе')

        url = yarl.URL(t.res['json']['url'])
        tap.eq(url.host, 'oauth.yandex.com', 'тестовый хост')

        state = url.query.get('state')

        tap.diag(url)

        await t.post_ok('api_profile_auth_done',
                        json={'code': 123, 'state': state})
        if t.status_is(200, diag=True):
            t.json_is('code', 'OK')
            t.json_has('token', 'токен есть')
            t.json_has('device', 'device есть')
            t.json_has('store_id', 'store_id есть')

            user = await User.load(t.res['json']['token'], by='token')
            tap.ok(user, 'пользователь создался в БД')
            tap.eq(user.provider, 'yandex', 'провайдер')


@pytest.mark.skip(reason="no way of currently testing this")
async def test_yandex_team(tap, api):
    with tap.plan(13):
        t = await api()

        await t.post_ok('api_profile_auth_prepare',
                        json={'provider': 'yandex-team'})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('url', 'урл есть в ответе')

        url = yarl.URL(t.res['json']['url'])
        tap.eq(url.host, 'oauth.yandex-team.ru', 'тестовый хост')

        state = url.query.get('state')

        tap.diag(url)

        await t.post_ok('api_profile_auth_done',
                        json={'code': 5049515, 'state': state})
        if t.status_is(200, diag=True):
            t.json_is('code', 'OK')
            t.json_has('token', 'токен есть')
            t.json_has('device', 'device есть')
            t.json_has('store_id', 'store_id есть')

            user = await User.load(t.res['json']['token'], by='token')
            tap.ok(user, 'пользователь создался в БД')
            tap.eq(user.provider, 'yandex-team', 'провайдер')


@pytest.mark.parametrize('role', [None, 'store_admin'])
async def test_invite(tap, api, dataset, role):
    with tap.plan(27, 'Использование инвайта'):

        store = await dataset.store()
        admin = await dataset.user(store=store, role='admin')
        t = await api(user=admin)

        await t.post_ok('api_profile_make_invite',
                        json={
                            'email': 'mail@to.domain',
                            'role': role,
                        })
        t.status_is(200, 'инвайт сгенерирован', diag=True)
        t.json_has('invite')
        invite = t.res['json']['invite']

        t = await api()

        await t.post_ok('api_profile_auth_prepare',
                        json={'provider': 'test', 'invite': invite})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('url', 'урл есть в ответе')

        url = yarl.URL(t.res['json']['url'])
        state = url.query.get('state')
        state_unpack = token.unpack(cfg('web.auth.secret'), state)
        tap.isa_ok(state_unpack, dict, 'state распакован')
        tap.in_ok('invite', state_unpack, 'invite есть')
        invite = state_unpack['invite']
        tap.eq(invite['store_id'], admin.store_id, 'склад')
        tap.eq(invite['role'], role, 'роль')

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

        await t.post_ok('api_profile_auth_done',
                        json={'code': 123, 'state': state})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('token', 'токен есть')
        t.json_has('device', 'device есть')
        t.json_has('store_id', 'store_id есть')

        payload = token.unpack(cfg('web.auth.secret'), t.res['json']['token'])
        tap.isa_ok(payload, dict, 'распакован токен')

        user = await User.load(payload['user_id'])
        tap.isa_ok(user, User, 'пользователь в БД')

        tap.eq(user.role, role if role else 'authen_guest', 'роль')
        tap.eq(user.store_id, admin.store_id, 'Склад назначен')
        tap.eq(user.company_id, admin.company_id, 'Организация назначена')


@pytest.mark.parametrize('role', [None, 'store_admin'])
async def test_invite_wrong_email(tap, api, uuid, role):
    with tap.plan(19, 'Использование инвайта не тем email'):
        t = await api(role='admin')

        await t.post_ok('api_profile_make_invite',
                        json={
                            'email': f'{uuid()}@to.domain.ru',
                            'role': role,
                        })
        t.status_is(200, 'инвайт сгенерирован', diag=True)
        t.json_has('invite')
        invite = t.res['json']['invite']

        t = await api()

        await t.post_ok('api_profile_auth_prepare',
                        json={'provider': 'test', 'invite': invite})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('url', 'урл есть в ответе')

        url = yarl.URL(t.res['json']['url'])
        state = url.query.get('state')
        state_unpack = token.unpack(cfg('web.auth.secret'), state)
        tap.isa_ok(state_unpack, dict, 'state распакован')
        tap.in_ok('invite', state_unpack, 'invite есть')
        invite = state_unpack['invite']
        tap.ok(invite['store_id'], 'склад')
        tap.eq(invite['role'], role, 'роль')

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

        await t.post_ok('api_profile_auth_done',
                        json={'code': 123, 'state': state})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_INVITE_EMAIL')

@pytest.mark.parametrize('role', [None, 'store_admin'])
async def test_invite_without_store(tap, api, dataset, role):
    with tap.plan(27, 'Использование инвайта'):
        company = await dataset.company()
        admin = await dataset.user(
            company=company,
            role='admin'
        )
        t = await api(user=admin)

        await t.post_ok('api_profile_make_invite',
                        json={
                            'email': 'mail@to.domain',
                            'role': role,
                        })
        t.status_is(200, 'инвайт сгенерирован', diag=True)
        t.json_has('invite')
        invite = t.res['json']['invite']

        t = await api()

        await t.post_ok('api_profile_auth_prepare',
                        json={'provider': 'test', 'invite': invite})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('url', 'урл есть в ответе')

        url = yarl.URL(t.res['json']['url'])
        state = url.query.get('state')
        state_unpack = token.unpack(cfg('web.auth.secret'), state)
        tap.isa_ok(state_unpack, dict, 'state распакован')
        tap.in_ok('invite', state_unpack, 'invite есть')
        invite = state_unpack['invite']
        tap.eq(invite['store_id'], admin.store_id, 'склад')
        tap.eq(invite['role'], role, 'роль')

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

        await t.post_ok('api_profile_auth_done',
                        json={'code': 123, 'state': state})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('token', 'токен есть')
        t.json_has('device', 'device есть')
        t.json_has('store_id', 'store_id есть')

        payload = token.unpack(cfg('web.auth.secret'), t.res['json']['token'])
        tap.isa_ok(payload, dict, 'распакован токен')

        user = await User.load(payload['user_id'])
        tap.isa_ok(user, User, 'пользователь в БД')

        tap.eq(user.role, role if role else 'authen_guest', 'роль')
        tap.eq(user.store_id, admin.store_id, 'Склад назначен')
        tap.eq(user.company_id, admin.company_id, 'Организация назначена')


async def test_problem_invite(tap, api, dataset):
    with tap.plan(11, 'Проблемы при создании инвайта'):

        store = await dataset.store()
        admin = await dataset.user(store=store, role='admin')
        t = await api(user=admin)

        await t.post_ok('api_profile_make_invite',
                        json={
                            'email': 'mail@to.domain',
                            'role': None
                        })
        t.status_is(200, 'инвайт сгенерирован', diag=True)
        t.json_has('invite')
        invite = t.res['json']['invite']

        t = await api()

        await t.post_ok('api_profile_auth_prepare',
                        json={'provider': 'test_fake', 'invite': invite})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('url', 'урл есть в ответе')

        url = yarl.URL(t.res['json']['url'])
        state = url.query.get('state')

        await t.post_ok('api_profile_auth_done',
                        json={'code': 123, 'state': state})

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message',
                  'Данной компании нельзя так авторизироваться.')


async def test_re_invite(tap, api, dataset):
    with tap.plan(24, 'Использование re инвайта'):

        store = await dataset.store()
        company = await dataset.company(ownership='franchisee')
        admin = await dataset.user(
            store=store,
            role='admin',
            company_id=company.company_id)
        t = await api(user=admin)

        await t.post_ok('api_profile_make_invite',
                        json={
                            'email': 'mail@to.domain',
                            'role': None
                        })
        t.status_is(200, 'инвайт сгенерирован', diag=True)
        t.json_has('invite')
        invite = t.res['json']['invite']

        t = await api()

        await t.post_ok('api_profile_auth_prepare',
                        json={'provider': 'test_fake', 'invite': invite})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('url', 'урл есть в ответе')

        url = yarl.URL(t.res['json']['url'])
        state = url.query.get('state')

        await t.post_ok('api_profile_auth_done',
                        json={'code': 123, 'state': state})

        t.status_is(200, diag=True)

        admin = await dataset.user(store=store, role='admin')
        t = await api(user=admin)

        # re-invite
        await t.post_ok('api_profile_make_invite',
                        json={
                            'email': 'mail@to.domain',
                            'role': 'category_manager'
                        })

        t.status_is(200, 'инвайт сгенерирован', diag=True)
        t.json_has('invite')
        invite = t.res['json']['invite']

        t = await api()

        await t.post_ok('api_profile_auth_prepare',
                        json={'provider': 'test', 'invite': invite})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('url', 'урл есть в ответе')

        url = yarl.URL(t.res['json']['url'])
        state = url.query.get('state')

        await t.post_ok('api_profile_auth_done',
                        json={'code': 123, 'state': state})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('token', 'токен есть')

        payload = token.unpack(cfg('web.auth.secret'), t.res['json']['token'])
        tap.isa_ok(payload, dict, 'распакован токен')

        user = await User.load(payload['user_id'])
        tap.isa_ok(user, User, 'пользователь в БД')

        tap.eq(user.role, 'category_manager', 'роль')
        tap.eq(user.provider, 'test', 'Склад назначен')


async def test_yandex_assign_role(tap, api, dataset, monkeypatch, uuid):
    provider_user_id = uuid()

    # pylint: disable=unused-argument
    async def get_user_info_mock(provider, code):
        return {
            'euid': provider_user_id,
            'nick': 'vasyazadov',
            'fullname': 'Vasilii Zadov',
            'email': 'mail@to.domain',
        }

    monkeypatch.setattr('stall.api.profile.auth_done._get_user_info',
                        get_user_info_mock)

    with tap.plan(32):
        company = await dataset.company()
        store = await dataset.store(company_id=company.company_id)
        admin = await dataset.user(store=store, role='admin')
        t = await api(user=admin)

        await t.post_ok('api_profile_make_invite',
                        json={
                            'email': 'mail@to.domain',
                            'role': 'store_admin',
                        })
        t.status_is(200, 'инвайт сгенерирован', diag=True)
        t.json_has('invite')
        invite = t.res['json']['invite']

        t = await api()

        await t.post_ok('api_profile_auth_prepare',
                        json={'provider': 'yandex-team', 'invite': invite})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('url', 'урл есть в ответе')

        url = yarl.URL(t.res['json']['url'])
        state = url.query.get('state')

        await t.post_ok('api_profile_auth_done',
                        json={'code': 123, 'state': state})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('token', 'токен есть')

        payload = token.unpack(cfg('web.auth.secret'), t.res['json']['token'])

        user = await User.load(payload['user_id'])
        tap.isa_ok(user, User, 'пользователь в БД')

        tap.eq(user.role, 'authen_guest', 'роль не установлена')
        tap.eq(user.provider, 'yandex-team', 'Провайдер Yandex-Team')
        tap.eq(user.provider_user_id, provider_user_id, 'Верный UID')
        tap.eq(user.store_id, None, 'Склад не назначен')
        tap.eq(user.company_id, None, 'Организация не назначена')

        user.role = 'store_admin'
        user.company_id = company.company_id
        tap.ok(await user.save(), 'Роль и компания назначены через IDM')

        t = await api()

        await t.post_ok('api_profile_auth_prepare',
                        json={'provider': 'yandex-team', 'invite': invite})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('url', 'урл есть в ответе')

        url = yarl.URL(t.res['json']['url'])
        state = url.query.get('state')

        await t.post_ok('api_profile_auth_done',
                        json={'code': 123, 'state': state})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('token', 'токен есть')

        payload = token.unpack(cfg('web.auth.secret'), t.res['json']['token'])

        user = await User.load(payload['user_id'])
        tap.isa_ok(user, User, 'пользователь в БД')

        tap.eq(user.role, 'store_admin', 'роль установлена')
        tap.eq(user.provider, 'yandex-team', 'Провайдер Yandex-Team')
        tap.eq(user.provider_user_id, provider_user_id, 'Верный UID')
        tap.eq(user.store_id, store.store_id, 'Склад назначен')
        tap.eq(user.company_id, company.company_id, 'Организация назначена')


@pytest.mark.parametrize('provider', ['yandex-team', 'yandex'])
async def test_cannot_change_company(tap, api, dataset, monkeypatch,
                                     uuid, provider):
    provider_user_id = uuid()

    # pylint: disable=unused-argument
    async def get_user_info_mock(provider, code):
        return {
            'euid': provider_user_id,
            'nick': 'vasyazadov',
            'fullname': 'Vasilii Zadov',
            'email': 'mail@to.domain',
        }

    monkeypatch.setattr('stall.api.profile.auth_done._get_user_info',
                        get_user_info_mock)

    with tap.plan(18):
        user = await dataset.user(role='store_admin',
                                  provider=provider,
                                  provider_user_id=provider_user_id)
        tap.ok(user.store_id, 'Склад есть')
        tap.ok(user.company_id, 'Компания есть')

        company2 = await dataset.company(ownership='franchisee')
        store2 = await dataset.store(company_id=company2.company_id)
        admin = await dataset.user(store=store2, role='admin')
        t = await api(user=admin)

        await t.post_ok('api_profile_make_invite',
                        json={
                            'email': 'mail@to.domain',
                            'role': 'store_admin',
                        })
        t.status_is(200, 'инвайт сгенерирован', diag=True)
        t.json_has('invite')
        invite = t.res['json']['invite']

        t = await api()

        await t.post_ok('api_profile_auth_prepare',
                        json={'provider': provider, 'invite': invite})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('url', 'урл есть в ответе')

        url = yarl.URL(t.res['json']['url'])
        state = url.query.get('state')

        await t.post_ok('api_profile_auth_done',
                        json={'code': 123, 'state': state})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('token', 'токен есть')

        payload = token.unpack(cfg('web.auth.secret'), t.res['json']['token'])

        user_loaded = await User.load(payload['user_id'])
        tap.isa_ok(user_loaded, User, 'пользователь в БД')

        tap.eq(user_loaded.provider, provider, 'Верный провайдер')
        tap.eq(user_loaded.provider_user_id, provider_user_id, 'Верный UID')
        tap.eq(user_loaded.store_id, user.store_id, 'Склад не поменялся')
        tap.eq(user_loaded.company_id, user.company_id,
               'Организация не поменялась')
