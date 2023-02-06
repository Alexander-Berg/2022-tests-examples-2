# pylint: disable=too-many-locals,too-many-statements

import asyncio
import datetime

import pytest

from libstall.util import time2iso, time2time
from scripts.cron import couriers_eda_equipment_exam as script
from stall.client.qc_exam import client as qc_client, QcExamError


async def test_first_start(
        tap, dataset, now, time_mock,
        ext_api, job, push_events_cache,
):
    with tap.plan(20, 'первый запуск ФК'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'equipment_qc_exam_period': 60,
            }
        )
        company = await dataset.company()
        store = await dataset.store(company=company)

        courier_1, courier_2, courier_3 = await asyncio.gather(
            dataset.courier(cluster=cluster, company=company),
            dataset.courier(cluster=cluster, company=company),
            dataset.courier(cluster=cluster, company=company),
        )

        async def reload_couriers():
            await asyncio.gather(
                courier_1.reload(),
                courier_2.reload(),
                courier_3.reload(),
            )

        await asyncio.gather(
            dataset.courier_shift(
                cluster=cluster,
                company=company,
                store=store,
                courier_id=courier_1.courier_id,
                status='processing',
                started_at=now() - datetime.timedelta(hours=1),
                closes_at=now() + datetime.timedelta(hours=3),
            ),
            dataset.courier_shift(
                cluster=cluster,
                company=company,
                store=store,
                courier_id=courier_1.courier_id,
                status='waiting',
                started_at=now() + datetime.timedelta(hours=1),
                closes_at=now() + datetime.timedelta(hours=3),
            ),
            dataset.courier_shift(
                cluster=cluster,
                company=company,
                store=store,
                courier_id=courier_2.courier_id,
                status='waiting',
                started_at=now() + datetime.timedelta(hours=1),
                closes_at=now() + datetime.timedelta(hours=3),
            ),
        )

        calls = []

        async def handle(request):
            calls.append(await request.json())
            return {'code': 'OK'}

        empty_exams = {
            'eda_equipment': {
                'started_at': None,
                'planned_at': None,
            },
        }

        tap.eq(courier_1.qc_exams, empty_exams, 'courier_1 exams empty')
        tap.eq(courier_2.qc_exams, empty_exams, 'courier_2 exams empty')
        tap.eq(courier_3.qc_exams, empty_exams, 'courier_3 exams empty')

        await script.process_cluster(cluster)

        await reload_couriers()
        tap.ok(courier_1.qc_exams['eda_equipment']['started_at'] is None,
               'first start does not set started_at')
        tap.ok(courier_1.qc_exams['eda_equipment']['planned_at'] is not None,
               'first start sets planned_at')
        tap.eq(courier_2.qc_exams, empty_exams, 'courier_2 exams empty')
        tap.eq(courier_3.qc_exams, empty_exams, 'courier_3 exams empty')

        await push_events_cache(courier_1, 'job_start_qc_exam')
        async with await ext_api(qc_client, handle):
            tap.ok(not await job.take(), 'courier has no tasks')

        time_mock.set(courier_1.qc_exams['eda_equipment']['planned_at'])
        await script.process_cluster(cluster)
        started_at = time2iso(time_mock.now())

        await reload_couriers()
        tap.eq(courier_1.qc_exams['eda_equipment']['started_at'], started_at,
               'exam started now')
        tap.ok(courier_1.qc_exams['eda_equipment']['planned_at'] is None,
               'planned_at reset')
        tap.eq(courier_2.qc_exams, empty_exams, 'courier_2 exams empty')
        tap.eq(courier_3.qc_exams, empty_exams, 'courier_3 exams empty')

        await push_events_cache(courier_1, 'job_start_qc_exam')
        async with await ext_api(qc_client, handle):
            tap.ok(await job.call(await job.take()), 'courier task done')
            tap.eq(len(calls), 1, 'one request to qc_exams service')
            tap.eq(calls[-1]['entity_id'], courier_1.external_id,
                   'qc_exam started exam for courier_1')
            calls.clear()

        time_mock.sleep(seconds=100)
        await script.process_cluster(cluster)

        await reload_couriers()
        tap.eq(courier_1.qc_exams['eda_equipment']['started_at'], started_at,
               'no more starts during current shift')
        tap.ok(courier_1.qc_exams['eda_equipment']['planned_at'] is None,
               'no more plans during current shift')
        tap.eq(courier_2.qc_exams, empty_exams, 'courier_2 exams empty')
        tap.eq(courier_3.qc_exams, empty_exams, 'courier_3 exams empty')

        await push_events_cache(courier_1, 'job_start_qc_exam')
        async with await ext_api(qc_client, handle):
            tap.ok(not await job.take(), 'courier has no tasks')


async def test_next_start(
        tap, dataset, now, time_mock,
        ext_api, job, push_events_cache,
):
    with tap.plan(10, 'следующий запуск ФК'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'equipment_qc_exam_period':
                    datetime.timedelta(days=1).total_seconds(),
            }
        )
        company = await dataset.company()
        store = await dataset.store(company=company)

        started_at = time2iso(
            # Прошлый запуск чуть меньше дня назад
            now() - datetime.timedelta(days=1) + datetime.timedelta(hours=1)
        )
        courier = await dataset.courier(
            cluster=cluster,
            company=company,
            qc_exams={
                'eda_equipment': {
                    'started_at': started_at,
                    'planned_at': None,
                }
            }
        )

        # В рамках этой смены запуска не будет
        # Так как она начинается меньше чем
        # через день после предыдущего запуска
        shift_1 = await dataset.courier_shift(
            cluster=cluster,
            company=company,
            store=store,
            courier_id=courier.courier_id,
            status='processing',
            started_at=now() - datetime.timedelta(minutes=1),
            closes_at=now() + datetime.timedelta(hours=4),
        )
        # В рамках этой смены запуск уже будет
        shift_2 = await dataset.courier_shift(
            cluster=cluster,
            company=company,
            store=store,
            courier_id=courier.courier_id,
            status='waiting',
            started_at=now() + datetime.timedelta(hours=4),
            closes_at=now() + datetime.timedelta(hours=8),
        )

        calls = []

        async def handle(request):
            calls.append(await request.json())
            return {'code': 'OK'}

        await script.process_cluster(cluster)

        await courier.reload()
        tap.eq(courier.qc_exams['eda_equipment']['started_at'], started_at,
               'exam not started during current shift')
        tap.ok(courier.qc_exams['eda_equipment']['planned_at'] is None,
               'exam not even planned')

        await push_events_cache(courier, 'job_start_qc_exam')
        async with await ext_api(qc_client, handle):
            tap.ok(not await job.take(), 'courier has no tasks')

        time_mock.set(shift_2.started_at)
        shift_1.status = 'complete'
        await shift_1.save()
        shift_2.status = 'processing'
        await shift_2.save()

        await script.process_cluster(cluster)

        await courier.reload()
        tap.eq(courier.qc_exams['eda_equipment']['started_at'], started_at,
               'exam not started yet')
        tap.ok(courier.qc_exams['eda_equipment']['planned_at'] is not None,
               'exam planned')

        time_mock.set(courier.qc_exams['eda_equipment']['planned_at'])
        await script.process_cluster(cluster)
        started_at = time2iso(time_mock.now())

        await courier.reload()
        tap.eq(courier.qc_exams['eda_equipment']['started_at'], started_at,
               'exam started now')
        tap.ok(courier.qc_exams['eda_equipment']['planned_at'] is None,
               'planned_at reset')

        await push_events_cache(courier, 'job_start_qc_exam')
        async with await ext_api(qc_client, handle):
            tap.ok(await job.call(await job.take()), 'courier task done')
            tap.eq(len(calls), 1, 'one request to qc_exams service')
            tap.eq(calls[-1]['entity_id'], courier.external_id,
                   'qc_exam started exam for courier')
            calls.clear()


@pytest.mark.parametrize(
    ['from_', 'to_', 'expect_interval'],
    [
        (None, None, (0, 0)),
        (None, 20, (0, 20)),
        (10, None, (10, 10)),
        (10, 20, (10, 20)),
        (20, 10, (10, 20)),
    ]
)
async def test_random_offset(
        tap, dataset, now, time_mock,
        from_, to_, expect_interval,
):
    with tap.plan(3, 'случайный выбор времени запуска'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'equipment_qc_exam_period':
                    datetime.timedelta(days=1).total_seconds(),
                'equipment_qc_exam_random_from': from_,
                'equipment_qc_exam_random_to': to_,
            }
        )
        company = await dataset.company()
        store = await dataset.store(company=company)

        started_at = time2iso(
            time_mock.now() - datetime.timedelta(days=1, hours=1)
        )
        courier = await dataset.courier(
            cluster=cluster,
            company=company,
            qc_exams={
                'eda_equipment': {
                    'started_at': started_at,
                    'planned_at': None,
                }
            }
        )
        shift = await dataset.courier_shift(
            cluster=cluster,
            company=company,
            store=store,
            courier_id=courier.courier_id,
            status='processing',
            started_at=now() - datetime.timedelta(minutes=1),
            closes_at=now() + datetime.timedelta(hours=4),
        )

        await script.process_cluster(cluster)

        await courier.reload()
        tap.eq(courier.qc_exams['eda_equipment']['started_at'], started_at,
               'started then')
        tap.ok(courier.qc_exams['eda_equipment']['planned_at'] is not None,
               'next start planned')

        tap.ok(
            shift.started_at + datetime.timedelta(seconds=expect_interval[0])
            <= time2time(courier.qc_exams['eda_equipment']['planned_at']) <=
            shift.started_at + datetime.timedelta(seconds=expect_interval[1]),
            'planned between from_ and to_'
        )


async def test_start_after_complete(
        tap, dataset, now, time_mock,
):
    with tap.plan(5, 'перепланируем если пропустили запуск'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'equipment_qc_exam_period':
                    datetime.timedelta(days=1).total_seconds(),
            }
        )
        company = await dataset.company()
        store = await dataset.store(company=company)

        started_at = time2iso(
            time_mock.now() - datetime.timedelta(days=1, hours=1)
        )
        courier = await dataset.courier(
            cluster=cluster,
            company=company,
            qc_exams={
                'eda_equipment': {
                    'started_at': started_at,
                    'planned_at': None,
                }
            }
        )
        shift_1 = await dataset.courier_shift(
            cluster=cluster,
            company=company,
            store=store,
            courier_id=courier.courier_id,
            status='processing',
            started_at=now() - datetime.timedelta(minutes=1),
            closes_at=now() + datetime.timedelta(hours=4),
        )
        shift_2 = await dataset.courier_shift(
            cluster=cluster,
            company=company,
            store=store,
            courier_id=courier.courier_id,
            status='waiting',
            started_at=now() + datetime.timedelta(hours=6),
            closes_at=now() + datetime.timedelta(hours=10),
        )

        await script.process_cluster(cluster)

        await courier.reload()
        tap.eq(courier.qc_exams['eda_equipment']['started_at'], started_at,
               'started then')
        tap.ok(courier.qc_exams['eda_equipment']['planned_at'] is not None,
               'next start planned')

        old_plan_at = courier.qc_exams['eda_equipment']['planned_at']

        time_mock.set(shift_2.started_at)
        shift_1.status = 'complete'
        await shift_1.save()
        shift_2.status = 'processing'
        await shift_2.save()

        await script.process_cluster(cluster)

        await courier.reload()
        tap.eq(courier.qc_exams['eda_equipment']['started_at'], started_at,
               'started then')
        tap.ok(courier.qc_exams['eda_equipment']['planned_at'] is not None,
               'next start planned')

        tap.ok(
            courier.qc_exams['eda_equipment']['planned_at'] > old_plan_at,
            'next start rescheduled'
        )


async def test_wrong_courier(
        tap, dataset, now, time_mock,
        ext_api, job, push_events_cache,
):
    with tap.plan(2, 'таск не ретраится для некорректного курьера'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'equipment_qc_exam_period': 60,
            }
        )
        company = await dataset.company()
        store = await dataset.store(company=company)
        courier = await dataset.courier(cluster=cluster, company=company)

        await dataset.courier_shift(
            cluster=cluster,
            company=company,
            store=store,
            courier_id=courier.courier_id,
            status='processing',
            started_at=now() - datetime.timedelta(hours=1),
            closes_at=now() + datetime.timedelta(hours=3),
        )

        # pylint: disable=unused-argument
        async def handle(request):
            return 400, {
                'code': 'EXAM_IS_NOT_ENABLED',
                'message': '__error_message__',
            }

        await script.process_cluster(cluster)

        await courier.reload()
        time_mock.set(courier.qc_exams['eda_equipment']['planned_at'])

        await script.process_cluster(cluster)
        started_at = time2iso(time_mock.now())

        await courier.reload()
        tap.eq(courier.qc_exams['eda_equipment']['started_at'], started_at,
               'exam started now')

        await push_events_cache(courier, 'job_start_qc_exam')
        async with await ext_api(qc_client, handle):
            tap.ok(await job.call(await job.take()), 'courier task done')


async def test_client_fail(
        tap, dataset, now, time_mock,
        ext_api, job, push_events_cache,
):
    with tap.plan(2, 'таск ретраится при лежащем сервисе'):
        cluster = await dataset.cluster(
            courier_shift_setup={
                'equipment_qc_exam_period': 60,
            }
        )
        company = await dataset.company()
        store = await dataset.store(company=company)
        courier = await dataset.courier(cluster=cluster, company=company)

        await dataset.courier_shift(
            cluster=cluster,
            company=company,
            store=store,
            courier_id=courier.courier_id,
            status='processing',
            started_at=now() - datetime.timedelta(hours=1),
            closes_at=now() + datetime.timedelta(hours=3),
        )

        # pylint: disable=unused-argument
        async def handle(request):
            return 500, {'code': 'INTERNAL_ERROR'}

        await script.process_cluster(cluster)

        await courier.reload()
        time_mock.set(courier.qc_exams['eda_equipment']['planned_at'])

        await script.process_cluster(cluster)
        started_at = time2iso(time_mock.now())

        await courier.reload()
        tap.eq(courier.qc_exams['eda_equipment']['started_at'], started_at,
               'exam started now')

        await push_events_cache(courier, 'job_start_qc_exam')
        async with await ext_api(qc_client, handle):
            with tap.raises(QcExamError):
                await job.call(await job.take())
