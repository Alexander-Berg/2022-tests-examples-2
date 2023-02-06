import pytest


@pytest.mark.parametrize('role', ['admin', 'store_admin', 'expansioner',
                                  'category_manager'])
async def test_load(tap, api, dataset, role):
    with tap.plan(7):
        group = await dataset.product_group(name='spam')

        tap.ok(group, 'group created')

        t = await api(role=role)

        await t.post_ok(
            'api_admin_product_groups_load',
            json={'group_id': group.group_id},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'group loaded')

        t.json_is('product_group.group_id', group.group_id, 'group_id')
        t.json_is(
            'product_group.external_id',
            group.external_id,
            'external_id',
        )
        t.json_is('product_group.name', group.name, 'name')


@pytest.mark.parametrize('role', ['executer', 'barcode_executer'])
async def test_load_not_found(tap, api, uuid, role):
    with tap.plan(3):
        t = await api(role=role)

        await t.post_ok(
            'api_admin_product_groups_load',
            json={'group_id': uuid()},
        )

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'group not found')


@pytest.mark.parametrize('role', ['admin', 'store_admin', 'expansioner',
                                  'category_manager'])
async def test_load_multiple(tap, api, dataset, role):
    with tap.plan(5):
        t = await api(role=role)
        product_group1 = await dataset.product_group()
        product_group2 = await dataset.product_group()
        await t.post_ok(
            'api_admin_product_groups_load',
            json={'group_id': [product_group1.group_id,
                               product_group2.group_id]})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код успеха')
        t.json_has('product_group', 'есть в выдаче')
        res = t.res['json']['product_group']
        tap.eq_ok(
            sorted([res[0]['group_id'], res[1]['group_id']]),
            sorted([product_group1.group_id,
                    product_group2.group_id]),
            'Пришли правильные объекты'
        )


@pytest.mark.parametrize('role', ['executer', 'barcode_executer'])
async def test_load_multiple_fail(tap, api, dataset, role):
    with tap.plan(2):
        t = await api(role=role)
        product_group1 = await dataset.product_group()
        await t.post_ok(
            'api_admin_product_groups_load',
            json={'group_id': [product_group1.group_id]})
        t.status_is(403, diag=True)


async def test_list_by_ids(tap, api, dataset):
    with tap.plan(16):
        t = await api(role='admin')
        group1 = await dataset.product_group(name='group1', order=1)
        group11 = await dataset.product_group(
            name='group11', parent_group_id=group1.group_id, order=2)
        group12 = await dataset.product_group(
            name='group12', parent_group_id=group1.group_id, order=3)
        group111 = await dataset.product_group(
            name='group111', parent_group_id=group11.group_id, order=4)
        group121 = await dataset.product_group(
            name='group121', parent_group_id=group12.group_id, order=5)
        group1111 = await dataset.product_group(
            name='group1111', parent_group_id=group111.group_id, order=6)
        group1211 = await dataset.product_group(
            name='group1211', parent_group_id=group121.group_id, order=7)
        await dataset.product_group(
            name='other1', parent_group_id=group12.group_id, order=8)
        await dataset.product_group(
            name='other2', parent_group_id=group111.group_id, order=9)

        await t.post_ok('api_admin_product_groups_load', json={
            'hierarchy': False,
            'group_id': [group1111.group_id, group1211.group_id]
        })

        t.status_is(200, diag=True)
        t.json_has('product_group', 'product_groups in response')
        received = t.res['json']['product_group']

        tap.eq_ok(
            sorted(g['name'] for g in received),
            sorted([group1111.name, group1211.name]),
            'Правильные названия групп'
        )

        await t.post_ok('api_admin_product_groups_load', json={
            'hierarchy': True,
            'group_id': [group1111.group_id, group1211.group_id]
        })
        t.status_is(200, diag=True)
        t.json_has('product_group', 'product_groups in response')
        received = t.res['json']['product_group']

        tap.eq_ok(
            sorted(g['name'] for g in received),
            sorted(['group1', 'group11', 'group12', 'group111',
                    'group121', 'group1111', 'group1211']),
            'Правильные названия групп'
        )

        await t.post_ok('api_admin_product_groups_load', json={
            'hierarchy': True,
            'group_id': [group111.group_id, group1211.group_id]
        })
        t.status_is(200, diag=True)
        t.json_has('product_group', 'product_groups in response')
        received = t.res['json']['product_group']

        tap.eq_ok(
            sorted(g['name'] for g in received),
            sorted(['group1', 'group11', 'group12',
                    'group111', 'group121', 'group1211']),
            'Правильные названия групп'
        )

        await t.post_ok('api_admin_product_groups_load', json={
            'hierarchy': True,
            'group_id': [group111.group_id, group1111.group_id]
        })
        t.status_is(200, diag=True)
        t.json_has('product_group', 'product_groups in response')
        received = t.res['json']['product_group']

        tap.eq_ok(
            sorted(g['name'] for g in received),
            sorted(['group1', 'group11', 'group111', 'group1111']),
            'Правильные названия групп (одна группа в родстве с другой)'
        )


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
            'api_admin_product_groups_load',
            json={'group_id': groups[0].group_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('product_group.name', 'нет перевода')

        await t.post_ok(
            'api_admin_product_groups_load',
            json={'group_id': [groups[1].group_id]},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('product_group.0.name', f'есть перевод {lang}')
