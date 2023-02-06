import json
import pytest
from stall.scripts.zones import import_zones, ZoneImportError
from stall.model.store import Store


@pytest.mark.skip(reason='zone выпилены')
async def test_import_zones(tap, dataset):
    with tap.plan(2):
        store1 = await dataset.store(external_id='1')
        store2 = await dataset.store(external_id='2')
        with open('tests/scripts/zones/data/zones.json', 'r') as fr:
            data_source = json.load(fr)

        await import_zones(data_source, write=True)

        loaded1 = await Store.load(store1.store_id)
        loaded2 = await Store.load(store2.store_id)
        tap.eq_ok(
            loaded1.zone.pure_python()['geometry'],
            data_source['groceries'][0]['zonesDetailed'][0]['zone'],
            'Записано правильно'
        )
        # tap.eq_ok(
        #     loaded1.ezones['main'].zone.pure_python()['geometry'],
        #     data_source['groceries'][0]['zonesDetailed'][0]['zone'],
        #     'Записано правильно'
        # )
        tap.eq_ok(
            loaded2.zone.pure_python()['geometry'],
            data_source['groceries'][1]['zonesDetailed'][1]['zone'],
            'Записано правильно'
        )
        # tap.eq_ok(
        #     loaded2.ezones['main'].zone.pure_python()['geometry'],
        #     data_source['groceries'][1]['zonesDetailed'][1]['zone'],
        #     'Записано правильно'
        # )


@pytest.mark.skip(reason='zone выпилены')
async def test_broken_ezones(tap):
    with open('tests/scripts/zones/data/zones_broken_no_id.json', 'r') as fr:
        data_source = json.load(fr)

    with tap.raises(ZoneImportError):
        await import_zones(data_source, write=True)
