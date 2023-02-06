import pytest

BRAND_ID = 1
PLACE_ID = 1
HANDLER = '/v1/place/products/search-by-barcode-or-vendor-code'

BARCODE = '1'
VENDOR_CODE = '1'


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'fill_data_for_full_response.sql',
    ],
)
async def test_full_schema(
        taxi_eats_nomenclature, load_json, mock_core_max_overweight,
):
    """
    Test a schema with all posible fields filled
    (and multiple values where possible)
    """
    place_id = PLACE_ID

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={place_id}',
        json={
            'items': [
                {'barcode': 'unknown_1', 'vendor_code': '1'},
                {'barcode': 'unknown_2', 'vendor_code': '2'},
                {'barcode': 'unknown_3', 'vendor_code': 'unknown'},
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json('full_response.json')


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_place_data.sql',
        'fill_data_for_minimal_response.sql',
    ],
)
async def test_minimal_schema(
        taxi_eats_nomenclature, load_json, mock_core_max_overweight,
):
    """
    Test a schema with minimal posible fields filled
    """
    place_id = PLACE_ID

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={place_id}',
        json={
            'items': [
                {'barcode': None, 'vendor_code': '1'},
                {'barcode': None, 'vendor_code': '2'},
                {'barcode': None, 'vendor_code': 'unknown'},
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json('minimal_response.json')


@pytest.mark.parametrize(
    'test_params,expected_partial_data',
    [
        pytest.param(
            {'measure_unit': 'KGRM', 'measure_value': 1},
            {'measure/unit': 'GRM', 'measure/value': 1000},
            id='kgrm to grm',
        ),
        pytest.param(
            {'measure_unit': 'LT', 'measure_value': 1},
            {'measure/unit': 'MLT', 'measure/value': 1000},
            id='lt to mlt',
        ),
        pytest.param(
            {'is_catch_weight': False, 'quantum': 0.3},
            {'measure/quantum': 1, 'is_catch_weight': False},
            id='quantum when not catch weight',
        ),
        pytest.param(
            {
                'measure_unit': 'GRM',
                'measure_value': 1000,
                'max_overweight': 50,
                'is_catch_weight': True,
                'quantum': 0.5,
            },
            {'measure/max_overweight': 500},
            id='max overweight when catch weight',
        ),
        pytest.param(
            {
                'measure_unit': 'GRM',
                'measure_value': 1000,
                'max_overweight': 50,
                'is_catch_weight': False,
                'quantum': 0.5,
            },
            {'measure/max_overweight': 500},
            id='max overweight when not catch weight',
        ),
        pytest.param(
            {'price': '99.99', 'include_pennies': True},
            {'price': '99.99'},
            id='include pennies',
        ),
        pytest.param(
            {'price': '99.99', 'include_pennies': False},
            {'price': '100'},
            id='do not include pennies',
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_specific_values(
        taxi_eats_nomenclature,
        pg_cursor,
        update_taxi_config,
        mock_core_max_overweight,
        # parametrize
        test_params,
        expected_partial_data,
):
    place_id = PLACE_ID
    if 'max_overweight' in test_params:
        mock_core_max_overweight.add_data(
            place_id, test_params['max_overweight'],
        )
        test_params.pop('max_overweight')
    if 'include_pennies' in test_params:
        update_taxi_config(
            'EATS_NOMENCLATURE_PRICE_ROUNDING',
            {
                str(BRAND_ID): {
                    'should_include_pennies_in_price': test_params[
                        'include_pennies'
                    ],
                },
            },
        )
        test_params.pop('include_pennies')

    _sql_add_product(pg_cursor, **test_params)

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={place_id}',
        json={'items': [{'barcode': BARCODE, 'vendor_code': VENDOR_CODE}]},
    )
    assert response.status_code == 200
    _verify_response_part(response.json(), **expected_partial_data)


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_empty_response(
        taxi_eats_nomenclature, load_json, mock_core_max_overweight,
):
    place_id = PLACE_ID

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={place_id}',
        json={'items': [{'barcode': None, 'vendor_code': None}]},
    )
    assert response.json() == load_json('empty_response.json')


def _verify_response_part(response, **kwargs):
    for argpath, expected_argvalue in kwargs.items():
        split_argpath = argpath.split('/')
        val = response['matched_items'][0]['item']
        for i in split_argpath:
            val = val[i]
        if isinstance(expected_argvalue, list):
            assert sorted(val) == sorted(expected_argvalue)
        else:
            assert val == expected_argvalue


def _sql_add_product(
        pg_cursor,
        measure_unit='GRM',
        measure_value=1000,
        quantum=1,
        is_catch_weight=False,
        price=1000,
):
    place_id = PLACE_ID
    vendor_code = VENDOR_CODE
    barcode = BARCODE

    unique_key = f'{vendor_code}|{barcode}'

    pg_cursor.execute(
        f"""
        select id
        from eats_nomenclature.measure_units
        where value = '{measure_unit}'
    """,
    )
    measure_unit_id = pg_cursor.fetchone()[0]

    pg_cursor.execute(
        f"""
        insert into eats_nomenclature.products(
            origin_id,
            description,
            shipping_type_id,
            vendor_id,
            name,
            quantum,
            measure_unit_id,
            measure_value,
            adult,
            is_catch_weight,
            is_choosable,
            brand_id
        )
        values (
            '{unique_key}',
            'descr_{unique_key}',
            1,
            1,
            'name_{unique_key}',
            {quantum},
            {measure_unit_id},
            {measure_value},
            false,
            {is_catch_weight},
            true,
            {BRAND_ID}
        )
        returning id
    """,
    )
    product_id = pg_cursor.fetchone()[0]

    pg_cursor.execute(
        f"""
        insert into eats_nomenclature.barcodes(
            unique_key,
            value
        )
        values ('{barcode}', '{barcode}')
        returning id
    """,
    )
    barcode_id = pg_cursor.fetchone()[0]

    pg_cursor.execute(
        f"""
        insert into eats_nomenclature.product_barcodes(
            product_id,
            barcode_id
        )
        values ({product_id}, {barcode_id})
    """,
    )

    pg_cursor.execute(
        f"""
        insert into eats_nomenclature.categories_products(
            assortment_id,
            category_id,
            product_id,
            sort_order
        )
        values (1, 1, {product_id}, 1)
    """,
    )

    pg_cursor.execute(
        f"""
        insert into eats_nomenclature.places_products(
            place_id,
            product_id,
            origin_id,
            price,
            old_price,
            vendor_code,
            available_from
        )
        values (
            {place_id},
            {product_id},
            '{unique_key}',
            {price},
            null,
            '{vendor_code}',
            now()
        )
        returning id
    """,
    )

    return product_id
