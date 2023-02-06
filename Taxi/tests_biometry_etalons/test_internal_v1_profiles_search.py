import copy

import pytest


PARK_FILTERED_REQUEST = {
    'filter': {'providers': ['signalq'], 'meta': {'park_id': '123'}},
    'limit': 1,
    'urls': {'ttl': 15},
}


PARK_FILTERED_RESPONSES = [
    {
        'profiles': [
            {
                'profile': {'id': 'xxx_yyy', 'type': 'park_driver_profile_id'},
                'provider': 'signalq',
                'profile_meta': {
                    'park_id': '123',
                    'device_serial': 'd1',
                    'park_id_car_id': '123_c1',
                },
                'profile_media': {
                    'photo': [
                        {
                            'media_id': '1',
                            'storage_bucket': 'yyy',
                            'storage_id': 'xxx',
                            'storage_type': 'signalq-s3',
                        },
                    ],
                },
            },
        ],
        'cursor': '2019-04-10T07:00:00+0000|xxx_yyy',
    },
    {
        'profiles': [
            {
                'profile': {'id': 'yyy_yyy', 'type': 'park_driver_profile_id'},
                'provider': 'signalq',
                'profile_meta': {
                    'park_id': '123',
                    'device_serial': 'd2',
                    'park_id_car_id': '123_c2',
                },
                'profile_media': {
                    'photo': [
                        {
                            'media_id': '2',
                            'storage_bucket': 'driver_photo',
                            'storage_id': 'ms0000000000000000000001',
                            'storage_type': 'media-storage',
                        },
                    ],
                },
            },
        ],
        'cursor': '2019-04-10T07:00:00+0000|yyy_yyy',
    },
    {'profiles': []},
]


NO_PARK_FILTERED_REQUEST = {'filter': {'providers': ['signalq']}, 'limit': 1}


NO_PARK_FILTERED_RESPONSES = copy.deepcopy(PARK_FILTERED_RESPONSES)
NO_PARK_FILTERED_RESPONSES[-1] = {
    'profiles': [
        {
            'profile': {'id': 'zzz_yyy', 'type': 'park_driver_profile_id'},
            'provider': 'signalq',
            'profile_meta': {
                'park_id': '789',
                'device_serial': 'd3',
                'park_id_car_id': '789_c3',
            },
            'profile_media': {
                'photo': [
                    {
                        'media_id': '2',
                        'storage_bucket': 'driver_photo',
                        'storage_id': 'ms0000000000000000000001',
                        'storage_type': 'media-storage',
                    },
                ],
            },
        },
    ],
    'cursor': '2019-04-10T07:00:00+0000|zzz_yyy',
}
NO_PARK_FILTERED_RESPONSES.append({'profiles': []})

DEVICE_FILTERED_REQUEST = {
    'filter': {
        'providers': ['signalq'],
        'meta': {'device_serial_numbers': ['d1', 'd3']},
    },
    'limit': 1,
    'urls': {'ttl': 15},
}

DEVICE_FILTERED_RESPONSES = copy.deepcopy(NO_PARK_FILTERED_RESPONSES)
del DEVICE_FILTERED_RESPONSES[1]

CAR_FILTERED_REQUEST = {
    'filter': {
        'providers': ['signalq'],
        'meta': {'park_id_car_ids': ['123_c2']},
    },
    'limit': 1,
    'urls': {'ttl': 15},
}

CAR_FILTERED_RESPONSES = [NO_PARK_FILTERED_RESPONSES[1], {'profiles': []}]

CREATED_AT_FILTERED_REQUEST = {
    'filter': {
        'providers': ['signalq'],
        'created_at': {
            'from': '2019-03-10T10:00:00+03:00',
            'to': '2019-05-12T10:00:00+03:00',
        },
    },
    'limit': 1,
    'urls': {'ttl': 15},
}

CREATED_AT_FILTERED_RESPONSES = [
    NO_PARK_FILTERED_RESPONSES[1],
    NO_PARK_FILTERED_RESPONSES[2],
    {'profiles': []},
]


@pytest.mark.parametrize(
    'request_base, responses',
    [
        (PARK_FILTERED_REQUEST, PARK_FILTERED_RESPONSES),
        (NO_PARK_FILTERED_REQUEST, NO_PARK_FILTERED_RESPONSES),
        (DEVICE_FILTERED_REQUEST, DEVICE_FILTERED_RESPONSES),
        (CAR_FILTERED_REQUEST, CAR_FILTERED_RESPONSES),
        (CREATED_AT_FILTERED_REQUEST, CREATED_AT_FILTERED_RESPONSES),
    ],
)
@pytest.mark.pgsql('biometry_etalons', files=['profiles.sql'])
async def test_internal_v1_profiles_search(
        taxi_biometry_etalons,
        pgsql,
        mockserver,
        media_storage,
        load_json,
        request_base,
        responses,
):
    media_storage.set_url('ms0000000000000000000001', 'http://selfie/001')

    cursor = None

    for expected_response in responses:
        if cursor:
            request_base['cursor'] = cursor

        response = await taxi_biometry_etalons.post(
            '/internal/biometry-etalons/v1/profiles/search', json=request_base,
        )

        assert response.status_code == 200

        response = response.json()

        for profile in response['profiles']:
            photos = profile.get('profile_media', {}).get('photo', [])
            for photo in photos:
                if 'urls' in request_base:
                    assert 'temporary_url' in photo
                    photo.pop('temporary_url')
                else:
                    assert 'temporary_url' not in photo

        assert response == expected_response

        cursor = response.get('cursor')
