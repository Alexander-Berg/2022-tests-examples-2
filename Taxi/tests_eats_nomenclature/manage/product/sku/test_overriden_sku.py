import pytest

HANDLER = '/v1/manage/product/sku/override/set'


@pytest.mark.parametrize(
    'product_id, sku_id',
    [
        ('11111111-1111-1111-1111-111111111112', None),
        (
            '11111111-1111-1111-1111-111111111112',
            '11111111-1111-1111-1111-111111111111',
        ),
        (
            '11111111-1111-1111-1111-111111111111',
            '11111111-1111-1111-1111-111111111112',
        ),
    ],
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_data.sql'])
async def test_404_product_or_sku_not_found(
        taxi_eats_nomenclature, product_id, sku_id,
):
    request = HANDLER + f'?product_id={product_id}'
    if sku_id:
        request += f'&sku_id={sku_id}'
    response = await taxi_eats_nomenclature.post(request)
    assert response.status == 404


@pytest.mark.pgsql('eats_nomenclature', files=['fill_data.sql'])
async def test_set_overriden_product_sku(taxi_eats_nomenclature, pgsql):
    _sql_set_product_sku(pgsql, 1, 3)
    product_id_1 = '11111111-1111-1111-1111-111111111111'
    product_id_2 = '22222222-2222-2222-2222-222222222222'
    product_id_3 = '33333333-3333-3333-3333-333333333333'
    sku_id_1 = '11111111-1111-1111-1111-111111111111'
    sku_id_2 = '22222222-2222-2222-2222-222222222222'

    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?product_id={product_id_1}&sku_id={sku_id_1}',
    )
    assert response.status == 204
    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?product_id={product_id_2}&sku_id={sku_id_2}',
    )
    assert response.status == 204
    sql_product_id_to_sku_id = _sql_get_product_id_to_sku_id(pgsql)
    expected_product_id_to_sku_id = {1: 1, 2: 2}
    assert sql_product_id_to_sku_id == expected_product_id_to_sku_id

    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?product_id={product_id_1}',
    )
    response = await taxi_eats_nomenclature.post(
        HANDLER + f'?product_id={product_id_3}',
    )
    assert response.status == 204
    sql_product_id_to_sku_id = _sql_get_product_id_to_sku_id(pgsql)
    expected_product_id_to_sku_id = {1: None, 2: 2, 3: None}
    assert sql_product_id_to_sku_id == expected_product_id_to_sku_id


def _sql_set_product_sku(pgsql, product_id, sku_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        insert into eats_nomenclature.overriden_product_sku(product_id, sku_id)
        values ({product_id}, {sku_id})
        """,
    )


def _sql_get_product_id_to_sku_id(pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        """
        select product_id, sku_id
        from eats_nomenclature.overriden_product_sku
        """,
    )
    product_id_to_sku_id = {}
    for product_id, sku_id in cursor.fetchall():
        product_id_to_sku_id[product_id] = sku_id
    return product_id_to_sku_id
