import tests.dataset as dt

from stall.model.event_cache import EventCache
from stall.logbroker import LogbrokerMessage
from stall.logbrokers.grocery_surge_calculated import Daemon


async def test_unknown_store(tap, now, uuid):
    with tap.plan(1, 'Невалидный стор'):
        message = LogbrokerMessage(
            'grocery-surge-calculated',
            data={
                'depot_id': uuid(),
                'timestamp': now()
            }
        )

        await Daemon.process_messages([message])
        tap.ok(True, 'Сообщение пропущено')


async def test_surge_level(tap, dataset: dt):
    with tap.plan(7, 'Сурж при правильном delivery type'):
        store = await dataset.store(
            state={
                'surge_level': None,
            }
        )
        cursor = await EventCache.list(
            by='look',
            conditions=(
                ('type', 'lp'),
                ('pk', store.store_id),
            ),
            db={'shard': store.shardno},
            direction='DESC',
        )
        existed_events = len(cursor.list)
        message = LogbrokerMessage(
            'grocery-surge-calculated',
            data={
                'depot_id': store.external_id,
                'delivery_type': ['pedestrian'],
                'meta':
                    {
                        'display_surge_level': 3,
                    }
            }
        )
        await Daemon.process_messages([message])

        tap.ok(await store.reload(), 'Перегружен')
        tap.eq_ok(store.state.surge_level,
                  3,
                  'Сурж изменен')

        cursor = await EventCache.list(
            by='look',
            conditions=(
                ('type', 'lp'),
                ('pk', store.store_id),
            ),
            db={'shard': store.shardno},
            direction='DESC',
        )
        tap.eq_ok(len(cursor.list), existed_events + 1,
                  'Новый контейнер событий')
        with cursor.list[0] as wrapper:
            tap.eq_ok(len(wrapper.events), 1, '1 событие в контейнере')
            event = wrapper.events[0]

            tap.eq_ok(event['key'], ['state', 'store',  store.store_id], 'key')
            tap.eq_ok(event['data']['store_id'], store.store_id,
                      'data.store_id')
            tap.eq_ok(event['data']['state']['surge_level'], 3,
                      'surge_level в данных')


async def test_not_pedestrian(tap, dataset: dt):
    with tap.plan(3, 'Сурж при неправильном delivery type'):
        store = await dataset.store(
            state={
                'surge_level': None,
            }
        )
        cursor = await EventCache.list(
            by='look',
            conditions=(
                ('type', 'lp'),
                ('pk', store.store_id),
            ),
            db={'shard': store.shardno},
            direction='DESC',
        )
        existed_events = len(cursor.list)
        message = LogbrokerMessage(
            'grocery-surge-calculated',
            data={
                'depot_id': store.external_id,
                'delivery_type': ['ne_pedestrian'],
                'meta':
                    {
                        'display_surge_level': 3,
                    }
            }
        )
        await Daemon.process_messages([message])

        tap.ok(await store.reload(), 'Перегружен')
        tap.eq_ok(store.state.surge_level,
                  None,
                  'Сурж не изменен')

        cursor = await EventCache.list(
            by='look',
            conditions=(
                ('type', 'lp'),
                ('pk', store.store_id),
            ),
            db={'shard': store.shardno},
            direction='DESC',
        )
        tap.eq_ok(len(cursor.list), existed_events,
                  'Новый контейнер событий не создан')
