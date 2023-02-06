async def test_freeze(tap, dataset):
    with tap.plan(9, 'Логика раскладки для холодильников'):

        product1 = await dataset.product(tags=[])
        product2 = await dataset.product(tags=['refrigerator'])
        product3 = await dataset.product(tags=['freezer'])

        shelf1  = await dataset.shelf(tags=[])
        shelf2  = await dataset.shelf(tags=['refrigerator'])
        shelf3  = await dataset.shelf(tags=['freezer'])

        with shelf1 as shelf:
            tap.ok(shelf.suitable_for_product(product1),
                   'Обычный продукт на обычную полку можно')
            tap.ok(not shelf.suitable_for_product(product2),
                   'Охлажденное на обычную полку нельзя')
            tap.ok(not shelf.suitable_for_product(product3),
                   'Замороженное на обычную полку нельзя')

        with shelf2 as shelf:
            tap.ok(not shelf.suitable_for_product(product1),
                   'Обычный продукт в холодильник нельзя')
            tap.ok(shelf.suitable_for_product(product2),
                   'Охлажденное в холодильник можно')
            tap.ok(not shelf.suitable_for_product(product3),
                   'Замороженное в холодильник нельзя')

        with shelf3 as shelf:
            tap.ok(not shelf.suitable_for_product(product1),
                   'Обычный продукт в морозильник нельзя')
            tap.ok(not shelf.suitable_for_product(product2),
                   'Охлажденное в морозильник нельзя')
            tap.ok(shelf.suitable_for_product(product3),
                   'Замороженное в морозильник можно')
