async def test_instance(tap, dataset):
    with tap.plan(5):

        tag = dataset.CourierShiftTag({
            'title': 'A1',
            'description': '54321',
        })
        tap.ok(tag, 'Объект создан')
        tap.ok(await tag.save(), 'сохранение')
        tap.ok(await tag.save(), 'обновление')

        tap.eq(tag.title, 'A1', 'title')
        tap.eq(tag.description, '54321', 'description')


async def test_dataset(tap, dataset):
    with tap.plan(1):
        tag = await dataset.courier_shift_tag()
        tap.ok(tag, 'Объект создан')
