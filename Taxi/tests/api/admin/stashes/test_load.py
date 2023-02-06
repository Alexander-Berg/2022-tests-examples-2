import pytest


async def test_load_nf(tap, api, uuid):
    with tap.plan(4, 'Неизвестный идентификатор'):
        t = await api(role='admin')

        await t.post_ok('api_admin_stashes_load',
                        json={'stash_id': uuid()})

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'нет доступа')
        t.json_is('message', 'Access denied', 'текст')


async def test_load(tap, api, dataset):
    with tap.plan(5, 'Успешная загрузка'):

        stash = await dataset.stash()

        t = await api(role='admin')

        await t.post_ok('api_admin_stashes_load',
                        json={'stash_id': stash.stash_id})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'получен')

        t.json_is('stash.stash_id', stash.stash_id)
        t.json_is('stash.name', stash.name)


@pytest.mark.parametrize('role', ['admin'])
async def test_load_multiple(tap, api, dataset, role):
    with tap.plan(5, 'Успешная загрузка списка'):
        t = await api(role=role)
        stash1 = await dataset.stash()
        stash2 = await dataset.stash()
        await t.post_ok(
            'api_admin_stashes_load',
            json={'stash_id': [stash1.stash_id,
                               stash2.stash_id]})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код успеха')
        t.json_has('stash', 'есть в выдаче')
        res = t.res['json']['stash']
        tap.eq_ok(
            sorted([res[0]['stash_id'], res[1]['stash_id']]),
            sorted([stash1.stash_id,
                    stash2.stash_id]),
            'Пришли правильные объекты'
        )


@pytest.mark.parametrize('role', ['admin'])
async def test_load_multiple_fail(tap, api, dataset, uuid, role):
    with tap.plan(2, 'Неизвестные идентификаторы в списке'):
        t = await api(role=role)
        stash1 = await dataset.stash()
        await t.post_ok(
            'api_admin_stashes_load',
            json={'stash_id': [stash1.stash_id,
                               uuid()]})
        t.status_is(403, diag=True)
