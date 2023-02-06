import pytest

DEFAULT_HEADERS = {
    'Accept-Language': 'en',
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


async def test_happy_path(
        taxi_cargo_orders, stq, my_waybill_info, default_order_id,
):
    response = await taxi_cargo_orders.post(
        'driver/v1/cargo-claims/v1/cargo/call-request',
        json={'cargo_ref_id': f'order/{default_order_id}', 'point_id': 123},
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {}

    assert stq.support_info_cargo_eda_callback_on_cancel.times_called == 1
    stq_call = stq.support_info_cargo_eda_callback_on_cancel.next_call()
    assert stq_call['id'] == 'taxi-order_phone_pd_id'

    kwargs = stq_call['kwargs']
    assert kwargs['request_id'] == 'taxi-order_phone_pd_id'
    assert kwargs['driver_phone_id'] == 'phone_pd_id'
    assert kwargs['taxi_order_id'] == 'taxi-order'


async def test_send_eda_order_id(
        taxi_cargo_orders, stq, my_waybill_info, default_order_id,
):
    my_waybill_info['execution']['points'][0][
        'external_order_id'
    ] = 'eda_order_id_1'
    response = await taxi_cargo_orders.post(
        'driver/v1/cargo-claims/v1/cargo/call-request',
        json={'cargo_ref_id': f'order/{default_order_id}', 'point_id': 123},
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {}

    assert stq.support_info_cargo_eda_callback_on_cancel.times_called == 1
    stq_call = stq.support_info_cargo_eda_callback_on_cancel.next_call()
    assert stq_call['id'] == 'taxi-order_phone_pd_id'
    assert stq_call['kwargs']['eda_order_id'] == 'eda_order_id_1'


async def test_no_performer_info(
        taxi_cargo_orders, stq, default_order_id, waybill_state, mockserver,
):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def _mock(request):
        return waybill_state.load_waybill(
            'cargo-dispatch/v1_waybill_info_tpl.json',
        )

    response = await taxi_cargo_orders.post(
        'driver/v1/cargo-claims/v1/cargo/call-request',
        json={
            'cargo_ref_id': 'order/00000000-0000-0000-0000-000000000000',
            'point_id': 123,
        },
        headers=DEFAULT_HEADERS,
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'bad_header', ['X-YaTaxi-Driver-Profile-Id', 'X-YaTaxi-Park-Id'],
)
async def test_no_auth(taxi_cargo_orders, default_order_id, bad_header: str):
    headers_bad_driver = DEFAULT_HEADERS.copy()
    headers_bad_driver[bad_header] = 'bad'

    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/call-request',
        headers=headers_bad_driver,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'last_known_status': 'new',
            'idempotency_token': 'some_token',
            'point_id': 123123,
        },
    )
    assert response.status_code == 403
    assert response.json() == {
        'code': 'not_authorized',
        'message': 'Попробуйте снова',
    }
