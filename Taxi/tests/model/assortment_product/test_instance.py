from stall.model.assortment_product import AssortmentProduct

async def test_assortment_product(tap, dataset):
    with tap.plan(6):

        assortment = await dataset.assortment(title='привет')
        tap.ok(assortment, 'Создан ассортимент')
        tap.ok(assortment.assortment_id, 'идентификатор')
        tap.eq(assortment.title, 'привет', 'название')

        product = await dataset.product()
        tap.ok(product, 'продукт создан')


        ap = AssortmentProduct({
            'assortment_id': assortment.assortment_id,
            'product_id': product.product_id,
            'max': 50,
        })

        tap.ok(ap, 'инстанцирован')
        tap.ok(await ap.save(), 'сохранён')



async def test_dataset(tap, dataset):
    with tap.plan(1):

        ap = await dataset.assortment_product()
        tap.ok(ap, 'продукт для ассортимента описан')


