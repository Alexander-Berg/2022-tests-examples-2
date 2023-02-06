import pytest

from tests_signal_device_api_admin import web_common


@pytest.mark.parametrize(
    'profile_id',
    [
        pytest.param('d1', id='driver_profile_id'),
        pytest.param('anon', id='profile_id'),
    ],
)
async def test_ok_partners(
        taxi_signal_device_api_admin, mockserver, profile_id,
):
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
    def _get_profile(request):
        request_parsed = request.json
        if request_parsed == {'provider': 'signalq', 'profile_ids': ['p1_d1']}:
            return {
                'profiles': [
                    {
                        'provider': 'signalq',
                        'profile': {
                            'type': 'park_driver_profile_id',
                            'id': 'p1_d1',
                        },
                    },
                ],
            }
        return {'profiles': []}

    @mockserver.json_handler(
        '/biometry-etalons/internal/biometry-etalons/v1/profile/split',
    )
    def _split(request):
        request_parsed = request.json
        if profile_id == 'p1':
            assert request_parsed == {
                'profile_id': 'p1_d1',
                'media_ids': ['m1'],
                'provider': 'signalq',
                'new_profile_meta': {'park_id': 'p1'},
            }
        elif profile_id == 'anon':
            assert request_parsed == {
                'profile_id': 'anon',
                'media_ids': ['m1'],
                'provider': 'signalq',
                'new_profile_meta': {'park_id': 'p1'},
            }
        return {'profile': {'id': 'bp1', 'type': 'type'}}

    response = await taxi_signal_device_api_admin.post(
        'fleet/signal-device-api-admin/v1/park/biometry-profiles/split',
        headers={
            **web_common.PARTNER_HEADERS_1,
            'X-Park-Id': 'p1',
            'X-Idempotency-Token': '5e603e40123f487ab4036369be02d4ea',
        },
        json={'profile_id': profile_id, 'media_ids': ['m1']},
    )
    assert response.status_code == 200, response.text
