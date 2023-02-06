import uuid


async def test_order_ready_dummy_200(
        taxi_grocery_dispatch, testpoint, grocery_dispatch_pg,
):
    dispatch_model = grocery_dispatch_pg.create_dispatch(status='scheduled')
    dispatch_model.auto_refresh = False

    @testpoint('test_order_ready')
    def check_accepting_data(data):
        data_dispatch = data['dispatch']
        assert data_dispatch['dispatch_id'] == dispatch_model.dispatch_id
        assert (
            data_dispatch['order']['order_id'] == dispatch_model.order.order_id
        )

    request = {'dispatch_id': dispatch_model.dispatch_id}

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/order_ready', json=request,
    )

    assert response.status_code == 200
    assert check_accepting_data.times_called == 1

    body = response.json()
    assert body['dispatch_id'] == dispatch_model.dispatch_id
    assert body['order_id'] == dispatch_model.order.order_id
    assert body['version'] > dispatch_model.version
    assert body['dispatch_type'] == dispatch_model.dispatch_name
    assert body['status'] == dispatch_model.status

    status_meta = body['status_meta']
    assert status_meta['_test'] == {'status': 'order_assembled'}


async def test_order_ready_dummy_not_found(taxi_grocery_dispatch):
    request = {'dispatch_id': str(uuid.uuid4())}
    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/order_ready', json=request,
    )
    assert response.status_code == 404


async def test_order_ready_dummy_idle_200(
        taxi_grocery_dispatch, testpoint, grocery_dispatch_pg,
):
    dispatch_model = grocery_dispatch_pg.create_dispatch(status='idle')

    request = {'dispatch_id': dispatch_model.dispatch_id}

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/order_ready', json=request,
    )

    assert response.status_code == 200
