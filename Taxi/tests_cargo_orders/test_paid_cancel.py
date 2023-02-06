import pytest

DEFAULT_PAID_CANCEL_RESPONSE = {
    'reason': 'point_is_ready',
    'paid_cancel_max_waiting_time': 999999,
}


@pytest.fixture(name='mock_dispatch_paid_cancel')
def _mock_dispatch_paid_cancel(mockserver):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/paid-cancel')
    def mock(request):
        if context.expected_request is not None:
            assert request.json == context.expected_request
        if context.response is not None:
            return context.response
        return DEFAULT_PAID_CANCEL_RESPONSE

    class Context:
        def __init__(self):
            self.expected_request = None
            self.response = None
            self.handler = mock

    context = Context()

    return context


async def test_200(
        taxi_cargo_orders, mock_dispatch_paid_cancel, default_order_id,
):
    response = await taxi_cargo_orders.post(
        'v1/order/paid-cancel',
        json={'cargo_ref_id': f'order/{default_order_id}'},
    )
    assert response.status_code == 200
    assert response.json() == DEFAULT_PAID_CANCEL_RESPONSE


async def test_404_dispatch(
        taxi_cargo_orders,
        mock_dispatch_paid_cancel,
        mockserver,
        default_order_id,
):
    mock_dispatch_paid_cancel.response = mockserver.make_response(
        json={'code': 'some_code', 'message': 'some_message'}, status=404,
    )

    response = await taxi_cargo_orders.post(
        'v1/order/paid-cancel',
        json={'cargo_ref_id': f'order/{default_order_id}'},
    )
    assert response.status_code == 410
    assert response.json() == {'code': 'some_code', 'message': 'some_message'}


async def test_no_order(taxi_cargo_orders):
    response = await taxi_cargo_orders.post(
        'v1/order/paid-cancel',
        json={'cargo_ref_id': 'order/00000000-0000-0000-0000-000000000000'},
    )
    assert response.status_code == 410
