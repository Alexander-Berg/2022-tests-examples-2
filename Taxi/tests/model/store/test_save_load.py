import random
import time

import libstall.util
from stall.model.store import Store


async def test_save_load(tap, uuid):
    with tap.plan(14):
        store = Store({
            'company_id': uuid(),
            'cluster': 'тест',
            'cluster_id': uuid(),
            'title': 'тестовый склад',
            'lang': 'ru_RU',
            'region_id': 213,
            'currency': 'RUB',
            'area': 880,
            'open_ts': libstall.util.now(),
            'courier_shift_setup': {
                'tags': ['test1', 'test2'],
            }
        })

        tap.ok(store, 'инстанцирован')

        tap.ok(await store.save(), 'сохранён')

        loaded = await Store.load(store.store_id)
        tap.ok(loaded, 'Загружен склад')
        tap.eq_ok(loaded.store_id, store.store_id, 'store_id')
        tap.eq_ok(loaded.status, store.status, 'status')
        tap.eq_ok(loaded.cluster, store.cluster, 'cluster')
        tap.eq_ok(loaded.cluster_id, store.cluster_id, 'cluster_id')
        tap.eq_ok(loaded.title, store.title, 'title')
        tap.eq_ok(loaded.lang, store.lang, 'lang')
        tap.eq_ok(loaded.region_id, store.region_id, 'region_id')
        tap.eq_ok(loaded.currency, store.currency, 'currency')
        tap.eq_ok(loaded.area, store.area, 'area')
        tap.eq_ok(loaded.open_ts, store.open_ts, 'open_ts')
        tap.eq_ok(
            loaded.courier_shift_setup,
            {
                'tags': ['test1', 'test2'],
            },
            'courier_shift_setup'
        )


async def test_dataset(tap, dataset):
    with tap.plan(3):
        store = await dataset.store(title="Привет, медвед")

        tap.ok(store, 'есть склад')
        tap.ok(await Store.load(store.store_id), 'сохранен в БД')
        tap.ok(store.title, 'Привет, медвед', 'title')


async def test_counters(tap, dataset):
    with tap.plan(7):
        store = await dataset.store(title="Привет, медвед")
        tap.ok(store, 'Склад создан')

        lsn = store.lsn

        with await store.save() as saved:
            tap.ok(saved,               'Сохранён')
            tap.ok(saved.serial,        'Последовательный номер')
            tap.ok(saved.lsn > lsn,     'Репликационный номер увеличен')

        lsn = store.lsn

        with await store.save() as saved:
            tap.ok(saved,               'Сохранён')
            tap.ok(saved.serial,        'Последовательный номер')
            tap.ok(saved.lsn > lsn,     'Репликационный номер увеличен')


async def test_geo(tap, dataset):
    with tap.plan(8):
        store = await dataset.store(
            address = "Россия, Москва, улица Паршина, 4, 123103",
            location = {'lat': 55.789502, 'lon': 37.461948}
        )
        tap.ok(store, 'Склад создан')
        tap.ok(await store.save(), 'Сохранен')

        tap.eq(store.address,
               "Россия, Москва, улица Паршина, 4, 123103", 'address')

        tap.eq(store.location.lat,  55.789502, 'lat')
        tap.eq(store.location.lon,  37.461948, 'lon')

        store.rehash(
            address=None,
            location=None,
            zone=[],
        )

        tap.ok(await store.save(), 'Сохранен')

        tap.eq(store.address, None, 'Адрес очищен')
        tap.eq(store.location, None, 'местоположение очищено')


def get_zone():
    return {
        'properties': {},
        "geometry": {'type': 'MultiPolygon',
                     'coordinates':
                         [
                             [
                                 [
                                     [66.0, 33.0],
                                     [66.0, 33.5],
                                     [66.5, 33.0 + random.randint(0, 10)],
                                     [66.0, 33.0]
                                 ]
                             ],
                             [
                                 [
                                     [66.3, 33.6],
                                     [66.4, 33.6],
                                     [66.3, 33.7],
                                     [66.3, 33.6]
                                 ]
                             ]
                         ]
                     },
        "type": "Feature",
    }


def get_timetable():
    return [{
        'type': 'everyday',
        'begin': f'07:{random.randint(0, 59):02d}:00',
        'end': '19:00:00',
    }]


async def test_open_ts(tap, uuid):
    # - saving active store sets open_ts field as current
    with tap.plan(13):
        store = Store({
            'company_id': uuid(),
            'cluster': 'тест',
            'cluster_id': uuid(),
            'title': 'тестовый склад',
            'lang': 'ru_RU',
            'region_id': 213,
            'currency': 'RUB',
            'area': 880,
            'status': 'active',
        })
        tap.ok(store, 'инстанцирован')
        tap.ok(await store.save(), 'сохранён')
        loaded = await Store.load(store.store_id)
        tap.ok(loaded, 'Загружен склад')
        tap.eq_ok(loaded.store_id, store.store_id, 'store_id')
        tap.eq_ok(loaded.status, store.status, 'status')
        tap.ok(loaded.open_ts, 'open_ts is not empty')
        tap.eq_ok(loaded.open_ts.tzname(), 'UTC', 'open_ts has UTC timezone')
        open_ts_before = store.open_ts
        #
        # - setting store to disabled leaves open_ts as is
        store.status = 'disabled'
        tap.ok(await store.save(), 'сохранён')
        loaded = await Store.load(store.store_id)
        tap.eq_ok(loaded.status, 'disabled', 'store has disabled status')
        tap.eq_ok(
            loaded.open_ts, open_ts_before,
            'open_ts is preserved on disabling store'
        )
        #
        # - setting store to disabled then to active again
        #   does not refresh open_ts field
        tap.ok(await store.save(), 'сохранён')
        loaded = await Store.load(store.store_id)
        store.status = 'active'
        time.sleep(1.0)
        tap.ok(await store.save(), 'сохранён')
        loaded = await Store.load(store.store_id)
        tap.eq_ok(loaded.open_ts, open_ts_before, 'open_ts was not refreshed')


async def test_open_ts_field_logic(tap, uuid):
    with tap.plan(20):
        # - creating disabled store leaves open_ts empty
        store = Store({
            'company_id': uuid(),
            'cluster': 'тест',
            'cluster_id': uuid(),
            'title': 'тестовый склад',
            'lang': 'ru_RU',
            'region_id': 213,
            'currency': 'RUB',
            'area': 880,
            'status': 'disabled',
        })
        tap.ok(store, 'инстанцирован')
        tap.ok(await store.save(), 'сохранён')
        loaded = await Store.load(store.store_id)
        tap.ok(loaded, 'Загружен склад')
        tap.eq_ok(loaded.store_id, store.store_id, 'store_id')
        tap.eq_ok(loaded.status, store.status, 'status')
        tap.ok(loaded.open_ts is None, 'open_ts is empty')
        #
        # - moving disabled, not opened store to active makes the store opened
        store = loaded
        store.status = 'active'
        tap.ok(await store.save(), 'сохранён как active')
        loaded = await Store.load(store.store_id)
        tap.eq_ok(loaded.status, 'active', 'store is active in db')
        tap.ok(loaded.open_ts, 'open_ts is not empty')
        #
        # - saving existing active store with no open_ts remains
        #   the field empty
        store = Store({
            'company_id': uuid(),
            'cluster': 'тест',
            'cluster_id': uuid(),
            'title': 'тестовый склад',
            'lang': 'ru_RU',
            'region_id': 213,
            'currency': 'RUB',
            'area': 880,
            'status': 'active',
        })
        tap.ok(await store.save(), 'сохранён впервые как active')
        loaded = await Store.load(store.store_id)
        tap.ok(loaded.open_ts, 'store is opened')
        store = loaded
        store.open_ts = None
        tap.ok(await store.save(), 'сохранён')
        loaded = await Store.load(store.store_id)
        tap.ok(loaded.open_ts is None, 'open_ts was set None')
        store = loaded
        # now the store is active and not opened
        time.sleep(1.0)
        tap.ok(await store.save(db=None, status='active'), 'сохранён')
        loaded = await Store.load(store.store_id)
        tap.ok(loaded.open_ts is None, 'open_ts is still None')
        #
        # - store is opened, is disabled. Save it.
        #   store.open_ts remains the same
        # 1. Create opened and disabled store
        store = Store({
            'company_id': uuid(),
            'cluster': 'тест',
            'cluster_id': uuid(),
            'title': 'тестовый склад',
            'lang': 'ru_RU',
            'region_id': 213,
            'currency': 'RUB',
            'area': 880,
            'status': 'active',
        })
        tap.ok(await store.save(), 'сохранён впервые')
        store.status = 'disabled'
        tap.ok(await store.save(), 'сохранён как disabled')
        loaded = await Store.load(store.store_id)
        tap.ok(loaded.open_ts, 'store is opened')
        open_ts_before = loaded.open_ts
        time.sleep(1.0)
        store = loaded
        # 2. Store preserves opened time on save
        store.status = 'active'
        tap.ok(await store.save(), 'сохранён как active')
        loaded = await Store.load(store.store_id)
        tap.eq_ok(loaded.open_ts, open_ts_before, 'open_ts was not refreshed')
