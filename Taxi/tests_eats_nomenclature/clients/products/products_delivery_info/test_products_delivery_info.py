import pytest

HANDLER = '/v1/products/delivery_info'
BRAND_ID = 1
PLACE_ID = 1


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data_for_full_response.sql'],
)
async def test_full_schema(taxi_eats_nomenclature, taxi_config):
    """
    Test a schema with all possible fields filled
    (and multiple values where possible)
    """
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_PROCESSING_TYPES_TO_RETURN': {
                'processing_types': ['охлажденный'],
            },
            'EATS_NOMENCLATURE_DELIVERY_TAGS': {
                'hot_drinks': {
                    '1': {'origin_ids_to_include': ['item_origin_2']},
                },
            },
        },
    )

    body = {'origin_ids': ['item_origin_1', 'item_origin_2']}

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={PLACE_ID}', json=body,
    )

    assert response.status == 200

    expected_response = {
        'products': [
            {
                'origin_id': 'item_origin_1',
                'delivery_tags': ['cold_or_frozen'],
            },
            {
                'origin_id': 'item_origin_2',
                'delivery_tags': ['cold_or_frozen', 'hot_drink'],
            },
        ],
    }
    response = response.json()
    response['products'] = sorted(
        response['products'], key=lambda k: k['origin_id'],
    )
    for product in response['products']:
        product['delivery_tags'] = sorted(product['delivery_tags'])
    assert response == expected_response


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data_for_minimal_response.sql'],
)
async def test_minimal_schema(taxi_eats_nomenclature):
    """
    Test a schema with minimal possible fields filled
    """
    body = {'origin_ids': ['item_origin_1']}
    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={PLACE_ID}', json=body,
    )

    assert response.status == 200

    expected_response = {
        'products': [{'origin_id': 'item_origin_1', 'delivery_tags': []}],
    }
    response = response.json()
    response['products'] = sorted(
        response['products'], key=lambda k: k['origin_id'],
    )
    assert response == expected_response


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=[
        'fill_dictionaries.sql',
        'fill_data_for_specific_delivery_tags_test.sql',
    ],
)
async def test_specific_values(taxi_eats_nomenclature, taxi_config):
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_PROCESSING_TYPES_TO_RETURN': {
                'processing_types': ['охлажденный'],
            },
            'EATS_NOMENCLATURE_DELIVERY_TAGS': {
                'hot_drinks': {
                    '1': {
                        'origin_ids_to_include': [
                            'item_origin_3',
                            'item_origin_5',
                        ],
                    },
                },
            },
        },
    )

    body = {
        'origin_ids': [
            # cold_or_frozen, get processing type from product attributes
            'item_origin_1',
            # cold_or_frozen, get processing type from sku attributes
            'item_origin_2',
            # hot_drink
            'item_origin_3',
            # no delivery tags
            'item_origin_4',
            # both possible delivery tags
            'item_origin_5',
        ],
    }

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={PLACE_ID}', json=body,
    )

    assert response.status == 200

    expected_response = {
        'products': [
            {
                'origin_id': 'item_origin_1',
                'delivery_tags': ['cold_or_frozen'],
            },
            {
                'origin_id': 'item_origin_2',
                'delivery_tags': ['cold_or_frozen'],
            },
            {'origin_id': 'item_origin_3', 'delivery_tags': ['hot_drink']},
            {'origin_id': 'item_origin_4', 'delivery_tags': []},
            {
                'origin_id': 'item_origin_5',
                'delivery_tags': ['cold_or_frozen', 'hot_drink'],
            },
        ],
    }
    response = response.json()
    response['products'] = sorted(
        response['products'], key=lambda k: k['origin_id'],
    )
    for product in response['products']:
        product['delivery_tags'] = sorted(product['delivery_tags'])
    assert response == expected_response
