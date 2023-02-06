from stall.model.product import Product


async def test_save_load(tap, uuid):
    with tap.plan(7):
        product = Product({
            'title': 'Пелёнки',
            'vars': {
                'number': 42,
                'string': '42',
                'array': [42],
                'object': {},
            },
            'products_scope': ['russia', 'israel'],
            'measure_unit': uuid(),
        })

        tap.ok(product, 'инстанцирован')

        tap.ok(await product.save(), 'сохранён')

        loaded = await Product.load(product.product_id)

        tap.ok(loaded, 'загружен')
        tap.eq(loaded.pure_python(),
               product.pure_python(),
               'сериализованные совпадают')

        tap.eq(loaded.title, 'Пелёнки', 'title')
        tap.eq(loaded.products_scope, ['russia', 'israel'], 'products_scope')
        tap.ok(product.measure_unit, 'какой-то юнит присвоили')


async def test_dataset(tap, dataset):
    with tap.plan(3):
        product = await dataset.product(title='Батончег марс')
        tap.ok(product, 'сгенерирован продукт')
        tap.ok(await product.load(product.product_id), 'загружен из БД')
        tap.eq(product.title, 'Батончег марс', 'значение атрибута')
