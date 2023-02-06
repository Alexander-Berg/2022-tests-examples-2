from datetime import timedelta, timezone

import pytest

from libstall.util import tzone
from scripts.cron.sync_courier_shift_counters import sync_courier_shift_counters
from scripts.cron.close_courier_shifts import close_courier_shifts
from stall.model.courier_shift import CourierShift, CourierShiftEvent


@pytest.mark.parametrize(
    'counters', [
        {'planned_sec': (3 + 4) * 3600, 'extra_sec': 3600},  # все ОК

        # выполняется синхронизация счетчиков
        {'planned_sec': 0, 'extra_sec': 3600},               # не совпал план
        {'planned_sec': (3 + 4) * 3600, 'extra_sec': 123},   # не совпал доп.
    ]
)
async def test_simple(tap, dataset, time_mock, counters):
    time_mock.set('2022-07-17 12:00:00+00:00')
    with tap.plan(2, f'Базовый успешный тест, counters={counters}'):
        _now = time_mock.now(timezone.utc).replace(hour=1)
        date = str(_now.date())
        store = await dataset.store(
            vars={
                'courier_shift_counters': {
                    date: counters,
                },
            },
        )

        # 4-х часовая planned-смена (request)
        await dataset.courier_shift(
            status='request',
            placement='planned',
            started_at=_now,
            closes_at=_now + timedelta(hours=4),
            store=store,
        )
        # 3-х часовая planned-смена (waiting)
        await dataset.courier_shift(
            status='waiting',
            placement='planned',
            started_at=_now,
            closes_at=_now + timedelta(hours=3),
            store=store
        )
        # 2-х часовая extra-смена (processing) с доп. часом
        await dataset.courier_shift(
            status='processing',
            placement='planned-extra',
            started_at=_now,
            closes_at=_now + timedelta(hours=2),
            store=store,
            vars={
                'extra_sec': 3600,
            }
        )

        await sync_courier_shift_counters(store_id=store.store_id)

        with await store.reload():
            counters = store.vars['courier_shift_counters'][date]
            tap.eq(counters['planned_sec'], (3 + 4) * 3600, 'planned_sec')
            tap.eq(counters['extra_sec'], 3600, 'extra_sec')


async def test_complete_leave(tap, dataset, time_mock):
    time_mock.set('2022-07-17 12:00:00+00:00')
    with tap.plan(2, 'Проверка complete/leave смен'):
        _now = time_mock.now(timezone.utc).replace(hour=1)
        date = str(_now.date())
        store = await dataset.store(
            vars={
                'courier_shift_counters': {
                    date: {
                        'planned_sec': 4 * 3600,
                        'extra_sec': 7200,
                    },
                },
            },
        )

        # 4-х часовая planned-смена (leave)
        await dataset.courier_shift(
            status='leave',
            placement='planned',
            started_at=_now,
            closes_at=_now + timedelta(hours=4),
            store=store,
        )
        # 2-х часовая extra-смена (completed) с доп. часом
        await dataset.courier_shift(
            status='complete',
            placement='planned-extra',
            started_at=_now,
            closes_at=_now + timedelta(hours=2),
            store=store,
            vars={
                'extra_sec': 7200,
            }
        )

        await sync_courier_shift_counters(store_id=store.store_id)

        with await store.reload():
            counters = store.vars['courier_shift_counters'][date]
            tap.eq(counters['planned_sec'], 4 * 3600, 'planned_sec')
            tap.eq(counters['extra_sec'], 7200, 'extra_sec')


@pytest.mark.parametrize('reissue_enable', (True, False))
@pytest.mark.parametrize('event_type,count', (
    ('reissued', 1),   # только первая смена считается (absent и closed игнор)
    ('request', 3),    # absent и closed тоже учитываются
))
async def test_reissue_absent_closed(
        tap, dataset, time_mock, reissue_enable, event_type, count
):
    time_mock.set('2022-07-17 12:00:00+00:00')
    with tap.plan(
            2,
            f'Учет переиздание absent/closed, {reissue_enable}/{event_type}',
    ):
        _now = time_mock.now(timezone.utc).replace(hour=1)
        date = str(_now.date())

        cluster = await dataset.cluster(courier_shift_setup={
            'reissue_enable': reissue_enable,
        })
        store = await dataset.store(
            cluster=cluster,
            vars={
                'courier_shift_counters': {
                    date: {
                        'planned_sec': count * 3600,
                        'extra_sec': count * 3600,
                    },
                },
            },
        )

        # 4-х часовая planned-смена (completed) с доп. часом
        await dataset.courier_shift(
            status='complete',
            placement='planned',
            started_at=_now,
            closes_at=_now + timedelta(hours=1),
            store=store,
            vars={
                'extra_sec': 3600,
            }
        )

        # смены, которые игнорируются, если
        for status in ('absent', 'closed'):
            await dataset.courier_shift(
                status=status,
                placement='planned',
                started_at=_now,
                closes_at=_now + timedelta(hours=1),
                store=store,
                vars={
                    'extra_sec': 3600,
                },
                shift_events=[CourierShiftEvent({'type': event_type})],
            )

        await sync_courier_shift_counters(store_id=store.store_id)

        with await store.reload():
            counters = store.vars['courier_shift_counters'][date]
            tap.eq(counters['planned_sec'], count * 3600, 'planned_sec')
            tap.eq(counters['extra_sec'], count * 3600, 'extra_sec')


async def test_yesterday_shifts(tap, dataset, time_mock):
    time_mock.set('2022-07-17 12:00:00+00:00')
    with tap.plan(3, 'Счетчики со вчерашних смен не играют значения'):
        today = time_mock.now(timezone.utc).replace(hour=1, minute=0, second=0)
        yesterday = today - timedelta(days=1)
        date_today, date_yesterday = str(today.date()), str(yesterday.date())

        store = await dataset.store(
            vars={
                'courier_shift_counters': {
                    date_yesterday: {
                        'planned_sec': 4 * 3600,
                        'extra_sec': 7200,
                    },
                    date_today: {
                        'planned_sec': 3 * 3600,
                        'extra_sec': -3600,
                    },
                },
            },
        )

        # Вчерашняя 6-х часовая planned-смена (completed) с 2мя доп. часами
        await dataset.courier_shift(
            status='complete',
            placement='planned',
            started_at=yesterday,
            closes_at=yesterday + timedelta(hours=6),
            store=store,
            vars={
                'extra_sec': 7200,
            }
        )
        # Сегодняшняя 3-х часовая planned-смена (request) порезанная на час
        await dataset.courier_shift(
            status='request',
            placement='planned',
            started_at=today,
            closes_at=today + timedelta(hours=3),
            store=store,
            vars={
                'extra_sec': -3600,
            }
        )

        await sync_courier_shift_counters(store_id=store.store_id)

        with await store.reload():
            counters = store.vars['courier_shift_counters'][date_today]
            tap.eq(counters['planned_sec'], 3 * 3600, 'план не изменился')
            tap.eq(counters['extra_sec'], -3600, 'extra_sec не изменился')
            tap.eq(store.vars['courier_shift_counters'].get(date_yesterday),
                   None,
                   'вчерашние счетчики сброшены')


@pytest.mark.parametrize('tz', [
    'US/Hawaii',         # UTC-10
    'Europe/London',     # UTC+0 (есть переход на летнее время)
    'Asia/Vladivostok',  # UTC+10
])
async def test_tz(tap, dataset, now, tz):
    with tap.plan(2, 'Проверка часового пояса'):
        _midnight = now(tzone(tz=tz)).replace(hour=0, minute=0, second=0)
        date = str(_midnight.date())
        store = await dataset.store(
            vars={
                'courier_shift_counters': {
                    date: {
                        'planned_sec': 4 * 3600,
                        'extra_sec': 0,
                    },
                },
            },
            tz=tz,
        )
        # 2ч-смена c начала дня (с 01:01 до 03:01)
        await dataset.courier_shift(
            status='request',
            placement='planned',
            started_at=_midnight + timedelta(hours=1, minutes=1),
            closes_at=_midnight + timedelta(hours=3, minutes=1),
            store=store,
        )
        # 2ч-смена с окончания дня (с 21:59 до 00:59)
        await dataset.courier_shift(
            status='request',
            placement='planned',
            started_at=_midnight + timedelta(hours=22, minutes=59),
            closes_at=_midnight + timedelta(hours=24, minutes=59),
            store=store,
        )

        await sync_courier_shift_counters(store_id=store.store_id)

        with await store.reload():
            counters = store.vars['courier_shift_counters'][date]
            tap.eq(counters['planned_sec'], 4 * 3600, 'planned_sec')
            tap.eq(counters['extra_sec'], 0, 'extra_sec')


async def test_reissue_x3_shift(tap, dataset, time_mock):
    time_mock.set('2022-07-17 12:00:00+00:00')
    with tap.plan(9, 'Прогнозирование счетчиков при переиздании смен'):
        _now = time_mock.now(timezone.utc).replace(hour=1)
        date = str(_now.date())

        cluster = await dataset.cluster(
            courier_shift_setup={
                'timeout_request': 3600,  # мин.размер 1ч
                'reissue_enable': True,
            },
        )
        store = await dataset.store(
            cluster=cluster,
            vars={
                'courier_shift_counters': {
                    date: {
                        'planned_sec': 4 * 3600,
                        'extra_sec': 3600,
                    },
                },
            },
        )

        # 5-часовая плановая смена, увеличенная на 1 час
        shift_request = await dataset.courier_shift(
            status='request',
            placement='planned',
            started_at=_now,
            closes_at=_now + timedelta(hours=5),
            store=store,
            vars={
                'extra_sec': 3600,
            }
        )

        # переиздаем смену несколько раз
        for _ in range(3):
            # "прошел 1 час", а смену никто не взял; переиздание
            _now += timedelta(hours=1, seconds=5)
            await close_courier_shifts(cluster_id=cluster.cluster_id, now_=_now)

            # пересчитываем счетчики
            await sync_courier_shift_counters(store_id=store.store_id)

            # старые копии не влияют на счетчики
            with await store.reload():
                counters = store.vars['courier_shift_counters'][date]
                tap.eq(counters['planned_sec'], 5 * 3600, 'planned_sec')
                tap.eq(counters['extra_sec'], 3600, 'extra_sec')

        # проверяем, что переизданная смена изменилась
        reissued_shifts = (
            await CourierShift.list(
                by='full',
                sort=tuple(),
                conditions=[
                    # чтобы получать последнюю переизданную
                    ('status', 'request'),
                    ('parent_ids', '@>', [shift_request.courier_shift_id]),
                ],
            )
        ).list
        child = sorted(reissued_shifts, key=lambda s: len(s.parent_ids))[-1]
        tap.eq(child.duration, 2 * 3600, 'длительность 2 часа')
        tap.eq(child.vars['extra_sec'], 3600, 'все еще числится доп.час')
        tap.eq(child.attr['planned_parent'], True, 'planned_parent метка')
