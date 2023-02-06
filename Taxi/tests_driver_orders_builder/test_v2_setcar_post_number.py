# pylint: disable=too-many-lines


async def test_park_number(
        taxi_driver_orders_builder, redis_store, params_wo_original_setcar,
):
    redis_store.set('Orders:CurrentNumber:park1', '12345')

    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )

    assert response.status_code == 200, response.text
    response_json = response.json()['setcar']
    assert 'number' in response_json
    assert response_json['number'] == 12346
