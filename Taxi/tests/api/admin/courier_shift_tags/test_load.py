import pytest


async def test_load_nf(tap, api, uuid):
    with tap.plan(4, 'Неизвестный идентификатор'):
        t = await api(role='admin')

        await t.post_ok('api_admin_courier_shift_tags_load',
                        json={'courier_shift_tag_id': uuid()})

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'нет доступа')
        t.json_is('message', 'Access denied', 'текст')


async def test_load(tap, api, dataset):
    with tap.plan(6, 'Успешная загрузка'):

        courier_shift_tag = await dataset.courier_shift_tag()

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_courier_shift_tags_load',
            json={
                'courier_shift_tag_id': courier_shift_tag.courier_shift_tag_id,
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'получен')

        t.json_is('courier_shift_tag.courier_shift_tag_id',
                  courier_shift_tag.courier_shift_tag_id)
        t.json_is('courier_shift_tag.title', courier_shift_tag.title)
        t.json_is('courier_shift_tag.description',
                  courier_shift_tag.description)


@pytest.mark.parametrize('role', ['admin'])
async def test_load_multiple(tap, api, dataset, role):
    with tap.plan(5, 'Успешная загрузка списка'):
        t = await api(role=role)
        courier_shift_tag1 = await dataset.courier_shift_tag()
        courier_shift_tag2 = await dataset.courier_shift_tag()
        await t.post_ok(
            'api_admin_courier_shift_tags_load',
            json={
                'courier_shift_tag_id': [
                    courier_shift_tag1.courier_shift_tag_id,
                    courier_shift_tag2.courier_shift_tag_id,
                ]
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код успеха')
        t.json_has('courier_shift_tag', 'есть в выдаче')
        res = t.res['json']['courier_shift_tag']
        tap.eq_ok(
            sorted([res[0]['courier_shift_tag_id'],
                    res[1]['courier_shift_tag_id']]),
            sorted([courier_shift_tag1.courier_shift_tag_id,
                    courier_shift_tag2.courier_shift_tag_id]),
            'Пришли правильные объекты'
        )


@pytest.mark.parametrize('role', ['admin'])
async def test_load_multiple_fail(tap, api, dataset, uuid, role):
    with tap.plan(2, 'Неизвестные идентификаторы в списке'):
        t = await api(role=role)
        courier_shift_tag1 = await dataset.courier_shift_tag()
        await t.post_ok(
            'api_admin_courier_shift_tags_load',
            json={
                'courier_shift_tag_id': [
                    courier_shift_tag1.courier_shift_tag_id,
                    uuid()
                ],
            }
        )
        t.status_is(403, diag=True)
