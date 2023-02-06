import pytest

BAD_PLACE_ID = 999
PLACE_ID_1 = 1
PLACE_ID_2 = 2
HANDLER = '/v1/place/products/search-by-vendor-code'


@pytest.mark.config(
    EATS_NOMENCLATURE_PRODUCTS_SEARCH_BY_VENDOR_CODE={'max_items_count': 5},
)
@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'fill_products.sql'],
)
async def test_search_products(taxi_eats_nomenclature):
    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?place_id={PLACE_ID_1}',
        json={'vendor_codes': ['123', '789', '234', '999']},
    )

    assert response.status_code == 200
    expected_response = {
        'found_items': [
            {
                'vendor_code': '123',
                'product_id': 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
            },
            {
                'vendor_code': '123',
                'product_id': 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b002',
            },
            {
                'vendor_code': '234',
                'product_id': 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
            },
        ],
        'not_found_vendor_codes': ['789', '999'],
    }
    response_json = response.json()
    response_json['found_items'] = sorted(
        response_json['found_items'], key=lambda item: item['product_id'],
    )
    response_json['not_found_vendor_codes'] = sorted(
        response_json['not_found_vendor_codes'],
    )
    assert response_json == expected_response

    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?place_id={PLACE_ID_2}',
        json={'vendor_codes': ['123', '789', '234', '999']},
    )

    assert response.status_code == 200
    expected_response = {
        'found_items': [
            {
                'vendor_code': '123',
                'product_id': 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b010',
            },
        ],
        'not_found_vendor_codes': ['234', '789', '999'],
    }
    response_json = response.json()
    response_json['found_items'] = sorted(
        response_json['found_items'], key=lambda item: item['product_id'],
    )
    response_json['not_found_vendor_codes'] = sorted(
        response_json['not_found_vendor_codes'],
    )
    assert response_json == expected_response

    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?place_id={PLACE_ID_2}',
        json={'vendor_codes': ['789', '234', '999']},
    )

    assert response.status_code == 200
    expected_response = {
        'found_items': [],
        'not_found_vendor_codes': ['234', '789', '999'],
    }
    response_json = response.json()
    response_json['found_items'] = sorted(
        response_json['found_items'], key=lambda item: item['product_id'],
    )
    response_json['not_found_vendor_codes'] = sorted(
        response_json['not_found_vendor_codes'],
    )
    assert response_json == expected_response


@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'fill_products.sql'],
)
async def test_bad_place_id(taxi_eats_nomenclature):
    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?place_id={BAD_PLACE_ID}',
        json={'vendor_codes': ['123', '234']},
    )
    assert response.status == 404


@pytest.mark.config(
    EATS_NOMENCLATURE_PRODUCTS_SEARCH_BY_VENDOR_CODE={'max_items_count': 1},
)
@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'fill_products.sql'],
)
async def test_bad_items_count(taxi_eats_nomenclature):
    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?place_id={PLACE_ID_1}',
        json={'vendor_codes': ['123', '234']},
    )
    assert response.status == 400
