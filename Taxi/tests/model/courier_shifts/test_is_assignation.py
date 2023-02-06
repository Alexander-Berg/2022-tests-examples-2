# pylint: disable=too-many-locals

from datetime import timedelta, time
import pytest
import pytz


@pytest.mark.parametrize(
    'start,close',
    [
        [11, 15],       # пересечение на 1 час слева
        [11, 19],       # охватывает целиком
        [15, 17],       # лежит внутри
        [17, 20],       # пересечение на 2 часа справа
    ]
)
async def test_intersection(tap, dataset, start, close, now, tzone):
    with tap.plan(1, 'Проверка пересечения смен'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now(tz=tzone(cluster.tz)) + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0,
        )
        await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=day.replace(hour=14),
            closes_at=day.replace(hour=18),
        )

        shift2 = await dataset.courier_shift(
            status='request',
            store=store,
            started_at=day.replace(hour=start),
            closes_at=day.replace(hour=close),
        )
        shift2.rehashed('started_at', True)

        try:
            await shift2.is_assignation(
                courier=courier,
                cluster=cluster,
                exclude=[shift2],
            )
        except dataset.CourierShift.ErIntersection:
            tap.passed('Пересекаются')
        else:
            tap.failed('Пересекаются')


@pytest.mark.parametrize(
    'start,close',
    [
        [11, 14],   # в стык слева
        [18, 20],   # в стык справа
    ]
)
async def test_not_intersection(tap, dataset, start, close, now, tzone):
    with tap.plan(1, 'Проверка не пересечения смен'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now(tz=tzone(cluster.tz)) + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0,
        )
        await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=day.replace(hour=14),
            closes_at=day.replace(hour=18),
        )

        shift2 = await dataset.courier_shift(
            status='request',
            store=store,
            started_at=day.replace(hour=start),
            closes_at=day.replace(hour=close),
        )
        shift2.rehashed('started_at', True)

        try:
            await shift2.is_assignation(
                courier=courier,
                cluster=cluster,
                exclude=[shift2],
            )
        except dataset.CourierShift.ErIntersection:
            tap.failed('Не пересекаются')
        else:
            tap.passed('Не пересекаются')


async def test_not_intersection_real(tap, dataset, now, tzone):
    with tap.plan(
            1,
            'Фактическое может пересекаться с плановым, но не фактическим. '
            'Из-за задержки курьер закрыл смену в плановом времени следующей.'
    ):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now(tz=tzone(cluster.tz)) + timedelta(days=2)).replace(
            hour=0, minute=0, second=0, microsecond=0,
        )
        await dataset.courier_shift(
            status='complete',
            store=store,
            courier=courier,
            started_at=day.replace(hour=14),
            closes_at=day.replace(hour=18),
            shift_events=[
                {'type': 'started', 'created': day.replace(hour=14)},
                {'type': 'stopped', 'created': day.replace(hour=18, minute=15)},
            ],
        )

        shift2 = await dataset.courier_shift(
            status='processing',
            store=store,
            courier=courier,
            started_at=day.replace(hour=18),
            closes_at=day.replace(hour=22),
            shift_events=[
                {'type': 'started', 'created': day.replace(hour=18, minute=15)},
            ],
        )
        shift2.rehashed('started_at', True)

        try:
            await shift2.is_assignation(
                courier=courier,
                cluster=cluster,
                exclude=[shift2],
            )
        except dataset.CourierShift.ErIntersection:
            tap.failed('Не пересекаются')
        else:
            tap.passed('Не пересекаются')


@pytest.mark.parametrize('working_interval', [
    pytest.param((time(9, 0), time(21, 0)), id='common_interval'),
    pytest.param((time(22, 0), time(7, 0)), id='night_interval'),
    pytest.param((time(9, 0), time(0, 0)), id='since_morning'),
    pytest.param((time(0, 0), time(21, 0)), id='till_evening'),
    pytest.param((time(0, 0), time(0, 0)), id='all_day'),
])
async def test_working_interval(tap, dataset, now, working_interval):
    with tap.plan(7, f'проверка рабочего времени {working_interval}'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'forbidden_before_time': working_interval[0],
                'forbidden_after_time': working_interval[1],
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        # Послезавтра 00:00:00 чтобы не флапали тесты на переходе дней
        day = (now(pytz.timezone(cluster.tz)) + timedelta(days=2)) \
            .replace(hour=0, minute=0, second=0, microsecond=0)

        started_at = day.replace(
            hour=working_interval[0].hour,
            minute=working_interval[0].minute
        )
        closes_at = day.replace(
            hour=working_interval[1].hour,
            minute=working_interval[1].minute
        )
        if closes_at < started_at:
            closes_at += timedelta(days=1)

        courier_shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='waiting',
            started_at=started_at,
            closes_at=closes_at,
            schedule=[{'tags': [], 'time': now() - timedelta(hours=1)}],
        )

        tap.ok(
            await courier_shift.is_assignation(
                courier=courier,
                cluster=cluster,
                exclude=[courier_shift],
            ),
            'нет выхода за пределы на границах времени'
        )

        out_of_working_interval = [
            (
                courier_shift.started_at - timedelta(hours=1),
                courier_shift.closes_at,
            ),
            (
                courier_shift.started_at,
                courier_shift.closes_at + timedelta(hours=1),
            ),
            (
                courier_shift.started_at - timedelta(hours=1),
                courier_shift.closes_at + timedelta(hours=1),
            ),
        ]
        at_working_interval = [
            (
                courier_shift.started_at + timedelta(hours=1),
                courier_shift.closes_at,
            ),
            (
                courier_shift.started_at,
                courier_shift.closes_at - timedelta(hours=1),
            ),
            (
                courier_shift.started_at + timedelta(hours=1),
                courier_shift.closes_at - timedelta(hours=1),
            ),
        ]

        for idx, interval in enumerate(out_of_working_interval):
            courier_shift.started_at = interval[0]
            courier_shift.closes_at = interval[1]

            with tap.raises(
                    dataset.CourierShift.ErWorkingInterval,
                    f'выход за границы рабочего времени [#{idx}]'
            ):
                await courier_shift.is_assignation(
                    courier=courier,
                    cluster=cluster,
                    exclude=[courier_shift],
                )

        for idx, interval in enumerate(at_working_interval):
            courier_shift.started_at = interval[0]
            courier_shift.closes_at = interval[1]

            tap.ok(
                await courier_shift.is_assignation(
                    courier=courier,
                    cluster=cluster,
                    exclude=[courier_shift],
                ),
                f'нет выхода за пределы на границах времени [#{idx}]'
            )
