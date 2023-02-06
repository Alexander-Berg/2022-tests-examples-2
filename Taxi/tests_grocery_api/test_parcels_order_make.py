import pytest


async def test_parcels_order_make_200(taxi_grocery_api, tristero_parcels):
    """ Happy path, checks request and response proxying """

    vendor = 'vendor-000001'
    ref_order = 'reforder-0000001'
    token = 'some-token'
    x_idempotency_token = 'some-idempotency-token'
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

    _prepare_tristero_parcels(tristero_parcels, vendor, ref_order, token)

    tristero_parcels.check_request(
        handler='/tristero-parcels/internal/v1/parcels/v1/order/make',
        json=json,
        headers=headers,
        params={},
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/parcels/order/make', headers=headers, json=json,
    )
    assert response.status_code == 200
    assert tristero_parcels.order_make_times_called == 1
    assert response.json() == {'order_id': '123456-grocery'}


async def test_parcels_order_make_404(taxi_grocery_api, tristero_parcels):
    """ Order not found scenario, grocery-api should proxy error
    code and message from tristero-parcels """

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/parcels/order/make',
        headers={'X-Idempotency-Token': 'some-idempotenct-token'},
        json={
            'vendor': 'some-vendor',
            'ref_order': 'some-ref-order',
            'token': 'some-token',
            'position': {'location': [37, 55], 'place_id': 'nvm'},
        },
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'ORDER_NOT_FOUND',
        'message': 'Order not found',
    }


@pytest.mark.parametrize(
    'order_status, parcel_status, error_code, error_message',
    [
        (
            'created',
            'in_depot',
            'ORDER_WRONG_STATE',
            'Order is in wrong state',
        ),
        (
            'received',
            'delivering',
            'PARCEL_WRONG_STATE',
            'Parcel is in wrong state',
        ),
    ],
)
async def test_parcels_order_make_400(
        taxi_grocery_api,
        tristero_parcels,
        order_status,
        parcel_status,
        error_code,
        error_message,
):
    """ Order or parcel in bad states, grocery-api should proxy error
    code and message from tristero-parcels """

    vendor = 'vendor-000001'
    ref_order = 'reforder-0000001'
    token = 'some-token'
    x_idempotency_token = 'some-idempotency-token'

    _prepare_tristero_parcels(
        tristero_parcels,
        vendor,
        ref_order,
        token,
        order_status=order_status,
        parcel_status=parcel_status,
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/parcels/order/make',
        headers={'X-Idempotency-Token': x_idempotency_token},
        json={
            'vendor': vendor,
            'ref_order': ref_order,
            'token': token,
            'position': {'location': [37, 55], 'place_id': 'nvm'},
        },
    )
    assert response.status_code == 400
    assert response.json() == {'code': error_code, 'message': error_message}


def _prepare_tristero_parcels(
        tristero_parcels,
        vendor: str,
        ref_order: str,
        token: str,
        order_status: str = 'received',
        parcel_status: str = 'in_depot',
):
    order = tristero_parcels.add_order(
        vendor=vendor,
        order_id='01234567-89ab-cdef-000a-000000000001',
        ref_order=ref_order,
        status=order_status,
        token=token,
    )
    order.add_parcel(
        parcel_id='98765432-10ab-cdef-0000-000001000001:st-pa',
        status=parcel_status,
    )
