import pytest
from dateutil.relativedelta import relativedelta

from scripts.couriers import CouriersDaemon
from stall.model.event_cache import EventCache


@pytest.mark.parametrize('years', [15, 20])
async def test_underage_tag_setting(
        tap, dataset, ext_api, uuid, now, years
):
    external_id = uuid()
    birthday = now().date() - relativedelta(years=years)

    # pylint: disable=unused-argument
    async def dp_handler(request):
        return {
            'profiles': [{
                'park_driver_profile_id': external_id,
                'is_deleted': False,
                'data': {
                    'external_ids': {
                        'eats': uuid(),
                    },
                    'orders_provider': {
                        'lavka': True,
                    },
                },
            }],
        }

    async def eda_handler(request):
        return {
            'courier': {
                'gender': 'male',
                'birthday': birthday,
            }
        }

    with tap.plan(7, 'заполнение пола, даты рождения и синк тегов'):
        courier = await dataset.courier(
            external_id=external_id,
            gender=None,
            birthday=None,
        )

        async with await ext_api('driver_profiles', dp_handler), \
                await ext_api('eda_core_couriers', eda_handler):
            # pylint: disable=protected-access
            await CouriersDaemon()._process(None)

        await courier.reload()

        tap.eq(courier.gender, 'male', 'пол установлен')
        tap.eq(courier.birthday, birthday, 'дата рождения установлена')

        candidates = await EventCache.list(
            tbl='couriers',
            pk=courier.courier_id,
            by='object',
            db={'shard': courier.shardno},
            full=True
        )
        tap.eq(len(candidates.list), 1, 'создана 1 обёртка для ивентов')
        with candidates.list[0] as event_cache:
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


async def test_underage_tag_not_changed(
        tap, dataset, ext_api, uuid, now,
):
    external_id = uuid()
    eda_id = uuid()
    birthday = now().date() - relativedelta(years=15)

    # pylint: disable=unused-argument
    async def dp_handler(request):
        return {
            'profiles': [{
                'park_driver_profile_id': external_id,
                'is_deleted': False,
                'data': {
                    'external_ids': {
                        'eats': eda_id,
                    },
                    'orders_provider': {
                        'lavka': True,
                    },
                },
            }],
        }

    # pylint: disable=unused-argument
    async def eda_handler(request):
        return {
            'courier': {
                'gender': 'male',
                'birthday': birthday,
            }
        }

    with tap.plan(3, 'если данные не изменились, теги не синкаем'):
        courier = await dataset.courier(
            external_id=external_id,
            gender='male',
            birthday=birthday,
        )

        async with await ext_api('driver_profiles', dp_handler), \
                await ext_api('eda_core_couriers', eda_handler):
            # pylint: disable=protected-access
            await CouriersDaemon()._process(None)

        await courier.reload()

        tap.eq(courier.gender, 'male', 'пол остался')
        tap.eq(courier.birthday, birthday, 'дата рождения осталась')

        candidates = await EventCache.list(
            tbl='couriers',
            pk=courier.courier_id,
            by='object',
            db={'shard': courier.shardno},
            full=True
        )
        tap.eq(len(candidates.list), 0, 'ивенты не создались')
