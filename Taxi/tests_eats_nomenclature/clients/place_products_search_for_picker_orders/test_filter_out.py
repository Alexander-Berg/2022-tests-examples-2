import pytest

BRAND_ID = 1
PLACE_ID = 1
HANDLER = '/v1/place/products/search-by-barcode-or-vendor-code'

BARCODE_TO_FILTER = '1'
BARCODE_TO_FIND = '2'
VENDOR_CODE = '1'


@pytest.mark.parametrize(
    'product_params',
    [
        pytest.param({'barcode': None}, id='missing barcode'),
        pytest.param({'barcode': ''}, id='single empty barcode'),
        pytest.param({'is_available': False}, id='unavailable'),
        pytest.param({'is_in_partner_category': False}, id='not in category'),
        pytest.param({'measure_unit': 'smth'}, id='unknown measure unit'),
        pytest.param(
            {'is_in_partner_category': False, 'is_in_promo_category': True},
            id='only in promo category',
        ),
        pytest.param({'brand_id': 9999}, id='wrong brand id'),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test(
        taxi_eats_nomenclature,
        pg_cursor,
        mock_core_max_overweight,
        # parametrize
        product_params,
):
    place_id = PLACE_ID

    # this product should be always present
    _sql_add_product(
        pg_cursor, vendor_code=VENDOR_CODE, barcode=BARCODE_TO_FIND,
    )
    # this product should be always filtered out
    _sql_add_product(pg_cursor, vendor_code=VENDOR_CODE, **product_params)

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={place_id}',
        json={
            'items': [
                {'barcode': None, 'vendor_code': VENDOR_CODE},
                {'barcode': BARCODE_TO_FILTER, 'vendor_code': None},
            ],
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert [i['vendor_code'] for i in response_json['matched_items']] == [
        VENDOR_CODE,
    ]
    assert [
        i['item']['barcode']['values'] for i in response_json['matched_items']
    ] == [[BARCODE_TO_FIND]]
    assert [i['barcode'] for i in response_json['not_matched_items']] == [
        BARCODE_TO_FILTER,
    ]


def _sql_add_product(
        pg_cursor,
        barcode=BARCODE_TO_FILTER,
        vendor_code=VENDOR_CODE,
        brand_id=BRAND_ID,
        is_available=True,
        is_in_partner_category=True,
        is_in_promo_category=False,
        measure_unit='GRM',
):
    place_id = PLACE_ID

    unique_key = f'{vendor_code}|{barcode}'

    if measure_unit == 'GRM':
        measure_unit_id = 1
    else:
        measure_unit_id = 999
        pg_cursor.execute(
            f"""
            insert into eats_nomenclature.measure_units(
                id,
                value,
                name
            )
            values ({measure_unit_id}, '{measure_unit}', '{measure_unit}')
            returning id
        """,
        )

    if brand_id != BRAND_ID:
        pg_cursor.execute(
            f"""
            insert into eats_nomenclature.brands(
                id,
                slug
            )
            values ({brand_id}, '{brand_id}')
        """,
        )

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
            0.2,
            {measure_unit_id},
            1000,
            false,
            false,
            true,
            {brand_id}
        )
        returning id
    """,
    )
    product_id = pg_cursor.fetchone()[0]

    if barcode is not None:
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

    if is_in_partner_category:
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

    if is_in_promo_category:
        category_name = 'promo_category_for_test'

        pg_cursor.execute(
            f"""
            insert into eats_nomenclature.categories_dictionary (id, name)
            values (999, '{category_name}')
            """,
        )

        pg_cursor.execute(
            f"""
            insert into eats_nomenclature.categories (
                assortment_id,
                name,
                origin_id,
                public_id,
                is_custom,
                is_base
            )
            values (
                1,
                '{category_name}',
                '{category_name}_origin',
                999,
                true,
                false
            )
            returning id
            """,
        )
        category_id = pg_cursor.fetchone()[0]

        pg_cursor.execute(
            f"""
            insert into eats_nomenclature.categories_relations (
                assortment_id,
                category_id,
                parent_category_id
            )
            values (1, {category_id}, null);
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
            values (1, {category_id}, {product_id}, 1)
        """,
        )

    pg_cursor.execute(
        f"""
        insert into eats_nomenclature.places_products(
            place_id,
            product_id,
            origin_id,
            price,
            vendor_code,
            available_from
        )
        values (
            {place_id},
            {product_id},
            '{unique_key}',
            999,
            '{vendor_code}',
            {'now()' if is_available else 'null'}
        )
        returning id
    """,
    )
