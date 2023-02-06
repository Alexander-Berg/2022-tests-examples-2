# pylint: disable=too-many-lines
from datetime import timedelta

import pytest

from scripts.cron.close_courier_shifts import (
    REISSUE_OFFSET,
    HOLD_ABSENT_TAIL,
    close_courier_shifts,
    get_shifts,
)
from stall.logbrokers.constants import DEFAULT_EVENT_LAG
from stall.model.courier_shift import (
    COURIER_SHIFT_STATUSES,
    COURIER_SHIFT_FINISH_STATUSES,
    CourierShift,
    CourierShiftEvent
)
from stall.model.courier_shift_tag import TAG_BEGINNER


async def test_get_shifts(tap, dataset, now):
    with tap.plan(4, 'Проверка порядка выдачи смен'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        _now = now()

        shift_processing = await dataset.courier_shift(
            status='processing',
            started_at=_now - timedelta(hours=4),
            closes_at=_now + timedelta(hours=1),
            store=store,
            courier=courier,
            shift_events=[CourierShiftEvent({'type': 'started'})],
        )

        shift_waiting = await dataset.courier_shift(
            status='waiting',
            started_at=_now - timedelta(minutes=1),
            closes_at=_now + timedelta(hours=4),
            store=store,
            courier=courier,
        )

        agen = get_shifts(now_=_now, cluster_id=cluster.cluster_id)
        async for shifts in agen:
            tap.eq(len(shifts), 1, 'только 1 смена')
            tap.eq(shifts[0].courier_shift_id,
                   shift_waiting.courier_shift_id,
                   'первой пришла waiting смена')
            break

        async for shifts in agen:
            tap.eq(len(shifts), 1, 'только 1 смена')
            tap.eq(shifts[0].courier_shift_id,
                   shift_processing.courier_shift_id,
                   'второй пришла processing смена')
            break


@pytest.mark.parametrize('status', COURIER_SHIFT_STATUSES)
async def test_unknown_cluster(tap, dataset, now, uuid, status):
    with tap.plan(2, 'Игнорируем смены без кластеров'):
        cluster_id = uuid()
        shift = await dataset.courier_shift(
            status=status,
            started_at=(now() - timedelta(days=10)),
            closes_at=(now() - timedelta(days=11)),
            cluster_id=cluster_id,
        )

        await close_courier_shifts(cluster_id=cluster_id)

        tap.ok(await shift.reload(), 'reload смены')
        tap.eq(shift.status, status, 'статус не изменился')

        cluster = await dataset.cluster()
        shift.cluster_id = cluster.cluster_id
        await shift.save()


@pytest.mark.parametrize('status', COURIER_SHIFT_FINISH_STATUSES)
async def test_ignore_some_statuses(tap, dataset, now, status):
    with tap.plan(1, 'Игнорируем смены в не обслуживаемых статусах'):
        cluster = await dataset.cluster(courier_shift_setup={})
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier()
        shift = await dataset.courier_shift(
            courier_id=courier.courier_id,
            status=status,
            started_at=(now() - timedelta(days=200)),
            closes_at=(now() - timedelta(days=199)),
            store=store,
            cluster=cluster,
        )

        await close_courier_shifts(cluster_id=cluster.cluster_id)

        tap.eq(shift.status, status, 'статус не изменился')


async def test_default_setup(tap, dataset, now):
    with tap.plan(9, 'Дефолтные настройки кластеров'):
        cluster = await dataset.cluster(courier_shift_setup={})
        store = await dataset.store(cluster=cluster)

        # template -> /dev/null
        # смену не предлагали, и она должна была начаться 0 секунд назад
        shift_template = await dataset.courier_shift(
            status='template',
            started_at=(now() - timedelta(days=180, minutes=2)),
            closes_at=(now() - timedelta(days=180, hours=2)),
            store=store,
        )

        # request -> closed
        # смену предлагали, но никто не взял
        shift_request = await dataset.courier_shift(
            status='request',
            started_at=(now() - timedelta(days=1)),
            closes_at=(now() - timedelta(minutes=10)),
            store=store,
        )

        # waiting -> absent
        # Курьер взял смену, но так и не вышел на нее
        shift_absent = await dataset.courier_shift(
            status='waiting',
            started_at=(now() - timedelta(days=1)),
            closes_at=(now() - timedelta(minutes=10)),
            store=store
        )

        # processing -> complete
        # Курьер начал, но не закрыл смену
        shift_processing = await dataset.courier_shift(
            status='complete',
            started_at=(now() - timedelta(days=1)),
            closes_at=(now() - timedelta(minutes=10)),
            store=store
        )

        # смена долгой в паузе, но по умолчанию пауза не ограничена
        courier = await dataset.courier()
        shift_long_pause = await dataset.courier_shift(
            courier_id=courier.courier_id,
            status='processing',
            started_at=(now() - timedelta(hours=6)),
            closes_at=(now() + timedelta(hours=2)),
            store=store,
            shift_events=[
                CourierShiftEvent({'type': 'started'}),
                CourierShiftEvent({
                    'type': 'paused',
                    'created': now() - timedelta(minutes=60)
                }),
            ],
        )

        await close_courier_shifts(cluster_id=cluster.cluster_id)

        tap.ok(not await CourierShift.load(shift_template.courier_shift_id),
               'Смена удалена')
        tap.ok(await shift_request.reload(), 'reload request-смены')
        tap.eq(shift_request.status, 'closed', 'request-смена закрыта')
        tap.ok(await shift_absent.reload(), 'reload waiting-смены')
        tap.eq(shift_absent.status, 'absent', 'waiting-смена стала absent')
        tap.ok(await shift_processing.reload(), 'reload processing смену')
        tap.eq(shift_processing.status,
               'complete',
               'processing смена стала complete')
        tap.ok(await shift_long_pause.reload(), 'reload смены с паузой')
        tap.eq(len(shift_long_pause.shift_events), 2, 'Не добавлено')


async def test_agencies_default_setup(tap, dataset, now):
    with tap.plan(8, 'Дефолтные настройки для выключенного переиздания'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'reissue_enable': False,     # переиздание выключено (агентство)
            }
        )
        store = await dataset.store(cluster=cluster)

        _now = now()

        # template-смену не предлагали, и она должна была ...
        template_1 = await dataset.courier_shift(
            status='template',
            started_at=_now - timedelta(seconds=60),  # начаться 60 сек. назад
            closes_at=_now + timedelta(hours=4),
            store=store,
        )
        template_2 = await dataset.courier_shift(
            status='template',
            started_at=_now - timedelta(hours=6),
            closes_at=_now - timedelta(seconds=30),   # уже закончиться
            store=store,
        )

        # request-смену предлагали, но никто не взял
        request_1 = await dataset.courier_shift(
            status='request',
            started_at=_now - timedelta(seconds=60),  # начаться 60 сек. назад
            closes_at=_now + timedelta(hours=4),
            store=store,
        )
        request_2 = await dataset.courier_shift(
            status='request',
            started_at=_now - timedelta(hours=6),
            closes_at=_now - timedelta(seconds=30),   # уже закончиться
            store=store,
        )

        # Курьер взял смену, но так и не вышел на нее
        waiting_1 = await dataset.courier_shift(
            status='waiting',
            started_at=_now - timedelta(seconds=60),  # начаться 60 сек. назад
            closes_at=_now + timedelta(hours=4),
            store=store,
        )
        waiting_2 = await dataset.courier_shift(
            status='waiting',
            started_at=_now - timedelta(hours=6),
            closes_at=_now - timedelta(seconds=30),   # уже закончиться
            store=store,
        )

        # processing -> complete
        # Курьер начал, но не закрыл смену
        processing = await dataset.courier_shift(
            status='complete',
            started_at=(now() - timedelta(days=1)),
            closes_at=(now() - timedelta(minutes=10)),
            store=store
        )

        # смена долгой в паузе, но по умолчанию пауза не ограничена
        processing_long_pause = await dataset.courier_shift(
            status='processing',
            started_at=(now() - timedelta(hours=6)),
            closes_at=(now() + timedelta(hours=2)),
            store=store,
            shift_events=[
                CourierShiftEvent({'type': 'started'}),
                CourierShiftEvent({
                    'type': 'paused',
                    'created': now() - timedelta(minutes=60)
                }),
            ],
        )

        await close_courier_shifts(cluster_id=cluster.cluster_id)

        # template
        with await template_1.reload() as shift:
            tap.eq(shift.status, 'template', 'template-смена не затронута')
        tap.ok(not await CourierShift.load(template_2.courier_shift_id),
               'Смена удалена')

        # request
        with await request_1.reload() as shift:
            tap.eq(shift.status, 'request', 'request-смена не затронута')
        with await request_2.reload() as shift:
            tap.eq(shift.status, 'closed', 'request-смена закрыта')

        # waiting
        with await waiting_1.reload() as shift:
            tap.eq(shift.status, 'waiting', 'waiting-смена не затронута')
        with await waiting_2.reload() as shift:
            tap.eq(shift.status, 'absent', 'waiting-смена переведена в absent')

        # processing
        with await processing.reload() as shift:
            tap.eq(shift.status, 'complete', 'переведена в complete')
        with await processing_long_pause.reload() as shift:
            tap.eq(len(shift.shift_events), 2, 'Не добавлено')


@pytest.mark.parametrize('reissue_enable', [True, False])
async def test_status_template(tap, dataset, now, reissue_enable):
    with tap.plan(3, f'Смена в template статусе, переиздание={reissue_enable}'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'reissue_enable': reissue_enable,   # переиздание вкл/выкл
                'timeout_template': 7 * 86400,      # 7 суток
            },
        )
        store = await dataset.store(cluster=cluster)

        # template. удаляем из базы вовсе
        # смену не предлагали, и она должна была начаться Х секунд назад
        shift_template_yes = await dataset.courier_shift(
            status='template',
            started_at=(now() - timedelta(days=7, minutes=3)),
            closes_at=(now() - timedelta(days=6, hours=18)),
            store=store,
        )
        shift_template_not = await dataset.courier_shift(
            status='template',
            started_at=(now() - timedelta(days=6, hours=23, minutes=58)),
            closes_at=(now() - timedelta(days=6, hours=18)),
            store=store,
        )

        await close_courier_shifts(cluster_id=cluster.cluster_id)

        tap.ok(not await CourierShift.load(shift_template_yes.courier_shift_id),
               'Смена удалена')
        tap.ok(await shift_template_not.reload(), 'reload смены 2')
        tap.eq(shift_template_not.status, 'template', 'смена не тронута')


async def test_status_request(tap, dataset, now):
    with tap.plan(5, 'Смена в request статусе'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'timeout_request': 8 * 3600,  # 8 часов
            },
        )
        store = await dataset.store(cluster=cluster)

        # request -> closed
        # смену предлагали, но никто не взял
        shift_request_yes = await dataset.courier_shift(
            status='request',
            started_at=(now() - timedelta(hours=8, minutes=3)),
            closes_at=(now() + timedelta(hours=2)),
            store=store,
        )
        shift_request_not = await dataset.courier_shift(
            status='request',
            started_at=(now() - timedelta(hours=7, minutes=57)),
            closes_at=(now() - timedelta(hours=2)),
            store=store,
        )

        await close_courier_shifts(cluster_id=cluster.cluster_id)

        tap.ok(await shift_request_yes.reload(), 'reload смены 1')
        tap.eq(shift_request_yes.status, 'closed', 'смена закрыта')
        tap.eq([e['type'] for e in shift_request_yes.shift_events],
               ['closed', 'reissued'],
               'добавлено 2 события')
        tap.ok(await shift_request_not.reload(), 'reload смены 2')
        tap.eq(shift_request_not.status, 'request', 'смена не тронута')


async def test_agencies_status_request(tap, dataset, now):
    with tap.plan(5, 'Смена в request статусе при выключенном переиздании'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'reissue_enable': False,     # переиздание выключено (агентство)
                'timeout_request': 8 * 3600,  # 8 часов
            },
        )
        store = await dataset.store(cluster=cluster)

        # request -> closed
        # смену предлагали, но никто не взял
        shift_request_yes = await dataset.courier_shift(
            status='request',
            started_at=(now() - timedelta(hours=8, minutes=3)),
            closes_at=(now() + timedelta(hours=2)),
            store=store,
        )
        shift_request_not = await dataset.courier_shift(
            status='request',
            started_at=(now() - timedelta(hours=7, minutes=57)),
            closes_at=(now() - timedelta(hours=2)),
            store=store,
        )

        await close_courier_shifts(cluster_id=cluster.cluster_id)

        tap.ok(await shift_request_yes.reload(), 'reload смены 1')
        tap.eq(shift_request_yes.status, 'closed', 'смена закрыта')
        tap.eq([e['type'] for e in shift_request_yes.shift_events],
               ['closed'],
               'добавлено 1 событие, нет переиздания')
        tap.ok(await shift_request_not.reload(), 'reload смены 2')
        tap.eq(shift_request_not.status, 'request', 'смена не тронута')


async def test_status_waiting(tap, dataset, now):
    with tap.plan(8, 'Смена в waiting статусе'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'started_after_time': 1800,  # 30 минут
            },
        )
        store = await dataset.store(cluster=cluster)
        tag = await dataset.courier_shift_tag()

        # waiting -> absent
        # Курьер взял смену, но так и не вышел на нее
        shift_waiting_yes = await dataset.courier_shift(
            status='waiting',
            started_at=(now() - timedelta(minutes=32)),
            closes_at=(now() + timedelta(hours=4)),
            store=store,
            tags=[TAG_BEGINNER, tag.title],        # смена и курьер новичок
            courier_tags=[tag.title],
        )
        # не подходит по времени
        shift_waiting_not_1 = await dataset.courier_shift(
            status='waiting',
            started_at=(now() - timedelta(minutes=28)),
            closes_at=(now() + timedelta(hours=4)),
            store=store,
        )
        # не подходит, т.к. есть событие "начата"
        shift_waiting_not_2 = await dataset.courier_shift(
            status='waiting',
            started_at=(now() - timedelta(minutes=32)),
            closes_at=(now() + timedelta(hours=4)),
            store=store,
            shift_events=[CourierShiftEvent({
                'type': 'started',      # такой смены быть не может, но все же
            })]
        )

        await close_courier_shifts(cluster_id=cluster.cluster_id)

        with await shift_waiting_yes.reload() as shift:
            tap.eq(shift.status, 'absent', 'смена закрыта')
            tap.eq([e['type'] for e in shift.shift_events],
                   ['absent', 'reissued'],
                   'добавлено 2 события')
            tap.eq(shift.tags, [TAG_BEGINNER, tag.title], 'теги остались')
            tap.eq(shift.courier_tags, [tag.title], 'теги курьера')

            event = shift.event_reissued()
            reissued = await CourierShift.load(event.detail['courier_shift_id'])
            tap.eq(reissued.tags, [tag.title], 'передан только нужный тег')
            tap.eq(reissued.courier_tags, None, 'теги курьера')

        with await shift_waiting_not_1.reload() as shift:
            tap.eq(shift.status, 'waiting', 'смена не тронута')

        with await shift_waiting_not_2.reload() as shift:
            tap.eq(shift.status, 'waiting', 'смена не тронута')


async def test_agencies_status_waiting(tap, dataset, now):
    with tap.plan(7, 'Смена в waiting статусе'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'reissue_enable': False,     # переиздание выключено (агентство)
                'started_after_time': 1800,  # 30 минут
            },
        )
        store = await dataset.store(cluster=cluster)

        # waiting -> absent
        # Курьер взял смену, но так и не вышел на нее
        shift_waiting_yes = await dataset.courier_shift(
            status='waiting',
            started_at=(now() - timedelta(minutes=32)),
            closes_at=(now() + timedelta(hours=4)),
            store=store,
        )
        # не подходит по времени
        shift_waiting_not_1 = await dataset.courier_shift(
            status='waiting',
            started_at=(now() - timedelta(minutes=28)),
            closes_at=(now() + timedelta(hours=4)),
            store=store,
        )
        # не подходит, т.к. есть событие "начата"
        shift_waiting_not_2 = await dataset.courier_shift(
            status='waiting',
            started_at=(now() - timedelta(minutes=32)),
            closes_at=(now() + timedelta(hours=4)),
            store=store,
            shift_events=[CourierShiftEvent({
                'type': 'started',      # такой смены быть не может, но все же
            })]
        )

        await close_courier_shifts(cluster_id=cluster.cluster_id)

        tap.ok(await shift_waiting_yes.reload(), 'reload смены 1')
        tap.eq(shift_waiting_yes.status, 'absent', 'смена закрыта')
        tap.eq([e['type'] for e in shift_waiting_yes.shift_events],
               ['absent'],
               'добавлено 1 событие, смена закрыта')
        tap.ok(await shift_waiting_not_1.reload(), 'reload смены 2')
        tap.eq(shift_waiting_not_1.status, 'waiting', 'смена не тронута')
        tap.ok(await shift_waiting_not_2.reload(), 'reload смены 3')
        tap.eq(shift_waiting_not_2.status, 'waiting', 'смена не тронута')


# pylint: disable=too-many-locals
@pytest.mark.parametrize('reissue_enable', [True, False])
async def test_status_processing(tap, dataset, now, reissue_enable):
    with tap.plan(21, f'processing-смена, переиздание={reissue_enable}'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'reissue_enable': reissue_enable,   # переиздание вкл/выкл
                'timeout_processing': 600,          # 10 минут
            },
        )
        store = await dataset.store(cluster=cluster)

        # подходит. курьер не закрыл смену + заказов нет вовсе.
        courier_yes_1 = await dataset.courier()
        shift_processing_yes_1 = await dataset.courier_shift(
            courier_id=courier_yes_1.courier_id,
            status='processing',
            started_at=(now() - timedelta(hours=4)),
            closes_at=(now() - timedelta(minutes=2)),
            store=store,
            shift_events=[CourierShiftEvent({'type': 'started'})],
        )
        # подходит. курьер не закрыл смену + есть законченный заказ
        courier_yes_2 = await dataset.courier()
        shift_processing_yes_2 = await dataset.courier_shift(
            courier_id=courier_yes_2.courier_id,
            status='processing',
            started_at=(now() - timedelta(hours=4)),
            closes_at=(now() - timedelta(minutes=2)),
            store=store,
            shift_events=[CourierShiftEvent({'type': 'started'})],
        )
        order_complete = await dataset.order(
            courier_shift=shift_processing_yes_2,
            courier_id=courier_yes_2.courier_id,
            status='complete',
            estatus='done',
        )
        # подходит, т.к. хотя курьер все еще исполняет заказ, его время вышло
        courier_yes_3 = await dataset.courier()
        shift_processing_yes_3 = await dataset.courier_shift(
            courier_id=courier_yes_3.courier_id,
            status='processing',
            started_at=(now() - timedelta(hours=4)),
            closes_at=(now() - timedelta(minutes=12)),    # 2 минуты как вышло
            store=store,
            shift_events=[CourierShiftEvent({'type': 'started'})],
        )
        order_processing_1 = await dataset.order(
            courier_shift=shift_processing_yes_3,
            courier_id=courier_yes_3.courier_id,
            status='processing',
            estatus='waiting',
        )

        # не подходит по времени
        courier_not_1 = await dataset.courier()
        shift_processing_not_1 = await dataset.courier_shift(
            courier_id=courier_not_1.courier_id,
            status='processing',
            started_at=(now() - timedelta(hours=4)),
            closes_at=(now() + timedelta(minutes=2)),
            store=store,
            shift_events=[CourierShiftEvent({'type': 'started'})],
        )
        # не подходит, т.к. есть пара событий "начата-закрыта"
        courier_not_2 = await dataset.courier()
        shift_processing_not_2 = await dataset.courier_shift(
            courier_id=courier_not_2.courier_id,
            status='processing',
            started_at=(now() - timedelta(hours=4)),
            closes_at=(now() - timedelta(minutes=2)),
            store=store,
            shift_events=[
                CourierShiftEvent({'type': 'started'}),
                CourierShiftEvent({'type': 'stopped'}),
            ]
        )
        # не подходит, т.к. курьер все еще исполняет заказ и он не "стух"
        courier_not_3 = await dataset.courier()
        shift_processing_not_3 = await dataset.courier_shift(
            courier_id=courier_not_3.courier_id,
            status='processing',
            started_at=(now() - timedelta(hours=4)),
            closes_at=(now() - timedelta(minutes=2)),     # у него еще 8 минут
            store=store,
            shift_events=[CourierShiftEvent({'type': 'started'})],
        )
        order_processing_2 = await dataset.order(
            courier_shift=shift_processing_not_3,
            courier_id=courier_not_3.courier_id,
            status='processing',
            estatus='waiting',
        )
        # не подходит, т.к. курьер возвращается на лавку
        courier_not_4 = await dataset.courier(
            last_order_time=(now() - timedelta(minutes=1)),
        )
        shift_processing_not_4 = await dataset.courier_shift(
            courier_id=courier_not_4.courier_id,
            status='processing',
            started_at=(now() - timedelta(hours=4)),
            closes_at=(now() - timedelta(minutes=2)),
            store=store,
            shift_events=[CourierShiftEvent({'type': 'started'})],
        )
        order_complete_2 = await dataset.order(
            courier_shift=shift_processing_not_4,
            courier_id=courier_not_4.courier_id,
            status='complete',
            estatus='done',
        )

        tap.ok(order_complete, 'Заказ complete создан')
        tap.ok(order_processing_1, 'Заказ processing создан')
        tap.ok(order_processing_2, 'Заказ processing создан')
        tap.ok(order_complete_2, 'Заказ complete создан')

        await close_courier_shifts(cluster_id=cluster.cluster_id)

        # курьер забыл закрыть смену и заказа у него не было
        tap.ok(await shift_processing_yes_1.reload(), 'reload смены yes_1')
        tap.eq(shift_processing_yes_1.status, 'complete', 'смена yes_1 закрыта')
        tap.eq([e['type'] for e in shift_processing_yes_1.shift_events][-2:],
               ['stopped', 'complete'],
               'добавлено 2 события')
        tap.ok(await shift_processing_yes_2.reload(), 'reload смены yes_2')
        tap.eq(shift_processing_yes_2.status, 'complete', 'смена yes_2 закрыта')
        tap.eq([e['type'] for e in shift_processing_yes_2.shift_events][-2:],
               ['stopped', 'complete'],
               'добавлено 2 события')

        # смена жестко закрыта по таймауту, хотя заказ был
        tap.ok(await shift_processing_yes_3.reload(), 'reload смены yes_3')
        tap.eq(shift_processing_yes_3.status, 'complete', 'смена yes_3 закрыта')
        tap.eq([e['type'] for e in shift_processing_yes_3.shift_events][-2:],
               ['stopped', 'complete'],
               'добавлено 2 события')

        tap.ok(await shift_processing_not_1.reload(), 'reload смены not_1')
        tap.eq(shift_processing_not_1.status, 'processing', 'смена не тронута')
        tap.ok(await shift_processing_not_2.reload(), 'reload смены not_2')
        tap.eq(shift_processing_not_2.status, 'processing', 'смена не тронута')
        tap.ok(await shift_processing_not_3.reload(), 'reload смены not_3')
        tap.eq(shift_processing_not_3.status, 'processing', 'смена не тронута')
        tap.ok(await shift_processing_not_4.reload(), 'reload смены not_4')
        tap.eq(shift_processing_not_4.status, 'processing', 'смена не тронута')


@pytest.mark.parametrize('reissue_enable', [True, False])
async def test_status_released(tap, dataset, now, uuid, reissue_enable):
    with tap.plan(19,  f'released-смена, переиздание={reissue_enable}'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'reissue_enable': reissue_enable,   # переиздание вкл/выкл
            },
        )
        store = await dataset.store(cluster=cluster)

        # подходит.
        shift_yes_1 = await dataset.courier_shift(
            store=store,
            cluster=cluster,
            status='released',
            started_at=(now() + timedelta(hours=4)),
            closes_at=(now() + timedelta(minutes=8)),
        )
        courier = await dataset.courier()
        shift_yes_2 = await dataset.courier_shift(
            store=store,
            cluster=cluster,
            status='released',
            started_at=(now() + timedelta(hours=4)),
            closes_at=(now() + timedelta(minutes=8)),
            shift_events=[
                CourierShiftEvent({
                    'type': 'swap_started',
                    'courier_id': courier.courier_id,
                    'detail': {'group_ids': [uuid(), uuid()]},
                    'created': (now() - timedelta(minutes=2)),
                }),
                CourierShiftEvent({'type': 'swap_finished'}),
                CourierShiftEvent({'type': 'refuse'}),
                CourierShiftEvent({'type': 'released'}),
            ]
        )
        # не подходит, т.к. не тот статус
        shift_not_1 = await dataset.courier_shift(
            store=store,
            cluster=cluster,
            status='waiting',
            started_at=(now() + timedelta(hours=4)),
            closes_at=(now() + timedelta(minutes=8)),
        )
        # не подходит, т.к. уже с событием "переиздана"
        shift_not_2 = await dataset.courier_shift(
            store=store,
            cluster=cluster,
            status='released',
            started_at=(now() + timedelta(hours=4)),
            closes_at=(now() + timedelta(minutes=8)),
            shift_events=[CourierShiftEvent({
                'type': 'reissued',
            })],
        )

        await close_courier_shifts(cluster_id=cluster.cluster_id)

        with await shift_yes_1.reload() as shift:
            tap.eq(shift.status, 'released', 'статус не изменился')
            tap.eq(len(shift.shift_events), 1, 'добавилось 1 событие')

            event = shift.shift_events[0]
            tap.eq(event.type, 'reissued', 'переиздана')

            reissued = await CourierShift.load(event.detail['courier_shift_id'])
            tap.eq(reissued.status, 'request', 'предложена')
            tap.eq(reissued.parent_ids,
                   [shift_yes_1.courier_shift_id],
                   'только 1 родитель')
            tap.eq(reissued.placement, shift_yes_1.placement, 'placement')

        with await shift_yes_2.reload() as shift:
            tap.eq(shift.status, 'released', 'статус не изменился')
            tap.eq(len(shift.shift_events), 5, 'добавилось 1 событие (4 было)')

            event = shift.shift_events[-1]
            tap.eq(event.type, 'reissued', 'переиздана')

            reissued = await CourierShift.load(event.detail['courier_shift_id'])
            tap.eq(reissued.status, 'request', 'предложена')
            tap.eq(reissued.parent_ids,
                   [shift_yes_2.courier_shift_id],
                   'только 1 родитель')
            tap.eq(reissued.placement, shift_yes_1.placement, 'placement')

        with await shift_not_1.reload() as shift:
            tap.eq(shift.status, 'waiting', 'статус не изменился')
            tap.eq(len(shift.shift_events), 0, 'новых событий нет')

        with await shift_not_2.reload() as shift:
            tap.eq(shift.status, 'released', 'статус не изменился')
            tap.eq(len(shift.shift_events), 1, 'остается 1 событие')

            event = shift.shift_events[0]
            tap.eq(event.type, 'reissued', 'старое событие на месте')
            tap.eq(event.detail, {}, 'переиздания не отмечено')
            reissued_shifts = await shift.list_reissued()
            tap.eq(reissued_shifts, [], 'переизданной смены нет')


@pytest.mark.parametrize('reissue_enable', [True, False])
async def test_rollback_swap(tap, dataset, now, uuid, reissue_enable):
    with tap.plan(20, f'Смена сломана при обмене, переиздан.={reissue_enable}'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'reissue_enable': reissue_enable,   # переиздание вкл/выкл
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier()
        courier2 = await dataset.courier()
        group_id_1 = uuid()

        # попытка захвата 3х смен провалилась
        shift_yes_to_1 = await dataset.courier_shift(
            status='waiting',   # успел захватить смену
            store=store,
            courier=courier,
            group_id=group_id_1,
        )
        shift_yes_to_2 = await dataset.courier_shift(
            status='waiting',   # а эту смену успел взять ДРУГОЙ курьер
            store=store,        # и это послужило причиной отката
            courier=courier2,
        )
        shift_yes_to_3 = await dataset.courier_shift(
            status='request',   # до этой смены не добрались
            store=store,
        )
        group_ids = [
            shift_yes_to_1.group_id,
            shift_yes_to_2.group_id,
            shift_yes_to_3.group_id,
        ]
        # смена, которую хотели поменять
        shift_yes_from = await dataset.courier_shift(
            status='waiting',
            store=store,
            courier=courier,
            shift_events=[
                CourierShiftEvent({
                    'type': 'swap_started',
                    'courier_id': courier.courier_id,
                    'detail': {'group_ids': group_ids},
                    'created': (now() - timedelta(minutes=2)),
                }),
            ]
        )
        # не подходит, т.к. это другая смена текущего курьера
        shift_not_to_1 = await dataset.courier_shift(
            status='waiting',
            store=store,
            courier=courier,
        )
        # не подходит, т.к. это смена другого курьера из этой же группы
        shift_not_to_2 = await dataset.courier_shift(
            status='waiting',
            group_id=group_id_1,
        )

        await close_courier_shifts(cluster_id=cluster.cluster_id)

        with await shift_yes_from.reload() as shift:
            tap.eq(shift.courier_id, courier.courier_id, 'курьер на месте')
            tap.eq(shift.status, 'waiting', 'статус не сменился')
            tap.eq(len(shift.shift_events), 2, 'добавилось 1 событие ...')
            tap.eq([e.type for e in shift.shift_events],
                   ['swap_started', 'swap_finished'],
                   'обмен сменами завершен')

        # занятая смена освобождена
        with await shift_yes_to_1.reload() as shift:
            tap.eq(shift.courier_id, None, 'курьер снят')
            tap.eq(shift.status, 'request', 'статус сменился на request')
            tap.eq(len(shift.shift_events), 1, 'добавилось 1 событие ...')
            tap.eq(shift.shift_events[0].type, 'request', 'и это request')

        # чужую смену не трогаем
        with await shift_yes_to_2.reload() as shift:
            tap.eq(shift.courier_id, courier2.courier_id, 'курьер на месте')
            tap.eq(shift.status, 'waiting', 'статус не изменился')
            tap.eq(len(shift.shift_events), 0, 'новых событий нет')

        # свободная осталась свободной
        with await shift_yes_to_3.reload() as shift:
            tap.eq(shift.courier_id, None, 'курьера нет')
            tap.eq(shift.status, 'request', 'статус остался request')
            tap.eq(len(shift.shift_events), 0, 'новых событий нет')

        # чужие смены не тронуты
        for shift in shift_not_to_1, shift_not_to_2:
            s = await shift.reload()
            tap.ne(s.courier_id, None, 'курьер снят')
            tap.eq(s.status, 'waiting', 'статус не изменился')
            tap.eq(len(s.shift_events), 0, 'новых событий нет')


async def test_ignore_swap(tap, dataset, now):
    with tap.plan(15, 'Игнорирование некоторых обменов'):
        cluster = await dataset.cluster()
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier()

        shift_indicator = await dataset.courier_shift(
            status='waiting',
            store=store,
            courier=courier,
        )

        # успешный обмен
        shift_1 = await dataset.courier_shift(
            status='released',
            store=store,
            courier=courier,
            shift_events=[
                CourierShiftEvent({
                    'type': 'swap_started',
                    'courier_id': courier.courier_id,
                    'detail': {'group_ids': [shift_indicator.group_id]},
                    'created': (now() - timedelta(minutes=2)),
                }),
                CourierShiftEvent({'type': 'swap_finished'}),
                CourierShiftEvent({'type': 'refuse'}),
                CourierShiftEvent({'type': 'released'}),
            ]
        )
        # уже откаченный обмен
        shift_2 = await dataset.courier_shift(
            status='waiting',
            store=store,
            courier=courier,
            shift_events=[
                CourierShiftEvent({
                    'type': 'swap_started',
                    'courier_id': courier.courier_id,
                    'detail': {'group_ids': [shift_indicator.group_id]},
                    'created': (now() - timedelta(minutes=2)),
                }),
                CourierShiftEvent({'type': 'swap_finished'}),
            ]
        )
        # слишком свежий обмен
        shift_3 = await dataset.courier_shift(
            status='waiting',
            store=store,
            courier=courier,
            shift_events=[
                CourierShiftEvent({
                    'type': 'swap_started',
                    'courier_id': courier.courier_id,
                    'detail': {'group_ids': [shift_indicator.group_id]},
                    'created': now(),
                }),
            ]
        )

        await close_courier_shifts(cluster_id=cluster.cluster_id)

        # проигнорирована, т.к. успешная (смену переиздали)
        with await shift_1.reload() as shift:
            tap.eq(shift.courier_id, courier.courier_id, 'курьер на месте')
            tap.eq(shift.status, 'released', 'статус не сменился')
            tap.eq(len(shift.shift_events), 5, 'добавилось 1 событие ...')
            tap.eq(
                [e.type for e in shift.shift_events],
                [
                    'swap_started', 'swap_finished', 'refuse', 'released',
                    'reissued'
                ],
                'смену переиздали'
            )

        # проигнорирована, т.к. уже откатили в ручке
        with await shift_2.reload() as shift:
            tap.eq(shift.courier_id, courier.courier_id, 'курьер на месте')
            tap.eq(shift.status, 'waiting', 'статус не сменился')
            tap.eq(len(shift.shift_events), 2, 'нет новых событий')
            tap.eq([e.type for e in shift.shift_events],
                   ['swap_started', 'swap_finished'],
                   'обмен начат и завершен')

        # проигнорирована, т.к. слишком горячая
        with await shift_3.reload() as shift:
            tap.eq(shift.courier_id, courier.courier_id, 'курьер на месте')
            tap.eq(shift.status, 'waiting', 'статус не сменился')
            tap.eq(len(shift.shift_events), 1, 'нет новых событий')
            tap.eq([e.type for e in shift.shift_events],
                   ['swap_started'],
                   'обмен начат')

        # индикатор не должен измениться
        with await shift_indicator.reload() as shift:
            tap.eq(shift.courier_id, courier.courier_id, 'курьер не удален')
            tap.eq(shift.status, 'waiting', 'статус не сменился')
            tap.eq(len(shift.shift_events), 0, 'нет новых событий')


async def test_too_long_pause(tap, dataset, now):
    with tap.plan(12, 'Смена в слишком длительной паузе'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'pause_duration': 600,  # 10 минут
            },
        )
        store = await dataset.store(cluster=cluster)

        # нет никаких событий
        courier_not_1 = await dataset.courier()
        shift_processing_not_1 = await dataset.courier_shift(
            courier_id=courier_not_1.courier_id,
            status='processing',
            started_at=(now() - timedelta(hours=4)),
            closes_at=(now() + timedelta(minutes=2)),
            store=store,
            shift_events=[CourierShiftEvent({'type': 'started'})],
        )
        # есть только событие начала, но время не превышено
        courier_not_2 = await dataset.courier()
        shift_processing_not_2 = await dataset.courier_shift(
            courier_id=courier_not_2.courier_id,
            status='processing',
            started_at=(now() - timedelta(hours=4)),
            closes_at=(now() + timedelta(minutes=2)),
            store=store,
            shift_events=[
                CourierShiftEvent({'type': 'started'}),
                CourierShiftEvent({
                    'type': 'paused',
                    'created': now() - timedelta(minutes=9, seconds=30)
                }),
            ]
        )
        # есть оба события. смена НЕ на паузе, но была очень долго
        courier_not_3 = await dataset.courier()
        shift_processing_not_3 = await dataset.courier_shift(
            courier_id=courier_not_3.courier_id,
            status='processing',
            started_at=(now() - timedelta(hours=4)),
            closes_at=(now() + timedelta(minutes=2)),
            store=store,
            shift_events=[
                CourierShiftEvent({'type': 'started'}),
                CourierShiftEvent({
                    'type': 'paused',
                    'created': now() - timedelta(minutes=20)
                }),
                CourierShiftEvent({
                    'type': 'unpaused',
                    'created': now()
                }),
            ]
        )
        # есть только событие начала, и пауза слишком длительная #1
        courier_yes_1 = await dataset.courier()
        shift_processing_yes_1 = await dataset.courier_shift(
            courier_id=courier_yes_1.courier_id,
            status='processing',
            started_at=(now() - timedelta(hours=4)),
            closes_at=(now() + timedelta(minutes=2)),
            store=store,
            shift_events=[
                CourierShiftEvent({'type': 'started'}),
                CourierShiftEvent({
                    'type': 'paused',
                    'created': now() - timedelta(minutes=10, seconds=5)
                }),
            ]
        )
        # взята вторая пауза, и она слишком длительная
        courier_yes_2 = await dataset.courier()
        shift_processing_yes_2 = await dataset.courier_shift(
            courier_id=courier_yes_2.courier_id,
            status='processing',
            started_at=(now() - timedelta(hours=4)),
            closes_at=(now() + timedelta(minutes=2)),
            store=store,
            shift_events=[
                CourierShiftEvent({'type': 'started'}),
                # первая пара
                CourierShiftEvent({
                    'type': 'paused',
                    'created': now() - timedelta(minutes=20)
                }),
                CourierShiftEvent({
                    'type': 'unpaused',
                    'created': now() - timedelta(minutes=15)
                }),

                # вторая пара (только "открывающее")
                CourierShiftEvent({
                    'type': 'paused',
                    'created': now() - timedelta(minutes=10, seconds=5)
                }),
            ]
        )
        # взята вторая пауза, и она слишком длительная
        courier_yes_3 = await dataset.courier()
        user_yes_3 = await dataset.user(store=store)
        shift_processing_yes_3 = await dataset.courier_shift(
            courier_id=courier_yes_3.courier_id,
            status='processing',
            started_at=(now() - timedelta(hours=4)),
            closes_at=(now() + timedelta(minutes=2)),
            store=store,
            shift_events=[
                CourierShiftEvent({'type': 'started'}),
                # вторая пара (только "открывающее")
                CourierShiftEvent({
                    'user_id': user_yes_3.user_id,
                    'type': 'paused',
                    'created': now() - timedelta(minutes=10, seconds=5),
                    'detail': {'duration': 600},
                }),
            ]
        )

        await close_courier_shifts(cluster_id=cluster.cluster_id)

        tap.ok(await shift_processing_not_1.reload(), 'reload смены 1')
        tap.eq(len(shift_processing_not_1.shift_events), 1, 'Не добавлено')
        tap.ok(await shift_processing_not_2.reload(), 'reload смены 2')
        tap.eq(len(shift_processing_not_2.shift_events), 2, 'Не добавлено')
        tap.ok(await shift_processing_not_3.reload(), 'reload смены 3')
        tap.eq(len(shift_processing_not_3.shift_events), 3, 'Не добавлено')
        tap.ok(await shift_processing_yes_1.reload(), 'reload смены 4')
        tap.eq(len(shift_processing_yes_1.shift_events), 3, 'Добавлено событие')
        tap.ok(await shift_processing_yes_2.reload(), 'reload смены 5')
        tap.eq(len(shift_processing_yes_2.shift_events), 5, 'Добавлено событие')
        tap.ok(await shift_processing_yes_3.reload(), 'reload смены 6')
        tap.eq(len(shift_processing_yes_3.shift_events), 3, 'Добавлено событие')


async def test_extra_pause(tap, dataset, now):
    with tap.plan(6, 'Смена в дополнительной паузе'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'pause_duration': 600,  # 10 минут
                'long_slot_duration': 14400,  # 4 часа
                'extra_pause': 300,  # 5 минут
            },
        )
        store = await dataset.store(cluster=cluster)

        courier_yes_1 = await dataset.courier()
        shift_processing_yes_1 = await dataset.courier_shift(
            courier_id=courier_yes_1.courier_id,
            status='processing',
            started_at=(now() - timedelta(hours=4)),
            closes_at=(now() + timedelta(minutes=2)),
            store=store,
            shift_events=[
                CourierShiftEvent({'type': 'started'}),
                CourierShiftEvent({
                    'type': 'paused',
                    'created': now() - timedelta(minutes=15, seconds=5)
                }),
            ]
        )

        courier_yes_2 = await dataset.courier()
        shift_processing_yes_2 = await dataset.courier_shift(
            courier_id=courier_yes_2.courier_id,
            status='processing',
            started_at=(now() - timedelta(hours=3)),
            closes_at=(now() + timedelta(minutes=2)),
            store=store,
            shift_events=[
                CourierShiftEvent({'type': 'started'}),
                CourierShiftEvent({
                    'type': 'paused',
                    'created': now() - timedelta(minutes=10, seconds=5)
                }),
            ]
        )

        courier_not_1 = await dataset.courier()
        shift_processing_not_1 = await dataset.courier_shift(
            courier_id=courier_not_1.courier_id,
            status='processing',
            started_at=(now() - timedelta(hours=4)),
            closes_at=(now() + timedelta(minutes=2)),
            store=store,
            shift_events=[
                CourierShiftEvent({'type': 'started'}),
                CourierShiftEvent({
                    'type': 'paused',
                    'created': now() - timedelta(minutes=10, seconds=5)
                }),
            ]
        )

        await close_courier_shifts(cluster_id=cluster.cluster_id)

        tap.ok(await shift_processing_yes_1.reload(), 'reload смены 1')
        tap.eq(len(shift_processing_yes_1.shift_events), 3, 'Добавлено событие')
        tap.ok(await shift_processing_yes_2.reload(), 'reload смены 2')
        tap.eq(len(shift_processing_yes_2.shift_events), 3, 'Добавлено событие')
        tap.ok(await shift_processing_not_1.reload(), 'reload смены 3')
        tap.eq(len(shift_processing_not_1.shift_events), 2, 'Не добавлено')


async def test_hold_absent_too_early(tap, dataset, now):
    with tap.plan(4, 'Выдавать hold_absent слишком рано.'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'started_after_time': 600,   # 10 мин
                'timeout_processing': 900,   # 15 мин
            }
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        _now = now()

        # Смена закончится через 17 минут.
        shift_left = await dataset.courier_shift(
            status='processing',
            started_at=(_now - timedelta(hours=3)),
            closes_at=(_now + timedelta(minutes=17)),
            store=store,
            courier=courier,
            shift_events=[CourierShiftEvent({'type': 'started'})],
        )
        # Смена, идущая следом через 3 минуты, после завершения этой
        shift_right = await dataset.courier_shift(
            status='waiting',
            started_at=(_now + timedelta(minutes=20)),
            closes_at=(_now + timedelta(hours=6)),
            store=store,
            courier=courier,
        )

        await close_courier_shifts(cluster_id=cluster.cluster_id, now_=_now)

        # смены не изменились
        with await shift_left.reload() as shift:
            tap.eq(shift.status, 'processing', 'статус смены слева')
            tap.eq(len(shift.shift_events), 1, 'новых событий нет')

        with await shift_right.reload() as shift:
            tap.eq(shift.status, 'waiting', 'статус смены справа')
            tap.eq(len(shift.shift_events), 0, 'событий нет')


async def test_hold_absent_alone(tap, dataset, now):
    with tap.plan(6, 'Выдавать hold_absent некому, соседей нет.'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'started_after_time': 0,     # начинать надо заранее
                'timeout_processing': 1800,  # 30 мин
            }
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        _now = now()

        # Смена начинает протухать, на 1 секунду
        shift_right = await dataset.courier_shift(
            status='waiting',
            started_at=(_now - timedelta(seconds=1)),
            closes_at=(_now + timedelta(hours=6)),
            store=store,
            courier=courier,
        )
        # Смена, идущая перед этой, за 30 секунд до
        # Чужого курьера.
        shift_left_1 = await dataset.courier_shift(
            status='processing',
            started_at=(_now - timedelta(hours=5)),
            closes_at=(_now - timedelta(seconds=31)),
            store=store,
            shift_events=[CourierShiftEvent({'type': 'started'})],
        )
        await dataset.order(
            courier_shift=shift_left_1,
            courier_id=shift_left_1.courier_id,
            status='processing',
            estatus='waiting',
        )
        # Смена, идущая перед этой, за 30 секунд до
        # Неподходящий статус, leave
        shift_left_2 = await dataset.courier_shift(
            status='leave',
            started_at=(_now - timedelta(hours=5)),
            closes_at=(_now - timedelta(seconds=31)),
            store=store,
            courier=courier,
        )

        await close_courier_shifts(cluster_id=cluster.cluster_id, now_=_now)

        # смена протухла
        with await shift_right.reload() as shift:
            tap.eq(shift.status, 'absent', 'смена протухла')
            tap.eq([e.type for e in shift.shift_events],
                   ['absent', 'reissued'],
                   '2 новых события')

        # чужая
        with await shift_left_1.reload() as shift:
            tap.eq(shift.status, 'processing', 'статус смены слева')
            tap.eq(len(shift.shift_events), 1, 'новых событий нет')

        # leave
        with await shift_left_2.reload() as shift:
            tap.eq(shift.status, 'leave', 'статус смены слева')
            tap.eq(len(shift.shift_events), 0, 'событий нет')


async def test_hold_absent_duration(tap, dataset, now, time2time):
    with tap.plan(9, 'Выдача hold_absent только одной смене курьера'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'timeout_processing': 900,
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        _now = now()

        shift_left = await dataset.courier_shift(
            status='processing',
            started_at=(_now - timedelta(hours=4)),
            closes_at=(_now - timedelta(minutes=10)),   # 10 мин задержки
            store=store,
            courier=courier,
            shift_events=[CourierShiftEvent({'type': 'started'})],
        )
        await dataset.order(
            courier_shift=shift_left,
            courier_id=shift_left.courier_id,
            status='processing',
            estatus='waiting',
        )

        shift_right = await dataset.courier_shift(
            status='waiting',
            started_at=(_now - timedelta(seconds=1)),
            closes_at=(_now + timedelta(hours=1)),
            store=store,
            courier=courier,
        )

        shift_right_2 = await dataset.courier_shift(
            status='waiting',
            started_at=(_now + timedelta(hours=1, seconds=1)),
            closes_at=(_now + timedelta(hours=6)),
            store=store,
            courier=courier,
        )

        await close_courier_shifts(cluster_id=cluster.cluster_id, now_=_now)

        # смена слева отмечена как проверенная
        with await shift_left.reload() as shift:
            tap.eq(shift.status, 'processing', 'статус смены слева')

        # смена справа отмечена как "защищенная от absent"
        _duration = 301 + HOLD_ABSENT_TAIL  # 900сек - 10мин + 1сек + tail
        with await shift_right.reload() as shift:
            tap.eq(shift.status, 'waiting', 'статус смены справа')
            tap.eq(len(shift.shift_events), 1, 'события добавлено')

            with shift.shift_events[-1] as event:
                tap.eq(event.type, 'hold_absent', 'hold_absent')
                tap.eq(event.detail['courier_shift_id'],
                       shift_left.courier_shift_id,
                       'courier_shift_id')
                tap.eq(event.detail['duration'], _duration, '~5 минут')
                tap.eq(time2time(event.detail['ends_at']),
                       shift.started_at + timedelta(seconds=_duration),
                       'ends_at')

        # смена справа №2 (слишком далеко, чтобы получать hold_absent)
        with await shift_right_2.reload() as shift:
            tap.eq(shift.status, 'waiting', 'статус смены слева')
            tap.eq(len(shift.shift_events), 0, 'события добавлено')


async def test_hold_absent_repeat(tap, dataset, now, time2time):
    with tap.plan(2, 'Проверка дублирования событий при N вызовах'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'started_after_time': 0,            # начинать надо заранее
                'timeout_processing': 1800,         # 30 мин
            }
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        _now = now()

        # смена слева задержалась на 10 мин
        shift_left = await dataset.courier_shift(
            status='processing',
            started_at=(_now - timedelta(hours=4)),
            closes_at=(_now - timedelta(minutes=10)),   # 10 мин задержки
            store=store,
            courier=courier,
            shift_events=[CourierShiftEvent({'type': 'started'})],
        )
        await dataset.order(
            courier_shift=shift_left,
            courier_id=shift_left.courier_id,
            status='processing',
            estatus='waiting',
        )
        # Подходит. Смена, идущая следом через 5 мин., после завершения этой
        shift_right = await dataset.courier_shift(
            status='waiting',
            started_at=(_now - timedelta(minutes=5)),
            closes_at=(_now + timedelta(hours=5)),
            store=store,
            courier=courier,
        )

        _duration = 1500 + HOLD_ABSENT_TAIL
        for delta in range(2):
            with tap.subtest(8, 'Повтор вызова не дублирует события') as _tap:
                # первый вызов будет с 0ым отступом.
                # второй - 1 минута, но это должна никак повлиять
                await close_courier_shifts(cluster_id=cluster.cluster_id,
                                           now_=_now + timedelta(minutes=delta))

                # смена слева не меняется
                with await shift_left.reload() as shift:
                    _tap.eq(shift.status, 'processing', 'статус смены слева')
                    _tap.eq(len(shift.shift_events), 1, 'события добавлено')

                # смена справа отмечена как "защищенная от absent"
                with await shift_right.reload() as shift:
                    _tap.eq(shift.status, 'waiting', 'статус смены справа')
                    _tap.eq(len(shift.shift_events), 1, 'события добавлено')

                    with shift.shift_events[-1] as event:
                        _tap.eq(event.type, 'hold_absent', 'hold_absent')
                        _tap.eq(event.detail['courier_shift_id'],
                                shift_left.courier_shift_id,
                                'courier_shift_id')
                        _tap.eq(event.detail['duration'], _duration, '25 минут')
                        _tap.eq(time2time(event.detail['ends_at']),
                                shift.started_at + timedelta(seconds=_duration),
                                'ends_at')


async def test_hold_absent_expired(tap, dataset, now):
    with tap.plan(3, 'Закрытие в absent смены с истекшим hold_absent'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'started_before_time': 600,  # запуск не ранее, чем за 10 минут
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        _now = now()

        # Смена слева уже завершилась
        shift_left = await dataset.courier_shift(
            status='complete',
            store=store,
            courier=courier,
        )
        # Смена, которая должна была запуститься 11 минут назад, потеряла щит
        _created = _now - timedelta(minutes=11)
        shift_right = await dataset.courier_shift(
            status='waiting',
            started_at=(_now - timedelta(minutes=11)),
            closes_at=(_now + timedelta(hours=6)),
            store=store,
            courier=courier,
            shift_events=[
                CourierShiftEvent({
                    'type': 'hold_absent',
                    'detail': {
                        'courier_shift_id': shift_left.courier_shift_id,
                        'duration': 600,      # защита на 10 минут (уже все)
                        'ends_at': _now - timedelta(seconds=60),
                    },
                    'created': _created,      # выдано 11 минут назад
                }),
            ]
        )

        await close_courier_shifts(cluster_id=cluster.cluster_id, now_=_now)

        # Смена справа закрылась в absent.
        with await shift_right.reload() as shift:
            tap.eq(shift.status, 'absent', 'статус смены справа')
            tap.eq(len(shift.shift_events), 3, '2 новых события')
            tap.eq([e.type for e in shift.shift_events],
                   ['hold_absent', 'absent', 'reissued'],
                   '2 новых события')


@pytest.mark.parametrize('started_after_time', (
    None,   # поблажек нет, опаздывать нельзя
    1799,   # не успевает на 1 сек
    1800,   # не успевает, т.к. нахлест
    # 1801  - авто запуск без hold_absent (см. test_auto_start_without_hold)
))
async def test_auto_start_with_hold(
        tap, dataset, now, time2time, job, push_events_cache,
        started_after_time,
):
    with tap.plan(9, 'Авто-старт + выдача hold_absent смене "почти не соседу"'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'timeout_processing': 1800,
                'auto_start_max_lag': 60,
                'started_after_time': started_after_time,
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        _now = now().replace(microsecond=0)

        shift_left = await dataset.courier_shift(
            status='processing',
            started_at=_now - timedelta(hours=4),
            closes_at=_now - timedelta(seconds=1800),    # пора закрыть
            store=store,
            courier=courier,
            shift_events=[CourierShiftEvent({'type': 'started'})],
        )
        await dataset.order(
            courier_shift=shift_left,
            courier_id=shift_left.courier_id,
            status='processing',
            estatus='waiting',
        )

        shift_right = await dataset.courier_shift(
            status='waiting',
            started_at=_now - timedelta(seconds=1800),  # пора запустить
            closes_at=_now + timedelta(hours=1),
            store=store,
            courier=courier,
        )

        await close_courier_shifts(cluster_id=cluster.cluster_id, now_=_now)

        # смена слева закрыта
        with await shift_left.reload() as shift:
            tap.eq(shift.status, 'complete', 'слева смена закрылась')

        await push_events_cache(shift, job_method='job_auto_start')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        # смена справа "защищена от absent" + "запущена"
        with await shift_right.reload() as shift:
            tap.eq(shift.status, 'processing', 'смена справа запустилась')
            tap.eq(len(shift.shift_events), 3, '+3 события')
            tap.eq([e['type'] for e in shift.shift_events],
                   ['hold_absent', 'started', 'processing'],
                   'добавлено 3 события')

            # hold_absent
            _duration = 1800 + HOLD_ABSENT_TAIL
            with shift.shift_events[0] as event:
                tap.eq(event.type, 'hold_absent', 'hold_absent')
                tap.eq(event.detail['courier_shift_id'],
                       shift_left.courier_shift_id,
                       'courier_shift_id')
                tap.eq(event.detail['duration'], _duration, '~5 минут')
                tap.eq(time2time(event.detail['ends_at']),
                       shift.started_at + timedelta(seconds=_duration),
                       'ends_at')


@pytest.mark.parametrize('started_after_time', (
    1801,   # авто запуск будет, НО hold_absent не успеют выдать
))
async def test_auto_start_without_hold(
        tap, dataset, now, job, push_events_cache, started_after_time,
):
    with tap.plan(4, 'Авто-старт БЕЗ hold_absent смене "почти не соседу"'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'timeout_processing': 1800,
                'auto_start_max_lag': 60,
                'started_after_time': started_after_time,
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        _now = now().replace(microsecond=0)

        shift_left = await dataset.courier_shift(
            status='processing',
            started_at=_now - timedelta(hours=4),
            closes_at=_now - timedelta(seconds=1800),   # пора закрыть
            store=store,
            courier=courier,
            shift_events=[CourierShiftEvent({'type': 'started'})],
        )
        await dataset.order(
            courier_shift=shift_left,
            courier_id=shift_left.courier_id,
            status='processing',
            estatus='waiting',
        )

        shift_right = await dataset.courier_shift(
            status='waiting',
            started_at=_now - timedelta(seconds=1800),  # пора запустить
            closes_at=_now + timedelta(hours=1),
            store=store,
            courier=courier,
        )

        await close_courier_shifts(cluster_id=cluster.cluster_id, now_=_now)

        # смена слева закрыта
        with await shift_left.reload() as shift:
            tap.eq(shift.status, 'complete', 'слева смена закрылась')

        await push_events_cache(shift, job_method='job_auto_start')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        # смена справа "защищена от absent" + "запущена"
        with await shift_right.reload() as shift:
            tap.eq(shift.status, 'processing', 'смена справа запустилась')
            tap.eq([e['type'] for e in shift.shift_events],
                   ['started', 'processing'],
                   'добавлено 2 события')


@pytest.mark.parametrize('reissue_enable', [True, False])
@pytest.mark.parametrize('auto_start_max_lag', [
    600,  # считаются соседями с самого начала
    0,    # изначально смены не соседи, но из-за задержки первой, становятся ими
])
async def test_neighbours(
        tap, dataset, now, job, push_events_cache,
        auto_start_max_lag, reissue_enable,
):
    with tap.plan(5, 'Авто-старт смены-соседа'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'timeout_processing': 1800,
                'auto_start_disable': False,
                # вкл/выкл переиздание смен
                'reissue_enable': reissue_enable,
                # соседи: все что <= X минут
                'auto_start_max_lag': auto_start_max_lag,
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)

        _now = now()

        # Смена слева еще исполняется
        shift_left = await dataset.courier_shift(
            status='processing',
            store=store,
            courier=courier,
            started_at=_now - timedelta(hours=6),
            closes_at=_now - timedelta(minutes=31),  # будет закрыта скриптом
            shift_events=[CourierShiftEvent({'type': 'started'})],
        )
        # Смена, которая должна была запуститься 25 минут назад
        _25_min_ago = _now - timedelta(minutes=25)
        shift_right = await dataset.courier_shift(
            status='waiting',
            started_at=_25_min_ago,             # между сменами 6 минут
            closes_at=_now + timedelta(hours=6),
            store=store,
            courier=courier,
            shift_events=[
                CourierShiftEvent({
                    'type': 'hold_absent',
                    'detail': {
                        'courier_shift_id': shift_left.courier_shift_id,
                        'duration': 25 * 60,      # защита на 25 минуты
                        'ends_at': _now + timedelta(seconds=60),
                    },
                    'created': _25_min_ago,       # выдано 25 минуты назад
                }),
            ]
        )

        await close_courier_shifts(cluster_id=cluster.cluster_id, now_=_now)

        await push_events_cache(shift_left, job_method='job_auto_start')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        # смена слева закрылась
        with await shift_left.reload() as shift:
            tap.eq(shift.status, 'complete', 'закрыта')
            tap.eq([e.type for e in shift.shift_events],
                   ['started', 'stopped', 'complete'],
                   '+1 новое события')

        # смена справа стартовала
        with await shift_right.reload() as shift:
            tap.eq(shift.status, 'processing', 'статус смены справа')
            tap.eq([e.type for e in shift.shift_events],
                   ['hold_absent', 'started', 'processing'],
                   '+2 новое события')


async def test_unpause_and_close(tap, dataset, now, uuid):
    with tap.plan(4, 'Слишком длительная пауза и вообще пора закрыть смену'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'started_after_time': 300,  # 5 минут
                'pause_duration': 600,      # 10 минут
            },
        )
        store = await dataset.store(cluster=cluster)

        # слишком длительная пауза + смена закончилась
        courier = await dataset.courier()
        event_started_id = uuid()
        shift = await dataset.courier_shift(
            courier_id=courier.courier_id,
            status='processing',
            started_at=(now() - timedelta(hours=4)),
            closes_at=(now() - timedelta(minutes=2)),
            store=store,
            shift_events=[
                CourierShiftEvent({
                    'shift_event_id': event_started_id,
                    'type': 'started',
                }),
                CourierShiftEvent({
                    'type': 'paused',
                    'created': now() - timedelta(minutes=10, seconds=5)
                }),
            ]
        )

        await close_courier_shifts(cluster_id=cluster.cluster_id)

        tap.ok(await shift.reload(), 'reload смены')
        tap.eq(len(shift.shift_events), 5, '+3 события')
        tap.eq([e['type'] for e in shift.shift_events],
               ['started', 'paused', 'unpaused', 'stopped', 'complete'],
               'последовательность событий верная')
        tap.eq(shift.status, 'complete', 'смена закрыта')


async def test_ignore_cluster_setup(tap, dataset, now):
    with tap.plan(3, 'Пользовательская пауза бесконечна'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'pause_duration': 60,      # 1 минута
            },
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier()
        user = await dataset.user(store=store)

        shift = await dataset.courier_shift(
            courier_id=courier.courier_id,
            status='processing',
            started_at=(now() - timedelta(hours=2)),
            closes_at=(now() + timedelta(hours=2)),
            store=store,
            shift_events=[
                CourierShiftEvent({'type': 'started'}),
                CourierShiftEvent({
                    'type': 'paused',
                    'created': now() - timedelta(minutes=10),
                    'user_id': user.user_id,
                }),
            ],
        )

        await close_courier_shifts(cluster_id=cluster.cluster_id)

        with await shift.reload():
            tap.eq(shift.status, 'processing', 'processing')
            tap.eq(len(shift.shift_events), 2, 'Событий не было')

            with shift.shift_events[-1] as event:
                tap.eq(event.type, 'paused', 'paused')


@pytest.mark.parametrize(
    'init_status,close_status,param_name',
    (
        ('request', 'closed', 'timeout_request'),
        ('waiting', 'absent', 'started_after_time'),
    )
)
async def test_close_and_reissue_shift(
        tap, dataset, now, uuid, init_status, close_status, param_name
):
    with tap.plan(30, f'Переиздание {init_status}-смены'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                param_name: 1800,           # 30 минут
                'slot_min_size': 3 * 3600   # 3 часа
            },
        )
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store=store)

        # подходит
        schedule = await dataset.courier_shift_schedule(store=store)
        shift_yes = await dataset.courier_shift(
            status=init_status,
            started_at=(now() - timedelta(minutes=32)),
            closes_at=(now() + timedelta(hours=4)),
            store=store,
            user=user,
            import_id=schedule.courier_shift_schedule_id,
            group_id=uuid(),
            guarantee=100,
            shift_events=[
                CourierShiftEvent({
                    'type': 'paused',
                    'created': now() - timedelta(minutes=20)
                }),
                CourierShiftEvent({
                    'type': 'unpaused',
                    'created': now()
                }),
            ],
            schedule=[{
                'tags': ['best'],
                'time': now() - timedelta(hours=1),
            }, {
                'tags': [],
                'time': now() + timedelta(hours=1),
            }],
        )
        # не подходит
        shift_not = await dataset.courier_shift(
            status=init_status,
            started_at=(now() - timedelta(minutes=28)),
            closes_at=(now() + timedelta(hours=4)),
            store=store,
            shift_events=[
                CourierShiftEvent({
                    'type': 'paused',
                    'created': now() - timedelta(minutes=20)
                }),
                CourierShiftEvent({
                    'type': 'unpaused',
                    'created': now()
                }),
            ]
        )

        await close_courier_shifts(cluster_id=cluster.cluster_id)

        tap.ok(await shift_yes.reload(), 'reload смены 1')
        tap.eq(shift_yes.status, close_status, 'смена закрыта')
        tap.eq(len(shift_yes.parent_ids), 0, 'родитель не появился')
        tap.eq(len(shift_yes.shift_events), 4, '2 новых события')
        tap.eq([e['type'] for e in shift_yes.shift_events],
               ['paused', 'unpaused', close_status, 'reissued'],
               'последовательность событий верная')

        tap.ok(await shift_not.reload(), 'reload смены 2')
        tap.eq(shift_not.status, init_status, 'смена не тронута')
        tap.eq(len(shift_not.shift_events), 2, 'нового события нет')

        reissued_shifts = (
            await CourierShift.list(
                by='full',
                sort=tuple(),   # отключаем сортировку
                conditions=[
                    ('parent_ids', '@>', [shift_yes.courier_shift_id]),
                ],
            )
        ).list
        tap.eq(len(reissued_shifts), 1, 'новая смена-потомок')

        # смена потомок - это копия родителя
        # + начало сдвинуто 1 час;
        # + статус request
        # + только одно request-событие в shift_events
        # + parent_ids увеличился на 1
        # + курьер теперь не задан
        # + id смены.
        reissued_shift = reissued_shifts[0]
        tap.eq(reissued_shift.import_id, shift_yes.import_id, 'import_id')
        tap.eq(reissued_shift.group_id, shift_yes.group_id, 'group_id')
        tap.eq(reissued_shift.company_id, shift_yes.company_id, 'company_id')
        tap.eq(reissued_shift.store_id, shift_yes.store_id, 'store_id')
        tap.eq(reissued_shift.cluster_id, shift_yes.cluster_id, 'cluster_id')
        tap.eq(reissued_shift.delivery_type, shift_yes.delivery_type, 'достав.')
        tap.eq(reissued_shift.closes_at, shift_yes.closes_at, 'closes_at')
        tap.eq(reissued_shift.tags, shift_yes.tags, 'tags')
        tap.eq(reissued_shift.guarantee, shift_yes.guarantee, 'guarantee')
        tap.eq(reissued_shift.placement, 'replacement', 'placement')
        tap.eq(reissued_shift.schedule, shift_yes.schedule, 'schedule')
        tap.eq(reissued_shift.user_id, None, 'переизданные без пользователя')

        # не совпадают поля
        tap.ne(reissued_shift.courier_shift_id,
               shift_yes.courier_shift_id,
               'courier_shift_id')
        tap.ne(reissued_shift.external_id, shift_yes.external_id, 'external_id')
        tap.is_ok(reissued_shift.courier_id, None, 'courier_id')
        tap.eq(reissued_shift.status, 'request', 'status')
        tap.eq(reissued_shift.started_at,
               shift_yes.started_at + timedelta(seconds=REISSUE_OFFSET),
               'started_at')
        tap.eq(len(reissued_shift.shift_events), 1, 'одно событие')
        tap.eq(reissued_shift.shift_events[0].type, 'request', 'request соб.')
        tap.eq(reissued_shift.source, 'system', 'источник создания смены')
        tap.eq(reissued_shift.parent_ids,
               shift_yes.parent_ids + [shift_yes.courier_shift_id],
               'parent_ids увеличился на 1')


async def test_multiple_reissuing(tap, dataset, now):
    with tap.plan(8, 'Многократное переиздание одной смены'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'timeout_request': 600,     # 10 минут
                'slot_min_size': 2 * 3600   # 2 часа
            },
        )
        store = await dataset.store(cluster=cluster)
        shift_yes = await dataset.courier_shift(
            status='request',
            started_at=(now() - timedelta(minutes=15)),   # duration 4.5 часа
            closes_at=(now() + timedelta(hours=4, minutes=15)),
            store=store
        )

        with tap.subtest(None, 'Переиздание смены 2 раза') as taps:
            for child_i in range(2):
                await close_courier_shifts(cluster_id=cluster.cluster_id)

                reissued_shifts = (
                    await CourierShift.list(
                        by='full',
                        sort=tuple(),   # отключаем сортировку
                        conditions=[
                            # чтобы получать последнюю переизданную
                            ('status', 'request'),
                            ('parent_ids', '@>', [shift_yes.courier_shift_id]),
                        ],
                    )
                ).list

                taps.eq(len(reissued_shifts), 1, 'количество активных смен')
                reissued_shift = reissued_shifts[0]
                taps.note(f'Смена-потомок №{child_i}'
                          f' c длительностью={reissued_shift.duration}')

                # "прошел 1 час", а смену никто не взял
                reissued_shift.started_at -= timedelta(seconds=REISSUE_OFFSET)
                reissued_shift.closes_at -= timedelta(seconds=REISSUE_OFFSET)
                await reissued_shift.save()

        # добиваем последнюю смену
        await close_courier_shifts(cluster_id=cluster.cluster_id)

        # проверяем все переизданные смены-потомки
        reissued_shifts = (
            await CourierShift.list(
                by='full',
                sort=tuple(),   # отключаем сортировку
                conditions=[
                    ('parent_ids', '@>', [shift_yes.courier_shift_id]),
                ],
            )
        ).list
        await shift_yes.reload()

        tap.eq(len(reissued_shifts), 2, 'переиздано 2 смены (3.5ч и 2.5ч)')

        reissued_shifts.sort(key=lambda x: len(x.parent_ids))
        last_reissued_shift_parents = reissued_shifts[-1].parent_ids
        reissued_shifts_ids = [s.courier_shift_id for s in reissued_shifts]

        tap.eq(last_reissued_shift_parents,
               [shift_yes.courier_shift_id] + reissued_shifts_ids[:-1],
               'порядок родителей верный')

        tap.ok(all(s.status == 'closed' for s in reissued_shifts),
               'все смены закрыты')

        with tap.subtest(None, 'длительность всех смен верная') as taps:
            for h, s in enumerate(reissued_shifts, 1):
                taps.eq(s.duration,
                        shift_yes.duration - REISSUE_OFFSET * h,
                        f'смена={h}, длительность={s.duration}')

        with tap.subtest(None, 'у родителей есть событие reissue') as taps:
            children = []
            for s in [shift_yes] + reissued_shifts[:-1]:
                events = [e for e in s.shift_events if e.type == 'reissued']
                taps.ok(len(events) == 1,
                        'только по одному reissued событию')
                children.append(events[0].detail['courier_shift_id'])

            tap.eq(reissued_shifts_ids,
                   children,
                   'порядок детей в событиях верный')

        last_reissued_events = reissued_shifts[-1].shift_events
        tap.ok(not [e for e in last_reissued_events if e.type == 'reissued'],
               'reissued у последней переизданной смены отсутствует')


async def test_stability(tap, dataset, now):
    with tap.plan(9, 'Проверяем, что не будет двойного переиздания'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'timeout_request': 1800,    # 30 минут
                'slot_min_size': 3 * 3600   # 3 часа
            },
        )
        store = await dataset.store(cluster=cluster)

        # будет переиздана
        shift_parent = await dataset.courier_shift(
            status='request',
            started_at=(now() - timedelta(minutes=32)),
            closes_at=(now() + timedelta(hours=4)),
            store=store,
        )
        # созданный потомок, при живом родителе
        shift_child = await dataset.courier_shift(
            status='request',
            started_at=(now() + timedelta(minutes=28)),
            closes_at=(now() + timedelta(hours=4)),
            store=store,
            parent_ids=[shift_parent.courier_shift_id],
        )

        await close_courier_shifts(cluster_id=cluster.cluster_id)

        tap.ok(await shift_parent.reload(), 'reload смены 1')
        tap.eq(shift_parent.status, 'closed', 'смена закрыта')
        tap.eq(len(shift_parent.parent_ids), 0, 'родитель не появился')
        tap.eq(len(shift_parent.shift_events), 2, '2 новых события')
        tap.eq([e['type'] for e in shift_parent.shift_events],
               ['closed', 'reissued'],
               'последовательность событий верная')

        tap.ok(await shift_child.reload(), 'reload смены 2')
        tap.eq(shift_child.status, 'request', 'смена не тронута')
        tap.eq(len(shift_child.shift_events), 0, 'нового события нет')

        reissued_shifts = (
            await CourierShift.list(
                by='full',
                sort=tuple(),   # отключаем сортировку
                conditions=[
                    ('parent_ids', '@>', [shift_parent.courier_shift_id]),
                ],
            )
        ).list
        tap.eq(len(reissued_shifts), 1, 'нет двойного переиздания')


@pytest.mark.parametrize(
    'parent_ids', (
        [],
        ['bla-bla-bla-father_in_a_house'],
    )
)
async def test_parent_ids(tap, dataset, now, parent_ids):
    with tap.plan(5, f'Проверяем, вариант "parent_ids=={parent_ids}"'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'timeout_request': 1800,    # 30 минут
                'slot_min_size': 3 * 3600   # 3 часа
            },
        )
        store = await dataset.store(cluster=cluster)

        # будет переиздана
        courier = await dataset.courier(cluster=cluster)
        shift_parent = await dataset.courier_shift(
            courier_id=courier.courier_id,
            status='request',
            started_at=(now() - timedelta(minutes=32)),
            closes_at=(now() + timedelta(hours=4)),
            store=store,
            parent_ids=parent_ids
        )

        await close_courier_shifts(cluster_id=cluster.cluster_id)

        tap.ok(await shift_parent.reload(), 'reload смены 1')
        tap.eq(shift_parent.status, 'closed', 'смена закрыта')
        tap.eq(len(shift_parent.shift_events), 2, '2 новых события')
        tap.eq([e['type'] for e in shift_parent.shift_events],
               ['closed', 'reissued'],
               'последовательность событий верная')

        reissued_shifts = (
            await CourierShift.list(
                by='full',
                sort=tuple(),
                conditions=[
                    ('parent_ids', '@>', [shift_parent.courier_shift_id]),
                ],
            )
        ).list
        tap.eq(len(reissued_shifts), 1, 'смена-потомок не дублируется')


@pytest.mark.parametrize(
    ['delta', 'should_close'],
    [
        # чекин пришёл позже
        (timedelta(seconds=10), True),
        # чекин пришёл немного раньше
        (-DEFAULT_EVENT_LAG + timedelta(seconds=10), True),
        (-DEFAULT_EVENT_LAG, True),
        # чекин пришёл сильно раньше
        (-DEFAULT_EVENT_LAG - timedelta(seconds=10), False),
    ]
)
async def test_statuses_race(tap, dataset, now, time_mock, delta, should_close):
    with tap.plan(2, 'гонка между статусами доставки заказа и чекина'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'timeout_processing': 30 * 60
            }
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)
        shift = await dataset.courier_shift(
            courier_id=courier.courier_id,
            status='processing',
            started_at=(now() - timedelta(hours=4)),
            closes_at=(now() - timedelta(minutes=5)),
            store=store,
            shift_events=[CourierShiftEvent({'type': 'started'})],
        )

        order = await dataset.order(
            courier_shift=shift,
            courier_id=courier.courier_id,
            status='processing',
            estatus='waiting',
        )

        time_mock.sleep(minutes=5)

        courier.checkin_time = now() + delta
        courier.last_order_time = now()
        await courier.save()

        order.status = 'complete'
        order.estatus = 'done'
        await order.save()

        time_mock.sleep(minutes=3)

        await close_courier_shifts(cluster_id=cluster.cluster_id)

        await shift.reload()
        if should_close:
            tap.eq(shift.status, 'complete', 'shift closed')
            tap.eq(shift.shift_events[-1].type, 'complete', 'shift event ok')
        else:
            tap.eq(shift.status, 'processing', 'shift closed')
            tap.eq(shift.shift_events[-1].type, 'started', 'shift event ok')
