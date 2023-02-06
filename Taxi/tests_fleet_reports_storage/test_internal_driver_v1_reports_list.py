import pytest

ENDPOINT = '/internal/driver/v1/reports/list'


@pytest.mark.pgsql('fleet_reports', files=['pg_fleet_reports.sql'])
async def test_success(taxi_fleet_reports_storage, mockserver):
    @mockserver.handler('/tmp/base_operation_00000000000000003')
    def _mock_mds(request):
        if request.method == 'GET':
            return mockserver.make_response('OK', 200)
        return mockserver.make_response('Wrong Method', 400)

    response = await taxi_fleet_reports_storage.get(
        ENDPOINT,
        params={
            'park_id': 'base_park_id_0',
            'driver_id': 'base_driver_id_0',
            'name': 'report_vat_by_driver',
        },
    )

    assert response.status_code == 200

    report = response.json()['reports'].pop()
    assert report['file_name'] == 'March 2021'
    assert report['link'] is not None
