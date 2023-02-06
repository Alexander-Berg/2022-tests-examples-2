import argparse
from io import StringIO
from scripts.dev.fill_stores_courier_data import main


async def test_common(tap, dataset, uuid):
    with tap:
        external_id = uuid()

        area_id = uuid()
        area_title = uuid()

        store = await dataset.store(external_id=external_id)

        file = StringIO(
            'region_id;region_name;area_id;place_id;area_name\n'
            f'1;Екатеринбург;{uuid()};{uuid()};{uuid()}\n'
            f'1;Екатеринбург;{area_id};{store.external_id};{area_title}\n'
            f'1;Екатеринбург;{uuid()};{uuid()};{uuid()}\n'
            f'2;Москва;{uuid()};{uuid()};{uuid()}\n'
        )
        args = argparse.Namespace(
            file=file,
            place_id=None,
            region_id=None,
            batch_size=10,
            apply=True,
        )

        counters = await main(args)
        file.seek(0)
        tap.eq(counters, {'rows': 4, 'fetched': 1, 'saved': 1}, 'counters ok')

        await store.reload()
        tap.eq(store.courier_area_id, area_id, 'area_id ok')
        tap.eq(store.courier_area_title, area_title, 'area_title ok')

        counters = await main(args)
        file.seek(0)
        tap.eq(counters, {'rows': 4, 'fetched': 1, 'saved': 0}, 'counters ok')

        args = argparse.Namespace(
            file=file,
            place_id=None,
            region_id=None,
            batch_size=1,
            apply=True,
        )
        counters = await main(args)
        file.seek(0)
        tap.eq(counters, {'rows': 4, 'fetched': 1, 'saved': 0}, 'counters ok')

        for place_id, expected in [
            (store.external_id, {'rows': 1, 'fetched': 1, 'saved': 0}),
            (uuid(), {'rows': 0, 'fetched': 0, 'saved': 0})
        ]:
            args = argparse.Namespace(
                file=file,
                place_id=place_id,
                region_id=None,
                batch_size=10,
                apply=True,
            )
            counters = await main(args)
            file.seek(0)
            tap.eq(counters, expected, 'counters ok')

        for region_id, expected in [
            ('1', {'rows': 3, 'fetched': 1, 'saved': 0}),
            ('2', {'rows': 1, 'fetched': 0, 'saved': 0}),
            (uuid(), {'rows': 0, 'fetched': 0, 'saved': 0}),
        ]:
            args = argparse.Namespace(
                file=file,
                place_id=None,
                region_id=region_id,
                batch_size=10,
                apply=True,
            )
            counters = await main(args)
            file.seek(0)
            tap.eq(counters, expected, 'counters ok')
