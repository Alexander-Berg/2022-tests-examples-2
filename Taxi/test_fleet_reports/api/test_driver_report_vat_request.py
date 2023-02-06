# pylint: disable=W0212
import datetime
import hashlib

import aiohttp.web
import pytest

ENDPOINT = '/internal/driver/v1/report-vat/request'


async def test_not_found(web_app_client, mock_fleet_parks, load_json):
    stub = load_json('stub.json')

    @mock_fleet_parks('/v1/parks/list')
    async def _v1_parks_list(request):
        assert request.json == stub['fleet_parks']['request']
        return aiohttp.web.json_response(stub['fleet_parks']['response'])

    response = await web_app_client.post(
        ENDPOINT,
        json={
            'driver_id': '7750dd3fc1104b6298bcf2483db20b50',
            'park_id': '1b0512eca97c4a1bbe53b50bdc0d5179',
            'period_at': '2021-03-01',
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status == 404


async def test_forbidden(web_app_client, mock_fleet_parks, load_json):
    stub = load_json('stub.json')

    @mock_fleet_parks('/v1/parks/list')
    async def _v1_parks_list(request):
        assert request.json == stub['fleet_parks']['request']
        return aiohttp.web.json_response(data={'parks': []})

    response = await web_app_client.post(
        ENDPOINT,
        json={
            'driver_id': '7750dd3fc1104b6298bcf2483db20b50',
            'park_id': '1b0512eca97c4a1bbe53b50bdc0d5179',
            'period_at': '2021-03-01',
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status == 403


@pytest.mark.translations(
    opteum_vat={
        'taximeter_report_file_name': {'ru': '{month} {year}'},
        'label_month_3': {'ru': 'Март'},
    },
)
@pytest.mark.pgsql('fleet_reports', files=('fleet_reports.sql',))
async def test_success(
        web_app_client,
        mock_fleet_parks,
        mock_fleet_reports_storage,
        load_json,
        patch,
        stq,
):
    stub = load_json('stub.json')

    @patch('datetime.datetime.utcnow')
    def _utcnow():
        return datetime.datetime.fromisoformat('2021-05-14T18:53:00+03:00')

    @patch('datetime.date.today')
    def _today():
        return datetime.datetime.fromisoformat('2021-05-14')

    @mock_fleet_parks('/v1/parks/list')
    async def _v1_parks_list(request):
        assert request.json == stub['fleet_parks']['request']
        return aiohttp.web.json_response(stub['fleet_parks']['response'])

    @mock_fleet_reports_storage('/internal/driver/v1/operations/create')
    async def _create(request):
        assert request.json == stub['fleet_reports_storage']['request']
        return aiohttp.web.json_response(data={})

    operation_id = hashlib.md5(
        ':'.join(
            [
                '1b0512eca97c4a1bbe53b50bdc0d5179',
                '7750dd3fc1104b6298bcf2483db20b50',
                '2021-03-01',
                '2021-05-14',
            ],
        ).encode(),
    ).hexdigest()

    response = await web_app_client.post(
        ENDPOINT,
        json={
            'driver_id': '7750dd3fc1104b6298bcf2483db20b50',
            'park_id': '1b0512eca97c4a1bbe53b50bdc0d5179',
            'period_at': '2021-03-01',
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status == 200
    data = await response.json()
    assert data == {'operation_id': operation_id}

    assert stq.fleet_reports_vat_taximeter.has_calls
