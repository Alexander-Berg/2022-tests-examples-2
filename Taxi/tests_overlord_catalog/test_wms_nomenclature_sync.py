import pytest


@pytest.mark.pgsql('overlord_catalog', files=[])
@pytest.mark.suspend_periodic_tasks('wms-nomenclature-sync-periodic')
async def test_basic(taxi_overlord_catalog, pgsql, mockserver, load_json):
    @mockserver.json_handler('/grocery-wms/api/external/products/v1/products')
    def mock_wms_products(request):
        if request.json['cursor']:
            return load_json('wms_products_response_end.json')
        return load_json('wms_products_response_1.json')

    @mockserver.json_handler('/grocery-wms/api/external/products/v1/groups')
    def mock_wms_categories(request):
        if request.json['cursor']:
            return load_json('wms_categories_response_end.json')
        return load_json('wms_categories_response_1.json')

    await taxi_overlord_catalog.run_periodic_task(
        'wms-nomenclature-sync-periodic',
    )
    assert mock_wms_products.times_called == 2
    assert mock_wms_categories.times_called == 2

    db = pgsql['overlord_catalog']
    cursor = db.cursor()
    cursor.execute(
        'SELECT product_id, title, amount, amount_unit, amount_unit_alias, '
        'manufacturer, country, brand, pfc, shelf_conditions, '
        'checkout_limit, shelf_life_measure_unit, measurements, '
        'country_of_origin, barcodes, ranks, important_ingredients, '
        'main_allergens, photo_stickers, custom_tags, logistic_tags, '
        'mark_count_pack, recycling_codes, private_label, supplier_tin '
        'from catalog_wms.goods order by 1, 2',
    )
    result = cursor.fetchall()
    assert result == [
        (
            '0464039a182c4487ac9fec55c4db8663000300010000',
            'Молоко пастеризованное отборное 3,4-4% ПРОСТОКВАШИНО 930 мл',
            930.0000,
            'мл',
            'millilitre',
            'some company',
            'country 1',
            'brand 1',
            '{"(protein,2.9000)","(fat,3.4000)",'
            '"(calories,61.0000)","(carbohydrate,4.7000)"}',
            '{"(shelf_life,11)","(store_conditions,sc1)",'
            '"(store_lo_temp,-10)","(store_hi_temp,-2)"}',
            1,
            'DAY',
            '(1,2,3,4,5)',
            ['RUS', 'BLR', 'MDG'],
            [],
            [50],
            ['milk'],
            ['lactose'],
            [],
            [],
            ['hot'],
            2,
            ['code_1', 'code_2'],
            True,
            'supplier-tin',
        ),
        (
            '6635df418e2e451ca6dcdcae31112c4f000200010000',
            'Кефир 1% ДОМИК В ДЕРЕВНЕ 515 г',
            515.0000,
            'г',
            'gram',
            'some company',
            'country 2',
            'brand 2',
            '{"(protein,3.0000)","(fat,1.0000)",'
            '"(calories,37.0000)","(carbohydrate,4.0000)"}',
            '{"(after_open,2)","(shelf_life,22)",'
            '"(write_off_before,2)","(store_conditions,sc2)"}',
            None,
            'DAY',
            '(10,,11,,12)',
            [],
            [],
            [50],
            ['milk'],
            ['lactose'],
            [],
            [],
            [],
            1,
            [],
            False,
            None,
        ),
        (
            '85822e27baca410e9334133bac1529f3000200010000',
            'Био баланс кефирный 0% ЮНИМИЛК 930 г',
            930.0000,
            'г',
            'gram',
            'some company',
            'country 3',
            'brand 3',
            '{"(protein,3.3000)","(fat,1.0000)",'
            '"(calories,40.0000)","(carbohydrate,4.4000)"}',
            '{"(after_open,3)","(shelf_life,33)",'
            '"(write_off_before,3)","(store_conditions,sc3)"}',
            None,
            'DAY',
            '(,,,,)',
            [],
            ['4680017927000'],
            [1234],
            ['milk'],
            ['lactose'],
            [],
            [],
            ['fragile', 'hot'],
            1,
            [],
            False,
            None,
        ),
    ]

    cursor = db.cursor()
    cursor.execute(
        'SELECT category_id, name, status, external_id '
        'from catalog_wms.categories order by 1, 2',
    )
    result = cursor.fetchall()
    assert result == [
        (
            '782757185fcf494290d7365c2f3dbf99000300010000',
            'Сметана',
            'active',
            'category_external_id',
        ),
        (
            '7d22d55fa8f140ebb92bf48b5e09ca62000200010000',
            'Сливки',
            'disabled',
            None,
        ),
        (
            'ecab35392a2944388f9b941eaf9e7834000200010000',
            'Масло',
            'active',
            None,
        ),
    ]

    with_timetable = '782757185fcf494290d7365c2f3dbf99000300010000'
    cursor = db.cursor()
    cursor.execute(
        f"""SELECT timetable from catalog_wms.categories
            where category_id = \'{with_timetable}\'""",
    )
    result = cursor.fetchall()
    assert result == [('{"(monday,\\"(07:00:00,00:00:00)\\")"}',)]
