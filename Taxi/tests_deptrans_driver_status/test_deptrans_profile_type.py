import pytest

ENDPOINT = '/driver/v1/deptrans-status/v1/profile/type'


def _get_headers(park_id, driver_id):
    return {
        'Accept-Language': 'ru',
        'X-YaTaxi-Park-Id': park_id,
        'X-YaTaxi-Driver-Profile-Id': driver_id,
        'X-Request-Application-Version': '9.60 (1234)',
    }


def _get_response(show_profile):
    if show_profile:
        return {'screen_type': 'show_profile'}

    return {
        'screen_type': 'choose_type',
        'screen_info': {
            'title': 'title_full_key_localized',
            'items': [
                'item_full_key_1_localized',
                'item_full_key_2_localized',
            ],
        },
    }


@pytest.mark.experiments3(filename='profile_type.json')
@pytest.mark.pgsql('deptrans_driver_status', files=['deptrans_profiles.sql'])
@pytest.mark.parametrize(
    ('park_id', 'driver_id', 'show_profile', 'personal_handler'),
    [
        pytest.param('park2', 'driver2', False, None, id='Without profile'),
        pytest.param(
            'park1', 'driver1', True, 'retrieve', id='Approved profile',
        ),
        pytest.param(
            'park1', 'driver2', True, 'bulk_retrieve', id='Approving profile',
        ),
        pytest.param('park2', 'driver1', True, 'retrieve', id='Temp profile'),
        pytest.param(
            'park3',
            'driver4',
            True,
            'bulk_retrieve',
            id='Temp profile pending permanent',
        ),
    ],
)
async def test_get_deptrans_profile_info(
        taxi_deptrans_driver_status,
        personal,
        park_id,
        driver_id,
        show_profile,
        personal_handler,
):
    response = await taxi_deptrans_driver_status.get(
        ENDPOINT, headers=_get_headers(park_id, driver_id),
    )
    assert response.status_code == 200
    assert response.json() == _get_response(show_profile)
    if personal_handler:
        assert personal[personal_handler].times_called == 1
