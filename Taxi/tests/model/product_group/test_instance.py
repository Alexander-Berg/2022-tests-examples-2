from stall.model.product_group import ProductGroup


async def test_product_group(tap, uuid):
    with tap.plan(13):
        data = {
            'external_id': uuid(),
            'name': 'test group',
            'code': 'spam',
            'description': 'spam',
            'order': 42,
            'images': ['https://s3/img.png', 'https://s3/img2.png'],
            'is_visible': True,
            'vars': {'a': 1, 'b': '2'},
            'products_scope': ['russia', 'israel'],
        }

        group = ProductGroup(data)

        tap.ok(group, 'Inited')
        tap.ok(not group.group_id, 'No id')
        tap.ok(await group.save(), 'Saved')
        tap.ok(group.group_id, 'id assigned')
        for field, values in data.items():
            tap.eq_ok(getattr(group, field), values, field)


async def test_dataset(tap, dataset):
    with tap.plan(2):
        group = await dataset.product_group(name='test group')

        tap.ok(group, 'Created')
        tap.eq_ok(group.name, 'test group', 'title')


async def test_dataset_courier_lunch(tap, dataset):
    with tap.plan(2, 'Создание группы обедов для курьеров x2'):
        product_group1 = await dataset.product_group_lunch()
        tap.ok(product_group1, 'Created')
        product_group2 = await dataset.product_group_lunch()
        tap.ok(product_group2, 'Created')
