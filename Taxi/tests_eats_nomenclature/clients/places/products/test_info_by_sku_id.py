import pytest

from . import constants


SKU_UUID = constants.SKU_UUID
HANDLER = constants.HANDLER


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_place_data.sql', 'fill_data_for_full_response.sql'],
)
async def test_full_schema(taxi_eats_nomenclature, taxi_config, load_json):
    """
    Test a schema with all posible fields filled
    (and multiple values where possible)
    """
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_PRICE_ROUNDING': {
                '__default__': {'should_include_pennies_in_price': True},
            },
        },
    )

    place_ids = [1, 2]

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}', json={'place_ids': place_ids, 'sku_id': SKU_UUID},
    )
    assert response.status_code == 200
    assert response.json() == load_json('full_response.json')


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_place_data.sql', 'fill_data_for_minimal_response.sql'],
)
async def test_minimal_schema(taxi_eats_nomenclature, load_json):
    """
    Test a schema with minimal posible fields filled
    """
    place_id = 1

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}', json={'place_ids': [place_id], 'sku_id': SKU_UUID},
    )
    assert response.status_code == 200
    assert response.json() == load_json('minimal_response.json')


@pytest.mark.pgsql('eats_nomenclature', files=['fill_place_data.sql'])
async def test_several_products(
        taxi_eats_nomenclature, sql_add_sku, sql_add_product,
):
    """
    Several products have the same sku_id
    """
    place_id = 1

    sku_id = sql_add_sku(SKU_UUID)
    product_public_id_1 = sql_add_product(
        origin_id='origin_id_1', sku_id=sku_id,
    )
    product_public_id_2 = sql_add_product(
        origin_id='origin_id_2', sku_id=sku_id,
    )

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}', json={'place_ids': [place_id], 'sku_id': SKU_UUID},
    )
    assert response.status_code == 200
    response_products = {
        product['product_id'] for product in response.json()['places_products']
    }
    assert response_products == {product_public_id_1, product_public_id_2}


@pytest.mark.pgsql('eats_nomenclature', files=['fill_place_data.sql'])
async def test_unavailable_product(
        taxi_eats_nomenclature, sql_add_sku, sql_add_product,
):
    """
    Filter out unavailable product
    """
    place_id = 1

    sku_id = sql_add_sku(SKU_UUID)
    available_product = sql_add_product(
        origin_id='origin_id_1', sku_id=sku_id, is_available=True,
    )
    sql_add_product(origin_id='origin_id_2', sku_id=sku_id, is_available=False)

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}', json={'place_ids': [place_id], 'sku_id': SKU_UUID},
    )
    assert response.status_code == 200
    response_products = {
        product['product_id'] for product in response.json()['places_products']
    }
    assert response_products == {available_product}


@pytest.mark.pgsql('eats_nomenclature', files=['fill_place_data.sql'])
@pytest.mark.parametrize(
    'overriden_sku_uuid, sku_uuid, product_in_response',
    [
        (
            '11111111-1111-1111-1111-111111111111',
            '22222222-2222-2222-2222-222222222222',
            True,
        ),
        (
            '22222222-2222-2222-2222-222222222222',
            '11111111-1111-1111-1111-111111111111',
            False,
        ),
        (None, '11111111-1111-1111-1111-111111111111', True),
    ],
)
async def test_overriden_product_sku(
        taxi_eats_nomenclature,
        sql_add_product,
        sql_add_sku,
        # parametrize
        overriden_sku_uuid,
        sku_uuid,
        product_in_response,
):
    """
    If product has overriden sku it should be used as product sku
    """
    place_id = 1

    sku_id = sql_add_sku(uuid=sku_uuid)
    overriden_sku_id = (
        sql_add_sku(uuid=overriden_sku_uuid) if overriden_sku_uuid else None
    )
    product_public_id = sql_add_product(
        origin_id='origin_id_1',
        sku_id=sku_id,
        overriden_sku_id=overriden_sku_id,
    )

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}', json={'place_ids': [place_id], 'sku_id': SKU_UUID},
    )
    assert response.status_code == 200
    response_products = {
        product['product_id'] for product in response.json()['places_products']
    }
    expected_products = {product_public_id} if product_in_response else set()
    assert response_products == expected_products
