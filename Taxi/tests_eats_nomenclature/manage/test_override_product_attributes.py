import pytest

HANDLER_SET = '/v1/manage/product/type/override/set'
HANDLER_REMOVE = '/v1/manage/product/type/override/remove'


def _sql_get_product_id(pgsql, public_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select id
        from eats_nomenclature.products
        where public_id = '{public_id}'
        """,
    )
    return cursor.fetchall()[0][0]


def _sql_get_product_type_id_by_value_uuid(pgsql, value_uuid):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select id
        from eats_nomenclature.product_types pt
        where pt.value_uuid = '{value_uuid}'
        """,
    )
    return cursor.fetchall()[0][0]


def _sql_get_product_type_id_by_product_id(pgsql, product_id):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select product_type_id
        from eats_nomenclature.overriden_product_attributes
        where product_id = {product_id}
        """,
    )
    result = cursor.fetchall()
    return result and result[0][0]


@pytest.mark.pgsql('eats_nomenclature', files=['fill_data.sql'])
async def test_set_product_type(taxi_eats_nomenclature, pgsql):
    public_id, value_uuid = (
        '11111111-1111-1111-1111-111111111111',
        'value_uuid_1',
    )
    response = await taxi_eats_nomenclature.post(
        HANDLER_SET + f'?product_id={public_id}&product_type_id={value_uuid}',
    )
    assert response.status == 204

    product_id = _sql_get_product_id(pgsql, public_id)

    product_type_id = _sql_get_product_type_id_by_value_uuid(pgsql, value_uuid)

    new_product_type_id_from_db = _sql_get_product_type_id_by_product_id(
        pgsql, product_id,
    )

    assert new_product_type_id_from_db == product_type_id

    # test on conflict do update
    value_uuid = 'value_uuid_5'
    response = await taxi_eats_nomenclature.post(
        HANDLER_SET + f'?product_id={public_id}&product_type_id={value_uuid}',
    )
    assert response.status == 204

    product_type_id = _sql_get_product_type_id_by_value_uuid(pgsql, value_uuid)

    new_product_type_id_from_db = _sql_get_product_type_id_by_product_id(
        pgsql, product_id,
    )

    assert new_product_type_id_from_db == product_type_id


@pytest.mark.pgsql('eats_nomenclature', files=['fill_data.sql'])
async def test_remove_product_type(taxi_eats_nomenclature, pgsql):
    public_id = '11111111-1111-1111-1111-111111111111'
    response = await taxi_eats_nomenclature.post(
        HANDLER_REMOVE + f'?product_id={public_id}',
    )
    assert response.status == 204

    product_id = _sql_get_product_id(pgsql, public_id)
    data_from_db = _sql_get_product_type_id_by_product_id(pgsql, product_id)

    assert not data_from_db


@pytest.mark.pgsql('eats_nomenclature', files=['fill_data.sql'])
async def test_404(taxi_eats_nomenclature):
    # test wrong product_id
    public_id, value_uuid = (
        '77777777-xxxx-7777-7777-777777777777',
        'value_uuid_1',
    )
    response = await taxi_eats_nomenclature.post(
        HANDLER_SET + f'?product_id={public_id}&product_type_id={value_uuid}',
    )
    assert response.status == 404

    response = await taxi_eats_nomenclature.post(
        HANDLER_REMOVE + f'?product_id={public_id}',
    )
    assert response.status == 404

    # test wrong product_type_id
    public_id, value_uuid = (
        '11111111-1111-1111-1111-111111111111',
        'value_uuid_9999',
    )
    response = await taxi_eats_nomenclature.post(
        HANDLER_SET + f'?product_id={public_id}&product_type_id={value_uuid}',
    )
    assert response.status == 404
