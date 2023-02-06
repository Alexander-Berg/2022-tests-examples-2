import datetime as dt
import json
import pytest

from libstall.polygon import MultiPolygon
from libstall.timetable import TimeTable
from stall.model.ezones import Ezones
from stall.model.store import Store
from stall.scripts.ezones import import_ezones, EzonesImportError


@pytest.mark.skip(reason='ezones выпилены')
async def test_import_ezones(tap, dataset):
    with tap.plan(10):
        store1 = await dataset.store(external_id='1')
        store1.timetable = [{
            'type': 'friday',
            'begin': '07:00',
            'end': '19:00',
        }]
        store1.ezones = None
        await store1.save()
        store2 = await dataset.store(external_id='abrakadabra')
        store2.timetable = [{
            'type': 'monday',
            'begin': '07:00',
            'end': '19:00',
        }]
        store2.ezones = None
        await store2.save()
        with open('tests/scripts/ezones/data/ezones.json', 'r') as fr:
            data_source = json.load(fr)

        await import_ezones(data_source, name='main',
                            delivery_type='yandex_taxi', write=True)

        loaded1 = await Store.load(store1.store_id)
        loaded2 = await Store.load(store2.store_id)
        tap.eq_ok(
            MultiPolygon(loaded1.ezones.pure_python()['main']['zone']),
            MultiPolygon(data_source['features'][0]['geometry']),
            'Записано правильно'
        )
        tap.eq_ok(
            loaded1.zone,
            MultiPolygon(data_source['features'][0]['geometry']),
            'Записано правильно'
        )
        tap.eq_ok(
            loaded1.ezones.pure_python()['main']['delivery_type'],
            'yandex_taxi',
            'Записано правильно'
        )
        tap.eq_ok(
            loaded1.ezones['main']['timetable'].pure_python(),
            loaded1.timetable.pure_python(),
            'Timetable is correct'
        )
        tap.eq_ok(
            loaded1.ezones.pure_python()['main']['status'],
            'active',
            'Статус записан правильно'
        )
        tap.eq_ok(
            MultiPolygon(loaded2.ezones.pure_python()['main']['zone']),
            MultiPolygon(data_source['features'][1]['geometry']),
            'Записано правильно'
        )
        tap.eq_ok(
            loaded2.zone,
            MultiPolygon(data_source['features'][1]['geometry']),
            'zone Записано правильно'
        )
        tap.eq_ok(
            loaded2.ezones.pure_python()['main']['delivery_type'],
            'yandex_taxi',
            'Записано правильно'
        )
        tap.eq_ok(
            loaded2.ezones['main']['timetable'].pure_python(),
            loaded2.timetable.pure_python(),
            'Timetable is correct'
        )
        tap.eq_ok(
            loaded2.ezones['main']['status'],
            'active',
            'Статус записан правильно'
        )


@pytest.mark.skip(reason='ezones выпилены')
async def test_import_with_timetable(tap, dataset):
    timetable_str = '[{"type": "everyday", "begin": "23:00", "end": "07:00"}]'
    with tap.plan(10):
        store1 = await dataset.store(external_id='1')
        store1.timetable = None
        store1.ezones = None
        await store1.save()
        store2 = await dataset.store(external_id='abrakadabra')
        store2.timetable = None
        store2.ezones = None
        await store2.save()
        with open('tests/scripts/ezones/data/ezones.json', 'r') as fr:
            data_source = json.load(fr)

        await import_ezones(
            data_source,
            name='main',
            delivery_type='yandex_taxi',
            timetable=timetable_str,
            write=True
        )

        loaded1 = await Store.load(store1.store_id)
        loaded2 = await Store.load(store2.store_id)
        tap.eq_ok(
            MultiPolygon(loaded1.ezones.pure_python()['main']['zone']),
            MultiPolygon(data_source['features'][0]['geometry']),
            'Записано правильно'
        )
        tap.eq_ok(
            loaded1.zone,
            MultiPolygon(data_source['features'][0]['geometry']),
            'zone Записано правильно'
        )
        tap.eq_ok(
            loaded1.ezones.pure_python()['main']['delivery_type'],
            'yandex_taxi',
            'Записано правильно'
        )
        tap.eq_ok(
            loaded2.ezones['main']['timetable'].pure_python(),
            TimeTable(timetable_str).pure_python(),
            'Timetable is correct'
        )
        tap.eq_ok(
            loaded1.ezones.pure_python()['main']['status'],
            'active',
            'Статус записан правильно'
        )

        tap.eq_ok(
            MultiPolygon(loaded2.ezones['main']['zone']),
            MultiPolygon(data_source['features'][1]['geometry']),
            'Записано правильно'
        )
        tap.eq_ok(
            loaded2.zone,
            MultiPolygon(data_source['features'][1]['geometry']),
            'zone Записано правильно'
        )
        tap.eq_ok(
            loaded2.ezones['main']['delivery_type'],
            'yandex_taxi',
            'Записано правильно'
        )
        tap.eq_ok(
            loaded2.ezones['main']['timetable'].pure_python(),
            TimeTable(timetable_str).pure_python(),
            'Timetable is correct'
        )
        tap.eq_ok(
            loaded2.ezones['main']['status'],
            'active',
            'Статус записан правильно'
        )


@pytest.mark.skip(reason='ezones выпилены')
async def test_broken_ezones(tap):
    with open('tests/scripts/ezones/data/ezones.json', 'r') as fr:
        data_source = json.load(fr)

    data_source['features'].append(data_source['features'][0])
    with tap.raises(EzonesImportError):
        await import_ezones(data_source, name='main',
                            delivery_type='yandex_taxi',
                            write=True)


@pytest.mark.skip(reason='ezones выпилены')
async def test_import_by_time(tap, dataset):
    store1 = await dataset.store(external_id='1')
    store1.ezones = Ezones(
        {'main': {'delivery_type': 'foot',
                  'zone': store1.zone,
                  'timetable': TimeTable([{'type': 'everyday',
                                           'begin': '07:00',
                                           'end': '23:59',
                                           }])},
         'ext1': {'delivery_type': 'yandex_taxi',
                  'zone': store1.zone,
                  'timetable': TimeTable([{'type': 'everyday',
                                           'begin': '07:00',
                                           'end': '23:30',
                                           }])},
         'ext2': {'delivery_type': 'yandex_taxi',
                  'zone': store1.zone,
                  'timetable': TimeTable([{'type': 'everyday',
                                           'begin': '6:00',
                                           'end': '7:00',
                                           }])},
         }
    )
    await store1.save()
    store2 = await dataset.store(external_id='abrakadabra')
    store2.ezones = Ezones(
        {'main': {'delivery_type': 'foot',
                  'zone': store1.zone,
                  'timetable': TimeTable([{'type': 'everyday',
                                           'begin': '07:00',
                                           'end': '23:59',
                                           }])},
         'ext1': {'delivery_type': 'yandex_taxi',
                  'zone': store1.zone,
                  'timetable': TimeTable([{'type': 'everyday',
                                           'begin': '07:00',
                                           'end': '00:00',
                                           }])},
         'ext2': {'delivery_type': 'yandex_taxi',
                  'zone': store1.zone,
                  'timetable': TimeTable([{'type': 'everyday',
                                           'begin': '6:00',
                                           'end': '7:00',
                                           }])},
         }
    )
    await store2.save()

    with open('tests/scripts/ezones/data/ezones.json', 'r') as fr:
        data_source = json.load(fr)

    await import_ezones(
        data_source,
        name='ext',
        delivery_type='yandex_taxi',
        timetable=None,
        write=True,
        by_time=dt.time(13, 0)
    )

    loaded1 = await Store.load(store1.store_id)
    loaded2 = await Store.load(store2.store_id)

    tap.eq_ok(
        MultiPolygon(loaded1.ezones.pure_python()['ext1']['zone']),
        MultiPolygon(data_source['features'][0]['geometry']),
        'Записано правильно'
    )
    tap.eq_ok(
        loaded1.ezones.pure_python()['ext1']['delivery_type'],
        'yandex_taxi',
        'Записано правильно'
    )
    tap.eq_ok(
        loaded1.ezones.pure_python()['ext1']['status'],
        'active',
        'Статус записан правильно'
    )
    tap.eq_ok(
        loaded1.ezones['ext1']['timetable'].pure_python(),
        [{'type': 'everyday',
          'begin': dt.time(7, 0),
          'end': dt.time(23, 30),
          }],
        'Timetable is correct'
    )

    tap.eq_ok(
        MultiPolygon(loaded2.ezones.pure_python()['ext1']['zone']),
        MultiPolygon(data_source['features'][1]['geometry']),
        'Записано правильно'
    )
    tap.eq_ok(
        loaded2.ezones.pure_python()['ext1']['delivery_type'],
        'yandex_taxi',
        'Записано правильно'
    )
    tap.eq_ok(
        loaded2.ezones.pure_python()['ext1']['status'],
        'active',
        'Статус записан правильно'
    )
    tap.eq_ok(
        loaded2.ezones['ext1']['timetable'].pure_python(),
        [{'type': 'everyday',
          'begin': dt.time(7, 0),
          'end': dt.time(0, 0),
          }],
        'Timetable is correct'
    )
