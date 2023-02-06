from stall.model.assortment_contractor_product import (
    AssortmentContractorProduct,
)


async def test_all_prices(tap, dataset):
    with tap.plan(1, 'Цены для всех продуктов'):
        product_1 = await dataset.product()
        product_2 = await dataset.product()
        store = await dataset.store()
        contractor_1 = await dataset.assortment_contractor(store=store)
        contractor_2 = await dataset.assortment_contractor(store=store)
        await dataset.assortment_contractor_product(
            product=product_1,
            assortment=contractor_1,
            price=9.99
        )
        await dataset.assortment_contractor_product(
            product=product_2,
            assortment=contractor_2,
            price=11.22
        )

        product_prices = (
            await AssortmentContractorProduct.get_prices_for_products(
                store_id=store.store_id,
                product_ids=[product_1.product_id, product_2.product_id]
            )
        )

        tap.eq(
            product_prices,
            {
                product_1.product_id: '9.99',
                product_2.product_id: '11.22',
            },
            'Цены собрали все'
        )


async def test_no_prices(tap, dataset):
    with tap.plan(1, 'Цен для всех продуктов нет'):
        product_1 = await dataset.product()
        product_2 = await dataset.product()
        store = await dataset.store()

        product_prices = (
            await AssortmentContractorProduct.get_prices_for_products(
                store_id=store.store_id,
                product_ids=[product_1.product_id, product_2.product_id]
            )
        )

        tap.eq(
            product_prices,
            {}, 'Цен нет'
        )


async def test_zero_price(tap, dataset):
    with tap.plan(1, 'Цена нулевая'):
        product = await dataset.product()
        store = await dataset.store()
        contractor = await dataset.assortment_contractor(store=store)
        await dataset.assortment_contractor_product(
            product=product,
            assortment=contractor,
            price=0
        )

        product_prices = (
            await AssortmentContractorProduct.get_prices_for_products(
                store_id=store.store_id,
                product_ids=[product.product_id],
            )
        )

        tap.eq(
            product_prices,
            {
                product.product_id: 0
            },
            'Нулевая цена проходит'
        )


async def test_another_store(tap, dataset):
    with tap.plan(1, 'Цены для всех продуктов'):
        product_1 = await dataset.product()
        product_2 = await dataset.product()
        store = await dataset.store()
        another_store = await dataset.store()
        contractor_1 = await dataset.assortment_contractor(store=store)
        contractor_2 = await dataset.assortment_contractor(
            store=another_store)
        await dataset.assortment_contractor_product(
            product=product_1,
            assortment=contractor_1,
            price=9.99
        )
        await dataset.assortment_contractor_product(
            product=product_2,
            assortment=contractor_2,
            price=11.22
        )

        product_prices = (
            await AssortmentContractorProduct.get_prices_for_products(
                store_id=store.store_id,
                product_ids=[product_1.product_id, product_2.product_id]
            )
        )

        tap.eq(
            product_prices,
            {
                product_1.product_id: 9.99,
            },
            'Цена только в текущем складе'
        )


async def test_price_from_parent(tap, dataset):
    with tap.plan(1, 'Цену нашли из родителя'):
        parent_product = await dataset.product()
        product_1 = await dataset.product(parent_id=parent_product.product_id)
        product_2 = await dataset.product(parent_id=parent_product.product_id)
        store = await dataset.store()
        contractor = await dataset.assortment_contractor(store=store)
        await dataset.assortment_contractor_product(
            product=product_1,
            assortment=contractor,
            price=19.99
        )
        await dataset.assortment_contractor_product(
            product=parent_product,
            assortment=contractor,
            price=11.22
        )

        product_prices = (
            await AssortmentContractorProduct.get_prices_for_products(
                store_id=store.store_id,
                product_ids=[product_1.product_id, product_2.product_id]
            )
        )

        tap.eq(
            product_prices,
            {
                product_1.product_id: 19.99,
                product_2.product_id: 11.22
            },
            'Цена из родителя, если не нашли в ассортименте'
        )
