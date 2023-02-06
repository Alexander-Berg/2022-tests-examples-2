import pytest


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test(pgsql, load_json, activate_assortment, brand_task_enqueue):
    upload_data = load_json('upload_data.json')
    assert len(upload_data['items']) == 1
    place_id = 1
    await brand_task_enqueue('1', brand_nomenclature=upload_data)
    new_availabilities = [{'origin_id': 'item_origin_1', 'available': True}]
    new_stocks = [{'origin_id': 'item_origin_1', 'stocks': None}]
    new_prices = [
        {'origin_id': 'item_origin_1', 'price': '1000', 'currency': 'RUB'},
    ]
    await activate_assortment(
        new_availabilities, new_stocks, new_prices, place_id, '1',
    )

    # Upload item with the same origin_id, but with different property value
    # (this will update existing item)
    upload_data['items'][0]['measure']['value'] += 10
    expected_measure_value = upload_data['items'][0]['measure']['value']

    await brand_task_enqueue('1', brand_nomenclature=upload_data)

    await activate_assortment(
        new_availabilities, new_stocks, new_prices, place_id, '1',
    )

    assert sql_count_products(pgsql) == 1
    assert sql_count_place_products(pgsql) == 1
    assert (
        sql_get_product_measure(pgsql, 'item_origin_1')
        == expected_measure_value
    )


def sql_count_products(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select count(*)
        from eats_nomenclature.products
        """,
    )
    return list(cursor)[0][0]


def sql_get_product_measure(pgsql, origin_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select measure_value
        from eats_nomenclature.products
        where origin_id=%s
        """,
        (origin_id,),
    )
    ret = list(cursor)
    assert len(ret) == 1
    return ret[0][0]


def sql_count_place_products(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select count(*)
        from eats_nomenclature.places_products
        """,
    )
    return list(cursor)[0][0]
