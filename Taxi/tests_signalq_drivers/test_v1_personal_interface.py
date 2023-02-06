import pytest

HEADERS = {
    'X-YaTaxi-Park-Id': 'p1',
    'X-YaTaxi-Driver-Profile-Id': 'd1',
    'X-Ya-User-Ticket': 'valid_user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-UID': '54591353',
    'X-Request-Application-Version': '9.60 (1234)',
}

BIOMETRY_ETALONS_RESPONSE = {
    'profiles': [
        {
            'provider': 'signalq',
            'profile': {'id': 'p1_d1', 'type': 'park_driver_profile_id'},
            'profile_media': {
                'photo': [
                    {
                        'media_id': 'm1',
                        'storage_id': 's1',
                        'storage_bucket': 'driver-photo',
                        'storge_type': 'media-storage',
                        'temporary_url': 'some_url',
                    },
                ],
            },
        },
    ],
}

GNSS = {
    'lat': 54.99250000,
    'lon': 73.36861111,
    'speed_kmph': 34.437895,
    'accuracy_m': 0.61340,
    'direction_deg': 245.895,
}

COMMENT = {
    'comments_count': 2,
    'last_comment': {
        'id': 'com1',
        'text': 'cute',
        'created_at': '2020-02-02T00:30:11+00:00',
    },
}

VEHICLE = {'id': 'car1', 'plate_number': 'A133ЮЯ116'}

DRIVER_EVENT = {
    'id': 'e1',
    'park_id': 'p1',
    'event_at': '2021-02-25T03:02:01+00:00',
    'gnss': GNSS,
    'type': 'sleep',
    'comments_info': COMMENT,
    'is_critical': True,
    'vehicle': VEHICLE,
    'video': {
        'presigned_url': {
            'link': 'pre_url_1',
            'expires_at': '2021-12-22T21:12:02+00:00',
        },
    },
    'external_photo': {
        'presigned_url': {
            'link': 'pre_url_2',
            'expires_at': '2021-12-22T21:12:02+00:00',
        },
    },
}

DRIVER_PROFILES_RESPONSE = {
    'profiles': [
        {
            'park_driver_profile_id': 'p1_d1',
            'data': {
                'full_name': {'first_name': 'Signal', 'last_name': 'Andreev'},
            },
        },
    ],
}

FULL_RESPONSE = {
    'events': [DRIVER_EVENT],
    'driver_name': 'Andreev Signal',
    'biometry_profile': {
        'profile_id': 'p1_d1',
        'profile_photos': [{'media_id': 'm1', 'link': 'some_url'}],
    },
}


@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.parametrize(
    'period_from, period_to, is_biometry_failed, '
    'is_driver_profiles_failed, expected_code, expected_response',
    [
        pytest.param(
            '2021-02-23T00:00:00+00:00',
            '2021-02-28T00:00:00+00:00',
            False,
            False,
            200,
            FULL_RESPONSE,
            id='ok test',
        ),
        pytest.param(
            '2021-02-23T00:00:00+00:00',
            '2021-02-28T00:00:00+00:00',
            True,
            False,
            200,
            {
                'events': FULL_RESPONSE['events'],
                'driver_name': FULL_RESPONSE['driver_name'],
            },
            id='test biometry failed',
        ),
        pytest.param(
            '2021-02-23T00:00:00+00:00',
            '2021-02-28T00:00:00+00:00',
            False,
            True,
            200,
            {
                'events': FULL_RESPONSE['events'],
                'biometry_profile': FULL_RESPONSE['biometry_profile'],
            },
            id='test driver-profiles failed',
        ),
        pytest.param(
            '2021-02-28T00:00:00+00:00',
            '2021-02-23T00:00:00+00:00',
            False,
            False,
            400,
            None,
            id='test wrong period',
        ),
    ],
)
async def test_personal_interface(
        taxi_signalq_drivers,
        mockserver,
        period_from,
        period_to,
        is_biometry_failed,
        is_driver_profiles_failed,
        expected_code,
        expected_response,
):
    @mockserver.json_handler(
        '/biometry-etalons/internal/biometry-etalons/v1/profiles/retrieve',
    )
    def _retrieve(request):
        assert request.json == {
            'provider': 'signalq',
            'profile_ids': ['p1_d1'],
            'urls': {'ttl': 1440, 'external': True},
            'meta_projection': [],
        }
        if is_biometry_failed:
            return mockserver.make_response(json={}, status=500)
        return mockserver.make_response(
            json=BIOMETRY_ETALONS_RESPONSE, status=200,
        )

    @mockserver.json_handler(
        '/signal-device-api-admin/internal/'
        'signal-device-api-admin/v1/driver/events',
    )
    def _get_events(request):
        assert request.json == {
            'period': {'from': period_from, 'to': period_to},
        }
        return mockserver.make_response(
            json={'events': [DRIVER_EVENT]}, status=200,
        )

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _get_name(request):
        assert request.json == {
            'id_in_set': ['p1_d1'],
            'projection': ['data.full_name'],
        }
        if is_driver_profiles_failed:
            return mockserver.make_response(json={}, status=500)
        return mockserver.make_response(
            json=DRIVER_PROFILES_RESPONSE, status=200,
        )

    response = await taxi_signalq_drivers.post(
        'driver/v1/signalq-drivers/v1/personal-interface',
        headers=HEADERS,
        json={'period': {'from': period_from, 'to': period_to}},
    )
    assert response.status_code == expected_code, response.text
    if expected_code != 200:
        return
    assert response.json() == expected_response
