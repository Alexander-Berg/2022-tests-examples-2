import pytest


async def test_load_nf(tap, api, uuid):
    with tap.plan(4, 'Неизвестный идентификатор'):
        t = await api(role='admin')

        await t.post_ok('api_admin_courier_shift_tags_load_title',
                        json={'title': uuid()})

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'нет доступа')
        t.json_is('message', 'Access denied', 'текст')


async def test_load(tap, api, dataset):
    with tap.plan(6, 'Успешная загрузка'):

        courier_shift_tag = await dataset.courier_shift_tag()

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_courier_shift_tags_load_title',
            json={
                'title': courier_shift_tag.title,
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'получен')

        t.json_is('courier_shift_tag.title',
                  courier_shift_tag.title)
        t.json_is('courier_shift_tag.title', courier_shift_tag.title)
        t.json_is('courier_shift_tag.description',
                  courier_shift_tag.description)


async def test_load_fail_cluster(tap, api, dataset):
    with tap.plan(7, 'Запрещаем доступ к тегам не своего кластера'):
        cluster1 = await dataset.cluster()
        cluster2 = await dataset.cluster()
        tag = await dataset.courier_shift_tag(cluster=cluster1)

        store = await dataset.store(cluster=cluster2)
        user = await dataset.user(store=store)

        # С пермитом есть доступ ко всем
        with user.role as role:
            role.add_permit('out_of_store', True)

            t = await api(user=user)

            await t.post_ok(
                'api_admin_courier_shift_tags_load_title',
                json={
                    'title': tag.title,
                },
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_is('courier_shift_tag.title', tag.title)

        # Без пермита есть доступ только к своим
        with user.role as role:
            role.remove_permit('out_of_store')

            t = await api(user=user)

            await t.post_ok(
                'api_admin_courier_shift_tags_load_title',
                json={
                    'title': tag.title,
                },
            )

            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')


@pytest.mark.parametrize('role', ['admin'])
async def test_load_multiple(tap, api, dataset, role):
    with tap.plan(5, 'Успешная загрузка списка'):
        t = await api(role=role)
        courier_shift_tag1 = await dataset.courier_shift_tag()
        courier_shift_tag2 = await dataset.courier_shift_tag()
        await t.post_ok(
            'api_admin_courier_shift_tags_load_title',
            json={
                'title': [
                    courier_shift_tag1.title,
                    courier_shift_tag2.title,
                ]
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код успеха')
        t.json_has('courier_shift_tag', 'есть в выдаче')
        res = t.res['json']['courier_shift_tag']
        tap.eq_ok(
            sorted([res[0]['title'],
                    res[1]['title']]),
            sorted([courier_shift_tag1.title,
                    courier_shift_tag2.title]),
            'Пришли правильные объекты'
        )


@pytest.mark.parametrize('role', ['admin'])
async def test_load_multiple_fail(tap, api, dataset, uuid, role):
    with tap.plan(2, 'Неизвестные идентификаторы в списке'):
        t = await api(role=role)
        courier_shift_tag1 = await dataset.courier_shift_tag()
        await t.post_ok(
            'api_admin_courier_shift_tags_load_title',
            json={
                'title': [
                    courier_shift_tag1.title,
                    uuid()
                ],
            }
        )
        t.status_is(403, diag=True)
