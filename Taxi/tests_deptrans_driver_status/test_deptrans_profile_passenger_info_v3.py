import pytest

URL = '/internal/v3/profile/passenger-info'

CONFIGS = {
    'DEPTRANS_DRIVER_STATUS_PROFILE_PASSENGER_INFO_SETTINGS': {
        'kis_art_img_tag': 'image_tag_for_kis_art',
        'cache_control_max_age': 3600,
    },
}
EXISTS_RESPONSE = {
    'passenger_info_data': {
        'title': 'Driver has KIS ART',
        'image_tag': 'image_tag_for_kis_art',
    },
}


@pytest.mark.pgsql('deptrans_driver_status', files=['deptrans_profiles.sql'])
@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'taxiontheway.driver_has_kis_art_profile': {
            'en': 'Driver has KIS ART',
        },
    },
)
@pytest.mark.config(**CONFIGS)
@pytest.mark.parametrize(
    ('park_driver_profile_id', 'expected_status', 'expected_body'),
    (
        pytest.param(
            'park2_driver1', 200, EXISTS_RESPONSE, id='Has temp profile',
        ),
        pytest.param(
            'park1_driver1', 200, EXISTS_RESPONSE, id='Has permanent profile',
        ),
        pytest.param('park2_driver2', 200, {}, id='Has not profile row in db'),
        pytest.param(
            'park1_driver2', 200, {}, id='Has profile row with None status',
        ),
        pytest.param(
            'park_wrong_driver_wrong', 404, None, id='No driver in cache',
        ),
    ),
)
async def test_handler(
        taxi_deptrans_driver_status,
        park_driver_profile_id,
        expected_status,
        expected_body,
):
    await taxi_deptrans_driver_status.invalidate_caches()
    response = await taxi_deptrans_driver_status.get(
        URL,
        params={'park_driver_profile_id': park_driver_profile_id},
        headers={'X-Request-Language': 'en'},
    )
    assert response.status == expected_status
    if expected_status == 200:
        assert response.json() == expected_body
        assert response.headers['Cache-Control'] == 'max-age=3600'
