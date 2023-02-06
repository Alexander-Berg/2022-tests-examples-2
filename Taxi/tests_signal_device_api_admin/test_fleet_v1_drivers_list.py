import pytest

from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/drivers/list'

DRIVER_PROFILE_1 = {
    'car': {'id': 'car1', 'normalized_number': 'О122КХ777'},
    'driver_profile': {
        'first_name': 'Petr',
        'middle_name': 'D`',
        'last_name': 'Ivanov',
        'driver_license': {
            'expiration_date': '2025-08-07T00:00:00+0000',
            'issue_date': '2015-08-07T00:00:00+0000',
            'normalized_number': '7723306794',
            'number': '7723306794',
        },
        'id': 'd1',
        'phones': ['+79265975310'],
    },
}

DRIVER_PROFILE_2 = {
    'car': {'id': 'car1', 'normalized_number': 'О122КХ777'},
    'driver_profile': {
        'first_name': 'Vtoroi',
        'last_name': 'Voditel',
        'driver_license': {
            'expiration_date': '2025-08-07T00:00:00+0000',
            'issue_date': '2015-08-07T00:00:00+0000',
            'normalized_number': '7723306794',
            'number': '7723306794',
        },
        'id': 'd100500',
        'phones': ['+79265975310'],
    },
}

DRIVER_PROFILES_LIST_SINGLE_RESPONSE = {
    'driver_profiles': [DRIVER_PROFILE_1],
    'offset': 0,
    'parks': [{'id': 'p1'}],
    'total': 1,
    'limit': 300,
}

DRIVER_PROFILES_LIST_BOTH_RESPONSE = {
    'driver_profiles': [DRIVER_PROFILE_1, DRIVER_PROFILE_2],
    'offset': 0,
    'parks': [{'id': 'p1'}],
    'total': 2,
    'limit': 300,
}

DRIVER_PROFILES_LIST_EMPTY_RESPONSE = {
    'driver_profiles': [],
    'offset': 0,
    'parks': [],
    'total': 0,
    'limit': 300,
}

BIOMETY_PROFILE_1 = {
    'provider': 'signalq',
    'profile': {'id': 'p1_d1', 'type': 'park_driver_profile_id'},
    'profile_media': {
        'photo': [
            {
                'media_id': '1',
                'storage_bucket': 'storage_bucket_etalon',
                'storage_id': 'storage_id_etalon',
                'temporary_url': 'url_1',
            },
        ],
    },
}

BIOMETY_PROFILE_2 = {
    'provider': 'signalq',
    'profile': {'id': 'p1_d100500', 'type': 'park_driver_profile_id'},
    'profile_media': {
        'photo': [
            {
                'media_id': '2',
                'storage_bucket': 'storage_bucket_etalon',
                'storage_id': 'storage_id_etalon',
                'temporary_url': 'url_2',
            },
        ],
    },
}

DRIVER1 = {
    'first_name': 'Petr',
    'id': 'd1',
    'middle_name': 'D`',
    'last_name': 'Ivanov',
    'license_number': '7723306794',
    'phones': ['+79265975310'],
    'avatar_url': 'url_1',
}

DRIVER2 = {
    'first_name': 'Vtoroi',
    'id': 'd100500',
    'last_name': 'Voditel',
    'license_number': '7723306794',
    'phones': ['+79265975310'],
    'avatar_url': 'url_2',
}

DRIVER2_NO_URL = {
    'first_name': 'Vtoroi',
    'id': 'd100500',
    'last_name': 'Voditel',
    'license_number': '7723306794',
    'phones': ['+79265975310'],
}


@pytest.mark.parametrize(
    'text_filter, page, limit, drivers_list, biometry_list, expected_response',
    [
        pytest.param(
            ' abCD ',
            1,
            2,
            [DRIVER_PROFILES_LIST_SINGLE_RESPONSE],
            [BIOMETY_PROFILE_1, BIOMETY_PROFILE_2],
            {'drivers': [DRIVER1], 'total': 1},
            id='test_one',
        ),
        pytest.param(
            ' abCD ',
            1,
            2,
            [DRIVER_PROFILES_LIST_BOTH_RESPONSE],
            [BIOMETY_PROFILE_1, BIOMETY_PROFILE_2],
            {'drivers': [DRIVER1, DRIVER2], 'total': 2},
            id='test_all',
        ),
        pytest.param(
            '',
            1,
            2,
            [DRIVER_PROFILES_LIST_BOTH_RESPONSE],
            [BIOMETY_PROFILE_1],
            {'drivers': [DRIVER1, DRIVER2_NO_URL], 'total': 2},
            id='test_no_url',
        ),
        pytest.param(
            ' abCD ',
            1,
            2,
            [DRIVER_PROFILES_LIST_EMPTY_RESPONSE],
            [],
            {'drivers': [], 'total': 0},
            id='test_empty',
        ),
    ],
)
async def test_general(
        taxi_signal_device_api_admin,
        parks,
        text_filter,
        page,
        limit,
        drivers_list,
        biometry_list,
        expected_response,
        mockserver,
):
    @mockserver.json_handler(
        '/biometry-etalons/internal/biometry-etalons/v1/profiles/retrieve',
    )
    def _retrieve(request):
        return {'profiles': biometry_list}

    parks.set_driver_profiles_response(drivers_list)
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={'text': text_filter, 'page': page, 'limit': limit},
        headers={
            **web_common.PARTNER_HEADERS_1,
            'X-Park-Id': 'p1',
            'X-YaTaxi-Fleet-Permissions': 'signalq_driver_card_biometry_view',
        },
    )
    assert response.status_code == 200, response.text
    assert response.json() == expected_response
    assert parks.driver_profiles_list.times_called == len(drivers_list)
