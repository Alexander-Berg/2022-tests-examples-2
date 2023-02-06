from tests_signal_device_api_admin import web_common


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
        '/biometry-etalons/internal/biometry-etalons/v1/profiles/retrieve',
    )
    def _get_photo(request):
        request_parsed = request.json
        assert request_parsed == {
            'provider': 'signalq',
            'profile_ids': ['p1_d1'],
            'urls': {'external': True, 'ttl': 1440},
            'meta_projection': [],
        }

        return {
            'profiles': [
                {
                    'provider': 'signalq',
                    'profile': {
                        'type': 'park_driver_profile_id',
                        'id': 'p1_d1',
                    },
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
            ],
        }

    response = await taxi_signal_device_api_admin.post(
        'fleet/signal-device-api-admin/v1/driver/biometry-profile/retrieve',
        params={'driver_profile_id': 'd1'},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'biometry_profile': {
            'profile_id': 'p1_d1',
            'profile_type': 'park_driver_profile_id',
            'media_by_types': {
                'photo': [{'media_id': '1', 'temporary_url': 'test'}],
            },
        },
    }
