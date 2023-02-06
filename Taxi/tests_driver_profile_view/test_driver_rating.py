import pytest

from tests_driver_profile_view import utils as constants

DB = 'db1'
UUID = 'uuid1'
SESSION = 'session1'

HANDLER = 'driver/v1/rating/item'

AUTH_PARAMS = {'db': DB, 'park_id': DB, 'session': SESSION}

HEADERS = {'User-Agent': 'Taximeter 8.80 (562)'}


def check_polling_header(header):
    parts = header.split(', ')
    parts.sort()
    assert parts == [
        'background=1200s',
        'full=600s',
        'idle=1800s',
        'powersaving=1200s',
    ]


@pytest.mark.driver_tags_error(
    handler='/v1/drivers/match/profile',
    error_code=500,
    error_message={'message': 'Server error', 'code': '500'},
)
async def test_tags_v1_drivers_match_profile_500_response(
        taxi_driver_profile_view,
        driver_authorizer,
        fleet_parks,
        driver_protocol,
        driver_ratings,
        load_json,
        taxi_config,
):
    driver_authorizer.set_session(DB, SESSION, UUID)
    response = await taxi_driver_profile_view.get(
        HANDLER, params=AUTH_PARAMS, headers=HEADERS,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    response_json = response.json()
    expected_response = load_json('expected_response_default.json')
    assert expected_response == response_json


@pytest.mark.skip(reason='TAXIBACKEND-42163')
@pytest.mark.driver_tags_error(
    handler='/v1/drivers/match/profile',
    error_code=500,
    error_message={'message': 'Server error', 'code': '500'},
)
async def test_driver_protocol_service_driver_info_500_response(
        taxi_driver_profile_view,
        driver_authorizer,
        fleet_parks,
        driver_protocol,
        driver_ratings,
        load_json,
        taxi_config,
):
    driver_protocol.set_return_error()
    driver_authorizer.set_session(DB, SESSION, UUID)
    response = await taxi_driver_profile_view.get(
        HANDLER, params=AUTH_PARAMS, headers=HEADERS,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    response_json = response.json()
    expected_response = load_json('expected_response_default.json')
    del expected_response['driver_points_settings']
    del expected_response['driver_points']
    del expected_response['rating']
    del expected_response['tariffs']
    assert expected_response == response_json


async def test_driver_ratings_v1_driver_ratings_retrieve_500_response(
        taxi_driver_profile_view,
        driver_authorizer,
        fleet_parks,
        driver_protocol,
        driver_ratings,
        load_json,
        taxi_config,
):
    driver_ratings.set_return_error()
    driver_authorizer.set_session(DB, SESSION, UUID)
    response = await taxi_driver_profile_view.get(
        HANDLER, params=AUTH_PARAMS, headers=HEADERS,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    response_json = response.json()
    expected_response = load_json('expected_response_default.json')
    del expected_response['rating']
    assert expected_response == response_json


async def test_fleet_parks_v1_parks_list_500_response(
        taxi_driver_profile_view,
        driver_authorizer,
        fleet_parks,
        driver_protocol,
        driver_ratings,
        load_json,
        taxi_config,
):
    fleet_parks.set_return_error()
    driver_authorizer.set_session(DB, SESSION, UUID)
    response = await taxi_driver_profile_view.get(
        HANDLER, params=AUTH_PARAMS, headers=HEADERS,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    response_json = response.json()
    expected_response = load_json('expected_response_default.json')
    del expected_response['completion_rate_settings']['city']
    del expected_response['ac_rate_settings']['city']
    del expected_response['l_settings']['city']
    assert expected_response == response_json


@pytest.mark.parametrize(
    'tags_value,expected_grade_for_branding',
    [
        ([], False),
        (['golden_crown'], True),
        (['exclude_golden_crown'], False),
        (['grade_for_branding'], True),
        (['exclude_golden_crown', 'golden_crown'], False),
        (['bla bla bla'], False),
    ],
)
async def test_tags_v1_drivers_match_profile_different_responses(
        taxi_driver_profile_view,
        driver_authorizer,
        fleet_parks,
        driver_protocol,
        driver_tags_mocks,
        driver_ratings,
        load_json,
        tags_value,
        expected_grade_for_branding,
        taxi_config,
):
    driver_tags_mocks.set_tags_info(dbid=DB, uuid=UUID, tags=tags_value)
    driver_authorizer.set_session(DB, SESSION, UUID)
    response = await taxi_driver_profile_view.get(
        HANDLER, params=AUTH_PARAMS, headers=HEADERS,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    response_json = response.json()
    expected_response = load_json('expected_response_default.json')
    expected_response['grade_for_branding'] = expected_grade_for_branding
    assert expected_response == response_json


@pytest.mark.parametrize(
    'parks_value,expected_city',
    [([], None), (constants.DEFAULT_PARKS, 'Дзержинский')],
)
async def test_fleet_parks_v1_parks_list_different_responses(
        taxi_driver_profile_view,
        driver_authorizer,
        fleet_parks,
        driver_protocol,
        driver_ratings,
        load_json,
        parks_value,
        expected_city,
        taxi_config,
):
    fleet_parks.set_parks(parks_value)
    driver_authorizer.set_session(DB, SESSION, UUID)
    response = await taxi_driver_profile_view.get(
        HANDLER, params=AUTH_PARAMS, headers=HEADERS,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    response_json = response.json()
    expected_response = load_json('expected_response_default.json')
    if expected_city:
        expected_response['l_settings']['city'] = expected_city
        expected_response['ac_rate_settings']['city'] = expected_city
        expected_response['completion_rate_settings']['city'] = expected_city
    else:
        del expected_response['completion_rate_settings']['city']
        del expected_response['ac_rate_settings']['city']
        del expected_response['l_settings']['city']
    assert expected_response == response_json


@pytest.mark.parametrize(
    'ratings_value,expected_rating',
    [
        (
            {'rating': '5.0', 'unique_driver_id': 'uuid'},
            {'rating': 5.0, 'displayed_total': 5.0, 'rating_string': '5.0'},
        ),
        (
            {'rating': '4.91', 'unique_driver_id': 'uuid'},
            {'rating': 4.91, 'displayed_total': 4.91, 'rating_string': '4.91'},
        ),
    ],
)
async def test_driver_ratings_v1_driver_ratings_retrieve_different_responses(
        taxi_driver_profile_view,
        driver_authorizer,
        fleet_parks,
        driver_protocol,
        driver_ratings,
        load_json,
        ratings_value,
        expected_rating,
        taxi_config,
):
    driver_ratings.set_ratings(ratings_value)
    driver_authorizer.set_session(DB, SESSION, UUID)
    response = await taxi_driver_profile_view.get(
        HANDLER, params=AUTH_PARAMS, headers=HEADERS,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    response_json = response.json()
    expected_response = load_json('expected_response_default.json')
    expected_response['rating']['driver'].update(**expected_rating)
    assert expected_response == response_json


@pytest.mark.parametrize(
    'tariffs_value', [None, [], constants.DEFAULT_TARIFFS],
)
async def test_driver_protocol_service_driver_info_different_tariffs(
        taxi_driver_profile_view,
        driver_authorizer,
        fleet_parks,
        driver_protocol,
        driver_ratings,
        load_json,
        tariffs_value,
):
    driver_protocol.set_tariffs(tariffs_value)
    driver_authorizer.set_session(DB, SESSION, UUID)
    response = await taxi_driver_profile_view.get(
        HANDLER, params=AUTH_PARAMS, headers=HEADERS,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    response_json = response.json()
    expected_response = load_json('expected_response_default.json')
    if tariffs_value:
        expected_response['tariffs'] = tariffs_value
    else:
        del expected_response['tariffs']
    assert expected_response == response_json


@pytest.mark.parametrize(
    'exam_score', [None, 0.0, 5.0, constants.DEFAULT_EXAM_SCORE],
)
async def test_driver_protocol_service_driver_info_different_exam_score(
        taxi_driver_profile_view,
        driver_authorizer,
        fleet_parks,
        driver_protocol,
        driver_ratings,
        load_json,
        exam_score,
):
    driver_protocol.set_exam_score(exam_score)
    driver_authorizer.set_session(DB, SESSION, UUID)
    response = await taxi_driver_profile_view.get(
        HANDLER, params=AUTH_PARAMS, headers=HEADERS,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    response_json = response.json()
    expected_response = load_json('expected_response_default.json')
    if exam_score:
        expected_response['rating']['driver']['exam_result'] = exam_score
    else:
        expected_response['rating']['driver']['exam_result'] = 0.0
    assert expected_response == response_json


@pytest.mark.skip(reason='TAXIBACKEND-42163')
@pytest.mark.parametrize(
    'karma_points', [None, constants.DEFAULT_KARMA_POINTS],
)
async def test_driver_protocol_service_driver_info_different_karma_points(
        taxi_driver_profile_view,
        driver_authorizer,
        fleet_parks,
        driver_protocol,
        driver_ratings,
        load_json,
        karma_points,
):
    driver_protocol.set_karma_points(karma_points)
    driver_authorizer.set_session(DB, SESSION, UUID)
    response = await taxi_driver_profile_view.get(
        HANDLER, params=AUTH_PARAMS, headers=HEADERS,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    response_json = response.json()
    expected_response = load_json('expected_response_default.json')
    if not karma_points:
        del expected_response['driver_points']
        del expected_response['driver_points_settings']
        del expected_response['rating']
    assert expected_response == response_json
