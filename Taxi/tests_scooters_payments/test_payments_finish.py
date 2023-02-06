import pytest


@pytest.mark.experiments3(filename='exp3_scooters_payments_config.json')
@pytest.mark.now('2022-07-06T12:00:00+00:00')
async def test_payments_finish(taxi_scooters_payments, mockserver, load_json):
    @mockserver.json_handler('/transactions-ng/v2/invoice/retrieve')
    def invoice_retrieve(request):
        assert request.json == {
            'id': 'SESSION_ID',
            'id_namespace': 'scooters',
            'prefer_transactions_data': False,
        }
        return load_json('invoice_retrieve_held.json')

    @mockserver.json_handler('/transactions-ng/v2/invoice/update')
    def invoice_update(request):
        assert request.json == load_json(
            'invoice_update_expected_request.json',
        )
        return {}

    @mockserver.json_handler('/transactions-ng/invoice/clear')
    def invoice_clear(request):
        assert request.json == load_json('invoice_clear_expected_request.json')
        return {}

    response = await taxi_scooters_payments.post(
        '/scooters-payments/v1/payments/finish',
        params={'session_id': 'SESSION_ID'},
        json={},
    )

    assert response.status_code == 200
    assert response.json() == {}

    assert invoice_retrieve.times_called == 1
    assert invoice_update.times_called == 1
    assert invoice_clear.times_called == 1


@pytest.mark.experiments3(filename='exp3_scooters_payments_config.json')
@pytest.mark.now('2022-07-06T12:00:00+00:00')
async def test_invoice_not_found(
        taxi_scooters_payments, mockserver, load_json,
):
    @mockserver.json_handler('/transactions-ng/v2/invoice/retrieve')
    def invoice_retrieve(request):
        assert request.json == load_json(
            'invoice_retrieve_expected_request.json',
        )
        return mockserver.make_response(
            status=404, json=load_json('invoice_retrieve_not_found.json'),
        )

    response = await taxi_scooters_payments.post(
        '/scooters-payments/v1/payments/finish',
        params={'session_id': 'SESSION_ID'},
        json={},
    )

    assert response.status_code == 404
    assert response.json() == load_json('invoice_retrieve_not_found.json')

    assert invoice_retrieve.times_called == 1


@pytest.mark.experiments3(filename='exp3_scooters_payments_config.json')
@pytest.mark.now('2022-07-06T12:00:00+00:00')
async def test_invoice_cleared(taxi_scooters_payments, mockserver, load_json):
    @mockserver.json_handler('/transactions-ng/v2/invoice/retrieve')
    def invoice_retrieve(request):
        assert request.json == load_json(
            'invoice_retrieve_expected_request.json',
        )
        return load_json('invoice_retrieve_cleared.json')

    response = await taxi_scooters_payments.post(
        '/scooters-payments/v1/payments/finish',
        params={'session_id': 'SESSION_ID'},
        json={},
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'bad_invoice_status',
        'message': 'cleared',
    }

    assert invoice_retrieve.times_called == 1
