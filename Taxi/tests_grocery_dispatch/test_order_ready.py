import pytest


@pytest.mark.parametrize(
    ['dispatch_status', 'resp_code'],
    [
        ('idle', 200),
        ('scheduled', 200),
        ('delivering', 200),
        ('revoked', 409),
        ('delivered', 409),
        ('canceled', 409),
        ('finished', 409),
    ],
)
async def test_order_ready(
        taxi_grocery_dispatch,
        cargo,
        cargo_pg,
        grocery_dispatch_pg,
        dispatch_status,
        resp_code,
):

    dispatch_info = grocery_dispatch_pg.create_dispatch(
        dispatch_name='cargo_sync', status=dispatch_status,
    )
    if resp_code == 200:
        cargo_pg.create_claim(dispatch_id=dispatch_info.dispatch_id)
        cargo.set_data(items=cargo.convert_items(dispatch_info.order.items))

    request = {'dispatch_id': dispatch_info.dispatch_id}
    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/order_ready', json=request,
    )

    assert response.status_code == resp_code
    if resp_code == 200 and dispatch_status != 'idle':
        assert cargo.times_set_points_ready_called() == 1
    else:
        assert cargo.times_set_points_ready_called() == 0


@pytest.mark.parametrize(
    ['dispatch_status', 'resp_code'],
    [
        ('rescheduling', 425),
        ('revoked', 425),
        ('delivered', 425),
        ('canceled', 425),
        ('finished', 425),
    ],
)
async def test_order_ready_status_concurrent_conflict(
        taxi_grocery_dispatch,
        cargo,
        cargo_pg,
        grocery_dispatch_pg,
        testpoint,
        dispatch_status,
        resp_code,
):

    dispatch_info = grocery_dispatch_pg.create_dispatch(
        dispatch_name='cargo_sync', status='scheduled',
    )

    @testpoint('update_dispatch_when_order_ready')
    async def update_dispatch(data):
        dispatch_info.status = dispatch_status

    cargo_pg.create_claim(dispatch_id=dispatch_info.dispatch_id)
    cargo.set_data(items=cargo.convert_items(dispatch_info.order.items))

    request = {'dispatch_id': dispatch_info.dispatch_id}
    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/order_ready', json=request,
    )

    assert response.status_code == resp_code
    assert update_dispatch.times_called == 1
