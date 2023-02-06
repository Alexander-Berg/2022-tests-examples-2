from stall.model.courier_shift import (
    COURIER_SHIFT_EVENT_TYPES,
    CourierShiftEvent
)


async def test_load(tap, api, dataset):
    with tap.plan(4, 'Получение по идентификатору'):

        store           = await dataset.store()
        user            = await dataset.user(store=store)
        courier_shift   = await dataset.courier_shift(store=store)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_load',
            json={'courier_shift_id': courier_shift.courier_shift_id},
        )

        t.status_is(200, diag=True)

        t.json_is('code', 'OK', 'код')
        t.json_is(
            'courier_shift.courier_shift_id',
            courier_shift.courier_shift_id,
            'идентификатор'
        )


async def test_load_by_list(tap, api, dataset):
    with tap.plan(5, 'Получение по списку идентификаторов'):

        store           = await dataset.store()
        user            = await dataset.user(store=store)
        courier_shift1  = await dataset.courier_shift(store=store)
        courier_shift2  = await dataset.courier_shift(store=store)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_courier_shifts_load',
            json={
                'courier_shift_id': [
                    courier_shift1.courier_shift_id,
                    courier_shift2.courier_shift_id
                ],
            },
        )

        t.status_is(200, diag=True)

        t.json_is('code', 'OK', 'код')
        t.json_has('courier_shift.0', 'Получены смены')
        t.json_has('courier_shift.1', 'Получены смены')


async def test_load_events(tap, api, dataset, uuid, now):
    with tap.plan(4, 'Получение по идентификатору'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        prev_shift = await dataset.courier_shift(store=store)
        courier_shift = await dataset.courier_shift(
            store=store,
            status='request',
            shift_events=[
                # событие swap_started обязано иметь group_ids в detail,
                # событие служит для отката обмена сменами в случае падения.
                CourierShiftEvent({
                    'type': 'swap_started',
                    'courier_id': courier.courier_id,
                    'detail': {'group_ids': {uuid(): uuid()}},
                }),
                CourierShiftEvent({
                    'type': 'hold_absent',
                    'detail': {
                        'courier_shift_id': prev_shift.courier_shift_id,
                        'duration': 100500,
                        'ends_at': now().replace(microsecond=0),
                    },
                }),
                # other
                *[
                    CourierShiftEvent({'type': status})
                    for status in COURIER_SHIFT_EVENT_TYPES
                    if status not in ('swap_started', 'hold_absent')
                ],
            ],
        )

        t = await api(role='admin')
        await t.post_ok(
            'api_admin_courier_shifts_load',
            json={'courier_shift_id': courier_shift.courier_shift_id},
        )

        t.status_is(200, diag=True)

        t.json_is('code', 'OK', 'код')
        t.json_is(
            'courier_shift.courier_shift_id',
            courier_shift.courier_shift_id,
            'идентификатор'
        )


async def test_stores_allow_own(tap, api, dataset):
    with tap.plan(4, 'Получение только для своих лавок: своя лавка'):

        store           = await dataset.store()
        user            = await dataset.user(
            store=store,
            stores_allow=[store.store_id],
        )
        courier_shift   = await dataset.courier_shift(store=store)

        t = await api(user=user)

        with user.role as role:
            role.add_permit('out_of_store', True)

            await t.post_ok(
                'api_admin_courier_shifts_load',
                json={'courier_shift_id': courier_shift.courier_shift_id},
            )

            t.status_is(200, diag=True)

            t.json_is('code', 'OK', 'код')
            t.json_is(
                'courier_shift.courier_shift_id',
                courier_shift.courier_shift_id,
                'идентификатор'
            )


async def test_stores_allow_other(tap, api, dataset):
    with tap.plan(4, 'Получение только для своих лавок: разрешенная лавка'):

        store           = await dataset.store()
        store2          = await dataset.store()
        user            = await dataset.user(
            store=store,
            stores_allow=[store2.store_id],
        )
        courier_shift   = await dataset.courier_shift(store=store2)

        t = await api(user=user)

        with user.role as role:
            role.add_permit('out_of_store', True)

            await t.post_ok(
                'api_admin_courier_shifts_load',
                json={'courier_shift_id': courier_shift.courier_shift_id},
            )

            t.status_is(200, diag=True)

            t.json_is('code', 'OK', 'код')
            t.json_is(
                'courier_shift.courier_shift_id',
                courier_shift.courier_shift_id,
                'идентификатор'
            )


async def test_stores_allow_fail(tap, api, dataset):
    with tap.plan(2, 'Получение только для своих лавок: не разрешена'):

        store           = await dataset.store()
        store2          = await dataset.store()
        user            = await dataset.user(
            store=store,
            stores_allow=[store.store_id],
        )
        courier_shift   = await dataset.courier_shift(store=store2)

        t = await api(user=user)
        with user.role as role:
            role.add_permit('out_of_store', True)

            await t.post_ok(
                'api_admin_courier_shifts_load',
                json={'courier_shift_id': courier_shift.courier_shift_id},
            )

            t.status_is(403, diag=True)
