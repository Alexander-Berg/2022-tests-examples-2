from urllib.parse import quote

from stall.config import cfg
from stall.model.user import User


async def test_bad_requests(tap, api, dataset):
    with tap.plan(32):
        company = await dataset.company(ownership='yandex')
        t = await api(role='token:web.idm.tokens.0')

        await t.post_ok('/api/idm/add-role/', form={})
        t.status_is(200, diag=True)
        t.json_is('code', 400)
        t.json_is('error', 'login is not specified')

        await t.post_ok('/api/idm/add-role/', form={
            'login': 'login1',
        })
        t.status_is(200, diag=True)
        t.json_is('code', 400)
        t.json_is('error', 'uid is not specified')

        await t.post_ok('/api/idm/add-role/', form={
            'login': 'login1',
            'uid': '534535345342',
        })
        t.status_is(200, diag=True)
        t.json_is('code', 400)
        t.json_is('error', 'role is not specified')

        await t.post_ok('/api/idm/add-role/', form={
            'login': 'login1',
            'uid': '534535345342',
            'role': '{"role": "store_admin"}',
        })
        t.status_is(200, diag=True)
        t.json_is('code', 400)
        t.json_is('error', 'path is not specified')

        await t.post_ok('/api/idm/add-role/', form={
            'login': 'login1',
            'uid': '534535345342',
            'role': '{"role": "store_admin"}',
            'path': quote('/hello/world/', safe=''),
        })
        t.status_is(200, diag=True)
        t.json_is('code', 400)
        t.json_is('error', 'fields is not specified')

        await t.post_ok('/api/idm/add-role/', form={
            'login': 'login1',
            'uid': '534535345342',
            'role': 'abrakadbra',
            'path': quote('/role/abrakadabra/', safe=''),
            'fields': quote(f'{{"company": "{company.company_id}"}}', safe=''),
        })
        t.status_is(200, diag=True)
        t.json_is('code', 400)
        t.json_is('error', 'Bad role')

        await t.post_ok('/api/idm/add-role/', form={
            'login': 'login1',
            'uid': '534535345342',
            'role': '{"hello": "world"}',
            'path': quote('/hello/world/', safe=''),
            'fields': quote(f'{{"company": "{company.company_id}"}}', safe=''),
        })
        t.status_is(200, diag=True)
        t.json_is('code', 400)
        t.json_is('error', 'Bad role')

        await t.post_ok('/api/idm/add-role/', form={
            'login': 'login1',
            'uid': '534535345342',
            'role': '{"role": "emperor_of_the_universe"}',
            'path': quote('/role/emperor_of_the_universe/', safe=''),
            'fields': quote(f'{{"company": "{company.company_id}"}}', safe=''),
        })
        t.status_is(200, diag=True)
        t.json_is('code', 400)
        t.json_is('error', 'Bad role')


async def test_bad_company(tap, api, dataset, uuid):
    with tap.plan(10):
        t = await api(role='token:web.idm.tokens.0')

        company = await dataset.company(ownership='franchisee')
        user = await dataset.user(role='authen_guest',
                                  provider='yandex-team',
                                  provider_user_id=uuid(),
                                  company_id=company.company_id)

        await t.post_ok('/api/idm/add-role/', form={
            'login': 'login1',
            'uid': user.provider_user_id,
            'role': '{"role": "store_admin"}',
            'path': quote('/role/store_admin/', safe=''),
            'fields': quote(f'{{"company": "{uuid()}"}}', safe=''),
        })
        t.status_is(200, diag=True)
        t.json_is('code', 404)
        t.json_is('error', 'Company not found')

        await user.reload()
        tap.eq(user.role.name, 'authen_guest', 'Роль не поменялась')

        await t.post_ok('/api/idm/add-role/', form={
            'login': 'login1',
            'uid': user.provider_user_id,
            'role': '{"role": "store_admin"}',
            'path': quote('/role/store_admin/', safe=''),
            'fields': quote(f'{{"company": "{company.company_id}"}}', safe=''),
        })
        t.status_is(200, diag=True)
        t.json_is('code', 403)
        t.json_is('error', 'Assigning this role for this '
                           'company via IDM is prohibited')

        await user.reload()
        tap.eq(user.role.name, 'authen_guest', 'Роль не поменялась')


async def test_add_role(tap, api, dataset):
    with tap.plan(26):
        t = await api(role='token:web.idm.tokens.0')

        company = await dataset.company(ownership='yandex')
        user = await dataset.user(role='authen_guest',
                                  provider='yandex-team',
                                  company_id=None)

        await t.post_ok('/api/idm/add-role/', form={
            'login': 'login1',
            'uid': user.provider_user_id,
            'role': '{"role": "store_admin"}',
            'path': quote('/role/store_admin/', safe=''),
            'fields': quote(f'{{"company": "{company.company_id}"}}', safe=''),
        })
        t.status_is(200, diag=True)
        t.json_is('code', 0)
        t.json_is('data.company', company.company_id)

        await user.reload()
        tap.eq(user.role.name, 'store_admin', 'Роль поменялась')
        tap.eq(user.company_id, company.company_id, 'Назначена компания')
        tap.eq(user.nick, 'login1', 'nick')

        await t.post_ok('/api/idm/add-role/', form={
            'login': 'login1',
            'uid': user.provider_user_id,
            'role': '{"role": "vice_store_admin"}',
            'path': quote('/role/vice_store_admin/', safe=''),
            'fields': quote(f'{{"company": "{company.company_id}"}}', safe=''),
        })
        t.status_is(200, diag=True)
        t.json_is('code', 409)
        t.json_is(
            'error',
            'У пользователя уже есть роль. Чтобы выдать новую, перейдите по '
            'ссылке https://idm.yandex-team.ru/system/lavka_wms_tst/roles'
            '#f-status=active,f-role=lavka_wms_tst,sort-by=-updated,'
            'f-is-expanded=true,f-user=user:login1 и отзовите старую роль'
        )

        await user.reload()
        tap.eq(user.role.name, 'store_admin', 'Роль не поменялась')
        tap.eq(user.company_id, company.company_id, 'Компания не поменялась')

        await t.post_ok('/api/idm/remove-role/', form={
            'login': 'login1',
            'uid': user.provider_user_id,
            'role': '{"role": "store_admin"}',
            'path': quote('/role/store_admin/', safe=''),
        })
        t.status_is(200, diag=True)
        t.json_is('code', 0)

        await user.reload()

        tap.eq(user.role.name, 'authen_guest', 'Роль отозвана')
        tap.eq(user.company_id, None, 'Нет компании')
        tap.eq(user.store_id, None, 'Нет склада')

        await t.post_ok('/api/idm/add-role/', form={
            'login': 'login1',
            'uid': user.provider_user_id,
            'role': '{"role": "vice_store_admin"}',
            'path': quote('/role/vice_store_admin/', safe=''),
            'fields': quote(f'{{"company": "{company.company_id}"}}', safe=''),
        })
        t.status_is(200, diag=True)
        t.json_is('code', 0)
        t.json_is('data.company', company.company_id)

        await user.reload()
        tap.eq(user.role.name, 'vice_store_admin', 'Новая роль назначена')
        tap.eq(user.company_id, company.company_id, 'Компания назначена')
        tap.eq(user.store_id, None, 'Склад не назначен')


async def test_new_user(tap, api, uuid, dataset):
    with tap.plan(8):
        t = await api(role='token:web.idm.tokens.0')

        company = await dataset.company(ownership='yandex')
        provider_user_id = uuid()

        await t.post_ok('/api/idm/add-role/', form={
            'login': 'login1',
            'uid': provider_user_id,
            'role': '{"role": "store_admin"}',
            'path': quote('/role/store_admin/', safe=''),
            'fields': quote(f'{{"company": "{company.company_id}"}}', safe=''),
        })
        t.status_is(200, diag=True)
        t.json_is('code', 0)
        t.json_is('data.company', company.company_id)

        user = await User.load(['yandex-team', provider_user_id],
                               by='provider')
        tap.ok(user, 'User created')
        tap.eq(user.company_id, company.company_id, 'Company assigned')
        tap.ok(not user.store_id, 'Store was not assigned')
        tap.eq(user.nick, 'login1', 'nick')


async def test_admin(tap, api, dataset):
    with tap.plan(6):
        t = await api(role='token:web.idm.tokens.0')

        user = await dataset.user(role='authen_guest',
                                  provider='yandex-team',
                                  company_id=None)

        await t.post_ok('/api/idm/add-role/', form={
            'login': 'login1',
            'uid': user.provider_user_id,
            'role': '{"role": "admin"}',
            'path': quote('/role/admin/', safe=''),
        })
        t.status_is(200, diag=True)
        t.json_is('code', 0)
        t.json_hasnt('data.company')

        await user.reload()
        tap.eq(user.role.name, 'admin', 'Роль поменялась')
        tap.eq(user.company_id, cfg(f'idm.default_company.{cfg("mode")}'),
               'Назначена компания по-умолчанию')
