# pylint: disable=C0302
import pytest

ENDPOINT = '/driver/v1/driver-money/v1/balance/reports/list'

FLEET_REPORTS_STORAGE_REQUEST = {
    'park_id': 'park_id_0',
    'driver_id': 'driver',
    'name': 'report_vat_by_driver',
}


@pytest.mark.now('2020-06-16T12:00:00+0300')
async def test_no_reports(
        taxi_driver_money, load_json, mockserver, driver_authorizer,
):
    service_stub = load_json('service.json')

    @mockserver.json_handler(
        '/fleet-reports-storage/internal/driver/v1/reports/list',
    )
    def _mock_fleet_reports_storage(request):
        assert request.method == 'GET'
        assert request.query == FLEET_REPORTS_STORAGE_REQUEST
        return {'reports': []}

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
    assert response.json() == service_stub['response']['no_reports']


@pytest.mark.now('2020-06-16T12:00:00+0300')
async def test_one_report(
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
        return frs_stub['response']['one_report']

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
    assert response.json() == service_stub['response']['one_report']


@pytest.mark.now('2020-06-16T12:00:00+0300')
async def test_many_reports(
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
    assert response.json() == service_stub['response']['many_reports']
