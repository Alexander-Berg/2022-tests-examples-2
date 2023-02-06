import pytest

BRAND_ID = 777


@pytest.mark.experiments3(filename='use_sku_experiment.json')
@pytest.mark.parametrize(
    'test_product_params, test_sku_params, expected_partial_data',
    [
        pytest.param(
            {'measure_unit': 'KGRM', 'measure_value': 1},
            None,
            {'measure_in_grams': 1000},
            id='kgrm to grm',
        ),
        pytest.param(
            {'measure_unit': 'LT', 'measure_value': 1},
            None,
            {'measure_in_milliliters': 1000},
            id='lt to mlt',
        ),
        pytest.param(
            {
                'measure_unit': 'GRM',
                'measure_value': 1000,
                'is_catch_weight': True,
                'quantum': 0.5,
            },
            None,
            {'measure_in_grams': 500},
            id='measure for weighted item',
        ),
        pytest.param(
            {
                'measure_unit': 'GRM',
                'measure_value': 1000,
                'is_catch_weight': False,
                'quantum': 0.5,
            },
            None,
            {'measure_in_grams': 1000},
            id='measure for not weighted item',
        ),
        pytest.param(
            {
                'measure_unit': 'GRM',
                'measure_value': 1000,
                'is_catch_weight': True,
            },
            {'weight': '700 г'},
            {'measure_in_grams': 1000},
            id='measure from sku for weighted item',
        ),
        pytest.param(
            {
                'measure_unit': 'GRM',
                'measure_value': 1000,
                'is_catch_weight': False,
            },
            {'weight': '700 г'},
            {'measure_in_grams': 700},
            id='measure from sku for not weighted item',
        ),
        pytest.param(
            {'volume_unit': 'CMQ', 'volume_value': 1},
            None,
            {'volume': 1},
            id='cmq to cmq',
        ),
        pytest.param(
            {'volume_unit': 'DMQ', 'volume_value': 1},
            None,
            {'volume': 1000},
            id='dmq to cmq',
        ),
        pytest.param(
            {'shipping_type': 'delivery'},
            None,
            {'is_delivery_available': True, 'is_pickup_available': False},
            id='delivery shipping type',
        ),
        pytest.param(
            {'shipping_type': 'pickup'},
            None,
            {'is_delivery_available': False, 'is_pickup_available': True},
            id='pickup shipping type',
        ),
        pytest.param(
            {'name': 'item_1'},
            {'alternate_name': 'item_sku_1'},
            {'name': 'item_sku_1'},
            id='name from sku',
        ),
        pytest.param(
            {'description': 'descr_1'},
            {},
            {
                'description': (
                    'Состав: composition_sku_1<br>'
                    + 'Пищевая ценность на 100 г: белки 100, жиры 100, '
                    + 'углеводы 100, энергетическая ценность 100 ккал<br>'
                    + 'Срок хранения: 100 д<br>Условия хранения: sr_1'
                ),
            },
            id='description from sku',
        ),
        pytest.param(
            {'adult': False},
            {'is_adult': True},
            {'is_adult': True},
            id='adult from sku adult',
        ),
        pytest.param(
            {'adult': False},
            {'is_alcohol': True},
            {'is_adult': True},
            id='adult from alcohol',
        ),
        pytest.param(
            {'adult': True},
            {},
            {'is_adult': False},
            id='ignore products adult',
        ),
        pytest.param(
            {'pictures': ['url_1', 'url_2']},
            {'pictures': ['sku_url_1']},
            {'image_urls': ['sku_url_1']},
            id='picture from sku',
        ),
        pytest.param(
            {},
            {
                'is_alcohol': True,
                'brand': 'Бренд',
                'alco_grape_cultivar': 'Сорт',
                'alco_flavour': 'Вкус',
                'alco_aroma': 'Аромат',
                'alco_pairing': 'Пейринг',
            },
            {
                'description': (
                    'Состав: composition_sku_1<br>'
                    + 'Пищевая ценность на 100 г: белки 100, жиры 100, '
                    + 'углеводы 100, энергетическая ценность 100 ккал<br>'
                    + 'Срок хранения: 100 д<br>Условия хранения: sr_1'
                    + '<br>Бренд: Бренд'
                    + '<br>Сорт винограда: Сорт'
                    + '<br>Вкус: Вкус'
                    + '<br>Аромат: Аромат'
                    + '<br>Пейринг: Пейринг'
                ),
            },
            id='alco_description',
        ),
        pytest.param(
            {},
            {
                'is_alcohol': False,
                'brand': 'Бренд',
                'alco_grape_cultivar': 'Сорт',
                'alco_flavour': 'Вкус',
                'alco_aroma': 'Аромат',
                'alco_pairing': 'Пейринг',
            },
            {
                'description': (
                    'Состав: composition_sku_1<br>'
                    + 'Пищевая ценность на 100 г: белки 100, жиры 100, '
                    + 'углеводы 100, энергетическая ценность 100 ккал<br>'
                    + 'Срок хранения: 100 д<br>Условия хранения: sr_1'
                ),
            },
            id='not_alco_description_with_filled_alco_fields',
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_brand_data.sql'],
)
async def test_specific_values(
        generate_product_snapshot_from_row,
        pg_cursor,
        put_products_snapshot_task_into_stq,
        sorted_logged_data,
        testpoint,
        verify_logged_part,
        # parametrize
        test_product_params,
        test_sku_params,
        expected_partial_data,
):
    if test_sku_params is not None:
        sku_id = _sql_add_sku(pg_cursor, **test_sku_params)
        test_product_params['sku_id'] = sku_id
    _sql_add_product(pg_cursor, **test_product_params)

    logged_data = []

    @testpoint('export-products-snapshot')
    def yt_logger(row):
        logged_data.append(generate_product_snapshot_from_row(row))

    await put_products_snapshot_task_into_stq(
        brand_id=BRAND_ID, task_id=str(BRAND_ID),
    )
    assert yt_logger.has_calls

    verify_logged_part(sorted_logged_data(logged_data), expected_partial_data)


def _sql_add_sku(
        pg_cursor,
        alternate_name='item_sku_1',
        composition='composition_sku_1',
        carbohydrates='100',
        proteins='100',
        fats='100',
        calories='100 ккал',
        expiration_info='100 д',
        storage_requirements='sr_1',
        weight='100 г',
        is_alcohol=False,
        is_adult=False,
        pictures=None,
        alco_grape_cultivar=None,
        alco_flavour=None,
        alco_aroma=None,
        alco_pairing=None,
        brand=None,
):
    pg_cursor.execute(
        f"""
        insert into eats_nomenclature.sku(
            alternate_name,
            composition,
            сarbohydrates,
            proteins,
            fats,
            calories,
            expiration_info,
            storage_requirements,
            weight,
            is_alcohol,
            is_adult,
            alco_grape_cultivar,
            alco_flavour,
            alco_aroma,
            alco_pairing
        )
        values (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        returning id
        """,
        (
            alternate_name,
            composition,
            carbohydrates,
            proteins,
            fats,
            calories,
            expiration_info,
            storage_requirements,
            weight,
            is_alcohol,
            is_adult,
            alco_grape_cultivar,
            alco_flavour,
            alco_aroma,
            alco_pairing,
        ),
    )
    sku_id = pg_cursor.fetchone()[0]

    if brand:
        pg_cursor.execute(
            f"""
            insert into eats_nomenclature.product_brands(
                value, value_uuid
            )
            values ('{brand}', '00000000-0000-0000-0000-000000000001')
            returning id
            """,
        )
        product_brand_id = pg_cursor.fetchone()[0]

        pg_cursor.execute(
            f"""
            insert into eats_nomenclature.sku_attributes(
                sku_id,
                product_brand_id
            )
            values ({sku_id}, {product_brand_id})
            """,
        )

    if pictures:
        for url in pictures:
            pg_cursor.execute(
                f"""
                insert into eats_nomenclature.pictures(
                    url,
                    processed_url
                )
                values ('{url}', '{url}')
                returning id
                """,
            )
            picture_id = pg_cursor.fetchone()[0]

            pg_cursor.execute(
                f"""
                insert into eats_nomenclature.sku_pictures(
                    sku_id,
                    picture_id
                )
                values ({sku_id}, {picture_id})
                """,
            )

    return sku_id


def _sql_add_product(
        pg_cursor,
        origin_id='item_origin_1',
        name='item_1',
        description='descr_1',
        adult=False,
        measure_unit='GRM',
        measure_value=1000,
        quantum=1,
        is_catch_weight=False,
        volume_unit='CMQ',
        volume_value=1000,
        shipping_type='all',
        sku_id=None,
        pictures=None,
):
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
        select id
        from eats_nomenclature.volume_units
        where value = '{volume_unit}'
    """,
    )
    volume_unit_id = pg_cursor.fetchone()[0]

    pg_cursor.execute(
        f"""
        select id
        from eats_nomenclature.shipping_types
        where value = '{shipping_type}'
    """,
    )
    shipping_type_id = pg_cursor.fetchone()[0]

    pg_cursor.execute(
        f"""
        insert into eats_nomenclature.products(
            brand_id,
            origin_id,
            name,
            description,
            adult,
            quantum,
            measure_unit_id,
            measure_value,
            is_catch_weight,
            volume_unit_id,
            volume_value,
            shipping_type_id,
            sku_id
        )
        values (
            {BRAND_ID},
            '{origin_id}',
            '{name}',
            '{description}',
            {adult},
            {quantum},
            {measure_unit_id},
            {measure_value},
            {is_catch_weight},
            {volume_unit_id},
            {volume_value},
            {shipping_type_id},
            {'null' if sku_id is None else sku_id}
        )
        returning id
        """,
    )
    product_id = pg_cursor.fetchone()[0]

    if pictures:
        for url in pictures:
            pg_cursor.execute(
                f"""
                insert into eats_nomenclature.pictures(
                    url,
                    processed_url
                )
                values ('{url}', '{url}')
                returning id
                """,
            )
            picture_id = pg_cursor.fetchone()[0]

            pg_cursor.execute(
                f"""
                insert into eats_nomenclature.product_pictures(
                    product_id,
                    picture_id
                )
                values ({product_id}, {picture_id})
                """,
            )

    return product_id
