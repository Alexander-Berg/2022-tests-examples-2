import aiohttp.web
import pytest

from tests_contractor_instant_payouts import utils

ENDPOINT = '/fleet/instant-payouts/v1/payouts/list/download-async'

OK_CSV_PARAMS = [('text/csv', 'utf-8', 3), ('text/csv', None, 7)]


def build_headers(accept_language=None, accept=None, accept_charset=None):
    headers = {
        **utils.SERVICE_HEADERS,
        'X-Ya-User-Ticket': 'ticket_valid1',
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-UID': '123',
        'X-Park-ID': '7ad36bc7560449998acbe2c57a75c293',
    }
    if accept_language is not None:
        headers['Accept-Language'] = accept_language
    if accept is not None:
        headers['Accept'] = accept
    return headers


@pytest.mark.now('2021-01-01T12:00:00+0000')
@pytest.mark.parametrize('accept, accept_charset, tz_offset', OK_CSV_PARAMS)
async def test_csv(
        taxi_contractor_instant_payouts,
        mockserver,
        accept,
        accept_charset,
        tz_offset,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_parks_list(request):
        return {
            'parks': [
                {
                    'city_id': 'city1',
                    'country_id': 'cid1',
                    'demo_mode': False,
                    'driver_partner_source': 'yandex',
                    'id': '7ad36bc7560449998acbe2c57a75c293',
                    'is_active': True,
                    'is_billing_enabled': False,
                    'is_franchising_enabled': False,
                    'locale': 'locale1',
                    'login': 'login1',
                    'name': 'name1',
                    'tz_offset': tz_offset,
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                },
            ],
        }

    @mockserver.json_handler(
        '/fleet-reports-storage/internal/user/v1/operations/create',
    )
    async def _create(request):
        assert request.json == {
            'client_type': 'yandex_user',
            'file_name': 'contractor_instant_payouts_2021-01-01.csv',
            'id': '6c5c10956c2bbe505bb8c42201efe5ef',
            'locale': 'ru',
            'name': 'contractor_instant_payouts_list',
            'park_id': '7ad36bc7560449998acbe2c57a75c293',
            'passport_uid': '123',
        }
        return aiohttp.web.json_response(data={})

    body = {'charset': accept_charset}
    response = await taxi_contractor_instant_payouts.post(
        ENDPOINT,
        headers=build_headers(
            accept_language='ru', accept=accept, accept_charset=accept_charset,
        ),
        params={'operation_id': '6c5c10956c2bbe505bb8c42201efe5ef'},
        json=body if accept_charset is not None else {},
    )

    assert response.status_code == 204, response.text
