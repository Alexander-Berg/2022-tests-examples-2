
import datetime


async def test_checkin_self_store(tap, api, dataset, now):
    tap.plan(6, 'Список курьеров с чекином в своей лавке')
    store = await dataset.store()
    courier1 = await dataset.courier(
        state={
            'checkin_store_id': store.store_id,
            'checkin_time': now() + datetime.timedelta(hours=2),
            'grocery_shift_status': None,
        }

    )
    courier2 = await dataset.courier(
        state={
            'checkin_store_id': store.store_id,
            'checkin_time': now() + datetime.timedelta(hours=1),
            'grocery_shift_status': 'open',
        }
    )
    courier3 = await dataset.courier(
        state={
            'checkin_store_id': None,
            'checkin_time': now() + datetime.timedelta(hours=1),
            'grocery_shift_status': 'close',
        }
    )

    user = await dataset.user(store=store, role='admin')
    with user.role as role:
        role.remove_permit('out_of_store')
        role.remove_permit('out_of_company')
        t = await api(user=user)

        await t.post_ok(
            'api_admin_couriers_checkins',
            json={'store_id': store.store_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        couriers_ids = set(courier['courier_id']
                           for courier in t.res['json']['couriers'])
        tap.ok(
            courier2.courier_id in couriers_ids,
            'Курьер с открытой сменой'
        )
        tap.ok(
            courier1.courier_id in couriers_ids,
            'Курьер без статуса смены'
        )
        tap.ok(
            courier3.courier_id not in couriers_ids,
            'Курьер с закрытой сменой не найден'
        )


async def test_checkin_foreing_store(tap, api, dataset):
    tap.plan(4, 'Список курьеров с чекином в чужой лавке')
    store = await dataset.store()
    foreign_store = await dataset.store()
    user = await dataset.user(store=store, role='admin')

    with user.role as role:
        role.remove_permit('out_of_store')
        role.remove_permit('out_of_company')

        foreign_courier = await dataset.courier(
            checkin_store_id=foreign_store.store_id
        )
        tap.ok(foreign_courier, 'Курьер зачекинился в чужом складе')

        t = await api(user=user)

        await t.post_ok(
            'api_admin_couriers_checkins',
            json={'store_id': foreign_store.store_id},
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
