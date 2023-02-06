# pylint: disable=too-many-locals
from datetime import timedelta


async def test_changes(tap, api, dataset, now, time2iso_utc):
    with tap.plan(18, 'Получение изменившихся смен'):
        cluster = await dataset.cluster()
        courier = await dataset.courier(
            cluster=cluster,
            status='active',
            vars={
                'external_ids': {
                    'eats': 12345,
                },
            },
        )

        base_time = now()
        old_started_at = base_time + timedelta(hours=1)
        new_started_at = base_time + timedelta(hours=2)
        old_closes_at = old_started_at + timedelta(hours=4)
        new_closes_at = new_started_at + timedelta(hours=4)
        old_store = await dataset.store(cluster=cluster, title='old_store')
        new_store = await dataset.store(cluster=cluster, title='new_store')

        shift = await dataset.courier_shift(
            store=old_store,
            courier=courier,
            status='waiting',
            started_at=new_started_at,
            closes_at=(base_time + timedelta(hours=2)),
            shift_events=[
                {
                    'type': 'change',
                    'detail': {
                        'old': {
                            'started_at': old_started_at,
                            'closes_at': old_closes_at,
                            'guarantee': None,
                            'store_id': old_store.store_id,
                        },
                        'new': {
                            'started_at': new_started_at,
                            'closes_at': new_closes_at,
                            'guarantee': 100.6,
                            'store_id': new_store.store_id,
                        },
                    },
                },
            ]
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_changes',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_is('data.0.id', shift.courier_shift_id)
        t.json_is('data.0.attributes.oldStartsAt', time2iso_utc(old_started_at))
        t.json_is('data.0.attributes.newStartsAt', time2iso_utc(new_started_at))
        t.json_is('data.0.attributes.oldEndsAt', time2iso_utc(old_closes_at))
        t.json_is('data.0.attributes.newEndsAt', time2iso_utc(new_closes_at))
        t.json_is('data.0.attributes.oldGuarantee', None)
        t.json_is('data.0.attributes.newGuarantee.value', '100.6')

        t.json_is('data.0.attributes.oldStartPoint.id', old_store.store_id)
        t.json_is('data.0.attributes.oldStartPoint.type', 'startPoint')
        t.json_is('data.0.attributes.oldStartPoint.attributes.name',
                  old_store.title)
        t.json_is('data.0.attributes.newStartPoint.id', new_store.store_id)
        t.json_is('data.0.attributes.newStartPoint.type', 'startPoint')
        t.json_is('data.0.attributes.newStartPoint.attributes.name',
                  new_store.title)

        t.json_hasnt('data.1')
        t.json_is('meta.count', 1)


async def test_empty(tap, api, dataset, now):
    with tap.plan(5, 'Нет изменившихся смен'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(
            cluster=cluster,
            status='active',
            vars={
                'external_ids': {
                    'eats': 12345,
                },
            },
        )

        await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=now() + timedelta(hours=1),
            closes_at=now() + timedelta(hours=2),
            shift_events=[],
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_changes',
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_hasnt('data.0')
        t.json_is('meta.count', 0)


async def test_flip_courier(tap, api, dataset):
    with tap.plan(4, 'Изменения предложенные курьеру_1 внутри смены '
                     'принадлежащей курьеру_2'):
        cluster = await dataset.cluster()
        courier_2 = await dataset.courier(
            cluster=cluster,
            status='active',
            vars={
                'external_ids': {
                    'eats': 12345,
                },
            },
        )

        old_store = await dataset.store(cluster=cluster, title='old_store')
        new_store = await dataset.store(cluster=cluster, title='new_store')

        # Была смена у курьера №1. Ему предложили изменения. Он промолчал.
        # Курьера сняли, а смена стала request. Админ ее поменял в обход change,
        # и назначил курьеру №2.
        await dataset.courier_shift(
            store=new_store,
            courier=courier_2,
            status='waiting',
            shift_events=[
                {
                    'type': 'change',
                    'detail': {
                        'old': {
                            'guarantee': None,
                            'store_id': old_store.store_id,
                        },
                        'new': {
                            'guarantee': 100.6,
                            'store_id': new_store.store_id,
                        },
                    },
                },
                # админ назначил нового курьера на освобожденную смену
                {
                    'type': 'rejected',
                }
            ]
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_changes',
            headers={
                'X-YaTaxi-Park-Id': courier_2.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier_2.profile_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_hasnt('data.0', 'предложенных изменений нет')
