from testsuite.utils import ordered_object


ENDPOINT = '/v1/contractor-profiles/retrieve-for-check-duplicates'
PARK_ID = 'park_id_2'
CONTRACTOR_PROFILE_ID = 'driver_1'


async def test_find_by_license(taxi_driver_profiles, load_json):
    license_pd_id = '1234'
    expocted_response = load_json('response_by_license.json')

    response = await taxi_driver_profiles.post(
        ENDPOINT,
        params={
            'park_id': PARK_ID,
            'contractor_profile_id': CONTRACTOR_PROFILE_ID,
        },
        json={'license_pd_id': license_pd_id},
    )

    assert response.status == 200
    ordered_object.assert_eq(
        response.json(), expocted_response, ['contractor_profiles'],
    )


async def test_find_by_password(taxi_driver_profiles, load_json):
    password = 'qwerty'
    expocted_response = load_json('response_by_password.json')

    response = await taxi_driver_profiles.post(
        ENDPOINT,
        params={
            'park_id': PARK_ID,
            'contractor_profile_id': CONTRACTOR_PROFILE_ID,
        },
        json={'payment_service_id': password},
    )

    assert response.status == 200
    ordered_object.assert_eq(
        response.json(), expocted_response, ['contractor_profiles'],
    )


async def test_find_by_phone_pd_id(taxi_driver_profiles, load_json):
    phone_pd_id = 'asdfgh'
    expocted_response = load_json('response_phone_pd_id.json')

    response = await taxi_driver_profiles.post(
        ENDPOINT,
        params={
            'park_id': PARK_ID,
            'contractor_profile_id': CONTRACTOR_PROFILE_ID,
        },
        json={'phone_pd_id': phone_pd_id},
    )

    assert response.status == 200
    ordered_object.assert_eq(
        response.json(), expocted_response, ['contractor_profiles'],
    )


async def test_find_by_all_fields(taxi_driver_profiles, load_json):
    license_pd_id = '1234'
    phone_pd_id = 'asdfgh'
    password = 'qwerty'
    expocted_response = load_json('response_by_all_fields.json')

    response = await taxi_driver_profiles.post(
        ENDPOINT,
        params={
            'park_id': PARK_ID,
            'contractor_profile_id': CONTRACTOR_PROFILE_ID,
        },
        json={
            'license_pd_id': license_pd_id,
            'phone_pd_id': phone_pd_id,
            'payment_service_id': password,
        },
    )

    assert response.status == 200
    ordered_object.assert_eq(
        response.json(), expocted_response, ['contractor_profiles'],
    )


async def test_invalid_request_body(taxi_driver_profiles):
    expocted_response = {'code': '400', 'message': 'empty request'}

    response = await taxi_driver_profiles.post(
        ENDPOINT,
        params={
            'park_id': PARK_ID,
            'contractor_profile_id': CONTRACTOR_PROFILE_ID,
        },
        json={},
    )

    assert response.status == 400
    assert response.json() == expocted_response


async def test_not_found(taxi_driver_profiles):
    license_pd_id = '12345'
    phone_pd_id = 'asdfghtest'
    expocted_response = {'contractor_profiles': []}

    response = await taxi_driver_profiles.post(
        ENDPOINT,
        params={
            'park_id': PARK_ID,
            'contractor_profile_id': CONTRACTOR_PROFILE_ID,
        },
        json={'license_pd_id': license_pd_id, 'phone_pd_id': phone_pd_id},
    )

    assert response.status == 200
    assert response.json() == expocted_response
