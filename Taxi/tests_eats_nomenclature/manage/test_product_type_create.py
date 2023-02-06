HANDLER = '/v1/manage/product_type/create'
NAME = 'type1'
TEST_UUID = '49c9d77a-aa48-4291-9523-0a406e4009fb'


async def test_create_product_type(taxi_eats_nomenclature, pgsql, testpoint):
    @testpoint(f'eats-nomenclature_insert_manual_product_type')
    def pass_uuid(param):
        return {'uuid': TEST_UUID}

    response = await taxi_eats_nomenclature.post(HANDLER + f'?name={NAME}')

    assert pass_uuid.has_calls
    assert response.status_code == 201
    assert response.json() == get_expected_response(NAME, pgsql, TEST_UUID)

    response_repeat = await taxi_eats_nomenclature.post(
        HANDLER + f'?name={NAME}',
    )
    assert response_repeat.status_code == 409
    assert response_repeat.json() == get_expected_response(
        NAME, pgsql, TEST_UUID,
    )


def sql_get_type_uuid(type_name, pgsql):
    cursor = pgsql['eats_nomenclature'].cursor()
    cursor.execute(
        f"""
        select pt.value_uuid from eats_nomenclature.product_types pt
        where pt.value = '{type_name}'
        """,
    )
    uuid = cursor.fetchone()
    assert uuid
    return uuid[0]


def get_expected_response(type_name, pgsql, expected_uuid):
    uuid = sql_get_type_uuid(type_name, pgsql)
    assert uuid == expected_uuid
    return {'product_type_id': uuid}
