# pylint: disable=unused-variable

from datetime import timedelta

import pytest

from stall.model.courier_shift import (
    COURIER_SHIFT_STATUSES,
    COURIER_SHIFT_ACTUAL_STATUSES,
)


@pytest.mark.parametrize('status', COURIER_SHIFT_ACTUAL_STATUSES)
async def test_list_actual(tap, dataset, now, status):
    with tap.plan(2, 'Получение рабочих смен'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        started_at = now().replace(hour=12, microsecond=0)
        closes_at  = now().replace(hour=13, microsecond=0)

        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status=status,
            started_at=started_at,
            closes_at=closes_at
        )

        shifts = await dataset.CourierShift.list_actual(
            courier_id=courier.courier_id,
            date_from=started_at.replace(
                hour=0, minute=0, second=0, microsecond=0),
            date_to=started_at.replace(
                hour=23, minute=59, second=59, microsecond=0),
        )
        tap.eq(len(shifts), 1, 'Смены получены')
        tap.eq(
            shifts[0].courier_shift_id,
            shift.courier_shift_id,
            'нужная смена'
        )


@pytest.mark.parametrize('status', [
    x for x in COURIER_SHIFT_STATUSES if x not in COURIER_SHIFT_ACTUAL_STATUSES
])
async def test_list_not_actual(tap, dataset, now, status):
    with tap.plan(1, 'Проверка не рабочих статусов'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        started_at = now().replace(hour=12, microsecond=0)
        closes_at  = now().replace(hour=13, microsecond=0)

        await dataset.courier_shift(
            store=store,
            courier=courier,
            status=status,
            started_at=started_at,
            closes_at=closes_at
        )

        shifts = await dataset.CourierShift.list_actual(
            courier_id=courier.courier_id,
            date_from=started_at.replace(
                hour=0, minute=0, second=0, microsecond=0),
            date_to=started_at.replace(
                hour=23, minute=59, second=59, microsecond=0),
        )
        tap.eq(len(shifts), 0, 'Смены не получены')


async def test_courier(tap, dataset, now):
    with tap.plan(2, 'Только для заданного курьера'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier1 = await dataset.courier(cluster=cluster)
        courier2 = await dataset.courier(cluster=cluster)

        started_at = now().replace(hour=12, microsecond=0)
        closes_at  = now().replace(hour=13, microsecond=0)

        shift1 = await dataset.courier_shift(
            store=store,
            courier=courier1,
            status='processing',
            started_at=started_at,
            closes_at=closes_at
        )
        shift2 = await dataset.courier_shift(
            store=store,
            courier=courier2,
            status='processing',
            started_at=started_at,
            closes_at=closes_at
        )

        shifts = await dataset.CourierShift.list_actual(
            courier_id=courier1.courier_id,
            date_from=started_at.replace(
                hour=0, minute=0, second=0, microsecond=0),
            date_to=started_at.replace(
                hour=23, minute=59, second=59, microsecond=0),
        )
        tap.eq(len(shifts), 1, 'Смены получены')
        tap.eq(
            shifts[0].courier_shift_id,
            shift1.courier_shift_id,
            'нужная смена'
        )


async def test_date(tap, dataset, now):
    with tap.plan(2, 'Только в заданный диапазон времени'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        started_at = now().replace(hour=12, microsecond=0)
        closes_at  = now().replace(hour=13, microsecond=0)

        shift1 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            started_at=started_at,
            closes_at=closes_at
        )
        shift2 = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            started_at=started_at + timedelta(days=2),
            closes_at=closes_at + timedelta(days=2),
        )

        shifts = await dataset.CourierShift.list_actual(
            courier_id=courier.courier_id,
            date_from=started_at.replace(
                hour=0, minute=0, second=0, microsecond=0),
            date_to=started_at.replace(
                hour=23, minute=59, second=59, microsecond=0),
        )
        tap.eq(len(shifts), 1, 'Смены получены')
        tap.eq(
            shifts[0].courier_shift_id,
            shift1.courier_shift_id,
            'нужная смена'
        )
