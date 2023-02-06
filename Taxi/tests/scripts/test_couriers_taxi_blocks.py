# pylint: disable=unused-argument,too-many-locals,protected-access
from aiohttp import web
import pytest

from libstall.util import uuid
from scripts.couriers_taxi_blocks import CouriersTaxiBlocklistDaemon
from stall import cfg
from stall.model.courier_block import CourierBlock


async def test_simple(tap, dataset, ext_api, push_events_cache, job):
    with tap.plan(8, 'Добавлена блокировка на курьера, со снятием с него смен'):
        cfg.set('business.daemon.couriers_taxi_blocks.enable_blocking', True)
        cluster = await dataset.cluster()
        courier_1 = await dataset.courier(cluster=cluster, license=uuid())
        courier_2 = await dataset.courier(cluster=cluster, license=uuid())

        shift_1 = await dataset.courier_shift(
            cluster=cluster,
            courier=courier_1,
            status='waiting',
        )

        block_id, reason, mechanics = uuid(), uuid(), uuid()

        async def handler(request):
            tap.note('Ручка вызвана')
            return 200, {
                'blocks': [{
                    "block_id": block_id,
                    "predicate_id": "33333333-3333-3333-3333-333333333333",
                    "kwargs": {
                        "license_id": {
                            "value": courier_1.license,
                            "indexible": True
                        }
                    },
                    "status": "active",
                    "text": reason,
                    "mechanics": mechanics,
                }],
                'revision': uuid(),
            }

        async with await ext_api('taxi_blocklist', handler):
            await CouriersTaxiBlocklistDaemon()._process()

        with await courier_1.reload() as courier:
            tap.eq(len(courier.blocks), 1, 'добавлена 1 блокировка')

            with courier.blocks[0] as block:
                tap.eq(block.block_id, block_id, 'block_id')
                tap.eq(block.source, 'taxi', 'source')
                tap.eq(block.reason, reason, 'reason')
                tap.eq(block.mechanics, mechanics, 'mechanics')

        with await courier_2.reload() as courier:
            tap.eq(len(courier.blocks), 0, 'блокировок нет')

        await push_events_cache(courier_1, job_method='job_courier_cancel_all')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shift_1.reload() as shift:
            tap.eq(shift.status, 'cancelled', 'смена отменена')


async def test_simple_park(tap, dataset, ext_api, push_events_cache, job):
    with tap.plan(7, 'Добавлена блокировка на курьера только в одном парке'):
        cfg.set('business.daemon.couriers_taxi_blocks.enable_blocking', True)
        _license = uuid()
        cluster = await dataset.cluster()
        courier_1 = await dataset.courier(cluster=cluster, license=_license)
        courier_2 = await dataset.courier(cluster=cluster, license=_license)

        shift_1 = await dataset.courier_shift(
            cluster=cluster,
            courier=courier_1,
            status='waiting',
        )

        block_id, reason = uuid(), uuid()

        async def handler(request):
            tap.note('Ручка вызвана')
            return 200, {
                'blocks': [{
                    "block_id": block_id,
                    "predicate_id": "33333333-3333-3333-3333-333333333333",
                    "kwargs": {
                        "license_id": {
                            "value": _license,
                            "indexible": True
                        },
                        "park_id": {
                            "value": courier_1.park_id,
                            "indexible": True
                        },
                    },
                    "status": "active",
                    "text": reason,
                    "mechanics": ""
                }],
                'revision': uuid(),
            }

        async with await ext_api('taxi_blocklist', handler):
            await CouriersTaxiBlocklistDaemon()._process()

        with await courier_1.reload() as courier:
            tap.eq(len(courier.blocks), 1, 'добавлена 1 блокировка')

            with courier.blocks[0] as block:
                tap.eq(block.block_id, block_id, 'block_id')
                tap.eq(block.source, 'taxi', 'source')
                tap.eq(block.reason, reason, 'reason')

        with await courier_2.reload() as courier:
            tap.eq(len(courier.blocks), 0, 'блокировок нет')

        await push_events_cache(courier_1, job_method='job_courier_cancel_all')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shift_1.reload() as shift:
            tap.eq(shift.status, 'cancelled', 'смена отменена')


async def test_enable_blocking(tap, dataset, ext_api, push_events_cache, job):
    with tap.plan(3, 'При выключенном флаге блокировки не назначаются'):
        cfg.set('business.daemon.couriers_taxi_blocks.enable_blocking', False)
        cluster = await dataset.cluster()
        courier_1 = await dataset.courier(cluster=cluster, license=uuid())

        shift_1 = await dataset.courier_shift(
            cluster=cluster,
            courier=courier_1,
            status='waiting',
        )

        block_id, reason = uuid(), uuid()

        async def handler(request):
            tap.note('Ручка вызвана')
            return 200, {
                'blocks': [{
                    "block_id": block_id,
                    "predicate_id": "33333333-3333-3333-3333-333333333333",
                    "kwargs": {
                        "license_id": {
                            "value": courier_1.license,
                            "indexible": True
                        }
                    },
                    "status": "active",
                    "text": reason,
                    "mechanics": ""
                }],
                'revision': uuid(),
            }

        async with await ext_api('taxi_blocklist', handler):
            await CouriersTaxiBlocklistDaemon()._process()

        with await courier_1.reload() as courier:
            tap.eq(len(courier.blocks), 0, 'блокировок нет')

        await push_events_cache(courier_1, job_method='job_courier_cancel_all')
        tap.eq(await job.take(), None, 'джоба не запущена')

        with await shift_1.reload() as shift:
            tap.eq(shift.status, 'waiting', 'смена осталась назначенной')


async def test_few_blocks(
        tap, dataset, ext_api, push_events_cache, job,
):
    with tap.plan(11, 'Несколько разных блокировок курьера'):
        cfg.set('business.daemon.couriers_taxi_blocks.enable_blocking', True)
        cluster = await dataset.cluster()
        courier_1 = await dataset.courier(cluster=cluster, license=uuid())
        shift_1 = await dataset.courier_shift(
            cluster=cluster,
            courier=courier_1,
            status='waiting',
        )

        # данные блокировок для валидации результата
        blocks = [
            {"block_id": uuid(), "reason": uuid()},
            {"block_id": uuid(), "reason": uuid()}
        ]
        i = 0

        async def handler(request):
            nonlocal i
            tap.note('Ручка вызвана')
            body = {
                'blocks': [{
                    "block_id": blocks[i]['block_id'],
                    "predicate_id": "33333333-3333-3333-3333-333333333333",
                    "kwargs": {
                        "license_id": {
                            "value": courier_1.license,
                            "indexible": True
                        }
                    },
                    "status": "active",
                    "text": blocks[i]['reason'],
                    "mechanics": ""
                }],
                'revision': uuid(),
            }
            i += 1          # будем несколько раз дергать ручку
            return 200, body

        tap.note('Первая блокировка')
        async with await ext_api('taxi_blocklist', handler):
            await CouriersTaxiBlocklistDaemon()._process()

        with await courier_1.reload() as courier:
            tap.eq(len(courier.blocks), 1, 'добавлена 1 блокировка')
            with courier.blocks[0] as block:
                tap.eq(block.block_id, blocks[0]['block_id'], 'block_id')
                tap.eq(block.source, 'taxi', 'source')
                tap.eq(block.reason, blocks[0]['reason'], 'reason')

        await push_events_cache(courier_1, job_method='job_courier_cancel_all')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with await shift_1.reload() as shift:
            tap.eq(shift.status, 'cancelled', 'смена отменена')

        tap.note('Вторая блокировка')
        async with await ext_api('taxi_blocklist', handler):
            await CouriersTaxiBlocklistDaemon()._process()

        with await courier_1.reload() as courier:
            tap.eq(len(courier.blocks), 2, 'добавлена 2ая блокировка')
            with courier.blocks[1] as block:
                tap.eq(block.block_id, blocks[1]['block_id'], 'block_id')
                tap.eq(block.source, 'taxi', 'source')
                tap.eq(block.reason, blocks[1]['reason'], 'reason')

        await push_events_cache(courier_1, job_method='job_courier_cancel_all')
        tap.ok(await job.call(await job.take()), 'Задание выполнено')


async def test_remove_block(tap, dataset, ext_api):
    with tap.plan(1, 'Снятие блокировки с курьера'):
        cfg.set('business.daemon.couriers_taxi_blocks.enable_blocking', True)
        active_block = CourierBlock({'source': 'taxi', 'reason': uuid()})
        courier_1 = await dataset.courier(
            license=uuid(),
            blocks=[active_block],
        )

        async def handler(request):
            tap.note('Ручка вызвана')
            body = {
                'blocks': [{
                    "block_id": active_block.block_id,
                    "predicate_id": "33333333-3333-3333-3333-333333333333",
                    "kwargs": {
                        "license_id": {
                            "value": courier_1.license,
                            "indexible": True
                        }
                    },
                    "status": "inactive",   # блокировка деактивирована
                    "text": uuid(),
                    "mechanics": ""
                }],
                'revision': uuid(),
            }
            return 200, body

        async with await ext_api('taxi_blocklist', handler):
            await CouriersTaxiBlocklistDaemon()._process()

        with await courier_1.reload() as courier:
            tap.eq(len(courier.blocks), 0, 'блокировка снята')


async def test_remove_block_park(tap, dataset, ext_api):
    with tap.plan(2, 'Снятие блокировки с курьера в отдельном парке'):
        cfg.set('business.daemon.couriers_taxi_blocks.enable_blocking', True)
        _license = uuid()
        active_block = CourierBlock({'source': 'taxi', 'reason': uuid()})
        ignore_block = CourierBlock({'source': 'taxi', 'reason': uuid()})
        courier_1 = await dataset.courier(
            license=_license,           # одна лицензия
            blocks=[active_block],
        )
        courier_2 = await dataset.courier(
            license=_license,           # одна лицензия (но разные park_id)
            blocks=[ignore_block],
        )

        async def handler(request):
            tap.note('Ручка вызвана')
            body = {
                'blocks': [{
                    "block_id": active_block.block_id,
                    "predicate_id": "33333333-3333-3333-3333-333333333333",
                    "kwargs": {
                        "license_id": {
                            "value": _license,
                            "indexible": True
                        },
                        "park_id": {
                            "value": courier_1.park_id,
                            "indexible": True
                        },
                    },
                    "status": "inactive",   # блокировка деактивирована
                    "text": uuid(),
                    "mechanics": ""
                }],
                'revision': uuid(),
            }
            return 200, body

        async with await ext_api('taxi_blocklist', handler):
            await CouriersTaxiBlocklistDaemon()._process()

        with await courier_1.reload() as courier:
            tap.eq(len(courier.blocks), 0, 'блокировка снята')

        with await courier_2.reload() as courier:
            tap.eq(len(courier.blocks), 1, 'блокировка на месте')


async def test_remove_part_of_block(tap, dataset, ext_api):
    with tap.plan(4, 'Снятие одной из двух блокировок'):
        cfg.set('business.daemon.couriers_taxi_blocks.enable_blocking', True)
        target_block = CourierBlock({'source': 'taxi', 'reason': uuid()})
        ignore_block = CourierBlock({'source': 'taxi', 'reason': uuid()})
        courier_1 = await dataset.courier(
            license=uuid(),
            blocks=[target_block, ignore_block],
        )

        async def handler(request):
            tap.note('Ручка вызвана')
            body = {
                'blocks': [{
                    "block_id": target_block.block_id,
                    "predicate_id": "33333333-3333-3333-3333-333333333333",
                    "kwargs": {
                        "license_id": {
                            "value": courier_1.license,
                            "indexible": True
                        }
                    },
                    "status": "inactive",   # блокировка деактивирована
                    "text": uuid(),
                    "mechanics": ""
                }],
                'revision': uuid(),
            }
            return 200, body

        async with await ext_api('taxi_blocklist', handler):
            await CouriersTaxiBlocklistDaemon()._process()

        with await courier_1.reload() as courier:
            tap.eq(len(courier.blocks), 1, 'только одна блокировка снята')

            with courier.blocks[0] as block:
                tap.eq(block.block_id, ignore_block.block_id, 'block_id')
                tap.eq(block.source, 'taxi', 'source')
                tap.eq(block.reason, ignore_block.reason, 'reason')


async def test_double_block(tap, dataset, ext_api):
    with tap.plan(2, 'Блокировка получена 2 раза, но установлена 1 раз'):
        cfg.set('business.daemon.couriers_taxi_blocks.enable_blocking', True)
        cluster = await dataset.cluster()
        courier_1 = await dataset.courier(cluster=cluster, license=uuid())
        block_id = uuid()

        async def handler(request):
            tap.note('Ручка вызвана')
            return 200, {
                'blocks': [{
                    "block_id": block_id,
                    "predicate_id": "33333333-3333-3333-3333-333333333333",
                    "kwargs": {
                        "license_id": {
                            "value": courier_1.license,
                            "indexible": True
                        }
                    },
                    "status": "active",
                    "text": uuid(),
                    "mechanics": ""
                }],
                'revision': uuid(),
            }

        async with await ext_api('taxi_blocklist', handler):
            # 2 раза одну и ту же блокировку
            await CouriersTaxiBlocklistDaemon()._process()
            await CouriersTaxiBlocklistDaemon()._process()

        with await courier_1.reload() as courier:
            tap.eq(len(courier.blocks), 1, 'добавлена только 1 блокировка')
            tap.eq(courier.blocks[0].block_id, block_id, 'block_id')


async def test_no_blocks(tap, dataset, ext_api):
    with tap.plan(1, 'Новых блокировок нет'):
        cfg.set('business.daemon.couriers_taxi_blocks.enable_blocking', True)
        cluster = await dataset.cluster()
        courier_1 = await dataset.courier(cluster=cluster, license=uuid())

        async def handler(request):
            tap.note('Ручка вызвана')
            return 200, {
                'blocks': [],
                'revision': uuid(),
            }

        async with await ext_api('taxi_blocklist', handler):
            await CouriersTaxiBlocklistDaemon()._process()

        with await courier_1.reload() as courier:
            tap.eq(len(courier.blocks), 0, 'блокировка не добавилась')


@pytest.mark.parametrize(
    'kwargs,title',
    [
        (  # блокировка курьера по водительскому удостоверению (ВУ)
            {
                "license_id": {
                    "value": uuid(),
                    "indexible": True
                }
            },
            'лицензии'
        ),
        (  # блокировка курьера по ВУ + park_id
            {
                "license_id": {
                    "value": uuid(),
                    "indexible": True
                },
                "park_id": {
                    "value": uuid(),
                    "indexible": True
                }
            },
            'лицензии и park_id'
        ),
    ]
)
async def test_unknown_courier(tap, dataset, ext_api, kwargs, title):
    with tap.plan(1, f'Блокировка на неизвестного курьера по {title}'):
        cfg.set('business.daemon.couriers_taxi_blocks.enable_blocking', True)
        cluster = await dataset.cluster()
        courier_1 = await dataset.courier(cluster=cluster, license=uuid())

        async def handler(request):
            tap.note('Ручка вызвана')
            return 200, {
                'blocks': [{
                    "block_id": uuid(),
                    "predicate_id": "33333333-3333-3333-3333-333333333333",
                    "kwargs": kwargs,
                    "status": "active",
                    "text": uuid(),
                    "mechanics": ""
                }],
                'revision': uuid(),
            }

        async with await ext_api('taxi_blocklist', handler):
            await CouriersTaxiBlocklistDaemon()._process()

        with await courier_1.reload() as courier:
            tap.eq(len(courier.blocks), 0, 'блокировка не добавилась')


@pytest.mark.parametrize(
    'body',
    [
        {'blocks': [], 'revision': uuid()},
        {'blocks': [], 'revision': None},
        {'blocks': None, 'revision': uuid()},
        {'blocks': []},
        {'revision': uuid()},
        {},
        None,
        '',
        'dfasdfsfdasdg',
        {'blocks': [{'kwargs': {'new': 'block'}}], 'revision': uuid()},
    ]
)
async def test_error_response(tap, dataset, ext_api, body):
    with tap.plan(1, f'Проверка обработки ошибок в ответах сервиса: {body}'):
        async def handler(request):
            tap.passed('Ручка вызвана')
            return 200, body

        async with await ext_api('taxi_blocklist', handler):
            await CouriersTaxiBlocklistDaemon()._process()


async def test_error_json_decoder(tap, dataset, ext_api):
    with tap.plan(1, 'Проверка обработки ошибки в JSON'):
        async def handler(request):
            tap.passed('Ручка вызвана')
            return web.Response(
                status=200,
                body='dfasdfsfdasdg',
                content_type='application/json'
            )

        async with await ext_api('taxi_blocklist', handler):
            await CouriersTaxiBlocklistDaemon()._process()
