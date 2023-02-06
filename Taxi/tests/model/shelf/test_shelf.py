from stall.model.shelf import Shelf


async def test_shelf(tap, dataset):
    with tap.plan(8):
        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')

        shelf = Shelf({
            'title': 'тестовая полка',
            'store_id': store.store_id,
            'width': 100,
            'height': 50,
            'depth': 70,
        })
        tap.ok(shelf, 'инстанцировано')

        tap.ok(await shelf.save(), 'сохранено')

        loaded = await Shelf.load(shelf.shelf_id)
        tap.ok(loaded, 'Полка загружена')

        tap.eq(loaded.pure_python(), shelf.pure_python(), 'Значения в полке')

        tap.eq(loaded.width, 100, 'width')
        tap.eq(loaded.height, 50, 'height')
        tap.eq(loaded.depth, 70, 'depth')


async def test_barcode(tap, dataset, uuid):
    with tap.plan(6):
        shelf = await dataset.shelf()

        tap.ok(shelf, 'Полка создана')
        tap.ok(shelf.store_id, 'Склад в ней проставлен')

        tap.ok(shelf.barcode, 'штрихкод сгенерирован')

        tap.ok(
            not await shelf.load([shelf.store_id, uuid()], by='barcode'),
            'По неправильному штрихкоду не грузит',
        )

        loaded = await shelf.load(
            [shelf.store_id, shelf.barcode], by='barcode',
        )
        tap.ok(loaded, 'Загружена по баркоду')
        tap.eq(loaded.shelf_id, shelf.shelf_id, 'идентификатор')
