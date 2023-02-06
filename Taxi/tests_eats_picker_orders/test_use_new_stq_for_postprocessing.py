from urllib import parse

import pytest

from . import utils

DEFAULT_EATS_ID = 'test_eats_id'
DEFAULT_PICKER_ID = 'test_picker_id'
DEFAULT_RECEIPT = {
    't': '20200618T105208',
    's': '1098.02',
    'fn': '4891689280440300',
    'i': '19097',
    'fp': '313667667',
    'n': '1',
}


@pytest.mark.parametrize(
    'api_handler',
    [
        pytest.param(
            '/4.0/eats-picker/api/v1/order/receipt', id='client handler',
        ),
        pytest.param('/api/v1/order/receipt', id='admin handler'),
    ],
)
@pytest.mark.now('2020-06-18T10:00:00')
@utils.use_postprocessing_config(True)
@utils.send_order_events_config()
async def test_use_new_stq_if_config_enabled(
        taxi_eats_picker_orders, mockserver, api_handler, stq, mock_processing,
):
    eats_id = DEFAULT_EATS_ID
    picker_id = DEFAULT_PICKER_ID

    @mockserver.json_handler('/edadeal-checkprovider/v1/checks')
    def _mock_edadeal(request):
        assert (
            dict(parse.parse_qsl(request.get_data().decode()))
            == DEFAULT_RECEIPT
        )
        assert request.headers['X-Correlation-Id'] == eats_id
        return mockserver.make_response(status=202)

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        if request.method == 'GET':
            assert request.query.get('card_type') == 'TinkoffBank'
            assert request.query.get('card_value') == 'test_cid_1'
            return mockserver.make_response(json={'amount': 2}, status=200)

        assert request.query.get('card_type') == 'TinkoffBank'
        assert request.query.get('card_value') == 'test_cid_1'
        assert request.json['amount'] == 0
        assert request.json['order_id'] == eats_id
        return mockserver.make_response(json={'order_id': eats_id}, status=200)

    core_picker_orders_statuses = []

    @mockserver.json_handler('/eats-core/v1/picker-orders/apply-state')
    def _mock_eats_core_picker_orders(request):
        assert request.method == 'POST'
        assert request.json['eats_id'] == eats_id
        status = request.json['status']
        assert status in ('complete', 'paid')
        assert request.json['timestamp'] == '2020-06-18T10:00:00+00:00'
        expected_reasons = {
            'paid': 'receipt-uploaded',
            'complete': 'picking_only:receipt-uploaded',
            'handing': 'picking_handing:receipt-uploaded',
        }
        assert request.json['reason'] == expected_reasons[status]
        core_picker_orders_statuses.append(status)

        return mockserver.make_response(json={'isSuccess': True}, status=200)

    response = await taxi_eats_picker_orders.post(
        api_handler,
        params={'eats_id': eats_id},
        json=DEFAULT_RECEIPT,
        headers=utils.da_headers(picker_id),
    )

    assert response.status_code == 200

    assert mock_processing.times_called == 1

    assert stq.order_paid_billing_events.times_called == 1
