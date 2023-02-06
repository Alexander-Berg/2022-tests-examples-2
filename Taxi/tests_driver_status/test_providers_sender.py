import json

import pytest


@pytest.mark.config(
    DRIVER_STATUS_ENABLE_EVENT_LISTENERS={
        '__default__': False,
        'providers-sender': True,
    },
)
@pytest.mark.pgsql('driver-status', files=['pg_fill_service_tables.sql'])
@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            {
                'driver_providers': ['park'],
                'park_providers': [],
                'integration_events': ['enabled', 'carstatus'],
                'expected_providers_mask': 0,
                'expected_event': True,
            },
        ),
        pytest.param(
            {
                'driver_providers': ['park'],
                'park_providers': ['park'],
                'integration_events': ['enabled'],
                'expected_providers_mask': 1,
                'expected_event': False,
            },
        ),
        pytest.param(
            {
                'driver_providers': ['park', 'yandex'],
                'park_providers': ['park'],
                'integration_events': ['carstatus'],
                'expected_providers_mask': 1,
                'expected_event': False,
            },
        ),
        pytest.param(
            {
                'driver_providers': ['park', 'formula'],
                'park_providers': ['park', 'formula'],
                'integration_events': ['enabled', 'carstatus'],
                'expected_providers_mask': 129,
                'expected_event': True,
            },
        ),
        pytest.param(
            {
                'driver_providers': ['park', 'yandex'],
                'park_providers': ['park', 'yandex'],
                'integration_events': ['enabled', 'carstatus'],
                'expected_providers_mask': 1,
                'expected_event': True,
            },
        ),
    ],
)
async def test_providers_sender(
        taxi_driver_status,
        testpoint,
        mockserver,
        redis_store,
        params,
        taxi_config,
):
    park_id = 'park0'
    driver_id = 'driver0'

    @testpoint('providers-sender-tp')
    def _redis_providers_sender_testpoint(request):
        return {}

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _driver_profiles(request):
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'park0_driver0',
                    'data': {'providers': params['driver_providers']},
                },
            ],
        }

    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _fleet_parks(request):
        return {
            'parks': [
                {
                    'id': 'park0',
                    'login': 'park_login',
                    'name': 'park_name',
                    'is_active': True,
                    'city_id': 'city_id',
                    'locale': 'locale',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'country_id': 'country_id',
                    'demo_mode': False,
                    'providers': params['park_providers'],
                    'integration_events': params['integration_events'],
                    'geodata': {'lat': 40, 'lon': 13, 'zoom': 9},
                },
            ],
        }

    await taxi_driver_status.enable_testpoints()
    _redis_providers_sender_testpoint.flush()

    response = await taxi_driver_status.post(
        'v2/status/client',
        headers={
            'X-YaTaxi-Park-Id': park_id,
            'X-YaTaxi-Driver-Profile-Id': driver_id,
            'X-Request-Application-Version': '9.40',
            'X-Request-Version-Type': '',
            'X-Request-Platform': 'android',
        },
        data=json.dumps({'target_status': 'free'}),
    )
    assert response.status_code == 200

    await _driver_profiles.wait_call()
    await _fleet_parks.wait_call()
    await _redis_providers_sender_testpoint.wait_call()

    redis_key = 'STATUS_DRIVERS:PROVIDERS:TASK'
    sent_data = json.loads(redis_store.lindex(redis_key, 0))
    assert sent_data['Db'] == park_id
    assert sent_data['Driver'] == driver_id
    assert sent_data['Providers'] == params['expected_providers_mask']
    if params['expected_event']:
        assert sent_data['IntegrationEvent'] is True
    else:
        assert 'IntegrationEvent' not in sent_data
