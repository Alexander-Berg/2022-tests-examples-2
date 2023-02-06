import pytest


@pytest.mark.parametrize('is_required', [True, False])
async def test_setcar_driver_freightage(
        mockserver,
        taxi_driver_orders_builder,
        load_json,
        params_wo_original_setcar,
        eulas,
        is_required,
):
    eulas.set_required(is_required)
    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )
    assert response.status_code == 200
    body = response.json()
    setcar = body['setcar']
    push = body['setcar_push']
    assert setcar['internal']['driver_freightage'] == is_required
    assert push['internal']['driver_freightage'] == is_required
