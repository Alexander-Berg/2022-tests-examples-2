import argparse

from scripts.dev.set_ttl_show_product import main as main_product
from scripts.dev.set_ttl_show_assortment_product import \
    main as main_as_p


async def test_set_ttl_show_product(tap, dataset):
    with tap.plan(2, 'обновляются непроставленные '
                     'значения ttl_show в ассортименте и продукте'):

        product_1 = await dataset.product(ttl_show=0)
        product_2 = await dataset.product(ttl_show=123)

        args = argparse.Namespace(
            apply=True,
            product_id=[product_1.product_id, product_2.product_id],
            ttl_show=666,
        )

        await main_product(args)
        await product_1.reload()
        await product_2.reload()

        tap.eq(product_1.ttl_show, 666,
               'установлено дефолтное значение для ttl_show')
        tap.eq(product_2.ttl_show, 123,
               'не 0 значение не меняется у продукта')


async def test_set_ttl_show_as_p(tap, dataset):
    with tap.plan(4, 'обновляются непроставленные '
                     'значения ttl_show в ассортименте и продукте'):

        product_1 = await dataset.product(ttl_show=0)
        assortment_1 = await dataset.assortment(ttl_show=999)
        product_2 = await dataset.product(ttl_show=123)
        assortment_2 = await dataset.assortment(ttl_show=0)

        assortment_product_1 = await dataset.assortment_product(
            product_id=product_1.product_id,
            assortment_id=assortment_1.assortment_id,
            ttl_show=0
        )
        assortment_product_2 = await dataset.assortment_product(
            product_id=product_1.product_id,
            ttl_show=345,
        )
        assortment_product_3 = await dataset.assortment_product(
            product_id=product_1.product_id,
            assortment_id=assortment_2.assortment_id,
            ttl_show=0,
        )
        assortment_product_4 = await dataset.assortment_product(
            product_id=product_2.product_id,
            assortment_id=assortment_1.assortment_id,
            ttl_show=0,
        )

        args = argparse.Namespace(
            apply=True,
            product_id=[product_1.product_id, product_2.product_id],
            assortment_id=[assortment_1.assortment_id,
                           assortment_2.assortment_id],
            ttl_show=666,
        )

        await main_as_p(args)
        await assortment_product_1.reload()
        await assortment_product_2.reload()
        await assortment_product_3.reload()
        await assortment_product_4.reload()

        tap.eq(assortment_product_1.ttl_show, 999,
               'устанавливается ttl_show как у ассортимента')
        tap.eq(assortment_product_2.ttl_show, 345,
               'не 0 значение не меняется в ассортименте')
        tap.eq(assortment_product_3.ttl_show, 666,
               'установлено дефолтное значение для ttl_show')
        tap.eq(assortment_product_4.ttl_show, 123,
               'устанавливается ttl_show как у продукта')
