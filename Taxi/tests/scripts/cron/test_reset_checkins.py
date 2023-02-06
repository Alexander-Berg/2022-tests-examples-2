import datetime
from libstall.util import time2time
from scripts.cron.reset_checkins import process
from stall.model.event_cache import EventCache


async def test_old_checkin(tap, now, cfg, dataset):
    with tap.plan(7, 'Старый чекин, сбросим его'):
        ttl = cfg('business.couriers.checkin.lifetime')
        store = await dataset.store()
        checkin_time = time2time(now() - datetime.timedelta(hours=2 * ttl))
        courier = await dataset.courier(
            state = {
                'checkin_time': checkin_time,
                'checkin_store_id': store.store_id,
            }
        )
        await process(store.store_id)

        tap.ok(await courier.reload(), 'Перегружен')
        tap.eq(courier.state.checkin_time, None, 'Скинули время')
        tap.eq(courier.state.checkin_store_id, None, 'Скинули лавку')

        candidates = await EventCache.top_candidates(
            shard=courier.shardno,
            limit=100,
            ev_type='lp',
            conditions=[
                ('tbl', 'couriers'),
                ('pk', courier.courier_id)
            ]
        )
        tap.eq(len(candidates), 1, '1 контейнер событий')
        events = candidates[0].events
        tap.eq(len(events), 1, '1 событие в контейнере')
        tap.eq(events[0]['key'], ['courier', 'store', store.store_id], 'Ключ')
        tap.eq(events[0]['data']['courier_id'], courier.courier_id, 'Курьер')


async def test_young_checkin(tap, now, cfg, dataset):
    with tap.plan(4, 'Нестарый чекин, оставим'):
        ttl = cfg('business.couriers.checkin.lifetime')
        store = await dataset.store()
        courier = await dataset.courier(
            state = {
                'checkin_time': now() - datetime.timedelta(hours=ttl // 2),
                'checkin_store_id': store.store_id,
            }
        )

        await process(store.store_id)

        tap.ok(await courier.reload(), 'Перегружен')
        tap.ne_ok(courier.state.checkin_time, None, 'Время осталось')
        tap.ne_ok(courier.state.checkin_store_id, None, 'Лавка осталась')

        candidates = await EventCache.top_candidates(
            shard=courier.shardno,
            limit=100,
            ev_type='lp',
            conditions=[
                ('tbl', 'couriers'),
                ('pk', courier.courier_id)
            ]
        )
        tap.eq(len(candidates), 0, 'Ничего не обновляли. Событий нет')
