import pytest
from ymlcfg.jpath import JPath


@pytest.mark.parametrize(
    'test_input,expected',
    [
        (
            {
                'grade1': [{'data': 'netto'}],
                'grade2': [{'data': 'color'}],
                'grade3': [{'data': 'shape'}],
                'grade_size': [{'data': 'L'}],
            },
            {
                'grade_values': ['netto', 'color', 'shape'],
                'grade_size': 'L',
                'grade_order': 0,
            },
        ),
    ]
)
async def test_sync_grades_basic(
        tap, load_json, uuid, test_input, expected, prod_sync
):
    with tap.plan(3, 'проверяем наличие родителя и грейдов'):
        a_product = load_json('data/product.pigeon.json')
        a_product['skuId'] = uuid()

        if test_input:
            for k, v in test_input.items():
                a_product['attributes'][k] = v[0]['data']

        product = await prod_sync.prepare_obj(JPath(a_product))
        await product.save()

        imported = product.vars['imported']
        tap.eq(
            imported['grade_values'],
            expected['grade_values'],
            'grade_values',
        )
        tap.eq(
            str(imported['grade_size']),
            str(expected['grade_size']),
            'grade_size',
        )
        tap.eq(
            imported['grade_order'],
            expected['grade_order'],
            'grade_order',
        )


@pytest.mark.parametrize(
    'test_input,expected',
    [
        (
            {
                'parent': [
                    {
                        'grade1': [{'data': 'netto'}],
                        'grade2': [{'data': 'color'}],
                    },
                    {'identifier': "1"},
                ],
                'product1': [
                    {
                        'grade_size': [{'data': 'S'}],
                        'grade_order': [{'data': 10}],
                        'parentItem': [{'data': '1'}],
                        'netto': [{'data': '100'}],
                        'color': [{'data': 'очень красный'}],
                    }
                ],
                'product2': [
                    {
                        'grade_size': [{'data': 'S'}],
                        'grade_order': [{'data': 11}],
                        'parentItem': [{'data': '1'}],
                        'netto': [{'data': '100'}],
                        'color': [{'color_data': None}],
                    }
                ],
                'product3': [
                    {
                        'grade_size': [{'data': 'M'}],
                        'grade_order': [{'data': 20}],
                        'parentItem': [{'data': '1'}],
                        'netto': [{'data': '500'}],
                        'color': [{'data': 'цвет попки младенца'}],
                    }
                ],
                'product4': [
                    {
                        'grade_size': [{'data': None}],
                        'grade_order': [{'data': None}],
                        'parentItem': [{'data': '1'}],
                        'netto': [{'data': '500'}],
                        'color': [{'data': 'цвет попки младенца'}],
                    }
                ],
            },
            {
                'parent': {
                    'grade_values': ['netto', 'color'],
                    'grade_size': None,
                    'grade_order': 0,
                },
                'product1': {
                    'grade_values': ['100', 'очень красный'],
                    'grade_size': 'S',
                    'grade_order': 10,
                },
                'product3': {
                    'grade_values': ['500', 'цвет попки младенца'],
                    'grade_size': 'M',
                    'grade_order': 20,
                },
                'product4': {
                    'grade_values': ['500', 'цвет попки младенца'],
                    'grade_size': None,
                    'grade_order': 0,
                },
            },
        ),
    ]
)
async def test_sync_grades_properties(
        tap, load_json, test_input, expected, prod_sync, uuid):
    with tap.plan(13, 'проверяем наличие родителя и грейдов'):
        pp_id = uuid()

        if test_input:
            products = []

            for p, i in test_input.items():
                a_product = load_json('data/product.pigeon.json')
                if 'parent' in p:
                    a_product['skuId'] = pp_id
                for k, v in i[0].items():
                    if 'data' in v[0]:
                        a_product['attributes'][k] = v[0]['data']
                if 'product' in p:
                    a_product['skuId'] = uuid()
                    a_product['attributes']['parentItem'] = pp_id
                product = await prod_sync.prepare_obj(JPath(a_product))
                if product:
                    await product.save()
                products.append(product)

        # проверяем родителя
        tap.eq(
            products[0].vars['imported']['grade_values'],
            expected['parent']['grade_values'],
            'parent grade_values',
        )
        tap.eq(
            products[0].vars['imported']['grade_order'],
            expected['parent']['grade_order'],
            'parent grade_order',
        )
        tap.eq(
            products[0].vars['imported']['grade_size'],
            expected['parent']['grade_size'],
            'parent grade_size',
        )
        # проверяем детей, продукта2 не должно существовать
        for i, p in enumerate(products[1:]):
            if i+1 != 2:
                tap.eq(
                    p.vars['imported']['grade_values'],
                    expected[f'product{i+1}']['grade_values'],
                    f'product{i+1} grade_values',
                )
                tap.eq(
                    p.vars['imported']['grade_order'],
                    expected[f'product{i+1}']['grade_order'],
                    f'product{i+1} grade_order',
                )
                tap.eq(
                    p.vars['imported']['grade_size'],
                    expected[f'product{i+1}']['grade_size'],
                    f'product{i+1} grade_size',
                )
        # проверяем что продукта 2 нет
        tap.eq(products[2], None, 'product2 does not exist')
