import pytest
from libstall.util import time2time

from stall.model.courier_block import CourierBlock


async def test_load(tap, api, dataset, uuid):
    with tap.plan(18, 'Получение по идентификатору'):
        cluster = await dataset.cluster()
        user = await dataset.user(role='admin')
        courier = await dataset.courier(
            external_id=uuid(),
            first_name=uuid(),
            middle_name=uuid(),
            last_name=uuid(),
            status='disabled',
            blocks=[
                CourierBlock({'source': 'eda', 'reason': uuid()}),
                CourierBlock({'source': 'wms', 'reason': uuid()}),
            ],
            cluster_id=cluster.cluster_id,
            delivery_type='rover',
            tags=['auto', 'velo'],
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_couriers_load',
            json={'courier_id': courier.courier_id},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')
        t.json_is('courier.courier_id', courier.courier_id, 'идентификатор')
        t.json_is('courier.external_id', courier.external_id, 'external_id')
        t.json_is('courier.first_name', courier.first_name, 'имя')
        t.json_is('courier.middle_name', courier.middle_name, 'отчество')
        t.json_is('courier.last_name', courier.last_name, 'фамилия')
        t.json_is('courier.status', courier.status, 'статус')

        # блокировки
        t.json_is('courier.blocks', courier.blocks, 'блокировки курьера')
        blocks = sorted(t.res['json']['courier']['blocks'],
                        key=lambda x: x['source'])
        tap.eq_ok(len(blocks), 2, '2 блокировки')
        tap.eq_ok(blocks[0]['source'], 'eda', 'блокировка еды')
        tap.eq_ok(blocks[0]['reason'], courier.blocks[0].reason, 'причина')
        tap.eq_ok(blocks[1]['source'], 'wms', 'блокировка еды')
        tap.eq_ok(blocks[1]['reason'], courier.blocks[1].reason, 'причина')

        t.json_is('courier.cluster_id', cluster.cluster_id, 'cluster_id')
        t.json_is('courier.delivery_type', courier.delivery_type, 'доставка')
        t.json_is('courier.tags', ['auto', 'velo'], 'теги')


async def test_load_by_list(tap, api, dataset):
    with tap.plan(5, 'Получение по списку идентификаторов'):
        user = await dataset.user(role='admin')
        courier1 = await dataset.courier()
        courier2 = await dataset.courier()

        t = await api(user=user)
        await t.post_ok(
            'api_admin_couriers_load',
            json={'courier_id': [courier1.courier_id, courier2.courier_id]},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')
        t.json_has('courier.0', 'Получен курьер 1')
        t.json_has('courier.1', 'Получен курьер 2')


async def test_access(tap, api, dataset):
    with tap.plan(3, 'Нет доступа'):
        user = await dataset.user(role='admin')
        courier = await dataset.courier()

        with user.role as role:
            role.remove_permit('couriers_load')

            t = await api(user=user)
            await t.post_ok(
                'api_admin_couriers_load',
                json={'courier_id': courier.courier_id},
            )

            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')


@pytest.mark.skip(reason="not now")
async def test_tags_store(tap, api, dataset):
    with tap.plan(4, 'Курьер привязан к лавке'):
        cluster = await dataset.cluster()
        store1 = await dataset.store(cluster=cluster)
        user = await dataset.user(role='admin', store=store1)
        courier = await dataset.courier(
            cluster=cluster,
            tags_store=[store1.store_id],
        )

        with user.role as role:
            role.remove_permit('out_of_store')

            t = await api(user=user)
            await t.post_ok(
                'api_admin_couriers_load',
                json={'courier_id': courier.courier_id},
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK', 'код')
            t.json_is('courier.courier_id', courier.courier_id)


@pytest.mark.skip(reason="not now")
async def test_tags_store_over(tap, api, dataset):
    with tap.plan(2, 'Курьер привязан к другой лавке'):
        cluster = await dataset.cluster()
        store1 = await dataset.store(cluster=cluster)
        store2 = await dataset.store(cluster=cluster)
        user = await dataset.user(role='admin', store=store1)
        courier = await dataset.courier(
            cluster=cluster,
            tags_store=[store2.store_id],
        )

        with user.role as role:
            role.remove_permit('out_of_store')

            t = await api(user=user)
            await t.post_ok(
                'api_admin_couriers_load',
                json={'courier_id': courier.courier_id},
            )
            t.status_is(403, diag=True)


@pytest.mark.skip(reason="not now")
async def test_tags_store_empty(tap, api, dataset):
    with tap.plan(2, 'Курьер не привязан к лавке'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(role='admin', store=store)
        courier = await dataset.courier(cluster=cluster)

        with user.role as role:
            role.remove_permit('out_of_store')

            t = await api(user=user)
            await t.post_ok(
                'api_admin_couriers_load',
                json={'courier_id': courier.courier_id},
            )
            t.status_is(403, diag=True)


async def test_load_state(tap, api, dataset, uuid, now):
    with tap.plan(6, 'Получение по идентификатору'):
        shift_id = uuid()
        grocery_shift_status_time = time2time(now())
        user = await dataset.user(role='admin')
        courier = await dataset.courier(
            state ={
                'grocery_shift_status': 'open',
                'grocery_shift_status_time': grocery_shift_status_time,
                'open_shifts': {
                    shift_id: {
                        'grocery_shift_id': shift_id,
                        'grocery_shift_status': 'open',
                        'grocery_shift_time': grocery_shift_status_time,
                    }
                },
            }
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_couriers_load',
            json={'courier_id': courier.courier_id},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')
        t.json_is(
            'courier.state.grocery_shift_status',
            'open',
            'grocery_shift_status'
        )
        t.json_is(
            'courier.state.grocery_shift_status_time',
            grocery_shift_status_time.isoformat(),
            'grocery_shift_status_time'
        )
        t.json_is(
            f'courier.state.open_shifts.{shift_id}.grocery_shift_id',
            shift_id,
            'идентификатор'
        )
