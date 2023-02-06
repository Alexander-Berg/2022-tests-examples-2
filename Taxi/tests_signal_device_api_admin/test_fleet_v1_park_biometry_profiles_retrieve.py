import pytest

from tests_signal_device_api_admin import web_common


@pytest.mark.pgsql('signal_device_api_meta_db', files=['test_data.sql'])
async def test_ok_partners(taxi_signal_device_api_admin, mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(),
                    'specifications': ['signalq'],
                },
            ],
        }

    @mockserver.json_handler(
        '/biometry-etalons/internal/biometry-etalons/v1/profiles/search',
    )
    def _get_photo(request):
        request_parsed = request.json
        assert request_parsed == {
            'limit': 10,
            'filter': {
                'providers': ['signalq'],
                'meta': {
                    'park_id': 'p1',
                    'device_serial_numbers': ['AB1', 'AB12FE45DD'],
                    'park_id_car_ids': ['p1_1', 'p1_2'],
                },
                'profile_types': ['anonymous'],
                'created_at': {'from': '2019-03-10T07:00:00+00:00'},
            },
            'urls': {'external': True, 'ttl': 1440},
            'meta_projection': [],
        }

        return {  # Random profile
            'profiles': [
                {
                    'provider': 'signalq',
                    'profile': {'type': 'anonymous', 'id': 'p1_d1'},
                    'profile_media': {
                        'photo': [
                            {
                                'media_id': '1',
                                'storage_id': 'xxx',
                                'storage_bucket': 'yyy',
                                'storage_type': 'signalq-s3',
                                'temporary_url': 'test',
                            },
                        ],
                    },
                },
                {
                    'provider': 'signalq',
                    'profile': {'type': 'anonymous', 'id': 'p1_d2'},
                },
            ],
            'cursor': 'xxx',
        }

    @mockserver.json_handler(
        '/fleet-vehicles/v1/vehicles/retrieve_by_number_with_normalization',
    )
    def _get_car_ids(request):
        request_parsed = request.json
        assert request_parsed == {
            'numbers_in_set': ['AB1', 'AB2'],
            'projection': ['park_id_car_id'],
        }

        return {
            'vehicles': [
                {'park_id_car_id': 'p1_1'},
                {'park_id_car_id': 'p1_2'},
            ],
        }

    response = await taxi_signal_device_api_admin.post(
        'fleet/signal-device-api-admin/v1/park/biometry-profiles/retrieve',
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
        json={
            'query': {
                'text': 'B',
                'filter': {'group_id': '635ffb7b-8c06-476d-a30a-4bc9ae65d272'},
            },
            'created_at': {'from': '2019-03-10T10:00:00+03:00'},
        },
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'profiles': [
            {
                'profile_id': 'p1_d1',
                'media_by_types': {
                    'photo': [{'media_id': '1', 'temporary_url': 'test'}],
                },
                'profile_type': 'anonymous',
            },
            {'profile_id': 'p1_d2', 'profile_type': 'anonymous'},
        ],
        'cursor': 'xxx',
    }
