HANDLER = '/v1/manage/sku/create'


async def test_201(
        taxi_eats_nomenclature,
        pg_realdict_cursor,
        sql_select_sku_data,
        sql_insert_brands,
        generate_sku_data,
):
    # Generate sku data.
    images = [{'url': 'url_1', 'brand_slug': 'brand_slug_1'}, {'url': 'url_2'}]
    sku_data = generate_sku_data(
        index=1,
        weight_unit='кг',
        volume_unit='л',
        calories_unit='кал',
        expiration_info_unit='ч',
        is_alcohol=True,
        is_fresh=False,
        is_adult=None,
        images=images,
        generate_attributes=True,
    )
    sql_insert_brands()

    response = await taxi_eats_nomenclature.post(HANDLER, json=sku_data)
    assert response.status_code == 201
    sku_uuid = response.json()['sku_id']

    sku_id = sql_select_sku_id_by_uuid(pg_realdict_cursor, sku_uuid)
    assert sql_select_sku_data(sku_id) == sku_data


def sql_select_sku_id_by_uuid(pg_realdict_cursor, sku_uuid):
    pg_realdict_cursor.execute(
        f"""
        select id from eats_nomenclature.sku
        where uuid = '{sku_uuid}'
        """,
    )
    rows = pg_realdict_cursor.fetchall()
    return rows[0]['id'] if rows else None
