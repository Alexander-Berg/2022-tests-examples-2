# pylint: disable=unused-argument

import json
import asyncio
from datetime import timedelta

from aiohttp import web

from scripts.cron import close_courier_shifts_by_candidates as script
from stall.client.candidates import client
from stall.model.courier_shift import CourierShiftEvent


# pylint: disable=too-many-locals
async def test_common(
        tap, dataset, ext_api, uuid, time_mock, now, push_events_cache,
):
    with tap.plan(22, 'закрываем смену спустя 10 секунд после начала ФК'):
        cluster = await dataset.cluster(
            geoarea=uuid(),
            courier_shift_setup={
                'candidates_equipment_threshold': 10,
            }
        )
        store = await dataset.store(cluster=cluster)

        courier_1, courier_2, courier_3 = await asyncio.gather(
            dataset.courier(cluster=cluster),
            dataset.courier(cluster=cluster),
            dataset.courier(cluster=cluster),
        )

        shift_1, shift_2, shift_3 = await asyncio.gather(
            dataset.courier_shift(
                store=store,
                courier=courier_1,
                status='processing',
                started_at=(now() - timedelta(hours=4)),
                closes_at=(now() + timedelta(minutes=2)),
                shift_events=[CourierShiftEvent({'type': 'started'})],
            ),
            dataset.courier_shift(
                store=store,
                courier=courier_1,
                status='waiting',
            ),
            dataset.courier_shift(
                store=store,
                courier=courier_2,
                status='processing',
                started_at=(now() - timedelta(hours=4)),
                closes_at=(now() + timedelta(minutes=2)),
                shift_events=[CourierShiftEvent({'type': 'started'})],
            )
        )

        # pylint: disable=unused-argument
        async def handle(request):
            return {
                'drivers': [{
                    'dbid': courier_1.vars['park_id'],
                    'uuid': courier_1.vars['uuid'],
                    'is_satisfied': False,
                    'reasons': {
                        'partners/qc_block': []
                    },
                    'details': {
                        'partners/qc_block': ['eda_equipment']
                    },
                }, {
                    'dbid': courier_2.vars['park_id'],
                    'uuid': courier_2.vars['uuid'],
                    'is_satisfied': False,
                    'reasons': {
                        'partners/qc_block': []
                    },
                    'details': {
                        'partners/qc_block': ['another_block']
                    },
                }, {
                    'dbid': courier_3.vars['park_id'],
                    'uuid': courier_3.vars['uuid'],
                    'is_satisfied': False,
                    'reasons': {
                        'partners/qc_block': []
                    },
                    'details': {
                        'partners/qc_block': ['eda_equipment']
                    },
                }]
            }

        async def _reload_all():
            await asyncio.gather(
                shift_1.reload(),
                shift_2.reload(),
                shift_3.reload(),
                courier_1.reload(),
                courier_2.reload(),
                courier_3.reload(),
            )

        async with await ext_api(client, handle):
            await script.process_cluster(cluster)

        appeared_at = now()

        await _reload_all()

        tap.eq(shift_1.status, 'processing', 'shift_1 is still processing')
        with shift_1.event_qc('eda_equipment') as event:
            tap.eq(event.type, 'qc_started', 'shift_1 latest qc started')
            tap.eq(event.created, appeared_at, 'shift_1 appeared now')

        tap.eq(shift_2.status, 'waiting', 'shift_2 is still waiting')
        tap.ok(not shift_2.event_qc('eda_equipment'), 'shift_2 qc none')

        tap.eq(shift_3.status, 'processing', 'shift_3 is still processing')
        tap.ok(not shift_3.event_qc('eda_equipment'), 'shift_3 qc none')

        time_mock.sleep(seconds=5)

        log_sent_tasks = []

        async def handle_stq(req):
            # pylint: disable=unused-argument
            log_sent_tasks.extend((await req.json()).get('tasks', []))
            return web.Response(
                status=200,
                text=json.dumps({
                    'tasks': [{
                        'task_id': uuid(),
                        'add_result': {
                            'code': 200,
                        },
                    }]
                }),
                content_type='application/json'
            )

        async with await ext_api('stq', handle_stq):
            await push_events_cache(shift_1, event_type='stq')

        tap.eq(len(log_sent_tasks), 2, 'Запрос к stq ушел')
        tap.eq(log_sent_tasks[0]['kwargs'], {
            'performer_id': courier_1.external_id,
            'title': {'key': 'photocontrol_push_title'},
            'text': {'key': 'photocontrol_push_body'},
        }, 'kwargs')

        async with await ext_api(client, handle):
            await script.process_cluster(cluster)

        await _reload_all()

        tap.eq(shift_1.status, 'processing', 'shift_1 is still processing')
        with shift_1.event_qc('eda_equipment') as event:
            tap.eq(event.type, 'qc_started', 'shift_1 latest qc started')
            tap.eq(event.created, appeared_at, 'shift_1 appeared then')

        tap.eq(shift_2.status, 'waiting', 'shift_2 is still waiting')
        tap.ok(not shift_2.event_qc('eda_equipment'), 'shift_2 qc none')

        tap.eq(shift_3.status, 'processing', 'shift_3 is still processing')
        tap.ok(not shift_3.event_qc('eda_equipment'), 'shift_3 qc none')

        time_mock.sleep(seconds=5)

        async with await ext_api(client, handle):
            await script.process_cluster(cluster)

        await _reload_all()

        tap.eq(shift_1.status, 'complete', 'shift_1 is complete')
        tap.ok(not shift_1.event_qc('eda_equipment'), 'shift_1 qc none')

        tap.eq(shift_2.status, 'waiting', 'shift_2 is still waiting')
        tap.ok(not shift_2.event_qc('eda_equipment'), 'shift_2 qc none')

        tap.eq(shift_3.status, 'processing', 'shift_3 is still processing')
        tap.ok(not shift_3.event_qc('eda_equipment'), 'shift_3 qc none')


async def test_order_processing(
        tap, dataset, ext_api, uuid, time_mock, now,
):
    with tap.plan(5, 'не закрываем если курьер на заказе'):
        cluster = await dataset.cluster(
            geoarea=uuid(),
            courier_shift_setup={
                'candidates_equipment_threshold': 10,
            }
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)
        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            started_at=(now() - timedelta(hours=4)),
            closes_at=(now() + timedelta(minutes=2)),
            shift_events=[CourierShiftEvent({'type': 'started'})],
        )
        order = await dataset.order(
            store=store,
            courier_shift=shift,
            status='processing',
        )

        # pylint: disable=unused-argument
        async def handle(request):
            return {
                'drivers': [{
                    'dbid': courier.vars['park_id'],
                    'uuid': courier.vars['uuid'],
                    'is_satisfied': False,
                    'reasons': {
                        'partners/qc_block': []
                    },
                    'details': {
                        'partners/qc_block': ['eda_equipment']
                    },
                }]
            }

        async with await ext_api(client, handle):
            await script.process_cluster(cluster)

        appeared_at = now()

        time_mock.sleep(seconds=15)

        async with await ext_api(client, handle):
            await script.process_cluster(cluster)

        await shift.reload()
        tap.eq(shift.status, 'processing', 'shift is still processing')
        with shift.event_qc('eda_equipment') as event:
            tap.eq(event.type, 'qc_started', 'shift_1 latest qc started')
            tap.eq(event.created, appeared_at, 'shift_1 appeared then')

        order.status = 'complete'
        await order.save()

        async with await ext_api(client, handle):
            await script.process_cluster(cluster)

        await shift.reload()
        tap.eq(shift.status, 'complete', 'shift is complete now')
        tap.ok(not shift.event_qc('eda_equipment'), 'shift qc none')


async def test_start_on_order(
        tap, dataset, ext_api, uuid, time_mock, now,
):
    with tap.plan(5, 'откладываем закрытие если курьер был на заказе'):
        cluster = await dataset.cluster(
            geoarea=uuid(),
            courier_shift_setup={
                'candidates_equipment_threshold': 10,
            }
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)
        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            started_at=(now() - timedelta(hours=4)),
            closes_at=(now() + timedelta(minutes=2)),
            shift_events=[CourierShiftEvent({'type': 'started'})],
        )
        order = await dataset.order(
            store=store,
            courier_shift=shift,
            status='processing',
        )

        # pylint: disable=unused-argument
        async def handle(request):
            return {
                'drivers': [{
                    'dbid': courier.vars['park_id'],
                    'uuid': courier.vars['uuid'],
                    'is_satisfied': False,
                    'reasons': {
                        'partners/qc_block': []
                    },
                    'details': {
                        'partners/qc_block': ['eda_equipment']
                    },
                }]
            }

        async with await ext_api(client, handle):
            await script.process_cluster(cluster)

        appeared_at = now()

        time_mock.sleep(seconds=4)

        order.status = 'complete'
        await order.save()
        courier.last_order_time = now()
        await courier.save()

        time_mock.sleep(seconds=1)

        courier.checkin_time = now()
        courier.state.checkin_time = now()
        courier.rehashed(state=True)
        await courier.save()

        # через 5 секунд будет 10 секунд спустя начала отсчёта
        # но будет лишь 5 секунд спустя доставки заказа
        time_mock.sleep(seconds=5)

        async with await ext_api(client, handle):
            await script.process_cluster(cluster)

        await shift.reload()
        tap.eq(shift.status, 'processing', 'shift is still processing')
        with shift.event_qc('eda_equipment') as event:
            tap.eq(event.type, 'qc_started', 'shift_1 latest qc started')
            tap.eq(event.created, appeared_at, 'shift_1 appeared then')

        # через 5 секунд будет 10 секунд спустя доставки заказа
        time_mock.sleep(seconds=5)

        async with await ext_api(client, handle):
            await script.process_cluster(cluster)

        await shift.reload()
        tap.eq(shift.status, 'complete', 'shift is complete now')
        tap.ok(not shift.event_qc('eda_equipment'), 'shift qc none')


async def test_pauses(
        tap, dataset, ext_api, uuid, time_mock, now,
):
    with tap.plan(5, 'учитываем время, которое курьер находился на паузе'):
        cluster = await dataset.cluster(
            geoarea=uuid(),
            courier_shift_setup={
                'candidates_equipment_threshold': 10,
            }
        )
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)
        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            started_at=(now() - timedelta(hours=4)),
            closes_at=(now() + timedelta(minutes=2)),
            shift_events=[CourierShiftEvent({'type': 'started'})],
        )

        # pylint: disable=unused-argument
        async def handle(request):
            return {
                'drivers': [{
                    'dbid': courier.vars['park_id'],
                    'uuid': courier.vars['uuid'],
                    'is_satisfied': False,
                    'reasons': {
                        'partners/qc_block': []
                    },
                    'details': {
                        'partners/qc_block': ['eda_equipment']
                    },
                }]
            }

        async with await ext_api(client, handle):
            await script.process_cluster(cluster)

        appeared_at = now()

        time_mock.sleep(seconds=2)

        # создадим две паузы подряд по секунде
        for _ in range(2):
            shift.shift_events = [{'type': 'paused',
                                   'created': time_mock.now()}]
            await shift.save()

            time_mock.sleep(seconds=1)

            shift.shift_events = [{'type': 'unpaused',
                                   'created': time_mock.now()}]
            await shift.save()

        # будет 10 секунд, но пауза длилась 2 секунды
        time_mock.sleep(seconds=6)

        async with await ext_api(client, handle):
            await script.process_cluster(cluster)

        await shift.reload()
        tap.eq(shift.status, 'processing', 'shift is still processing')
        with shift.event_qc('eda_equipment') as event:
            tap.eq(event.type, 'qc_started', 'shift_1 latest qc started')
            tap.eq(event.created, appeared_at, 'shift_1 appeared then')

        # будет 10 секунд учитывая паузу 2 секунды
        time_mock.sleep(seconds=2)

        async with await ext_api(client, handle):
            await script.process_cluster(cluster)

        await shift.reload()
        tap.eq(shift.status, 'complete', 'shift is complete now')
        tap.ok(not shift.event_qc('eda_equipment'), 'shift qc none')


async def test_check_reset(
        tap, dataset, ext_api, uuid, time_mock, now,
):
    with tap.plan(4, 'прохождение контроля'):
        cluster = await dataset.cluster(geoarea=uuid())
        store = await dataset.store(cluster=cluster)
        courier = await dataset.courier(cluster=cluster)
        shift = await dataset.courier_shift(
            store=store,
            courier=courier,
            status='processing',
            started_at=(now() - timedelta(hours=4)),
            closes_at=(now() + timedelta(minutes=2)),
            shift_events=[CourierShiftEvent({'type': 'started'})],
        )

        responses_iter = iter([
            [{
                'dbid': courier.vars['park_id'],
                'uuid': courier.vars['uuid'],
                'is_satisfied': False,
                'reasons': {
                    'partners/qc_block': []
                },
                'details': {
                    'partners/qc_block': ['eda_equipment']
                },
            }],
            [{
                'dbid': courier.vars['park_id'],
                'uuid': courier.vars['uuid'],
                'is_satisfied': True,
            }]
        ])

        # pylint: disable=unused-argument
        async def handle(request):
            return {
                'drivers': next(responses_iter, [])
            }

        async with await ext_api(client, handle):
            await script.process_cluster(cluster)

        await shift.reload()
        with shift.event_qc('eda_equipment') as event:
            tap.eq(event.type, 'qc_started', 'shift qc started')
            tap.eq(event.created, now(), 'shift qc started now')

        async with await ext_api(client, handle):
            await script.process_cluster(cluster)

        await shift.reload()
        with shift.event_qc('eda_equipment') as event:
            tap.eq(event.type, 'qc_done', 'shift qc done')
            tap.eq(event.created, now(), 'shift qc done now')
