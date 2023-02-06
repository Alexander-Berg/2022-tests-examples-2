from stall.model.assortment import Assortment


async def test_assortment(tap):
    with tap.plan(4):

        assortment = Assortment({
            'title': 'Тестовый ассортимент',
        })

        tap.ok(assortment, 'Инстанцирован')

        tap.ok(not assortment.assortment_id, 'идентификатора пока нет')

        tap.ok(await assortment.save(), 'Сохранён в БД')

        tap.ok(assortment.assortment_id, 'идентификатор')


async def test_dataset(tap, dataset):
    with tap.plan(2):
        assortment = await dataset.assortment(title='привет')
        tap.ok(assortment, 'ассортимент создан')
        tap.eq(assortment.title, 'привет', 'название')
