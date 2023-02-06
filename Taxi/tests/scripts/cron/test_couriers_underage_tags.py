from datetime import timedelta

from scripts.cron import couriers_underage_tags
from stall.model.event_cache import EventCache


# pylint: disable=too-many-locals
async def test_common(tap, dataset, uuid, time_mock):
    with tap.plan(36, 'скрипт выбирает именинников с прошлого запуска'):
        async def _check_courier_tasks(courier, expected_count, desc):
            candidates = await EventCache.list(
                tbl='couriers',
                pk=courier.courier_id,
                by='object',
                db={'shard': courier.shardno},
                full=True
            )
            tap.eq(len(candidates.list), expected_count, desc)
            for event_cache in candidates.list:
                tap.eq(len(event_cache['events']), 1, 'Создан 1 ивент')
                event = event_cache['events'][0]
                tap.eq(event['type'], 'queue', 'запланирован таск в джобы')
                tap.eq(
                    event['data']['callback'],
                    'stall.model.courier.Courier.job_sync_underage_tag',
                    'таск на синхронизацию тегов'
                )
                tap.eq(
                    event['data']['courier_id'],
                    courier.courier_id,
                    'таск для текущего курьера'
                )

        today = time_mock.now().date()

        # Не зацепит при первом запуске, так как дельта в 2 дня
        birthday_1 = today - timedelta(days=3)
        courier_1 = await dataset.courier(birthday=birthday_1)

        # Обновится
        birthday_2 = today - timedelta(days=1)
        courier_2 = await dataset.courier(birthday=birthday_2)

        # Обновится при запуске через день
        birthday_3 = today + timedelta(days=1)
        courier_3 = await dataset.courier(birthday=birthday_3)

        # Обновится при запуске через два дня
        birthday_4 = today + timedelta(days=2)
        courier_4 = await dataset.courier(birthday=birthday_4)

        stash_name = uuid()

        tap.note('первый запуск')
        await couriers_underage_tags.process(stash_name)

        await _check_courier_tasks(courier_1, 0, 'первый нет')
        await _check_courier_tasks(courier_2, 1, 'второй да')
        await _check_courier_tasks(courier_3, 0, 'третий нет')
        await _check_courier_tasks(courier_4, 0, 'четвёртый нет')

        time_mock.sleep(days=1)
        tap.note('запуск на второй день')
        await couriers_underage_tags.process(stash_name)

        await _check_courier_tasks(courier_1, 0, 'первый нет')
        await _check_courier_tasks(courier_2, 1, 'второй да')
        await _check_courier_tasks(courier_3, 1, 'третий да')
        await _check_courier_tasks(courier_4, 0, 'четвёртый нет')

        time_mock.sleep(days=1)
        tap.note('запуск на третий день')
        await couriers_underage_tags.process(stash_name)

        await _check_courier_tasks(courier_1, 0, 'первый нет')
        await _check_courier_tasks(courier_2, 1, 'второй да')
        await _check_courier_tasks(courier_3, 1, 'третий да')
        await _check_courier_tasks(courier_4, 1, 'четвёртый да')
