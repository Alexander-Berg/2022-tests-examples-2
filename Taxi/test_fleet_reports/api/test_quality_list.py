import aiohttp.web
import pytest


@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
async def test_success(web_app_client, headers, mock_api7, load_json):
    stub = load_json('success.json')
    stub_api7_drivers = load_json('success_api7_drivers.json')

    @mock_api7('/v1/parks/driver-profiles/list')
    async def _list_driver_profiles(request):
        assert request.json == stub_api7_drivers['request_drivers']
        return aiohttp.web.json_response(stub_api7_drivers['response_drivers'])

    response = await web_app_client.post(
        '/reports-api/v1/quality/list',
        headers=headers,
        json={
            'period': {'from': '2020-03-02', 'to': '2020-03-15'},
            'limit': 25,
            'sort_order': {'direction': 'asc', 'field': 'rating_end'},
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']


@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
async def test_success_with_driver_ids(
        web_app_client, headers, mock_api7, load_json,
):
    stub = load_json('success.json')
    stub_api7_drivers = load_json('success_api7_drivers.json')

    @mock_api7('/v1/parks/driver-profiles/list')
    async def _list_driver_profiles(request):
        assert (
            request.json
            == stub_api7_drivers['request_drivers_with_driver_ids']
        )
        return aiohttp.web.json_response(
            stub_api7_drivers['response_drivers_with_driver_ids'],
        )

    response = await web_app_client.post(
        '/reports-api/v1/quality/list',
        headers=headers,
        json={
            'period': {'from': '2020-03-02', 'to': '2020-03-15'},
            'limit': 25,
            'sort_order': {'direction': 'asc', 'field': 'rating_end'},
            'driver_ids': ['038b62af7118498583d3ec1d05132fee'],
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response_with_driver_ids']


@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
async def test_success_period_one_week(
        web_app_client, headers, mock_api7, load_json,
):
    stub = load_json('success.json')
    stub_api7_drivers = load_json('success_api7_drivers.json')

    @mock_api7('/v1/parks/driver-profiles/list')
    async def _list_driver_profiles(request):
        assert request.json == stub_api7_drivers['request_drivers_p1w']
        return aiohttp.web.json_response(
            stub_api7_drivers['response_drivers_p1w'],
        )

    response = await web_app_client.post(
        '/reports-api/v1/quality/list',
        headers=headers,
        json={
            'period': {'from': '2020-03-09', 'to': '2020-03-15'},
            'limit': 25,
            'sort_order': {'direction': 'asc', 'field': 'rating_end'},
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response_p1w']


@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
async def test_success_empty(web_app_client, headers, load_json):
    stub = load_json('success.json')

    response = await web_app_client.post(
        '/reports-api/v1/quality/list',
        headers=headers,
        json={
            'period': {'from': '2020-03-30', 'to': '2020-04-05'},
            'limit': 25,
            'sort_order': {'direction': 'asc', 'field': 'rating_end'},
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response_empty']


@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
async def test_success_support_mode(
        web_app_client, mock_parks, headers_support, mock_api7, load_json,
):
    stub = load_json('success.json')
    stub_api7_drivers = load_json('success_api7_drivers.json')

    @mock_api7('/v1/parks/driver-profiles/list')
    async def _list_driver_profiles(request):
        assert request.json == stub_api7_drivers['request_drivers']
        return aiohttp.web.json_response(stub_api7_drivers['response_drivers'])

    response = await web_app_client.post(
        '/reports-api/v1/quality/list',
        headers=headers_support,
        json={
            'period': {'from': '2020-03-02', 'to': '2020-03-15'},
            'limit': 25,
            'sort_order': {'direction': 'asc', 'field': 'rating_end'},
        },
    )

    assert response.status == 200

    report = []
    for item in stub['service_response']['report']:
        del item['driver']['phone']
        report.append(item)
    stub['service_response']['report'] = report

    data = await response.json()
    assert data == stub['service_response']
