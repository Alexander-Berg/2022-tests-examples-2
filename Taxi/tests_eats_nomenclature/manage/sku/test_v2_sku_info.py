import pytest

HANDLER = '/v2/manage/sku/info'


@pytest.mark.config(
    EATS_NOMENCLATURE_HANDLER_LIMIT_ITEMS={
        'api_v2_manage_sku_info_post': {'max_items_count': 10},
    },
)
async def test_response(
        taxi_eats_nomenclature,
        pg_realdict_cursor,
        sql_insert_sku,
        sql_insert_sku_pictures,
        sql_insert_brands,
):
    expected_sku_info = get_expected_sku_info()
    sql_insert_brands()
    for sku_info in expected_sku_info:
        sku_id = sql_insert_sku(sku_info, sku_info['id'])
        sql_insert_sku_attributes(pg_realdict_cursor, sku_id, sku_info)
        sql_insert_sku_pictures(sku_id, sku_info['images'])

    # add units to some nutrition values
    _sql_update_nutrition_values(
        pg_realdict_cursor,
        sku_uuid='sku_uuid_3',
        # invalid unit, no carbohydrates in response
        carbohydrates='2.1 кг',
        # ' г' should be removed
        proteins='5.6 г',
        # '  г ' should be removed
        fats='10  г ',
    )

    request_sku_ids = [
        'unknown_sku_uuid',
        'sku_uuid_1',
        'sku_uuid_2',
        'sku_uuid_3',
    ]
    response = await taxi_eats_nomenclature.post(
        HANDLER, json={'sku_ids': request_sku_ids},
    )
    assert response.status_code == 200

    assert _sorted(response.json()['sku_info']) == _sorted(expected_sku_info)


@pytest.mark.config(
    EATS_NOMENCLATURE_HANDLER_LIMIT_ITEMS={
        'api_v2_manage_sku_info_post': {'max_items_count': 3},
    },
)
async def test_requested_items_limit(taxi_eats_nomenclature):
    request_sku_ids = ['sku_uuid_1', 'sku_uuid_2', 'sku_uuid_3', 'sku_uuid_4']
    response = await taxi_eats_nomenclature.post(
        HANDLER, json={'sku_ids': request_sku_ids},
    )
    assert response.status_code == 400


def get_expected_sku_info():
    return [
        {
            'id': 'sku_uuid_1',
            'name': 'sku_name_1',
            'brand': 'brand_1',
            'weight': {'value': '100', 'unit': 'г'},
            'volume': {'value': '100'},
            'composition': 'composition_1',
            'calories': {'value': '100.12', 'unit': 'ккал'},
            'expiration_info': {'value': '24', 'unit': 'ч'},
            'country': 'country_1',
            'is_fresh': False,
            'is_adult': True,
            'images': [
                {'url': 'url_1', 'brand_slug': 'brand_slug_1'},
                {'url': 'url_2', 'brand_slug': 'brand_slug_2'},
            ],
            'fat_content': '1.1',
            'milk_type': 'Milk type 1',
            'cultivar': 'Cultivar 1',
            'flavour': 'Flavour 1',
            'meat_type': 'Meat type 1',
            'carcass_part': 'Carcass part 1',
            'egg_category': 'Egg category 1',
        },
        {
            'id': 'sku_uuid_2',
            'name': 'sku_name_2',
            'weight': {'value': '200'},
            'volume': {'value': '50', 'unit': 'мл'},
            'carbohydrates': '15.1',
            'proteins': '13.84',
            'fats': '12',
            'storage_requirements': 'storage_requirements_2',
            'package_info': 'package_info_2',
            'is_alcohol': True,
            'images': [
                {'url': 'url_3', 'brand_slug': 'brand_slug_1'},
                {'url': 'url_4'},
            ],
            'fat_content': '2.2',
            'milk_type': 'Milk type 2',
            'cultivar': 'Cultivar 2',
            'alco_grape_cultivar': 'Aco grape cultivar 1',
            'alco_aroma': 'Alco aroma 1',
            'alco_flavour': 'Alco flavour 1',
            'alco_pairing': 'Alco pairing 1',
        },
        {
            'id': 'sku_uuid_3',
            'name': 'sku_name_3',
            'images': [],
            'proteins': '5.6',
            'fats': '10',
            'flavour': 'Flavour 3',
            'meat_type': 'Meat type 3',
            'carcass_part': 'Carcass part 3',
            'egg_category': 'Egg category 3',
        },
    ]


def sql_insert_sku_attributes(pg_realdict_cursor, sku_id, sku_info):
    product_brand_id = 'null'
    product_type_id = 'null'
    if 'brand' in sku_info:
        pg_realdict_cursor.execute(
            f"""
        insert into eats_nomenclature.product_brands (
            value_uuid, value
        )
        values (
            'uuid_{sku_id}', '{sku_info['brand']}'
        )
        returning id
        """,
        )
        product_brand_id = pg_realdict_cursor.fetchall()[0]['id']

    if 'type' in sku_info:
        pg_realdict_cursor.execute(
            f"""
        insert into eats_nomenclature.product_types (
            value_uuid, value
        )
        values (
            'uuid_{sku_id}', '{sku_info['type']}'
        )
        returning id
        """,
        )
        product_type_id = pg_realdict_cursor.fetchall()[0]['id']

    pg_realdict_cursor.execute(
        f"""
        insert into eats_nomenclature.sku_attributes (
            sku_id, product_brand_id, product_type_id
        )
        values (
            {sku_id}, {product_brand_id}, {product_type_id}
        )
        """,
    )


def _sorted(data):
    for sku in data:
        sku['images'] = sorted(sku['images'], key=lambda item: item['url'])
    return sorted(data, key=lambda item: item['id'])


def _sql_update_nutrition_values(
        pg_realdict_cursor, sku_uuid, carbohydrates, proteins, fats,
):
    pg_realdict_cursor.execute(
        f"""
        update eats_nomenclature.sku
        set сarbohydrates = '{carbohydrates}',
            proteins =  '{proteins}',
            fats =  '{fats}'
        where uuid = '{sku_uuid}'
        """,
    )
