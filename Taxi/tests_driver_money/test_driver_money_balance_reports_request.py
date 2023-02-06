# pylint: disable=C0302
import pytest

ENDPOINT = '/driver/v1/driver-money/v1/balance/reports/request'

FLEET_REPORTS_STORAGE_REQUEST = {
    'park_id': 'park_id_0',
    'driver_id': 'driver',
    'name': 'report_vat_by_driver',
}

FLEET_REPORTS_REQUEST = {
    'park_id': 'park_id_0',
    'driver_id': 'driver',
    'period_at': '2021-05-01',
}


@pytest.mark.now('2020-06-16T12:00:00+0300')
async def test_request(
        taxi_driver_money, load_json, mockserver, driver_authorizer,
):
    frs_stub = load_json('fleet_reports_storage.json')
    service_stub = load_json('service.json')

    @mockserver.json_handler(
        '/fleet-reports-storage/internal/driver/v1/reports/list',
    )
    def _mock_fleet_reports_storage(request):
        assert request.method == 'GET'
        assert request.query == FLEET_REPORTS_STORAGE_REQUEST
        return frs_stub['response']['many_reports']

    @mockserver.json_handler(
        '/fleet-reports/internal/driver/v1/report-vat/request',
    )
    def _mock_fleet_reports(request):
        assert request.json == FLEET_REPORTS_REQUEST
        return {'operation_id': 'operation_id_0'}

    driver_authorizer.set_session('park_id_0', 'driver_session', 'driver')

    response = await taxi_driver_money.post(
        ENDPOINT,
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
        json=service_stub['request'],
    )
    assert response.status_code == 200
    assert response.json() == service_stub['response']['success']


@pytest.mark.now('2020-06-16T12:00:00+0300')
async def test_request_restricted(
        taxi_driver_money, load_json, mockserver, driver_authorizer,
):
    frs_stub = load_json('fleet_reports_storage.json')
    service_stub = load_json('service.json')

    @mockserver.json_handler(
        '/fleet-reports-storage/internal/driver/v1/reports/list',
    )
    def _mock_fleet_reports_storage(request):
        assert request.method == 'GET'
        assert request.query == FLEET_REPORTS_STORAGE_REQUEST
        return frs_stub['response']['no_reports']

    @mockserver.json_handler(
        '/fleet-reports/internal/driver/v1/report-vat/request',
    )
    def _mock_fleet_reports(request):
        assert request.json == FLEET_REPORTS_REQUEST
        return mockserver.make_response(
            json={'code': 'FORBIDDEN', 'message': 'forbidden'}, status=403,
        )

    driver_authorizer.set_session('park_id_0', 'driver_session', 'driver')

    response = await taxi_driver_money.post(
        ENDPOINT,
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
        json=service_stub['request'],
    )
    assert response.status_code == 200
    assert response.json() == service_stub['response']['restricted']


@pytest.mark.now('2020-06-16T12:00:00+0300')
async def test_request_error(
        taxi_driver_money, load_json, mockserver, driver_authorizer,
):
    frs_stub = load_json('fleet_reports_storage.json')
    service_stub = load_json('service.json')

    @mockserver.json_handler(
        '/fleet-reports-storage/internal/driver/v1/reports/list',
    )
    def _mock_fleet_reports_storage(request):
        assert request.method == 'GET'
        assert request.query == FLEET_REPORTS_STORAGE_REQUEST
        return frs_stub['response']['no_reports']

    @mockserver.json_handler(
        '/fleet-reports/internal/driver/v1/report-vat/request',
    )
    def _mock_fleet_reports(request):
        assert request.json == FLEET_REPORTS_REQUEST
        return mockserver.make_response(
            json={'code': 'ERROR', 'message': 'error'}, status=500,
        )

    driver_authorizer.set_session('park_id_0', 'driver_session', 'driver')

    response = await taxi_driver_money.post(
        ENDPOINT,
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
        json=service_stub['request'],
    )
    assert response.status_code == 200
    assert response.json() == service_stub['response']['error']


@pytest.mark.now('2020-06-16T12:00:00+0300')
async def test_request_try_again_later(
        taxi_driver_money, load_json, mockserver, driver_authorizer,
):
    frs_stub = load_json('fleet_reports_storage.json')
    service_stub = load_json('service.json')

    @mockserver.json_handler(
        '/fleet-reports-storage/internal/driver/v1/reports/list',
    )
    def _mock_fleet_reports_storage(request):
        assert request.method == 'GET'
        assert request.query == FLEET_REPORTS_STORAGE_REQUEST
        return frs_stub['response']['no_reports']

    @mockserver.json_handler(
        '/fleet-reports/internal/driver/v1/report-vat/request',
    )
    def _mock_fleet_reports(request):
        assert request.json == FLEET_REPORTS_REQUEST
        return mockserver.make_response(
            json={'code': 'NOT_FOUND', 'message': 'not found'}, status=404,
        )

    driver_authorizer.set_session('park_id_0', 'driver_session', 'driver')

    response = await taxi_driver_money.post(
        ENDPOINT,
        headers={
            'User-Agent': 'Taximeter 8.90 (228)',
            'Accept-Language': 'ru',
            'X-Request-Application-Version': '8.90',
            'X-YaTaxi-Park-Id': 'park_id_0',
            'X-YaTaxi-Driver-Profile-Id': 'driver',
        },
        json=service_stub['request'],
    )
    assert response.status_code == 200
    assert response.json() == service_stub['response']['try_again_later']
