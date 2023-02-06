import pytest

HANDLER = '/v1/manage/sku/update'


@pytest.mark.parametrize('update_new_fields', [True, False, None])
async def test_200(
        taxi_eats_nomenclature,
        sql_insert_sku,
        sql_insert_sku_pictures,
        sql_insert_brands,
        sql_select_sku_data,
        generate_sku_data,
        # parametrize params
        update_new_fields,
):
    # Fill old data.
    sku_uuid = 'd112f20d-20e1-4e2e-bb5e-ce0c4f5d47d5'
    sku_id = fill_old_sku_data(
        sql_insert_sku,
        sql_insert_sku_pictures,
        sql_insert_brands,
        generate_sku_data,
        sku_uuid,
    )

    # Generate new data.
    new_images = [
        {'url': 'url_3', 'brand_slug': 'brand_slug_1'},
        {'url': 'url_4', 'brand_slug': 'brand_slug_2'},
    ]
    new_sku_data = generate_sku_data(
        index=2,
        weight_unit='кг',
        volume_unit='л',
        calories_unit='кал',
        expiration_info_unit='ч',
        is_alcohol=False,
        is_fresh=False,
        is_adult=False,
        images=new_images,
        generate_attributes=(update_new_fields is True),
    )

    url = HANDLER + f'?sku_id={sku_uuid}'
    if update_new_fields is not None:
        url += f'&update_new_fields={update_new_fields}'

    response = await taxi_eats_nomenclature.post(url, json=new_sku_data)
    assert response.status_code == 200

    if update_new_fields is not True:
        new_sku_data['fat_content'] = None
        new_sku_data['milk_type'] = None
        new_sku_data['cultivar'] = None
        new_sku_data['flavour'] = None
        new_sku_data['meat_type'] = None
        new_sku_data['carcass_part'] = None
        new_sku_data['egg_category'] = None
        new_sku_data['alco_grape_cultivar'] = None
        new_sku_data['alco_aroma'] = None
        new_sku_data['alco_flavour'] = None
        new_sku_data['alco_pairing'] = None

    assert sql_select_sku_data(sku_id) == new_sku_data


async def test_404(taxi_eats_nomenclature, generate_sku_data):
    # Don't fill old data.
    sku_uuid = 'd112f20d-20e1-4e2e-bb5e-ce0c4f5d47d5'

    # Generate new data.
    new_images = [
        {'url': 'url_3', 'brand_slug': 'brand_slug_1'},
        {'url': 'url_4', 'brand_slug': 'brand_slug_2'},
    ]
    new_sku_data = generate_sku_data(
        index=2,
        weight_unit='кг',
        volume_unit='л',
        calories_unit='кал',
        expiration_info_unit='ч',
        is_alcohol=False,
        is_fresh=False,
        is_adult=False,
        images=new_images,
    )

    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?sku_id={sku_uuid}', json=new_sku_data,
    )

    assert response.status_code == 404


def fill_old_sku_data(
        sql_insert_sku,
        sql_insert_sku_pictures,
        sql_insert_brands,
        generate_sku_data,
        sku_uuid,
):
    old_images = [
        {'url': 'url_1', 'brand_slug': 'brand_slug_1'},
        {'url': 'url_2'},
    ]
    old_sku_data = generate_sku_data(
        index=1,
        weight_unit='г',
        volume_unit='мл',
        calories_unit='ккал',
        expiration_info_unit='д',
        is_alcohol=True,
        is_fresh=True,
        is_adult=True,
        images=old_images,
    )
    sql_insert_brands()
    sku_id = sql_insert_sku(old_sku_data, sku_uuid)
    sql_insert_sku_pictures(sku_id, old_sku_data['images'])
    return sku_id
