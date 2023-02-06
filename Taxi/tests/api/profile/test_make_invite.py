from libstall.util import token
from stall import cfg


async def test_make_invite_sub_error(tap, api, uuid):
    with tap.plan(3, 'Нет права создать кого-то не в sub'):
        t = await api(role='admin')

        await t.post_ok(
            'api_profile_make_invite',
            json={
                'email': f'{uuid()}@yandex.ru',
                'role': 'guest',
            }
        )
        t.status_is(403, 'нет права создать инвайт для гостя')
        t.json_is('code', 'ER_WRONG_INVITE_ROLE')


async def test_make_invite_sub(tap, api, dataset, now, uuid):
    with tap.plan(14, 'Успешное создание инвайта'):
        user = await dataset.user(role='admin')
        tap.ok(user.store_id, 'Пользователь создан')
        tap.eq(user.role, 'admin', 'роль')
        t = await api(user=user)

        await t.post_ok(
            'api_profile_make_invite',
            json={
                'email': f'{uuid()}@yandex.ru',
                'role': 'executer',
            }
        )
        t.status_is(200, 'Инвайт сгенерирован')
        t.json_is('code', 'OK')
        t.json_has('invite')

        invite = token.unpack(cfg('web.auth.secret'), t.res['json']['invite'])
        tap.isa_ok(invite, dict, 'распакован')
        tap.in_ok('created', invite, 'created')
        tap.eq(invite['role'], 'executer', 'роль')
        tap.eq(invite['ttl'], 24, 'ttl')
        tap.eq(invite['store_id'], user.store_id, 'склад')
        tap.eq(invite['company_id'], user.company_id, 'компания')
        tap.eq(invite['provider_id'], None, 'поставщика нет')
        tap.ok(invite['created'] <= now().timestamp(), 'время создания')


async def test_make_invite_provider_error(tap, api, uuid, dataset):
    with tap.plan(3, 'Нельзя обычным пользователям без прикрепления'):

        user = await dataset.user(role='admin', provider_id=None)
        t = await api(user=user)

        await t.post_ok(
            'api_profile_make_invite',
            json={
                'email': f'{uuid()}@yandex.ru',
                'role': 'provider',
            }
        )
        t.status_is(403, 'нет права создать инвайт без привязки')
        t.json_is('code', 'ER_WRONG_INVITE_SOURCE')


async def test_make_invite_provider(tap, api, dataset, now, uuid):
    with tap.plan(14, 'Успешное создание инвайта'):
        provider = await dataset.provider()
        user = await dataset.user(role='admin', provider=provider)
        tap.ok(user.provider_id, 'Пользователь создан')
        tap.eq(user.role, 'admin', 'роль')
        t = await api(user=user)

        await t.post_ok(
            'api_profile_make_invite',
            json={
                'email': f'{uuid()}@yandex.ru',
                'role': 'provider',
            }
        )
        t.status_is(200, 'Инвайт сгенерирован')
        t.json_is('code', 'OK')
        t.json_has('invite')

        invite = token.unpack(cfg('web.auth.secret'), t.res['json']['invite'])

        tap.isa_ok(invite, dict, 'распакован')
        tap.in_ok('created', invite, 'created')
        tap.eq(invite['role'], 'provider', 'роль')
        tap.eq(invite['ttl'], 24, 'ttl')
        tap.eq(invite['provider_id'], provider.provider_id, 'поставщик есть')
        tap.eq(invite['store_id'], None, 'склада нет')
        tap.eq(invite['company_id'], user.company_id, 'компания')
        tap.ok(invite['created'] <= now().timestamp(), 'время создания')
