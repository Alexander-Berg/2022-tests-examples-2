# pylint: disable=unused-argument,protected-access,too-many-locals

import pytest

from scripts.couriers_eats import CouriersEatsDaemon


@pytest.mark.parametrize(
    'work_status', ['blocked', 'candidate',  'ill', 'deactivated', 'inactive'],
)
async def test_block(
        tap, dataset, ext_api, unique_int, work_status, push_events_cache, job
):
    with tap.plan(13, 'Установка блокировки курьера'):
        eda_id = unique_int()

        cluster = await dataset.cluster()
        courier = await dataset.courier(
            cluster=cluster,
            vars={'external_ids': {'eats': eda_id}},
        )
        shift = await dataset.courier_shift(
            cluster=cluster,
            courier=courier,
            status='waiting',
        )

        lsn = courier.lsn

        async def handler(request):
            tap.passed('Ручка вызвана')

            body = {
                "couriers": [
                    {
                        "id": str(eda_id),
                        "first_name": "Новый сотрудник 2",
                        "middle_name": "Курьерович",
                        "last_name": "Каменщиков",
                        "phone_number": "198b09b397ea41c7a42862b9a39beaf8",
                        "project_type": "lavka",
                        "work_status": str(work_status),
                        "work_region": {
                            "id": 1,
                            "name": "Москва"
                        },
                        "billing_type": "courier_service",
                        "courier_service_id": 271,
                        "is_hard_of_hearing": False,
                        "is_picker": False,
                        "is_dedicated_picker": False,
                        "is_storekeeper": False,
                        "comment": "adssda",
                        "work_status_updated_at": "2021-07-20T18:06:41+03:00",
                        "updated_at": "2021-11-23T12:56:53+03:00"
                    }
                ]
            }
            return 200, body

        async with await ext_api('eda_core_couriers', handler):
            daemon = CouriersEatsDaemon()
            tap.ok(daemon, 'Демон создан')

            tap.ok(await daemon._process(), 'Пачка обработана')
            daemon.shutdown()

        with await courier.reload():
            tap.eq(len(courier.blocks), 1, 'Блокировка добавлена')
            tap.eq(courier.blocks[0].source, 'eda', 'eda')
            tap.eq(courier.blocks[0].reason, work_status, 'reason')

            tap.ok(courier.lsn > lsn, 'Обновление прошло в базе')

        await push_events_cache(courier, job_method='job_courier_cancel_all')
        task = await job.take()
        tap.ok(task, 'задача поставлена')
        tap.ok(task.data['courier_id'], courier.courier_id, 'courier_id')
        tap.ok(await job.call(task), 'Задание выполнено')

        with await shift.reload() as shift:
            tap.eq(shift.status, 'cancelled', 'отменена')
            with shift.shift_events[-2] as event:
                tap.eq(event.detail['reason'], work_status, 'причина верная')
                tap.eq(event.detail['source'], 'eda', 'источник верный')


@pytest.mark.parametrize(
    'work_status', ['active', 'lost', 'on_vacation'],
)
async def test_unblock(
        tap, dataset, ext_api, unique_int, work_status, push_events_cache, job
):
    with tap.plan(6, 'Снятие блокировки курьера'):
        eda_id = unique_int()

        courier = await dataset.courier(
            vars = {'external_ids': {'eats': eda_id}},
            blocks = [{'source': 'eda', 'reason': 'blocked'}],
        )

        lsn = courier.lsn

        async def handler(request):
            tap.passed('Ручка вызвана')

            body = {
                "couriers": [
                    {
                        "id": str(eda_id),
                        "first_name": "Новый сотрудник 2",
                        "middle_name": "Курьерович",
                        "last_name": "Каменщиков",
                        "phone_number": "198b09b397ea41c7a42862b9a39beaf8",
                        "project_type": "lavka",
                        "work_status": str(work_status),
                        "work_region": {
                            "id": 1,
                            "name": "Москва"
                        },
                        "billing_type": "courier_service",
                        "courier_service_id": 271,
                        "is_hard_of_hearing": False,
                        "is_picker": False,
                        "is_dedicated_picker": False,
                        "is_storekeeper": False,
                        "comment": "adssda",
                        "work_status_updated_at": "2021-07-20T18:06:41+03:00",
                        "updated_at": "2021-11-23T12:56:53+03:00"
                    }
                ]
            }

            return 200, body

        async with await ext_api('eda_core_couriers', handler):
            daemon = CouriersEatsDaemon()
            tap.ok(daemon, 'Демон создан')

            tap.ok(await daemon._process(), 'Пачка обработана')
            daemon.shutdown()

        with await courier.reload():
            tap.eq(len(courier.blocks), 0, 'Блокировка снята')
            tap.ok(courier.lsn > lsn, 'Обновлене прошло в базе')

        await push_events_cache(courier, job_method='job_courier_cancel_all')
        task = await job.take()
        tap.ok(not task, 'задачи на снятие смен нет')


@pytest.mark.parametrize(
    'work_status', ['blocked'],
)
async def test_no_changes(
        tap, dataset, ext_api, unique_int, work_status, push_events_cache, job
):
    with tap.plan(6, 'Изменений нет: не пишем в базу'):
        eda_id = unique_int()

        courier = await dataset.courier(
            vars = {'external_ids': {'eats': eda_id}},
            blocks = [{'source': 'eda', 'reason': work_status}],
        )

        lsn = courier.lsn

        async def handler(request):
            tap.passed('Ручка вызвана')

            body = {
                "couriers": [
                    {
                        "id": str(eda_id),
                        "first_name": "Новый сотрудник 2",
                        "middle_name": "Курьерович",
                        "last_name": "Каменщиков",
                        "phone_number": "198b09b397ea41c7a42862b9a39beaf8",
                        "project_type": "lavka",
                        "work_status": str(work_status),
                        "work_region": {
                            "id": 1,
                            "name": "Москва"
                        },
                        "billing_type": "courier_service",
                        "courier_service_id": 271,
                        "is_hard_of_hearing": False,
                        "is_picker": False,
                        "is_dedicated_picker": False,
                        "is_storekeeper": False,
                        "comment": "adssda",
                        "work_status_updated_at": "2021-07-20T18:06:41+03:00",
                        "updated_at": "2021-11-23T12:56:53+03:00"
                    }
                ]
            }

            return 200, body

        async with await ext_api('eda_core_couriers', handler):
            daemon = CouriersEatsDaemon()
            tap.ok(daemon, 'Демон создан')

            tap.ok(await daemon._process(), 'Пачка обработана')
            daemon.shutdown()

        with await courier.reload():
            tap.eq(len(courier.blocks), 1, 'Блокировка осталась')
            tap.eq(courier.lsn, lsn, 'Без изменений в базу не пишем')

        await push_events_cache(courier, job_method='job_courier_cancel_all')
        task = await job.take()
        tap.ok(not task, 'задачи на снятие смен нет')


@pytest.mark.parametrize(
    'work_status', ['active'],
)
async def test_unblock_source(tap, dataset, ext_api, unique_int, work_status):
    with tap.plan(5, 'Снимаем только едовые блокировки'):
        eda_id = unique_int()

        courier = await dataset.courier(
            vars = {'external_ids': {'eats': eda_id}},
            blocks = [
                {'source': 'eda', 'reason': 'blocked'},
                {'source': 'wms', 'reason': 'unknown'},
            ],
        )

        async def handler(request):
            tap.passed('Ручка вызвана')

            body = {
                "couriers": [
                    {
                        "id": str(eda_id),
                        "first_name": "Новый сотрудник 2",
                        "middle_name": "Курьерович",
                        "last_name": "Каменщиков",
                        "phone_number": "198b09b397ea41c7a42862b9a39beaf8",
                        "project_type": "lavka",
                        "work_status": str(work_status),
                        "work_region": {
                            "id": 1,
                            "name": "Москва"
                        },
                        "billing_type": "courier_service",
                        "courier_service_id": 271,
                        "is_hard_of_hearing": False,
                        "is_picker": False,
                        "is_dedicated_picker": False,
                        "is_storekeeper": False,
                        "comment": "adssda",
                        "work_status_updated_at": "2021-07-20T18:06:41+03:00",
                        "updated_at": "2021-11-23T12:56:53+03:00"
                    }
                ]
            }
            return 200, body

        async with await ext_api('eda_core_couriers', handler):
            daemon = CouriersEatsDaemon()
            tap.ok(daemon, 'Демон создан')

            tap.ok(await daemon._process(), 'Пачка обработана')
            daemon.shutdown()

        with await courier.reload():
            tap.eq(len(courier.blocks), 1, 'Блокировка снята')
            tap.eq(courier.blocks[0].source, 'wms', 'Друга блокировка осталась')


async def test_fail(tap, dataset, ext_api, unique_int):
    with tap.plan(4, 'Ошибка запроса'):
        eda_id = unique_int()

        courier = await dataset.courier(
            vars = {'external_ids': {'eats': eda_id}},
            blocks = [
                {'source': 'eda', 'reason': 'blocked'},
            ],
        )

        async def handler(request):
            tap.passed('Ручка вызвана')
            return 500, ''

        async with await ext_api('eda_core_couriers', handler):
            daemon = CouriersEatsDaemon()
            tap.ok(daemon, 'Демон создан')

            tap.ok(not await daemon._process(), 'Пачка обработана')
            daemon.shutdown()

        with await courier.reload():
            tap.eq(len(courier.blocks), 1, 'Блокировка осталась')


@pytest.mark.parametrize(
    'work_status', ['active'],
)
async def test_unknown(tap, dataset, ext_api, unique_int, work_status, uuid):
    with tap.plan(4, 'Неизвестный курьер просто пропускается'):
        eda_id = unique_int()

        courier = await dataset.courier(
            vars = {'external_ids': {'eats': eda_id}},
            blocks = [{'source': 'eda', 'reason': 'blocked'}],
        )

        async def handler(request):
            tap.passed('Ручка вызвана')

            body = {
                "couriers": [
                    {
                        "id": uuid(),
                        "first_name": "Новый сотрудник 2",
                        "middle_name": "Курьерович",
                        "last_name": "Каменщиков",
                        "phone_number": "198b09b397ea41c7a42862b9a39beaf8",
                        "project_type": "lavka",
                        "work_status": str(work_status),
                        "work_region": {
                            "id": 1,
                            "name": "Москва"
                        },
                        "billing_type": "courier_service",
                        "courier_service_id": 271,
                        "is_hard_of_hearing": False,
                        "is_picker": False,
                        "is_dedicated_picker": False,
                        "is_storekeeper": False,
                        "comment": "adssda",
                        "work_status_updated_at": "2021-07-20T18:06:41+03:00",
                        "updated_at": "2021-11-23T12:56:53+03:00"
                    }
                ]
            }

            return 200, body

        async with await ext_api('eda_core_couriers', handler):
            daemon = CouriersEatsDaemon()
            tap.ok(daemon, 'Демон создан')

            tap.ok(await daemon._process(), 'Пачка обработана')
            daemon.shutdown()

        with await courier.reload():
            tap.eq(len(courier.blocks), 1, 'Блокировка осталась')


async def test_block_change(tap, dataset, ext_api, unique_int):
    with tap.plan(14, 'Изменение блокировки'):
        eda_id = unique_int()

        courier = await dataset.courier(
            vars = {'external_ids': {'eats': eda_id}},
        )

        lsn = courier.lsn

        async def handler1(request):
            tap.passed('Ручка вызвана')

            body = {
                "couriers": [
                    {
                        "id": str(eda_id),
                        "first_name": "Новый сотрудник 2",
                        "middle_name": "Курьерович",
                        "last_name": "Каменщиков",
                        "phone_number": "198b09b397ea41c7a42862b9a39beaf8",
                        "project_type": "lavka",
                        "work_status": "blocked",
                        "work_region": {
                            "id": 1,
                            "name": "Москва"
                        },
                        "billing_type": "courier_service",
                        "courier_service_id": 271,
                        "is_hard_of_hearing": False,
                        "is_picker": False,
                        "is_dedicated_picker": False,
                        "is_storekeeper": False,
                        "comment": "adssda",
                        "work_status_updated_at": "2021-07-20T18:06:41+03:00",
                        "updated_at": "2021-11-23T12:56:53+03:00"
                    }
                ]
            }
            return 200, body

        async with await ext_api('eda_core_couriers', handler1):
            daemon = CouriersEatsDaemon()
            tap.ok(daemon, 'Демон создан')

            tap.ok(await daemon._process(), 'Пачка обработана')
            daemon.shutdown()

        with await courier.reload():
            tap.eq(len(courier.blocks), 1, 'Блокировка добавлена')
            tap.eq(courier.blocks[0].source, 'eda', 'eda')
            tap.eq(courier.blocks[0].reason, 'blocked', 'reason')

            tap.ok(courier.lsn > lsn, 'Обновлене прошло в базе')

        async def handler2(request):
            tap.passed('Ручка вызвана')

            body = {
                "couriers": [
                    {
                        "id": str(eda_id),
                        "first_name": "Новый сотрудник 2",
                        "middle_name": "Курьерович",
                        "last_name": "Каменщиков",
                        "phone_number": "198b09b397ea41c7a42862b9a39beaf8",
                        "project_type": "lavka",
                        "work_status": "ill",
                        "work_region": {
                            "id": 1,
                            "name": "Москва"
                        },
                        "billing_type": "courier_service",
                        "courier_service_id": 271,
                        "is_hard_of_hearing": False,
                        "is_picker": False,
                        "is_dedicated_picker": False,
                        "is_storekeeper": False,
                        "comment": "adssda",
                        "work_status_updated_at": "2021-07-20T18:06:41+03:00",
                        "updated_at": "2021-11-23T12:56:53+03:00"
                    }
                ]
            }
            return 200, body

        async with await ext_api('eda_core_couriers', handler2):
            daemon = CouriersEatsDaemon()
            tap.ok(daemon, 'Демон создан')

            tap.ok(await daemon._process(), 'Пачка обработана')
            daemon.shutdown()

        with await courier.reload():
            tap.eq(len(courier.blocks), 1, 'Блокировка осталась одна')
            tap.eq(courier.blocks[0].source, 'eda', 'eda')
            tap.eq(courier.blocks[0].reason, 'ill', 'Блокировка обнавлена')

            tap.ok(courier.lsn > lsn, 'Обновлене прошло в базе')


async def test_cluster_add(tap, dataset, ext_api, unique_int):
    with tap.plan(5, 'Установка кластера'):
        eda_id = unique_int()

        cluster = await dataset.cluster(eda_region_id=str(unique_int()))
        courier = await dataset.courier(
            cluster_id = None,
            vars = {'external_ids': {'eats': eda_id}},
        )

        lsn = courier.lsn

        async def handler(request):
            tap.passed('Ручка вызвана')

            body = {
                "couriers": [
                    {
                        "id": str(eda_id),
                        "first_name": "Новый сотрудник 2",
                        "middle_name": "Курьерович",
                        "last_name": "Каменщиков",
                        "phone_number": "198b09b397ea41c7a42862b9a39beaf8",
                        "project_type": "lavka",
                        "work_status": "active",
                        "work_region": {
                            "id": str(cluster.eda_region_id),
                            "name": "Москва"
                        },
                        "billing_type": "courier_service",
                        "courier_service_id": 271,
                        "is_hard_of_hearing": False,
                        "is_picker": False,
                        "is_dedicated_picker": False,
                        "is_storekeeper": False,
                        "comment": "adssda",
                        "work_status_updated_at": "2021-07-20T18:06:41+03:00",
                        "updated_at": "2021-11-23T12:56:53+03:00"
                    }
                ]
            }
            return 200, body

        async with await ext_api('eda_core_couriers', handler):
            daemon = CouriersEatsDaemon()
            tap.ok(daemon, 'Демон создан')

            tap.ok(await daemon._process(), 'Пачка обработана')
            daemon.shutdown()

        with await courier.reload():
            tap.eq(courier.cluster_id, cluster.cluster_id, 'кластер установлен')

            tap.ok(courier.lsn > lsn, 'Обновлене прошло в базе')


async def test_cluster_change(tap, dataset, ext_api, unique_int):
    with tap.plan(6, 'Изменение кластера'):
        eda_id = unique_int()

        cluster1 = await dataset.cluster(eda_region_id=str(unique_int()))
        cluster2 = await dataset.cluster(eda_region_id=str(unique_int()))
        tap.ok(
            cluster1.eda_region_id != cluster2.eda_region_id,
            'Кластера уникальны'
        )

        courier = await dataset.courier(
            cluster = cluster1,
            vars = {'external_ids': {'eats': eda_id}},
        )

        lsn = courier.lsn

        async def handler(request):
            tap.passed('Ручка вызвана')

            body = {
                "couriers": [
                    {
                        "id": str(eda_id),
                        "first_name": "Новый сотрудник 2",
                        "middle_name": "Курьерович",
                        "last_name": "Каменщиков",
                        "phone_number": "198b09b397ea41c7a42862b9a39beaf8",
                        "project_type": "lavka",
                        "work_status": "active",
                        "work_region": {
                            "id": str(cluster2.eda_region_id),
                            "name": "Москва"
                        },
                        "billing_type": "courier_service",
                        "courier_service_id": 271,
                        "is_hard_of_hearing": False,
                        "is_picker": False,
                        "is_dedicated_picker": False,
                        "is_storekeeper": False,
                        "comment": "adssda",
                        "work_status_updated_at": "2021-07-20T18:06:41+03:00",
                        "updated_at": "2021-11-23T12:56:53+03:00"
                    }
                ]
            }
            return 200, body

        async with await ext_api('eda_core_couriers', handler):
            daemon = CouriersEatsDaemon()
            tap.ok(daemon, 'Демон создан')

            tap.ok(await daemon._process(), 'Пачка обработана')
            daemon.shutdown()

        with await courier.reload():
            tap.eq(courier.cluster_id, cluster2.cluster_id, 'кластер изменен')

            tap.ok(courier.lsn > lsn, 'Обновлене прошло в базе')


async def test_delivery_change(tap, dataset, ext_api, unique_int):
    with tap.plan(5, 'Изменение типа доставки'):
        eda_id = unique_int()
        courier = await dataset.courier(
            delivery_type='car',
            vars={'external_ids': {'eats': eda_id}},
        )

        lsn = courier.lsn

        async def handler(request):
            tap.passed('Ручка вызвана')

            body = {
                "couriers": [
                    {
                        "id": str(eda_id),
                        "first_name": "Новый сотрудник 2",
                        "middle_name": "Курьерович",
                        "last_name": "Каменщиков",
                        "phone_number": "198b09b397ea41c7a42862b9a39beaf8",
                        "project_type": "lavka",
                        "work_status": "active",
                        "courier_type": "electric_bicycle",
                        "billing_type": "courier_service",
                        "courier_service_id": 271,
                        "is_hard_of_hearing": False,
                        "is_picker": False,
                        "is_dedicated_picker": False,
                        "is_storekeeper": False,
                        "comment": "adssda",
                        "work_status_updated_at": "2021-07-20T18:06:41+03:00",
                        "updated_at": "2021-11-23T12:56:53+03:00"
                    }
                ]
            }
            return 200, body

        async with await ext_api('eda_core_couriers', handler):
            daemon = CouriersEatsDaemon()
            tap.ok(daemon, 'Демон создан')
            tap.ok(await daemon._process(), 'Пачка обработана')
            daemon.shutdown()

        with await courier.reload():
            tap.eq(courier.delivery_type, 'foot', 'тип доставки изменен')
            tap.ok(courier.lsn > lsn, 'Обновлене прошло в базе')


@pytest.mark.parametrize('cs_id,cs_name', [
    (123, 'asd'),
    (456, None),
    (None, 'zxc'),
    (None, None),
])
async def test_courier_service(
        tap, dataset, ext_api, unique_int, cs_id, cs_name,
):
    with tap.plan(6, 'Установка курьерской службы'):
        eda_id = unique_int()
        courier = await dataset.courier(
            vars={'external_ids': {'eats': eda_id}},
        )
        lsn = courier.lsn

        async def handler(request):
            tap.passed('Ручка вызвана')

            body = {
                "couriers": [{
                    "id": str(eda_id),
                    "project_type": "lavka",
                    "updated_at": "2021-11-23T12:56:53+03:00",
                    "courier_service": {
                        "id": cs_id,
                        "name": cs_name,
                    },
                }]
            }
            return 200, body

        async with await ext_api('eda_core_couriers', handler):
            daemon = CouriersEatsDaemon()
            tap.ok(daemon, 'Демон создан')
            tap.ok(await daemon._process(), 'Пачка обработана')
            daemon.shutdown()

        with await courier.reload():
            if cs_id or cs_name:
                tap.ok(courier.lsn > lsn, 'Обновление прошло в базе')
            else:
                tap.ok(courier.lsn == lsn, 'Обновления нет в базе')
            tap.eq(courier.courier_service_id, cs_id, 'ID службы')
            tap.eq(courier.courier_service_name, cs_name, 'Название службы')
