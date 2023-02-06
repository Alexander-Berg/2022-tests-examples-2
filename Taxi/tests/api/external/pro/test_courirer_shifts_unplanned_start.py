from stall.model.cluster import Cluster
from stall.model.courier import Courier
from stall.model.courier_shift import CourierShift
from stall.model.store import Store


async def test_start(tap, api, dataset, uuid):
    with tap.plan(12, 'начало свободного слота прогоняет все статусы'):
        cluster: Cluster = await dataset.cluster()
        store: Store = await dataset.store(cluster=cluster)
        await dataset.zone(store=store)

        courier: Courier = await dataset.courier(
            cluster=cluster,
            extra_vars={'can_take_unplanned_shift': True},
        )

        event_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_unplanned_start',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': event_id,
                'location': {
                    'latitude': 55.70,
                    'longitude': 37.50,
                },
            }
        )
        t.status_is(204, diag=True)

        current_shift = await CourierShift.get_current(courier.courier_id)
        tap.ok(current_shift, 'courier has current shift')
        tap.eq(current_shift.external_id, event_id, 'shift created by api')
        tap.eq(current_shift.placement, 'unplanned', 'shift created unplanned')
        tap.eq(len(current_shift.shift_events), 3, 'shift has 3 events')

        with current_shift.shift_events[0] as event:
            tap.eq(event.type, 'waiting', 'shift assigned')
            tap.eq(event.courier_id, courier.courier_id, 'assigned by courier')

        with current_shift.shift_events[1] as event:
            tap.eq(event.type, 'started', 'shift started')
            tap.eq(event.courier_id, courier.courier_id, 'started by courier')

        with current_shift.shift_events[2] as event:
            tap.eq(event.type, 'processing', 'shift processing')
            tap.eq(event.courier_id, courier.courier_id, 'process by courier')


async def test_existing(tap, api, dataset, uuid):
    with tap.plan(4, 'идемпотентность создания'):
        cluster: Cluster = await dataset.cluster()
        store: Store = await dataset.store(cluster=cluster)
        await dataset.zone(store=store)

        courier: Courier = await dataset.courier(
            cluster=cluster,
            extra_vars={'can_take_unplanned_shift': True},
        )

        event_id = uuid()

        shift = await dataset.courier_shift(
            cluster=cluster, courier=courier,
            external_id=event_id,
            status='processing',
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_unplanned_start',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': event_id,
                'location': {
                    'latitude': 55.70,
                    'longitude': 37.50,
                },
            }
        )
        t.status_is(204, diag=True)

        current_shift = await CourierShift.get_current(courier.courier_id)
        tap.ok(current_shift, 'courier has current shift')
        tap.ok(current_shift.courier_shift_id, shift.courier_shift_id,
               'shift was not duplicated')


async def test_cannot_take_unplanned(tap, api, dataset, uuid):
    with tap.plan(3, 'нет оснований разрешать свободные слоты'):
        cluster: Cluster = await dataset.cluster()
        store: Store = await dataset.store(cluster=cluster)
        await dataset.zone(store=store)

        courier: Courier = await dataset.courier(cluster=cluster)

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_unplanned_start',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.70,
                    'longitude': 37.50,
                },
            }
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.validator.'
            'common.courier_not_found'
        )


async def test_rover(tap, api, dataset, uuid):
    with tap.plan(2, 'свободные слоты роверам'):
        cluster: Cluster = await dataset.cluster()
        store: Store = await dataset.store(cluster=cluster)
        await dataset.zone(store=store, delivery_type='rover')

        courier: Courier = await dataset.courier(
            cluster=cluster, delivery_type='rover',
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_unplanned_start',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.70,
                    'longitude': 37.50,
                },
            }
        )
        t.status_is(204, diag=True)


async def test_storekeeper(tap, api, dataset, uuid):
    with tap.plan(2, 'свободные слоты кладовщикам'):
        cluster: Cluster = await dataset.cluster()
        store: Store = await dataset.store(cluster=cluster)
        await dataset.zone(store=store)

        courier: Courier = await dataset.courier(
            cluster=cluster, extra_vars={'is_storekeeper': True},
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_unplanned_start',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.70,
                    'longitude': 37.50,
                },
            }
        )
        t.status_is(204, diag=True)


async def test_no_zone(tap, api, dataset, uuid):
    with tap.plan(4, 'начало слота вне зоны'):
        cluster: Cluster = await dataset.cluster()
        # store: Store = await dataset.store(cluster=cluster)
        # await dataset.zone(store=store)

        courier: Courier = await dataset.courier(
            cluster=cluster,
            extra_vars={'can_take_unplanned_shift': True},
        )

        event_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_unplanned_start',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': event_id,
                'location': {
                    'latitude': 1000.70,
                    'longitude': 1000.50,
                },
            }
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.opened_shift.save.error.unavailable_zone'
        )

        tap.ok(not await CourierShift.get_current(courier.courier_id),
               'no shifts created')


async def test_foreign_zone(tap, api, dataset, uuid):
    with tap.plan(4, 'начало слота в зоне чужого склада'):
        cluster: Cluster = await dataset.cluster()
        store: Store = await dataset.store(cluster=cluster)
        await dataset.zone(store=store)

        courier: Courier = await dataset.courier(
            cluster=cluster,
            extra_vars={'can_take_unplanned_shift': True},
            tags_store=[uuid()],
        )

        event_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_unplanned_start',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': event_id,
                'location': {
                    'latitude': 55.70,
                    'longitude': 37.50,
                },
            }
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.opened_shift.save.error.unavailable_zone'
        )

        tap.ok(not await CourierShift.get_current(courier.courier_id),
               'no shifts created')


async def test_correct_store(tap, api, dataset, uuid):
    with tap.plan(4, 'начало слота в своём складу'):
        cluster: Cluster = await dataset.cluster(
            courier_shift_setup={
                'slot_start_range': 1,
            }
        )
        store: Store = await dataset.store(
            cluster=cluster, location=(55.70, 37.50),
        )
        await dataset.zone(store=store)

        courier: Courier = await dataset.courier(
            cluster=cluster,
            extra_vars={'can_take_unplanned_shift': True},
            tags_store=[store.store_id],
        )

        event_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_unplanned_start',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': event_id,
                'location': {
                    'latitude': 55.70,
                    'longitude': 37.50,
                },
            }
        )
        t.status_is(204, diag=True)

        current_shift = await CourierShift.get_current(courier.courier_id)
        tap.ok(current_shift, 'courier has current shift')
        tap.ok(current_shift.external_id, event_id, 'shift created')


async def test_far_from_store(tap, api, dataset, uuid):
    with tap.plan(4, 'начало слота вне зоны'):
        cluster: Cluster = await dataset.cluster(
            courier_shift_setup={
                'slot_start_range': 1,
            }
        )
        store: Store = await dataset.store(
            cluster=cluster, location=(90, 180),
        )
        await dataset.zone(store=store)

        courier: Courier = await dataset.courier(
            cluster=cluster,
            extra_vars={'can_take_unplanned_shift': True},
            tags_store=[store.store_id],
        )

        event_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_unplanned_start',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': event_id,
                'location': {
                    'latitude': 55.70,
                    'longitude': 37.50,
                },
            }
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.opened_shift.save.error.unavailable_zone'
        )

        tap.ok(not await CourierShift.get_current(courier.courier_id),
               'no shifts created')


async def test_courier_has_shift(tap, api, dataset, uuid):
    with tap.plan(3, 'не начинаем слот если уже есть активный'):
        cluster: Cluster = await dataset.cluster()
        store: Store = await dataset.store(cluster=cluster)
        await dataset.zone(store=store)

        courier: Courier = await dataset.courier(
            cluster=cluster,
            extra_vars={'can_take_unplanned_shift': True},
        )

        await dataset.courier_shift(
            cluster=cluster, courier=courier,
            status='processing',
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_unplanned_start',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.70,
                    'longitude': 37.50,
                },
            }
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.validator.'
            'start.has_active_shift'
        )


async def test_courier_has_block(tap, api, dataset, uuid):
    with tap.plan(3, 'у курьера есть блокировка'):
        cluster: Cluster = await dataset.cluster()
        store: Store = await dataset.store(cluster=cluster)
        await dataset.zone(store=store)

        courier: Courier = await dataset.courier(
            cluster=cluster,
            extra_vars={'can_take_unplanned_shift': True},
            blocks=[{'source': 'wms', 'reason': uuid()}],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_unplanned_start',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.70,
                    'longitude': 37.50,
                },
            }
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.shift_flow_manager.remote_services.'
            'invalid_work_status'
        )


async def test_courier_inactive(tap, api, dataset, uuid):
    with tap.plan(3, 'неактивный курьер'):
        cluster: Cluster = await dataset.cluster()
        store: Store = await dataset.store(cluster=cluster)
        await dataset.zone(store=store)

        courier: Courier = await dataset.courier(
            cluster=cluster,
            extra_vars={'can_take_unplanned_shift': True},
            status='disabled',
        )

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_unplanned_start',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': uuid(),
                'location': {
                    'latitude': 55.70,
                    'longitude': 37.50,
                },
            }
        )
        t.status_is(401, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'unauthorized'
        )


async def test_multiple_stores(tap, api, dataset, uuid):
    with tap.plan(4, 'из нескольких складов выбираем ближайший'):
        cluster: Cluster = await dataset.cluster()
        store: Store = await dataset.store(cluster=cluster)
        far_store: Store = await dataset.store(
            cluster=cluster, location=(90, 180)
        )
        await dataset.zone(store=store)
        await dataset.zone(store=far_store)

        courier: Courier = await dataset.courier(
            cluster=cluster,
            extra_vars={'can_take_unplanned_shift': True},
            tags_store=[store.store_id, far_store.store_id],
        )

        event_id = uuid()

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_pro_courier_shifts_unplanned_start',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
                'X-App-Version': '1.2.3',
            },
            json={
                'id': event_id,
                'location': {
                    'latitude': 55.70,
                    'longitude': 37.50,
                },
            }
        )
        t.status_is(204, diag=True)

        current_shift = await CourierShift.get_current(courier.courier_id)
        tap.ok(current_shift, 'courier has current shift')
        tap.ok(current_shift.store_id, store.store_id,
               'shift created for closest store')
