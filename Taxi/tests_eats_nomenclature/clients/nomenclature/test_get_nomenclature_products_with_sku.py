import pytest

AUTH_HEADERS = {'x-device-id': 'device_id'}


@pytest.mark.experiments3(filename='experiment_on.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data.sql', 'fill_sku.sql'],
)
async def test_get_nomenclature_products_w_disabled_fallback(
        taxi_eats_nomenclature, load_json, sql_set_brand_fallback,
):
    brand_id = 1

    sql_set_brand_fallback(brand_id)

    response = await taxi_eats_nomenclature.get(
        '/v1/nomenclature?slug=slug&category_id=category_1_origin',
        headers=AUTH_HEADERS,
    )
    assert response.status == 200

    assert sort_by_id(
        map_response(load_json('response_with_sku.json')),
    ) == sort_by_id(map_response(response.json()))


@pytest.mark.experiments3(filename='experiment_on.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data.sql', 'fill_sku.sql'],
)
async def test_get_nomenclature_products_w_enabled_pic_fallback(
        taxi_eats_nomenclature, load_json, sql_set_brand_fallback,
):
    brand_id = 1

    sql_set_brand_fallback(brand_id, fallback_to_product_picture=True)

    response = await taxi_eats_nomenclature.get(
        '/v1/nomenclature?slug=slug&category_id=category_1_origin',
        headers=AUTH_HEADERS,
    )
    assert response.status == 200

    assert sort_by_id(
        map_response(load_json('response_with_sku_and_pic_fallback.json')),
    ) == sort_by_id(map_response(response.json()))


@pytest.mark.experiments3(filename='experiment_on.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data.sql', 'fill_sku.sql'],
)
async def test_get_nomenclature_products_w_enabled_vnd_fallback(
        taxi_eats_nomenclature, load_json, sql_set_brand_fallback,
):
    brand_id = 1

    sql_set_brand_fallback(brand_id, fallback_to_product_vendor=True)

    response = await taxi_eats_nomenclature.get(
        '/v1/nomenclature?slug=slug&category_id=category_1_origin',
        headers=AUTH_HEADERS,
    )
    assert response.status == 200

    assert sort_by_id(
        map_response(load_json('response_with_sku_and_vnd_fallback.json')),
    ) == sort_by_id(map_response(response.json()))


@pytest.mark.experiments3(filename='experiment_off.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data.sql', 'fill_sku.sql'],
)
async def test_experiment_off(
        taxi_eats_nomenclature, sql_set_brand_fallback, load_json,
):
    brand_id = 1

    sql_set_brand_fallback(
        brand_id,
        fallback_to_product_picture=True,
        fallback_to_product_vendor=True,
    )

    response = await taxi_eats_nomenclature.get(
        '/v1/nomenclature?slug=slug&category_id=category_1_origin',
        headers=AUTH_HEADERS,
    )
    assert response.status == 200

    assert sort_by_id(
        map_response(load_json('response_wo_sku_and_w_vnd_fallback.json')),
    ) == sort_by_id(map_response(response.json()))


@pytest.mark.experiments3(filename='experiment_on_with_excluded_brands.json')
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data.sql', 'fill_sku.sql'],
)
async def test_get_nomenclature_products_excluded_brands(
        taxi_eats_nomenclature, load_json, sql_set_brand_fallback,
):
    brand_id = 1

    sql_set_brand_fallback(brand_id)

    response = await taxi_eats_nomenclature.get(
        '/v1/nomenclature?slug=slug&category_id=category_1_origin',
        headers=AUTH_HEADERS,
    )
    assert response.status == 200

    assert sort_by_id(
        map_response(load_json('response_without_sku.json')),
    ) == sort_by_id(map_response(response.json()))


def map_response(json):
    categories = json['categories']
    products = []
    for category in categories:
        products += category['items']

    return [
        {
            'is_available': p['is_available'],
            'location': p.get('location') or None,
            'price': p.get('price') or None,
            'old_price': p.get('old_price') or None,
            'vat': p.get('vat') or None,
            'vendor_code': p.get('vendor_code') or None,
            'id': p['id'],
            'general': p['description']['general'],
            'is_catch_weight': p['is_catch_weight'],
            'shipping_type': p['shipping_type'],
            'is_choosable': p['is_choosable'],
            'quantum': p.get('measure', {}).get('quantum') or 0.0,
            'measure_unit': p.get('measure', {}).get('unit') or None,
            'measure_value': p.get('measure', {}).get('value') or None,
            'volume_unit': p.get('volume', {}).get('unit') or None,
            'volume_value': p.get('volume', {}).get('value') or None,
            'name': p['name'],
            'package_info': (
                p.get('description', {}).get('package_info') or None
            ),
            'expires_in': p.get('description', {}).get('expires_in') or None,
            'storage_requirements': (
                p.get('description', {}).get('storage_requirements') or None
            ),
            'purpose': p.get('description', {}).get('purpose') or None,
            'nutritional_value': (
                p.get('description', {}).get('nutritional_value') or None
            ),
            'composition': p.get('description', {}).get('composition') or None,
            'adult': p['adult'],
            'sort_order': p['sort_order'],
            'images': [img['url'] for img in p['images']],
            'brand': p.get('brand') or None,
            'is_sku': p.get('is_sku'),
        }
        for p in products
    ]


def sort_by_id(data):
    return sorted(data, key=lambda k: k['id'])
