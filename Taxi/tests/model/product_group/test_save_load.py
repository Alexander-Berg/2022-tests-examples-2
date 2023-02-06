from stall.model.product_group import ProductGroup


async def test_save_load(tap):
    with tap.plan(4):
        group = ProductGroup({'name': 'Ноутбуки'})

        tap.ok(group, 'инстанцирован')

        tap.ok(await group.save(), 'сохранён')

        loaded = await ProductGroup.load(group.group_id)

        tap.ok(loaded, 'загружен')
        tap.eq(loaded.pure_python(),
               group.pure_python(),
               'сериализованные совпадают')

async def test_dataset(tap, dataset):
    with tap.plan(3):
        group = await dataset.product_group(name='Детские товары')
        tap.ok(group, 'сгенерирован продукт')
        tap.ok(await group.load(group.group_id), 'загружен из БД')
        tap.eq(group.name, 'Детские товары', 'значение атрибута')
