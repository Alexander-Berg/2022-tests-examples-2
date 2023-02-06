import pytest


async def test_order_make_200(
        taxi_tristero_parcels, tristero_parcels_db, grocery_orders_make,
):
    """ Happy path, checks request and response proxying """

    vendor = 'vendor-000001'
    ref_order = 'reforder-0000001'
    token = 'some-token'
    x_idempotency_token = 'some-idempotency-token'
    personal_phone_id = 'some-personal-phone-id'
    position = {
        'location': [37, 55],
        'place_id': 'yamaps://12345',
        'floor': '13',
        'flat': '666',
        'doorcode': '42',
        'doorcode_extra': '0123',
        'entrance': '2',
        'building_name': 'super appartments',
        'doorbell_name': 'grocery lover',
        'left_at_door': False,
        'comment': 'test comment',
    }

    headers = {'X-Idempotency-Token': x_idempotency_token}
    json = {
        'vendor': vendor,
        'ref_order': ref_order,
        'token': token,
        'position': position,
    }

    with tristero_parcels_db as db:
        order = db.add_order(
            1,
            status='received',
            personal_phone_id=personal_phone_id,
            vendor=vendor,
            token=token,
            ref_order=ref_order,
        )
        parcel = order.add_parcel(11, status='in_depot')

    grocery_orders_make.check_request(
        {
            'items': [{'id': parcel.product_key, 'quantity': '1'}],
            'locale': '',
            'personal_phone_id': personal_phone_id,
            'position': position,
            'yandex_uid': order.uid,
        },
    )

    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/v1/order/make', headers=headers, json=json,
    )

    assert response.status_code == 200
    assert grocery_orders_make.times_called == 1
    assert response.json() == {'grocery_order_id': '12345-grocery'}


@pytest.mark.parametrize(
    'ref_order, token, status',
    [
        pytest.param('reforder-0000001', 'some-token', 200, id='ok order'),
        pytest.param(
            'reforder-0000002', 'some-token', 404, id='bad ref_order',
        ),
        pytest.param('reforder-0000001', 'bad-token', 404, id='bad token'),
    ],
)
async def test_order_make_404(
        taxi_tristero_parcels,
        tristero_parcels_db,
        grocery_orders_make,
        ref_order,
        token,
        status,
):
    """ Return 404 if order not found or token does not match """

    vendor = 'vendor-000001'
    x_idempotency_token = 'some-idempotency-token'
    position = {'location': [37, 55], 'place_id': 'yamaps://12345'}

    headers = {'X-Idempotency-Token': x_idempotency_token}
    json = {
        'vendor': vendor,
        'ref_order': ref_order,
        'token': token,
        'position': position,
    }

    with tristero_parcels_db as db:
        order = db.add_order(
            1,
            status='received',
            personal_phone_id='some-personal-phone-id',
            vendor=vendor,
            token='some-token',
            ref_order='reforder-0000001',
        )
        order.add_parcel(11, status='in_depot')

    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/v1/order/make', headers=headers, json=json,
    )
    assert response.status_code == status
    assert grocery_orders_make.times_called == (1 if status == 200 else 0)
    if status == 404:
        assert response.json()['code'] == 'ORDER_NOT_FOUND'


@pytest.mark.parametrize(
    'order_status, parcel_status, personal_phone_id, status, error_code',
    [
        pytest.param(
            'received',
            'in_depot',
            'some-personal-phone-id',
            200,
            None,
            id='ok',
        ),
        pytest.param(
            'delivered',
            'in_depot',
            'some-personal-phone-id',
            400,
            'ORDER_WRONG_STATE',
            id='bad order state',
        ),
        pytest.param(
            'received',
            'delivering',
            'some-personal-phone-id',
            400,
            'PARCEL_WRONG_STATE',
            id='bad parcel state',
        ),
        pytest.param(
            'received',
            'in_depot',
            None,
            400,
            'MISSING_PHONE_ID',
            id='no personal_phone_id',
        ),
    ],
)
async def test_order_make_400(
        taxi_tristero_parcels,
        tristero_parcels_db,
        grocery_orders_make,
        order_status,
        parcel_status,
        personal_phone_id,
        status,
        error_code,
):
    """ Return 400 if order can not be dispatched """

    vendor = 'vendor-000001'
    ref_order = 'reforder-0000001'
    token = 'some-token'
    x_idempotency_token = 'some-idempotency-token'
    position = {'location': [37, 55], 'place_id': 'yamaps://12345'}

    headers = {'X-Idempotency-Token': x_idempotency_token}
    json = {
        'vendor': vendor,
        'ref_order': ref_order,
        'token': token,
        'position': position,
    }

    with tristero_parcels_db as db:
        order = db.add_order(
            1,
            status=order_status,
            personal_phone_id=personal_phone_id,
            vendor=vendor,
            token=token,
            ref_order=ref_order,
        )
        order.add_parcel(11, status=parcel_status)

    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/v1/order/make', headers=headers, json=json,
    )
    assert response.status_code == status
    assert grocery_orders_make.times_called == (1 if status == 200 else 0)
    if status != 200:
        assert response.json()['code'] == error_code


@pytest.mark.parametrize(
    'error_code',
    [
        'MISSING_PHONE_ID',
        'INVALID_ITEMS',
        'CREATE_CART_ERROR',
        'CHECKOUT_CART_ERROR',
    ],
)
async def test_order_make_proxy_error(
        taxi_tristero_parcels,
        tristero_parcels_db,
        grocery_orders_make,
        error_code,
):
    """ Should proxy 400 error from grocery-orders """

    vendor = 'vendor-000001'
    ref_order = 'reforder-0000001'
    token = 'some-token'
    x_idempotency_token = 'some-idempotency-token'
    personal_phone_id = 'some-personal-phone-id'
    position = {'location': [37, 55], 'place_id': 'yamaps://12345'}

    headers = {'X-Idempotency-Token': x_idempotency_token}
    json = {
        'vendor': vendor,
        'ref_order': ref_order,
        'token': token,
        'position': position,
    }

    with tristero_parcels_db as db:
        order = db.add_order(
            1,
            status='received',
            personal_phone_id=personal_phone_id,
            vendor=vendor,
            token=token,
            ref_order=ref_order,
        )
        order.add_parcel(11, status='in_depot')

    grocery_orders_make.set_response_status(400, error_code)

    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/v1/order/make', headers=headers, json=json,
    )
    assert response.status_code == 400
    assert grocery_orders_make.times_called == 1
    assert response.json()['code'] == error_code


async def test_order_make_500(
        taxi_tristero_parcels, tristero_parcels_db, grocery_orders_make,
):
    """ Should return 500 error if grocery-orders returns 500 """

    vendor = 'vendor-000001'
    ref_order = 'reforder-0000001'
    token = 'some-token'
    x_idempotency_token = 'some-idempotency-token'
    personal_phone_id = 'some-personal-phone-id'
    position = {'location': [37, 55], 'place_id': 'yamaps://12345'}

    headers = {'X-Idempotency-Token': x_idempotency_token}
    json = {
        'vendor': vendor,
        'ref_order': ref_order,
        'token': token,
        'position': position,
    }

    with tristero_parcels_db as db:
        order = db.add_order(
            1,
            status='received',
            personal_phone_id=personal_phone_id,
            vendor=vendor,
            token=token,
            ref_order=ref_order,
        )
        order.add_parcel(11, status='in_depot')

    grocery_orders_make.set_response_status(500)

    response = await taxi_tristero_parcels.post(
        '/internal/v1/parcels/v1/order/make', headers=headers, json=json,
    )
    assert response.status_code == 500
    assert grocery_orders_make.times_called == 1
