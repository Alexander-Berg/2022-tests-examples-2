import pytest

from testsuite.utils import http

from fleet_rent.entities import park
from fleet_rent.generated.web import web_context as wc


@pytest.mark.now('2020-01-03T10:00:00+03:00')
@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
async def test_vehicle_rent(
        web_app_client,
        web_context: wc.Context,
        load_json,
        mock_parks,
        mock_billing_reports,
        mock_driver_profiles,
        mock_unique_drivers,
        mock_udriver_photos,
        patch,
):
    @patch('fleet_rent.services.park_info.ParkInfoService.get_park_info')
    async def _get_park_info_b(park_id: str):
        return park.Park(
            id=park_id, name='name', clid='clid', owner=None, tz_offset=10,
        )

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _get_driver_profiles(request: http.Request):
        return load_json('driver_profiles.json')

    @mock_udriver_photos('/driver-photos/v1/fleet/photos')
    async def _get_driver_photos(request: http.Request):
        return load_json('udriver_photos.json')

    @mock_unique_drivers('/v1/driver/uniques/retrieve_by_profiles')
    async def _get_unique_driver_ids(request: http.Request):
        return load_json('unique_drivers.json')

    @mock_billing_reports('/v1/balances/select')
    async def _balances_select(request):
        return {
            'entries': [
                {
                    'account': {
                        'account_id': 3460192,
                        'agreement_id': 'taxi/driver_balance',
                        'currency': 'RUB',
                        'entity_external_id': (
                            'taximeter_driver_id/park_id1/driver_id1'
                        ),
                        'sub_account': 'total',
                    },
                    'balances': [
                        {
                            'accrued_at': '2019-12-27T12:02:01+00:00',
                            'balance': '228.0000',
                            'last_created': '2019-09-20T17:06:47.945513+00:00',
                            'last_entry_id': 806300194,
                        },
                    ],
                },
                {
                    'account': {
                        'account_id': 3460195,
                        'agreement_id': 'taxi/driver_balance',
                        'currency': 'RUB',
                        'entity_external_id': (
                            'taximeter_driver_id/park_id1/driver_id2'
                        ),
                        'sub_account': 'total',
                    },
                    'balances': [
                        {
                            'accrued_at': '2019-12-27T12:02:01+00:00',
                            'balance': '1488.0000',
                            'last_created': '2019-12-27T12:02:01+00:00',
                            'last_entry_id': 806300195,
                        },
                    ],
                },
            ],
        }

    @mock_parks('/cars/list')
    async def _cars_list(request: http.Request):
        cars = {
            'id': 'one',
            'brand': 'bmw',
            'model': 'x5',
            'color': 'green',
            'year': 100,
            'number': 'A000AA',
            'status': 'working',
        }
        return {'cars': [cars], 'limit': 100, 'total': 1}

    @mock_parks('/driver-profiles/list')
    async def _driver_profiles_list(request: http.Request):
        return {
            'driver_profiles': [
                {
                    'accounts': [{'currency': 'RUB', 'id': 'driver_id'}],
                    'driver_profile': {'id': 'driver_id'},
                },
            ],
            'limit': 1,
            'offset': 0,
            'parks': [{'id': 'driver_park_id'}],
            'total': 1,
        }

    response = await web_app_client.post(
        '/fleet/rent/v1/vehicles/by-days',
        headers={
            'X-Yandex-UID': '100',
            'X-Park-Id': 'park_id1',
            'X-Ya-User-Ticket': 'abc',
            'X-Ya-User-Ticket-Provider': 'yandex',
        },
        json={
            'from': '2020-01-03T00:00:00+10:00',
            'days': 3,
            'limit': 100,
            'filter': {
                'statuses': ['working'],
                'amenities': ['wifi'],
                'categories': ['business'],
                'search_text': 'A999AA199',
                'is_rental': False,
            },
        },
    )

    expected_response = {
        'drivers': [
            {
                'balance': '228.0000',
                'first_name': 'Саппорт',
                'id': 'driver_id1',
                'last_name': 'Саппортов',
                'portrait_url': 'avatar_url_1',
            },
            {
                'balance': '1488.0000',
                'first_name': 'Гаврила',
                'id': 'driver_id2',
                'last_name': 'Мишин',
                'middle_name': 'Андреевич',
                'portrait_url': 'avatar_url_2',
            },
        ],
        'total': 1,
        'vehicles': [
            {
                'brand': 'bmw',
                'data_by_day': [
                    {
                        'rents': [
                            {
                                'balance_notify_limit': '1001',
                                'driver_id': 'driver_id2',
                                'daily_price': '500',
                                'id': 'record_id2',
                            },
                            {
                                'affiliation_id': 'affiliation1',
                                'balance_notify_limit': '1000',
                                'driver_id': 'driver_id1',
                                'id': 'record_id1',
                            },
                        ],
                    },
                    {
                        'rents': [
                            {
                                'affiliation_id': 'affiliation1',
                                'balance_notify_limit': '1000',
                                'daily_price': '100',
                                'driver_id': 'driver_id1',
                                'id': 'record_id1',
                            },
                        ],
                    },
                    {
                        'rents': [
                            {
                                'affiliation_id': 'affiliation1',
                                'balance_notify_limit': '1000',
                                'driver_id': 'driver_id1',
                                'id': 'record_id1',
                            },
                        ],
                    },
                ],
                'id': 'one',
                'model': 'x5',
                'number': 'A000AA',
                'status': 'working',
            },
        ],
    }

    assert response.status == 200, response.text
    assert await response.json() == expected_response
