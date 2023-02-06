import pytest

HANDLER = '/driver/v1/profile-view/v1/rating/details'

HEADERS = {
    'Accept-Language': 'ru',
    'X-YaTaxi-Park-Id': 'park_id',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.60 (1234)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


@pytest.mark.parametrize(
    [
        'set_unique',
        'fail_trackstory',
        'rating_response',
        'expected_code',
        'expected_response',
    ],
    [
        pytest.param(
            True,
            False,
            'rating_details_response1.json',
            200,
            'expected_response1.json',
            id='Happy path',
            marks=pytest.mark.experiments3(
                filename='detailed_rating_additional_info.json',
            ),
        ),
        pytest.param(
            True,
            True,
            'rating_details_response1.json',
            200,
            'expected_response1.json',
            id='Trackstory timeout',
            marks=pytest.mark.experiments3(
                filename='detailed_rating_additional_info.json',
            ),
        ),
        pytest.param(False, False, None, 500, None, id='Without unique'),
        pytest.param(
            True,
            False,
            'rating_details_response2.json',
            200,
            'expected_response2.json',
            id='Empty fallback',
        ),
        pytest.param(
            True,
            False,
            'rating_details_response1.json',
            200,
            'expected_response5.json',
            id='Not enough fallback 25',
            marks=[
                pytest.mark.config(MINIMAL_SCORES_COUNT_FOR_RATING_DETAILS=25),
            ],
        ),
        pytest.param(
            True,
            False,
            'rating_details_response3.json',
            200,
            'expected_response3.json',
            id='Rolling groups',
            marks=[
                pytest.mark.experiments3(
                    filename='detailed_rating_additional_info.json',
                ),
                pytest.mark.now('2021-03-09T18:00:00+0000'),
            ],
        ),
        pytest.param(
            True,
            False,
            'rating_details_response3.json',
            200,
            'expected_response4.json',
            id='Rolling groups with replaced weights',
            marks=[
                pytest.mark.experiments3(
                    filename='detailed_rating_additional_info.json',
                ),
                pytest.mark.config(RATING_DETAILS_USE_ACTUAL_WEIGHTS=False),
                pytest.mark.now('2021-03-10T18:00:00+0000'),
            ],
        ),
        pytest.param(
            True,
            False,
            'rating_details_response4.json',
            200,
            'expected_response6.json',
            id='rating_precision',
            marks=[
                pytest.mark.experiments3(
                    filename='detailed_rating_additional_info.json',
                ),
                pytest.mark.experiments3(
                    filename='driver_rating_precision.json',
                ),
            ],
        ),
    ],
)
async def test_driver_rating_detailed(
        taxi_driver_profile_view,
        unique_drivers_mocks,
        driver_trackstory_mocks,
        fleet_parks,
        mockserver,
        load_json,
        set_unique,
        fail_trackstory,
        rating_response,
        expected_code,
        expected_response,
):
    @mockserver.json_handler('/driver-ratings/v2/driver/rating/with-details')
    def _rating_v2_with_details(request):
        return load_json(rating_response)

    if set_unique:
        unique_drivers_mocks.set_unique_driver_id(
            'park_id', 'driver_id', 'unique_driver_id',
        )
    driver_trackstory_mocks.should_fail = fail_trackstory

    response = await taxi_driver_profile_view.get(
        HANDLER, params={'tz': 'Europe/Moscow'}, headers=HEADERS,
    )

    assert response.status_code == expected_code
    if expected_code == 200:
        assert response.json() == load_json(expected_response)
