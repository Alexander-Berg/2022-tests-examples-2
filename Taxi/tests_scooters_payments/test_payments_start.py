import pytest

from tests_scooters_payments import consts


@pytest.mark.experiments3(filename='exp3_scooters_payments_config.json')
@pytest.mark.now('2022-07-06T12:00:00+00:00')
async def test_payments_start(taxi_scooters_payments, mockserver, load_json):
    @mockserver.json_handler('/scooter-backend/api/taxi/sessions/current')
    def sessions_current(request):
        assert request.query == {'session_id': 'SESSION_ID'}
        return load_json('sessions_current.json')

    @mockserver.json_handler('/transactions-ng/v2/invoice/create')
    def invoice_create(request):
        assert request.json == load_json(
            'invoice_create_expected_request.json',
        )
        return {}

    @mockserver.json_handler('/transactions-ng/v2/invoice/update')
    def invoice_update(request):
        assert request.json == load_json(
            'invoice_update_expected_request.json',
        )
        return {}

    response = await taxi_scooters_payments.post(
        '/scooters-payments/v1/payments/start',
        headers=consts.AUTH_HEADERS,
        params={'session_id': 'SESSION_ID'},
        json={},
    )

    assert response.status_code == 200
    assert response.json() == {}

    assert sessions_current.times_called == 1
    assert invoice_create.times_called == 1
    assert invoice_update.times_called == 1


@pytest.mark.experiments3(filename='exp3_scooters_payments_config.json')
@pytest.mark.now('2022-07-06T12:00:00+00:00')
async def test_drive_deposit(taxi_scooters_payments, mockserver, load_json):
    @mockserver.json_handler('/scooter-backend/api/taxi/sessions/current')
    def sessions_current(request):
        assert request.query == {'session_id': 'SESSION_ID'}
        response = load_json('sessions_current.json')
        prices = response['segment']['session']['specials']['current_offer'][
            'prices'
        ]
        prices['use_deposit'] = True
        prices['deposit'] = 50000
        return response

    @mockserver.json_handler('/transactions-ng/v2/invoice/create')
    def invoice_create(_):
        pass

    @mockserver.json_handler('/transactions-ng/v2/invoice/update')
    def invoice_update(_):
        pass

    response = await taxi_scooters_payments.post(
        '/scooters-payments/v1/payments/start',
        headers=consts.AUTH_HEADERS,
        params={'session_id': 'SESSION_ID'},
        json={},
    )

    assert response.status_code == 200
    assert response.json() == {}

    assert sessions_current.times_called == 1
    assert invoice_create.times_called == 0
    assert invoice_update.times_called == 0
