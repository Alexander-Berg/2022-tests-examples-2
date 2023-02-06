import pytest


EMPTY_REQUEST: dict = {'product_ids': []}
EMPTY_RESPONSE: dict = {'products': []}
HANDLER = '/v1/products/info'
HEADERS = {'x-device-id': 'device_id'}

BRAND_ID = 777


@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'fill_products.sql'],
)
async def test_empty_request(taxi_eats_nomenclature):
    response = await taxi_eats_nomenclature.post(HANDLER, json=EMPTY_REQUEST)
    assert response.status == 200
    assert response.json() == EMPTY_RESPONSE


@pytest.mark.parametrize(
    'experiment', ['enabled', 'enabled_with_excluded_brands', 'disabled'],
)
@pytest.mark.parametrize('use_sku', [True, False, None])
@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'fill_products.sql'],
)
async def test_experiment(
        taxi_eats_nomenclature,
        load_json,
        sql_set_brand_fallback,
        experiments3,
        use_sku,
        experiment,
):
    experiment_data = load_json('use_sku_experiment.json')
    if experiment == 'enabled':
        experiment_data['experiments'][0]['match']['predicate'][
            'type'
        ] = 'true'
    elif experiment == 'enabled_with_excluded_brands':
        experiment_data['experiments'][0]['match']['predicate'][
            'type'
        ] = 'true'
        experiment_data['experiments'][0]['clauses'][0]['value'][
            'excluded_brand_ids'
        ] = [2]
    elif experiment == 'disabled':
        experiment_data['experiments'][0]['match']['predicate'][
            'type'
        ] = 'false'
    experiments3.add_experiments_json(experiment_data)

    sql_set_brand_fallback(
        brand_id=1,
        fallback_to_product_picture=True,
        fallback_to_product_vendor=True,
    )
    sql_set_brand_fallback(
        brand_id=2,
        fallback_to_product_picture=True,
        fallback_to_product_vendor=True,
    )

    unknown_public_id = '12345678-1ff2-4bc4-b78d-dcaa1f69b001'
    request = {
        'product_ids': [
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b005',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b006',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b008',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b009',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b010',
            unknown_public_id,
        ],
    }
    handler = HANDLER
    if use_sku is not None:
        handler += f'?use_sku={use_sku}'
    response = await taxi_eats_nomenclature.post(
        handler, json=request, headers=HEADERS,
    )

    assert response.status == 200
    response_json = response.json()
    response_json['products'].sort(key=lambda item: item['id'])
    if use_sku or use_sku is None and experiment == 'enabled':
        assert response_json == load_json('response_with_sku.json')
    elif use_sku is None and experiment == 'enabled_with_excluded_brands':
        assert response_json == load_json(
            'response_with_sku_and_disabled_brand.json',
        )
    else:
        assert response_json == load_json('response_without_sku.json')


@pytest.mark.parametrize(
    """use_sku, fallback_to_product_picture,
       fallback_to_product_vendor, response_file""",
    [
        (False, False, False, 'response_without_sku.json'),
        (False, False, True, 'response_without_sku.json'),
        (False, True, False, 'response_without_sku.json'),
        (False, True, True, 'response_without_sku.json'),
        (True, False, False, 'response_w_sku_no_vendor.json'),
        (True, False, True, 'response_with_sku.json'),
        (True, True, False, 'response_w_sku_no_vendor.json'),
        (True, True, True, 'response_with_sku.json'),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'fill_products.sql'],
)
async def test_200(
        taxi_eats_nomenclature,
        load_json,
        sql_set_brand_fallback,
        use_sku,
        fallback_to_product_picture,
        fallback_to_product_vendor,
        response_file,
):
    sql_set_brand_fallback(
        brand_id=1,
        fallback_to_product_picture=fallback_to_product_picture,
        fallback_to_product_vendor=fallback_to_product_vendor,
    )
    sql_set_brand_fallback(
        brand_id=2,
        fallback_to_product_picture=fallback_to_product_picture,
        fallback_to_product_vendor=fallback_to_product_vendor,
    )

    unknown_public_id = '12345678-1ff2-4bc4-b78d-dcaa1f69b001'
    request = {
        'product_ids': [
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b005',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b006',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b007',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b008',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b009',
            'bb231b95-1ff2-4bc4-b78d-dcaa1f69b010',
            unknown_public_id,
        ],
    }
    handler = HANDLER
    if use_sku is not None:
        handler += f'?use_sku={use_sku}'
    response = await taxi_eats_nomenclature.post(
        handler, json=request, headers=HEADERS,
    )

    assert response.status == 200
    response_json = response.json()
    response_json['products'].sort(key=lambda item: item['id'])

    expected_response = load_json(response_file)
    if not use_sku and not fallback_to_product_vendor:
        _remove_brands_from_response(expected_response)
    if use_sku and not fallback_to_product_picture:
        _remove_product_image_from_response(expected_response)

    assert response_json == expected_response


@pytest.mark.parametrize(
    """override_sku_type, response_file""",
    [
        ('override_with_null', 'response_override_without_sku.json'),
        ('override_with_sku', 'response_override_with_sku.json'),
        ('no_override', 'response_default_sku.json'),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'fill_products.sql'],
)
async def test_override_sku(
        taxi_eats_nomenclature,
        load_json,
        sql_set_brand_fallback,
        pgsql,
        # parametrize
        override_sku_type,
        response_file,
):
    product_id_to_override = 409
    if override_sku_type == 'override_with_null':
        sku_id_to_override_with = None
    elif override_sku_type == 'override_with_sku':
        sku_id_to_override_with = 4

    sql_set_brand_fallback(
        brand_id=1,
        fallback_to_product_picture=True,
        fallback_to_product_vendor=True,
    )
    sql_set_brand_fallback(
        brand_id=2,
        fallback_to_product_picture=True,
        fallback_to_product_vendor=True,
    )

    if override_sku_type != 'no_override':
        _sql_set_overriden_product_sku(
            pgsql, product_id_to_override, sku_id_to_override_with,
        )

    request = {'product_ids': ['bb231b95-1ff2-4bc4-b78d-dcaa1f69b009']}
    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?use_sku=true', json=request, headers=HEADERS,
    )

    assert response.status == 200
    response_json = response.json()
    response_json['products'].sort(key=lambda item: item['id'])

    expected_response = load_json(response_file)

    assert response_json == expected_response


@pytest.mark.parametrize(
    'test_sku_params, expected_partial_data',
    [
        pytest.param(
            {
                'is_alcohol': True,
                'brand': 'Бренд',
                'alco_grape_cultivar': 'Сорт',
                'alco_flavour': 'Вкус',
                'alco_aroma': 'Аромат',
                'alco_pairing': 'Пейринг',
            },
            {
                'general': (
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
            {
                'is_alcohol': True,
                'brand': 'Бренд',
                'alco_flavour': 'Вкус',
                'alco_aroma': 'Аромат',
                'alco_pairing': 'Пейринг',
            },
            {
                'general': (
                    'Состав: composition_sku_1<br>'
                    + 'Пищевая ценность на 100 г: белки 100, жиры 100, '
                    + 'углеводы 100, энергетическая ценность 100 ккал<br>'
                    + 'Срок хранения: 100 д<br>Условия хранения: sr_1'
                    + '<br>Бренд: Бренд'
                    + '<br>Вкус: Вкус'
                    + '<br>Аромат: Аромат'
                    + '<br>Пейринг: Пейринг'
                ),
            },
            id='alco_description_without_grape_cultivar',
        ),
        pytest.param(
            {
                'is_alcohol': True,
                'brand': 'Бренд',
                'alco_grape_cultivar': 'Сорт',
                'alco_aroma': 'Аромат',
                'alco_pairing': 'Пейринг',
            },
            {
                'general': (
                    'Состав: composition_sku_1<br>'
                    + 'Пищевая ценность на 100 г: белки 100, жиры 100, '
                    + 'углеводы 100, энергетическая ценность 100 ккал<br>'
                    + 'Срок хранения: 100 д<br>Условия хранения: sr_1'
                    + '<br>Бренд: Бренд'
                    + '<br>Сорт винограда: Сорт'
                    + '<br>Аромат: Аромат'
                    + '<br>Пейринг: Пейринг'
                ),
            },
            id='alco_description_without_flavour',
        ),
        pytest.param(
            {
                'is_alcohol': True,
                'brand': 'Бренд',
                'alco_grape_cultivar': 'Сорт',
                'alco_flavour': 'Вкус',
                'alco_pairing': 'Пейринг',
            },
            {
                'general': (
                    'Состав: composition_sku_1<br>'
                    + 'Пищевая ценность на 100 г: белки 100, жиры 100, '
                    + 'углеводы 100, энергетическая ценность 100 ккал<br>'
                    + 'Срок хранения: 100 д<br>Условия хранения: sr_1'
                    + '<br>Бренд: Бренд'
                    + '<br>Сорт винограда: Сорт'
                    + '<br>Вкус: Вкус'
                    + '<br>Пейринг: Пейринг'
                ),
            },
            id='alco_description_without_aroma',
        ),
        pytest.param(
            {
                'is_alcohol': True,
                'brand': 'Бренд',
                'alco_grape_cultivar': 'Сорт',
                'alco_flavour': 'Вкус',
                'alco_aroma': 'Аромат',
            },
            {
                'general': (
                    'Состав: composition_sku_1<br>'
                    + 'Пищевая ценность на 100 г: белки 100, жиры 100, '
                    + 'углеводы 100, энергетическая ценность 100 ккал<br>'
                    + 'Срок хранения: 100 д<br>Условия хранения: sr_1'
                    + '<br>Бренд: Бренд'
                    + '<br>Сорт винограда: Сорт'
                    + '<br>Вкус: Вкус'
                    + '<br>Аромат: Аромат'
                ),
            },
            id='alco_description_without_pairing',
        ),
        pytest.param(
            {
                'is_alcohol': False,
                'brand': 'Бренд',
                'alco_grape_cultivar': 'Сорт',
                'alco_flavour': 'Вкус',
                'alco_aroma': 'Аромат',
                'alco_pairing': 'Пейринг',
            },
            {
                'general': (
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
async def test_description(
        pg_cursor,
        taxi_eats_nomenclature,
        # parametrize
        test_sku_params,
        expected_partial_data,
):
    sku_id = _sql_add_sku(pg_cursor, **test_sku_params)
    test_product_params = {'sku_id': sku_id}
    public_id = _sql_add_product(pg_cursor, **test_product_params)

    response = await taxi_eats_nomenclature.post(
        HANDLER + '?use_sku=true',
        json={'product_ids': [public_id]},
        headers=HEADERS,
    )

    assert response.status == 200
    response_json = response.json()

    assert response_json['products'][0]['description'] == expected_partial_data


def _remove_brands_from_response(response):
    for product in response['products']:
        del product['brand']


def _remove_product_image_from_response(response):
    response['products'][1]['images'] = []


def _sql_set_overriden_product_sku(pgsql, product_id, sku_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """
        insert into overriden_product_sku(product_id, sku_id)
        values(%s, %s)
        """,
        (product_id, sku_id),
    )


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
        returning public_id
        """,
    )
    return pg_cursor.fetchone()[0]
