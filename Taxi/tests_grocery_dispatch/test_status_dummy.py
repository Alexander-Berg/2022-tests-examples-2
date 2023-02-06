async def test_dummy_status_not_invoked_when_idle(
        taxi_grocery_dispatch, testpoint, grocery_dispatch_pg,
):
    dispatch = grocery_dispatch_pg.create_dispatch()

    @testpoint('test_dispatch_status')
    def check_status_data(data):
        pass

    request = {'dispatch_id': dispatch.dispatch_id}

    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/status', json=request,
    )

    assert response.status_code == 200
    assert check_status_data.times_called == 0

    body = response.json()
    assert body['dispatch_id'] == dispatch.dispatch_id
    assert body['order_id'] == dispatch.order.order_id
    assert body['version'] == dispatch.version
    assert body['dispatch_type'] == dispatch.dispatch_name
    assert body['status'] == dispatch.status
