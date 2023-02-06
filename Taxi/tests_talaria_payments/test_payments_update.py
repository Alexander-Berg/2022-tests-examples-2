import pytest


@pytest.mark.parametrize(
    [
        'invoice_case_1',
        'invoice_update_response',
        'invoice_case_2',
        'expected_response',
    ],
    [
        ('no_conflict', 200, None, 200),
        ('no_conflict_dif_version', None, None, 200),
        ('items_mismatch', None, None, 409),
        ('not_found', None, None, 404),
        ('no_conflict', 404, None, 500),
        ('no_conflict', 409, 'no_conflict_dif_version', 200),
        ('no_conflict', 409, 'items_mismatch', 409),
    ],
)
async def test_main(
        taxi_talaria_payments,
        mockserver,
        load_json,
        invoice_case_1: str,
        invoice_update_response: int,
        invoice_case_2: str,
        expected_response: int,
):
    @mockserver.json_handler('/transactions-ng/v2/invoice/retrieve')
    def invoice_retrieve(request):
        assert request.json == load_json('invoice_retrieve_request.json')
        if invoice_retrieve.times_called == 0:
            invoice_case = invoice_case_1
        else:
            invoice_case = invoice_case_2

        if invoice_case == 'not_found':
            invoice_retrieve_response = 404
            response = {'code': 'code', 'message': 'message'}
        else:
            invoice_retrieve_response = 200
            response = load_json(
                f'invoice_retrieve_response_{invoice_case}.json',
            )

        return mockserver.make_response(
            status=invoice_retrieve_response, json=response,
        )

    @mockserver.json_handler('/transactions-ng/v2/invoice/update')
    def invoice_update(request):
        assert request.json == load_json('invoice_update_request.json')
        if invoice_update_response == 200:
            response = {}
        else:
            response = {'code': 'code', 'message': 'message'}
        return mockserver.make_response(
            status=invoice_update_response, json=response,
        )

    response = await taxi_talaria_payments.post(
        '/talaria-payments/v1/payments/update',
        headers={'x-api-key': 'wind_api_key', 'X-Real-IP': '1.1.1.1'},
        json=load_json('payments_update_request.json'),
    )
    assert response.status_code == expected_response
    assert invoice_retrieve.times_called == (1 if invoice_case_1 else 0) + (
        1 if invoice_case_2 else 0
    )

    if invoice_update_response is not None:
        assert invoice_update.times_called == 1
    else:
        assert invoice_update.times_called == 0
