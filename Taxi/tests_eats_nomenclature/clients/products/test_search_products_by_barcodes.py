import pytest

from ... import utils

PLACE_ID_1 = 1
BRAND_ID_1 = 1
BAD_PLACE_ID = 999
HANDLER = '/v1/place/products/search-by-barcodes'


@pytest.mark.parametrize(
    **utils.gen_list_params(
        'request_fuzzy_search', values=[True, False, None],
    ),
)
@pytest.mark.parametrize(**utils.gen_bool_params('config_fuzzy_search'))
@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'fill_products.sql'],
)
async def test_search(
        taxi_eats_nomenclature,
        taxi_config,
        request_fuzzy_search,
        config_fuzzy_search,
):
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_PRODUCTS_SEARCH_BY_BARCODE': {
                'max_items_count': 10,
                'per_brand_search_settings': {
                    BRAND_ID_1: {
                        'fuzzy_search_enabled': config_fuzzy_search,
                        'min_barcode_length': 6,
                    },
                },
            },
        },
    )
    url = (
        HANDLER
        + f'?place_id={PLACE_ID_1}'
        + (
            f'&fuzzy_search={request_fuzzy_search}'
            if request_fuzzy_search is not None
            else ''
        )
    )
    response = await taxi_eats_nomenclature.post(
        url, json={'barcodes': ['111111111', '222222', '222220', '3333333']},
    )
    assert response.status_code == 200

    expected_response = get_expected_response(
        request_fuzzy_search, config_fuzzy_search,
    )
    expected_response['found_items'] = sorted(
        expected_response['found_items'],
        key=lambda item: (
            item['product_id'],
            item['requested_barcode'],
            item['matched_barcode'],
        ),
    )
    response_json = response.json()
    response_json['found_items'] = sorted(
        response_json['found_items'],
        key=lambda item: (
            item['product_id'],
            item['requested_barcode'],
            item['matched_barcode'],
        ),
    )
    response_json['not_found_barcodes'] = sorted(
        response_json['not_found_barcodes'],
    )
    assert response_json == expected_response


@pytest.mark.config(
    EATS_NOMENCLATURE_PRODUCTS_SEARCH_BY_BARCODE={
        'max_items_count': 5,
        'per_brand_search_settings': {
            '__default__': {
                'fuzzy_search_enabled': False,
                'min_barcode_length': 6,
            },
        },
    },
)
@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'fill_products.sql'],
)
async def test_bad_place_id(taxi_eats_nomenclature):
    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?place_id={BAD_PLACE_ID}',
        json={'barcodes': ['123', '234']},
    )
    assert response.status == 404


@pytest.mark.config(
    EATS_NOMENCLATURE_PRODUCTS_SEARCH_BY_BARCODE={
        'max_items_count': 1,
        'per_brand_search_settings': {
            '__default__': {
                'fuzzy_search_enabled': False,
                'min_barcode_length': 6,
            },
        },
    },
)
@pytest.mark.pgsql(
    'eats_nomenclature', files=['fill_dictionaries.sql', 'fill_products.sql'],
)
async def test_bad_items_count(taxi_eats_nomenclature):
    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?place_id={PLACE_ID_1}', json={'barcodes': []},
    )
    assert response.status == 400

    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?place_id={PLACE_ID_1}', json={'barcodes': ['123', '234']},
    )
    assert response.status == 400


def get_expected_response(request_fuzzy_search, config_fuzzy_search):
    if request_fuzzy_search is True or (
            request_fuzzy_search is None and config_fuzzy_search is True
    ):
        return {
            'found_items': [
                {
                    'requested_barcode': '111111111',
                    'matched_barcode': '111111111',
                    'product_id': 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
                },
                {
                    'requested_barcode': '111111111',
                    'matched_barcode': '1111111',
                    'product_id': 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b003',
                },
                {
                    'requested_barcode': '111111111',
                    'matched_barcode': '111111111',
                    'product_id': 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
                },
                {
                    'requested_barcode': '222222',
                    'matched_barcode': '222222',
                    'product_id': 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b005',
                },
                {
                    'requested_barcode': '3333333',
                    'matched_barcode': '3333330',
                    'product_id': 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b006',
                },
                {
                    'requested_barcode': '111111111',
                    'matched_barcode': '111111111',
                    'product_id': 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b010',
                },
            ],
            'not_found_barcodes': ['222220'],
        }
    if request_fuzzy_search is False or (
            request_fuzzy_search is None and config_fuzzy_search is False
    ):
        return {
            'found_items': [
                {
                    'requested_barcode': '111111111',
                    'matched_barcode': '111111111',
                    'product_id': 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b001',
                },
                {
                    'requested_barcode': '111111111',
                    'matched_barcode': '111111111',
                    'product_id': 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b004',
                },
                {
                    'requested_barcode': '222222',
                    'matched_barcode': '222222',
                    'product_id': 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b005',
                },
                {
                    'requested_barcode': '111111111',
                    'matched_barcode': '111111111',
                    'product_id': 'bb231b95-1ff2-4bc4-b78d-dcaa1f69b010',
                },
            ],
            'not_found_barcodes': ['222220', '3333333'],
        }
    return {}
