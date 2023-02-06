import yarl

import pytest

from stall import cfg
from libstall.util import token

@pytest.mark.parametrize('provider', ['yandex', 'yandex-team', 'test'])
async def test_prepare(tap, api, provider):
    with tap.plan(9):
        t = await api()

        await t.post_ok('api_profile_auth_prepare',
                        json={'provider': provider})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('url', 'урл есть в ответе')

        url = yarl.URL(t.res['json']['url'])

        state = url.query.get('state')
        tap.ok(state, 'стейт есть в урле')

        payload = token.unpack(cfg('web.auth.secret'), state)

        tap.isa_ok(payload, dict, 'распакован')

        tap.isa_ok(payload['now'], (float, int), 'значение now')
        tap.eq(payload['provider'], provider, 'значение provider')
        tap.like(payload['device'], r'^[a-f0-9A-F]{32}$', 'значение device')


@pytest.mark.parametrize('provider', ['yandex', 'yandex-team', 'test'])
async def test_invite(tap, api, provider, uuid):
    with tap.plan(11, 'Инвайт'):
        t = await api(role='admin')
        await t.post_ok('api_profile_make_invite',
                        json={'role': 'executer', 'email': f'{uuid()}@ya.ru'})
        t.status_is(200, diag=True, desc='Инвайт сгенерирован')
        t.json_has('invite')
        invite = t.res['json']['invite']


        t = await api()
        await t.post_ok('api_profile_auth_prepare',
                        json={'provider': provider, 'invite': invite})
        t.status_is(200, diag=True, desc='state подготовлен')
        t.json_has('url')

        url = yarl.URL(t.res['json']['url'])
        state = url.query.get('state')
        tap.ok(state, 'стейт есть в урле')

        payload = token.unpack(cfg('web.auth.secret'), state)
        tap.isa_ok(payload, dict, 'распакован state')
        tap.in_ok('invite', payload, 'invite в нём есть')
        tap.ok(payload['invite'], 'инвайт есть в state')
        tap.ok(payload['invite']['role'], 'executer', 'роль в инвайте')


async def test_invite_ttl(tap, api, uuid):
    with tap.plan(6, 'Инвайт устарел'):
        t = await api(role='admin')
        await t.post_ok('api_profile_make_invite',
                        json={'role': 'executer', 'email': f'{uuid()}@ya.ru'})
        t.status_is(200, diag=True, desc='Инвайт сгенерирован')
        t.json_has('invite')
        invite = token.unpack(cfg('web.auth.secret'), t.res['json']['invite'])
        invite['created'] = 0
        invite = token.pack(cfg('web.auth.secret'), **invite)

        t = await api()
        await t.post_ok('api_profile_auth_prepare',
                        json={'provider': 'yandex', 'invite': invite})
        t.status_is(410, diag=True, desc='state подготовлен')
        t.json_is('code', 'ER_INVATE_EXPIRED')
