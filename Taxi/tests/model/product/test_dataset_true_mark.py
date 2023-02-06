from libstall.util.barcode import true_mark_unpack
from stall.model.product import Product

async def test_dataset_product_true_mark(tap, dataset):
    with tap.plan(25, 'проверяем создание продукта с честным знаком'):
        p1 = await dataset.product(true_mark=False)
        p2 = await dataset.product(
            true_mark=True, vars={'imported': {'lol': 'kek'}}
        )
        for p in (p1, p2):
            tap.eq(len(p.barcode), 2, 'два баркода')
            tap.ok(any(len(b) == 13 for b in p.barcode), 'len13-barcode')
            tap.ok(any(len(b) == 14 for b in p.barcode), 'len14-barcode')

        tap.ok(not p1.vars('imported.true_mark'), 'нету честного знака')
        tap.ok(p2.vars('imported.true_mark'), 'есть честный знак')
        tap.eq(p2.vars('imported.lol'), 'kek', 'варсы не перезаписались')

        p = await dataset.product(true_mark=False, barcode=[])
        tap.eq(len(p.barcode), 2, 'все равно есть два баркода :)')
        p = await dataset.product(barcode=[])
        tap.eq(len(p.barcode), 0, 'а так нету')

        bar12 = '7'*12
        prefix_variants = ['777', '0777', '77', '70', '07', '00', '']
        barcodes = [prefix + bar12 for prefix in prefix_variants]

        ps = [
            await dataset.product(true_mark=True, barcode=[b])
            for b in barcodes
        ]
        for p in ps:
            tap.ok(
                any(len(b) == 13 and b[0] != '0' for b in p.barcode),
                'len13-barcode'
            )
            tap.ok(
                any(len(b) == 14 and b[0] == '0' for b in p.barcode),
                'len14-barcode'
            )


async def test_true_mark_value(tap, dataset, uuid):
    with tap.plan(16, 'проверяем генерацию честного знака'):
        bar12 = uuid()[:12]
        prefix_variants = ['777', '0777', '77', '70', '07', '00', '']
        barcodes = [prefix + bar12 for prefix in prefix_variants]
        ps = [
            await dataset.product(true_mark=True, barcode=[b])
            for b in barcodes
        ] + [await dataset.product(true_mark=True, barcode=[])]

        for p in ps:
            gs_codes = [
                await dataset.true_mark_value(product_id=p.product_id),
                await dataset.true_mark_value(product=p),
            ]
            for gs_code in gs_codes:
                true_mark_dict = true_mark_unpack(gs_code)

                possible_products = (await Product.list(
                    by='barcode',
                    barcode=true_mark_dict['barcode'],
                    full=True,
                )).list
                poss_pids = {pp.product_id for pp in possible_products}
                tap.ok(p.product_id in poss_pids, 'продукт найден по баркоду')
