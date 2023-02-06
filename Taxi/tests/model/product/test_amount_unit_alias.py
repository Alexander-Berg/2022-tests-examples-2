import pytest


async def test_alias(tap, dataset):
    with tap:
        product = await dataset.product(amount_unit='gram')
        tap.ok(product, 'product created')

        tap.eq(product.amount_unit_alias, 'gram',
               'amount_unit used as alias')


async def test_fallback(tap, dataset):
    with tap:
        product = await dataset.product(amount_unit='__some_unit__')
        tap.ok(product, 'product created')

        tap.eq(product.amount_unit_alias, 'unit',
               'amount_unit_alias is a fallback value')


@pytest.mark.parametrize(['amount_unit', 'expected'], [
    ('г', 'gram'),
    ('кг.', 'kilogram'),
    (' таблетка.', 'unit'),
    ('-gram ', 'gram'),
    ('piece', 'unit'),
    ('unit', 'unit'),
    ('', 'unit'),
    (' 2313..', 'unit'),
    ('Кг', 'kilogram'),
    ('centiliter', 'centiliter')
])
async def test_mapping(tap, dataset, amount_unit, expected):
    with tap:
        product = await dataset.product(amount_unit=amount_unit)
        tap.ok(product, 'product created')

        tap.eq(product.amount_unit_alias, expected,
               f'{amount_unit} -> {expected}')
