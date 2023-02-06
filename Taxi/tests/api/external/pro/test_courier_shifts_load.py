from datetime import timedelta

import pytest

from stall.model.courier_shift import ZONE_DELIVERY_TYPES


@pytest.mark.parametrize('delivery_type', ZONE_DELIVERY_TYPES)
async def test_load(tap, api, dataset, now, delivery_type):
    with tap.plan(6, 'Загрузка смены'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'started_after_time': 10 * 60,  # 10 мин
            },
        )
        store = await dataset.store(
            cluster=cluster,
            currency='RUB',
        )
        courier = await dataset.courier(
            cluster=cluster,
            vars={
                'external_ids': {
                    'eats': 12345,
                },
            },
        )

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=(now() - timedelta(minutes=15)),
            delivery_type=delivery_type,
        )

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_load',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            }
        )
        t.status_is(200, diag=True)
        t.json_has('data')
        t.json_is('data.id', shift.courier_shift_id)
        t.json_is('data.attributes.status', 'Planned')
        t.json_is('data.attributes.courierId', courier.courier_id)


async def test_not_found(tap, api, dataset, uuid):
    with tap.plan(3, 'Смена не найдена'):
        courier = await dataset.courier()

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_load',
            params_path={
                'courier_shift_id': uuid(),
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            }
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.change_request.validator.shift_does_not_exist'
        )


async def test_alien(tap, api, dataset):
    with tap.plan(3, 'Смена не принадлежит курьеру'):
        courier = await dataset.courier()
        shift = await dataset.courier_shift()

        t = await api(role='token:web.external.tokens.0')
        await t.get_ok(
            'api_external_pro_courier_shifts_load',
            params_path={
                'courier_shift_id': shift.courier_shift_id,
            },
            headers={
                'X-YaTaxi-Park-Id': courier.park_id,
                'X-YaTaxi-Driver-Profile-Id': courier.profile_id,
            }
        )
        t.status_is(400, diag=True)
        t.json_is(
            'errors.0.attributes.code',
            'core.courier_shift.change_request.validator.shift_does_not_exist'
        )
