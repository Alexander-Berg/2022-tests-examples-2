import pytest


@pytest.mark.parametrize(
    [
        'park_id',
        'driver_profile_id',
        'unique_driver_id',
        'return_code',
        'response_json',
    ],
    (
        pytest.param(
            '7f704bb2221b4922bbd627391078e542',
            'ba5aa2932db04dc4a60fc30102fed047',
            '34256bf766d749fb905ff4d9',
            200,
            {
                'status': 'approved_high_class',
                'description_key': (
                    'diagnostic_driverphoto_approved_high_class_description'
                ),
                'text_key': 'diagnostic_driverphoto_approved_high_class_text',
                'title_key': 'diagnostic_driverphoto_title',
                'action_key': 'diagnostic_driverphoto_action',
            },
            id='Admin photo exists, approved for regular and high classes',
        ),
        pytest.param(
            '7f704bb2221b4922bbd627391078e542',
            'ba5aa2932db04dc4a60fc30102fed047',
            '34256bf766d749fb905ff4d1',
            200,
            {
                'status': 'approved',
                'description_key': (
                    'diagnostic_driverphoto_approved_description'
                ),
                'text_key': 'diagnostic_driverphoto_approved_text',
                'title_key': 'diagnostic_driverphoto_title',
                'action_key': 'diagnostic_driverphoto_action',
            },
            id='Regular photo exists, approved for regular classes',
        ),
        pytest.param(
            '7f704bb2221b4922bbd627391078e542',
            'ba5aa2932db04dc4a60fc30102fed047',
            '64256bf766d749fb905ff4d9',
            200,
            {
                'status': 'on_moderation',
                'description_key': (
                    'diagnostic_driverphoto_on_moderation_description'
                ),
                'text_key': 'diagnostic_driverphoto_on_moderation_text',
                'title_key': 'diagnostic_driverphoto_title',
                'action_key': 'diagnostic_driverphoto_action',
            },
            id='Existing photo on moderation',
        ),
        pytest.param(
            '7f704bb2221b4922bbd627391078e542',
            'ba5aa2932db04dc4a60fc30102fed047',
            '34256bf766d749fb905ff4d8',
            200,
            {
                'status': 'rejected',
                'description_key': (
                    'diagnostic_driverphoto_no_person_description'
                ),
                'text_key': 'diagnostic_driverphoto_rejected_text',
                'title_key': 'diagnostic_driverphoto_title',
                'action_key': 'diagnostic_driverphoto_action',
            },
            id='Existing photo rejected',
        ),
        pytest.param(
            '7f704bb2221b4922bbd627391078e542',
            'ba5aa2932db04dc4a60fc30102fed047',
            '34256bf766d749fb905ff4d0',
            200,
            {
                'status': 'on_moderation',
                'description_key': (
                    'diagnostic_driverphoto_on_moderation_description'
                ),
                'text_key': 'diagnostic_driverphoto_on_moderation_text',
                'title_key': 'diagnostic_driverphoto_title',
                'action_key': 'diagnostic_driverphoto_action',
            },
            id='Existing photo rejected (need_biometry)',
        ),
        pytest.param(
            '7f704bb2221b4922bbd627391078e542',
            'ba5aa2932db04dc4a60fc30102fed047',
            '34256bf766d749fb905ff4d2',
            200,
            {
                'status': 'rejected',
                'description_key': (
                    'diagnostic_driverphoto_too_small_description'
                ),
                'text_key': 'diagnostic_driverphoto_rejected_text',
                'title_key': 'diagnostic_driverphoto_title',
                'action_key': 'diagnostic_driverphoto_action',
            },
            id='Photo was too small',
        ),
        pytest.param(
            '7f704bb2221b4922bbd627391078e542',
            'ba5aa2932db04dc4a60fc30102fed047',
            '000000f766d93ee2c9000000',  # not set in pg_driver_photos.sql
            200,
            {
                'status': 'no_photo',
                'description_key': (
                    'diagnostic_driverphoto_no_photo_description'
                ),
                'text_key': 'diagnostic_driverphoto_no_photo_text',
                'title_key': 'diagnostic_driverphoto_title',
                'action_key': 'diagnostic_driverphoto_action',
            },
            id='No photos for unique driver id',
        ),
        pytest.param(
            '7f704bb2221b4922bbd627391078e542',
            'ba5aa2932db04dc4a60fc30102fed047',
            '34256bf766d749fb905ff4d3',
            200,
            {
                'status': 'rejected',
                'description_key': (
                    'diagnostic_driverphoto_wrong_photo_format_description'
                ),
                'text_key': 'diagnostic_driverphoto_rejected_text',
                'title_key': 'diagnostic_driverphoto_title',
                'action_key': 'diagnostic_driverphoto_action',
            },
            id='Wrong photo format',
        ),
        pytest.param(
            '7f704bb2221b4922bbd627391078e542',
            'ba5aa2932db04dc4a60fc30102fed047',
            '34256bf766d749fb905ff4d4',
            200,
            {
                'status': 'rejected',
                'description_key': (
                    'diagnostic_driverphoto_studio_dark_description'
                ),
                'text_key': 'diagnostic_driverphoto_rejected_text',
                'title_key': 'diagnostic_driverphoto_title',
                'action_key': 'diagnostic_driverphoto_action',
            },
            id='Studio photo too dark',
        ),
        pytest.param(
            '3456',
            '4567',
            'rejected_no_reason_driver_id',
            200,
            {
                'status': 'rejected',
                'description_key': (
                    'diagnostic_driverphoto_unknown_reason_description'
                ),
                'text_key': 'diagnostic_driverphoto_rejected_text',
                'title_key': 'diagnostic_driverphoto_title',
                'action_key': 'diagnostic_driverphoto_action',
            },
            id='Rejected for no reason',
        ),
        pytest.param(
            '7f704bb2221b4922bbd627391078e542',
            'ba5aa2932db04dc4a60fc30102fed047',
            None,
            404,
            {},
            id='No matching unique driver id',
        ),
        pytest.param(
            None,
            'ba5aa2932db04dc4a60fc30102fed047',
            None,
            400,
            {},
            id='Missing park id',
        ),
        pytest.param(
            '7f704bb2221b4922bbd627391078e542',
            None,
            None,
            400,
            {},
            id='Missing driver profile id',
        ),
    ),
)
async def test_get_photo_status(
        taxi_udriver_photos,
        mock_unique_drivers,
        park_id,
        driver_profile_id,
        unique_driver_id,
        return_code,
        response_json,
):
    mock_unique_drivers(unique_driver_id)

    params = {}
    if park_id is not None:
        params['park_id'] = park_id
    if driver_profile_id is not None:
        params['driver_profile_id'] = driver_profile_id
    target_url = '/driver-photos/v1/photos/status'
    response = await taxi_udriver_photos.get(target_url, params=params)
    assert response.status == return_code
    if response.status == 200:
        content = response.json()
        assert content == response_json


@pytest.mark.parametrize(['ud_error_code'], ((300,), (400,), (500,)))
async def test_unique_drivers_service_fail_propagates(
        taxi_udriver_photos, mock_unique_drivers, ud_error_code,
):
    mock_unique_drivers('unused', return_code=ud_error_code)

    params = {'park_id': 'park_5', 'driver_profile_id': 'driver_profile_5'}
    target_url = '/driver-photos/v1/photos/status'
    response = await taxi_udriver_photos.get(target_url, params=params)
    assert response.status == 500
