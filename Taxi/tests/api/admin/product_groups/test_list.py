import pytest

from stall.model.product_group import ProductGroup


@pytest.mark.parametrize('data', [{}, {'ids': []}, {'full': False}])
async def test_list(tap, api, dataset, data):
    with tap.plan(6):

        t = await api(role='admin')

        for i in range(123):
            await dataset.product_group(name=f'group-{i}', order=i)

        group_ids_from_db = {
            i.group_id for i in await ProductGroup.list(by='full')
        }

        await t.post_ok('api_admin_product_groups_list', json=data)

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'code')
        t.json_has('product_groups', 'product_groups')

        cursor_str = t.res['json']['cursor']
        groups = t.res['json']['product_groups']
        with tap.subtest(None, 'Дочитываем до конца') as taps:
            t.tap = taps
            while cursor_str:
                await t.post_ok('api_admin_product_groups_list',
                                json={'cursor': cursor_str})
                t.status_is(200, diag=True)
                t.json_is('code', 'OK', 'ответ получен')
                groups.extend(t.res['json']['product_groups'])
                cursor_str = t.res['json']['cursor']
        t.tap = tap

        group_ids_from_api = {
            i['group_id'] for i in groups
        }

        tap.ok(
            not {
                g for g in group_ids_from_db if g not in group_ids_from_api
            },
            'Неизвестных id не появилось'
        )


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

        await t.post_ok('api_admin_product_groups_list', json={
            'hierarchy': False,
            'ids': [group1111.group_id, group1211.group_id]
        })

        t.status_is(200, diag=True)
        t.json_has('product_groups', 'product_groups in response')
        received = t.res['json']['product_groups']

        tap.eq_ok(
            [g['name'] for g in received],
            [group1111.name, group1211.name],
            'Правильные названия групп'
        )

        await t.post_ok('api_admin_product_groups_list', json={
            'hierarchy': True,
            'ids': [group1111.group_id, group1211.group_id]
        })
        t.status_is(200, diag=True)
        t.json_has('product_groups', 'product_groups in response')
        received = t.res['json']['product_groups']

        tap.eq_ok(
            [g['name'] for g in received],
            ['group1', 'group11', 'group12', 'group111',
             'group121', 'group1111', 'group1211'],
            'Правильные названия групп'
        )

        await t.post_ok('api_admin_product_groups_list', json={
            'hierarchy': True,
            'ids': [group111.group_id, group1211.group_id]
        })
        t.status_is(200, diag=True)
        t.json_has('product_groups', 'product_groups in response')
        received = t.res['json']['product_groups']

        tap.eq_ok(
            [g['name'] for g in received],
            ['group1', 'group11', 'group12',
             'group111', 'group121', 'group1211'],
            'Правильные названия групп'
        )

        await t.post_ok('api_admin_product_groups_list', json={
            'hierarchy': True,
            'ids': [group111.group_id, group1111.group_id]
        })
        t.status_is(200, diag=True)
        t.json_has('product_groups', 'product_groups in response')
        received = t.res['json']['product_groups']

        tap.eq_ok(
            [g['name'] for g in received],
            ['group1', 'group11', 'group111', 'group1111'],
            'Правильные названия групп (одна группа в родстве с другой)'
        )


async def test_empty_ids(tap, api):
    t = await api(role='admin')
    with tap.plan(8):
        await t.post_ok('api_admin_product_groups_list',
                        json={'hierarchy': True, 'ids': []})
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('details',
                  {'message': 'If hierarchy is True, ids MUST NOT be empty'})

        await t.post_ok('api_admin_product_groups_list',
                        json={'hierarchy': True})
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('details',
                  {'message': 'If hierarchy is True, ids MUST NOT be empty'})


@pytest.mark.parametrize('lang', ('ru_RU', 'en_US'))
async def test_locales(tap, api, dataset, lang):
    with tap.plan(9):
        user = await dataset.user(lang=lang)

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
            'api_admin_product_groups_list',
            json={'ids': [groups[0].group_id]},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('product_groups.0.name', 'нет перевода')

        await t.post_ok(
            'api_admin_product_groups_list',
            json={'ids': [groups[1].group_id]},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('product_groups.0.name', f'есть перевод {lang}')
