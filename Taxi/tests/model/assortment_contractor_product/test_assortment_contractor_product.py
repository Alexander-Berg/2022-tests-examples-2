from stall.model.assortment_contractor_product import (
    AssortmentContractorProduct
)


async def test_acp(tap, dataset, uuid):
    with tap.plan(4):

        product = await dataset.product()
        ass = await dataset.assortment_contractor()

        acp = AssortmentContractorProduct({
            'assortment_id': ass.assortment_id,
            'contractor_id': uuid(),
            'product_id': product.product_id,
            'cursor': uuid(),
        })

        tap.ok(acp, 'Инстанцирован')
        tap.ok(not acp.acp_id, 'идентификатора пока нет')
        tap.ok(await acp.save(), 'Сохранён в БД')
        tap.ok(acp.acp_id, 'идентификатор')


async def test_dataset(tap, dataset):
    with tap.plan(4):
        acp = await dataset.assortment_contractor_product()
        tap.ok(acp, 'ассортимент создан')
        tap.ok(acp.acp_id, 'есть айди')
        tap.ok(acp.assortment_id, 'есть ассортимент')
        tap.ok(acp.product_id, 'есть продукт')
