
async def test_dataset(tap, cfg, dataset):

    day   = cfg('business.product.valid_type.day')
    short = cfg('business.product.valid_type.short') - 1
    long  = cfg('business.product.valid_type.short') + 1

    with tap.plan(5):
        with await dataset.product(valid=None) as product:
            tap.eq(product.valid_type, 'long', 'Долгий')

        with await dataset.product(valid=1) as product:
            tap.eq(product.valid_type, 'day', 'Дневной')

        with await dataset.product(valid=day) as product:
            tap.eq(product.valid_type, 'day', 'Дневной')

        with await dataset.product(valid=short) as product:
            tap.eq(product.valid_type, 'short', 'Короткий')

        with await dataset.product(valid=long) as product:
            tap.eq(product.valid_type, 'long', 'Долгий')
