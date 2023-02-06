import pytest


@pytest.mark.parametrize(
    'invoice_retrieve_resp_json, expected_status, expected_status_reason',
    [
        ('invoice_retrieve_response_init.json', 'pending', None),
        ('invoice_retrieve_response_processing.json', 'pending', None),
        ('invoice_retrieve_response_done.json', 'success', None),
        ('invoice_retrieve_response_no_operation.json', 'pending', None),
        (
            'invoice_retrieve_response_failed.json',
            'failed',
            {
                'code': 'not_enough_funds',
                'description': 'not_enough_funds_description',
            },
        ),
    ],
)
async def test_main(
        taxi_talaria_payments,
        mockserver,
        load_json,
        invoice_retrieve_resp_json,
        expected_status,
        expected_status_reason,
):
    @mockserver.json_handler('/transactions-ng/v2/invoice/retrieve')
    def invoice_retrieve(request):
        assert request.json == load_json('invoice_retrieve_request.json')

        return load_json(invoice_retrieve_resp_json)

    response = await taxi_talaria_payments.get(
        '/talaria-payments/v1/payments/retrieve',
        headers={'x-api-key': 'wind_api_key', 'X-Real-IP': '1.1.1.1'},
        params={'payment_id': 'payment_id'},
    )
    assert response.status_code == 200
    body = response.json()
    expected_response = load_json('payments_retrieve_response.json')
    expected_response['status'] = expected_status
    if expected_status_reason is not None:
        expected_response['status_reason'] = expected_status_reason

    assert body == expected_response
    assert invoice_retrieve.times_called == 1


async def test_404(taxi_talaria_payments, mockserver, load_json):
    @mockserver.json_handler('/transactions-ng/v2/invoice/retrieve')
    def invoice_retrieve(request):
        assert request.json == load_json('invoice_retrieve_request.json')

        return mockserver.make_response(
            status=404,
            json={'code': 'error_code', 'message': 'error_message'},
        )

    response = await taxi_talaria_payments.get(
        '/talaria-payments/v1/payments/retrieve',
        headers={'x-api-key': 'wind_api_key', 'X-Real-IP': '1.1.1.1'},
        params={'payment_id': 'payment_id'},
    )
    assert response.status_code == 404
    body = response.json()
    assert body == {'code': 'error_code', 'message': 'error_message'}
    assert invoice_retrieve.times_called == 1
