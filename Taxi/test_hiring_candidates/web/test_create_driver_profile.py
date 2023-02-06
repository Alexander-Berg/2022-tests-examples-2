import uuid

import pytest

from hiring_candidates.internal import constants

IDEMPOTENCY_KEY = {'X-Idempotency-Token': uuid.uuid4().hex}
PARK_ID = '10502db64af54e58a91cc26198417f74'
DRIVER_PROFILE_ID = 'b933d336672c443c9f5866c034691bcb'


@pytest.mark.usefixtures('personal')
@pytest.mark.parametrize('status', ['400', '401', '403', '500'])
async def test_match_with_parks_bad_response(
        mock_parks_driver_profile_post,
        mock_driver_profiles_update,
        taxi_hiring_candidates_web,
        get_all_driver_profiles,
        load_json,
        status,
):
    # arrange
    driver_profiles_response = 204
    request_data = load_json('request.json')
    parks_response = load_json('parks_response.json')[status]
    event_fields = load_json('event_fields.json')
    excluded_fields_from_parks = event_fields['excluded']
    expected_response = load_json('expected_response.json')[status]
    parks_request = mock_parks_driver_profile_post(parks_response, status)
    mock_driver_profiles_update(driver_profiles_response)

    # act
    response = await taxi_hiring_candidates_web.post(
        '/v1/driver-profile/create',
        headers=IDEMPOTENCY_KEY,
        params={'park_id': PARK_ID},
        json=request_data,
    )

    # assert
    assert parks_request.has_calls
    parks_request_body = parks_request.next_call()['request']
    assert not any(
        key in excluded_fields_from_parks
        for key in parks_request_body.json[constants.DRIVER_PROFILE]
    )

    body = await response.json()
    assert response.status == int(status)
    assert body == expected_response


@pytest.mark.usefixtures('personal')
@pytest.mark.parametrize(
    'request_type',
    [
        'normal_license',
        'non_alphanum_symbols_license',
        'white_space_license',
        'underscore_license',
        'cyrillic_letters_license',
        'courier_fake_key_license',
    ],
)
async def test_driver_license_normalization(
        taxi_hiring_candidates_web,
        mock_parks_driver_profile_post,
        mock_driver_profiles_update,
        get_all_driver_profiles,
        load_json,
        request_type,
):
    # arrange
    status = '200'
    driver_profiles_response = 204
    request_body = load_json('requests.json')[request_type]
    parks_response = load_json('parks_responses.json')[request_type]
    event_fields = load_json('event_fields.json')
    excluded_fields_from_parks = event_fields['excluded']
    expected_data = load_json('expected_data.json')[request_type]
    parks_request = mock_parks_driver_profile_post(parks_response, status)
    mock_driver_profiles_update(driver_profiles_response)

    # act
    response = await taxi_hiring_candidates_web.post(
        '/v1/driver-profile/create',
        headers=IDEMPOTENCY_KEY,
        params={'park_id': PARK_ID},
        json=request_body,
    )

    # assert
    assert parks_request.has_calls
    parks_request_body = parks_request.next_call()['request']
    assert not any(
        key in excluded_fields_from_parks
        for key in parks_request_body.json[constants.DRIVER_PROFILE]
    )

    body = await response.json()
    driver_profile = get_all_driver_profiles()[0]
    assert response.status == int(status)
    assert body == parks_response
    assert driver_profile['driver_license_pd_id'] == expected_data['pd_id']
    assert (
        driver_profile['normalized_driver_license_pd_id']
        == expected_data['normalized_driver_license_pd_id']
    )


@pytest.mark.usefixtures('personal')
@pytest.mark.parametrize(
    'driver_profiles_response', ['204', '400', '404', '500'],
)
async def test_hiring_details_failing_cases(
        mock_driver_profiles_update,
        mock_parks_driver_profile_post,
        taxi_hiring_candidates_web,
        get_all_driver_profiles,
        load_json,
        driver_profiles_response,
):
    """
    The single purpose of this test is to make sure
    that failing request to driver_profiles to update
    hiring_details does not break the main request flow
    """

    # arrange
    parks_status = 200
    driver_profiles_response = 204
    request_data = load_json('request.json')
    parks_response = load_json('parks_response.json')
    event_fields = load_json('event_fields.json')
    excluded_fields_from_parks = event_fields['excluded']
    expected_data = load_json('expected_data.json')
    parks_request = mock_parks_driver_profile_post(
        parks_response, parks_status,
    )
    mock_driver_profiles_update(driver_profiles_response)

    # act
    response = await taxi_hiring_candidates_web.post(
        '/v1/driver-profile/create',
        headers=IDEMPOTENCY_KEY,
        params={'park_id': PARK_ID},
        json=request_data,
    )

    # assert
    assert parks_request.has_calls
    parks_request_body = parks_request.next_call()['request']
    assert not any(
        key in excluded_fields_from_parks
        for key in parks_request_body.json[constants.DRIVER_PROFILE]
    )

    body = await response.json()
    driver_profiles = get_all_driver_profiles()
    assert response.status == int(parks_status)
    assert body == parks_response
    assert driver_profiles[0] == expected_data


@pytest.mark.usefixtures('personal')
async def test_create_multiple_profiles(
        mock_parks_driver_profile_post,
        mock_driver_profiles_update,
        taxi_hiring_candidates_web,
        get_all_driver_profiles,
        load_json,
):
    """
    Test checks non required param driver_profile_id
    It should set id as driver_profile_id
    """

    # arrange
    driver_profiles_response = 204
    status = 200
    requests_data = load_json('requests.json')
    parks_responses = load_json('parks_responses.json')
    expected_data = load_json('expected_data.json')
    mock_driver_profiles_update(driver_profiles_response)

    mock_parks_driver_profile_post(parks_responses['profile_2'], status)
    response_profile_1 = await taxi_hiring_candidates_web.post(
        '/v1/driver-profile/create',
        headers=IDEMPOTENCY_KEY,
        params={'park_id': PARK_ID},
        json=requests_data['profile_1'],
    )
    mock_parks_driver_profile_post(parks_responses['profile_1'], status)

    # act
    response_profile_2 = await taxi_hiring_candidates_web.post(
        '/v1/driver-profile/create',
        headers=IDEMPOTENCY_KEY,
        params={'park_id': PARK_ID, 'driver_profile_id': DRIVER_PROFILE_ID},
        json=requests_data['profile_2'],
    )

    # assert
    driver_profiles = get_all_driver_profiles()
    assert response_profile_1.status == int(status)
    assert response_profile_2.status == int(status)
    assert driver_profiles[0]['executor_profile_id'] == DRIVER_PROFILE_ID
    assert driver_profiles[0] == expected_data['profile_2']
    assert driver_profiles[1] == expected_data['profile_1']
