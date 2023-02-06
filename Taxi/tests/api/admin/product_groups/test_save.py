import pytest

from stall.model.product_group import ProductGroup
from stall.model.role import PERMITS

ROLES_WITHOUT_ADMIN = [
    role for role in PERMITS['roles']
    if role != 'admin' and not PERMITS['roles'][role].get('virtual', False)
]


async def test_save_create(tap, api, dataset, uuid):
    with tap.plan(16):
        user = await dataset.user(role='admin')
        t = await api(user=user)

        # ok case

        parent_external_id = uuid()

        await t.post_ok(
            'api_admin_product_groups_save',
            json={
                'external_id': parent_external_id,
                'name': 'parent',
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'parent product group created')

        t.json_has('product_group.group_id', 'group_id')
        t.json_has('product_group.created', 'created')
        t.json_has('product_group.updated', 'updated')
        t.json_is(
            'product_group.external_id',
            parent_external_id,
            'external_id',
        )
        t.json_is('product_group.name', 'parent', 'name')

        # ok case: with parent_group_id

        parent_group = await ProductGroup.load(
            parent_external_id,
            by='external',
        )

        tap.ok(parent_group, 'parent group loaded from db')

        child_external_id = uuid()

        await t.post_ok(
            'api_admin_product_groups_save',
            json={
                'external_id': child_external_id,
                'parent_group_id': parent_group.group_id,
                'name': 'child',
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'child product group created')

        t.json_is(
            'product_group.external_id',
            child_external_id,
            'external_id',
        )
        t.json_is(
            'product_group.parent_group_id',
            parent_group.group_id,
            'parent_group_id',
        )
        t.json_is('product_group.name', 'child', 'name')
        t.json_is('product_group.user_id', user.user_id)


async def test_save_update(tap, api, dataset, uuid):
    with tap.plan(13):
        group = await dataset.product_group(name='spam')

        tap.ok(group, 'product group created')

        t = await api(role='admin')

        # ok case

        await t.post_ok(
            'api_admin_product_groups_save',
            json={
                'group_id': group.group_id,
                'name': 'eggs',
                'user_id': 'hello',
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'product group loaded')

        t.json_is('product_group.group_id', group.group_id, 'group id')
        t.json_is('product_group.name', 'eggs', 'name')
        t.json_isnt('product_group.user_id', 'hello')

        # err case: self ref

        await t.post_ok(
            'api_admin_product_groups_save',
            json={
                'group_id': group.group_id,
                'parent_group_id': group.group_id,
            },
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST', 'self ref')

        # err case: parent group not found

        await t.post_ok(
            'api_admin_product_groups_save',
            json={
                'group_id': group.group_id,
                'parent_group_id': uuid(),
            },
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST', 'parent group not found')


async def test_save_bad_data(tap, api):
    with tap.plan(3):

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_product_groups_save',
            json={'name': 'spam'},
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST', 'create rejected')


async def test_save_bad_parent_group_id(tap, api, dataset, uuid):
    with tap.plan(7):
        group = await dataset.product_group(name='spam')

        tap.ok(group, 'product group created')

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_product_groups_save',
            json={
                'group_id': group.group_id,
                'parent_group_id': group.group_id,
            },
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST', 'self ref')

        await t.post_ok(
            'api_admin_product_groups_save',
            json={
                'group_id': group.group_id,
                'parent_group_id': uuid(),
            },
        )

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST', 'parent group not found')


async def test_timetable(tap, api, uuid):
    with tap.plan(10, 'расписание для группы продуктов'):
        t = await api(role='admin')

        await t.post_ok(
            'api_admin_product_groups_save',
            json={
                'external_id': uuid(),
                'name': 'нет расписания',
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('product_group.timetable', [])

        ext_id = uuid()
        timetable = [
            {
                'type': 'everyday',
                'begin': '19:00:00',
                'end': '23:59:59',
            },
        ]

        await t.post_ok(
            'api_admin_product_groups_save',
            json={
                'external_id': ext_id,
                'name': 'алко по вечерам',
                'timetable': timetable,
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        for i, tt_item in enumerate(timetable):
            for k, v in tt_item.items():
                t.json_is(f'product_group.timetable.{i}.{k}', v)


@pytest.mark.parametrize('lang', ('ru_RU', 'en_US'))
async def test_locales(tap, api, dataset, lang):
    with tap.plan(9):
        user = await dataset.user(role='admin', lang=lang)

        groups = [
            await dataset.product_group(
                name='нет перевода',
            ),
            await dataset.product_group(
                name='есть перевод',
                vars={
                    'locales': {
                        'name': {lang: f'есть перевод {lang}'},
                    }
                },
            ),
        ]

        tap.ok(groups, 'создали группы')

        t = await api(user=user)

        await t.post_ok(
            'api_admin_product_groups_save',
            json={
                'group_id': groups[0].group_id,
                'name': 'в ответ получем дефолт',
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('product_group.name', 'в ответ получем дефолт')

        await t.post_ok(
            'api_admin_product_groups_save',
            json={
                'group_id': groups[1].group_id,
                'name': 'в ответ получем перевод',
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('product_group.name', f'есть перевод {lang}')


@pytest.mark.parametrize('role', ROLES_WITHOUT_ADMIN)
async def test_permits(tap, api, dataset, role):
    with tap.plan(7, f'пермиты для product_group, role={role}'):
        product_group = await dataset.product_group()
        name_old = product_group.name
        timetable = [
            {
                'type': 'everyday',
                'begin': '19:00:00',
                'end': '23:59:59',
            },
        ]

        user = await dataset.user(role=role)
        t = await api(user=user)
        await t.post_ok(
            'api_admin_product_groups_save',
            json={
                'group_id': product_group.group_id,
                'timetable': timetable,
                'name': 'Не изменюсь'
            },
        )

        if role in {'company_admin', 'chief_manager',
                    'content_manager', 'support_it'}:
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            for i, tt_item in enumerate(timetable):
                for k, v in tt_item.items():
                    t.json_is(f'product_group.timetable.{i}.{k}', v)
            t.json_is('product_group.name', name_old)
        else:
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')
            t.json_is('code', 'ER_ACCESS')
            t.json_is('code', 'ER_ACCESS')
            t.json_is('code', 'ER_ACCESS')
            t.json_has('message')
