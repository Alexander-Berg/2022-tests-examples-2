async def test_fill_with_trash_ok(taxi_driver_profiles, mongodb):

    fill_with_trash_response = await taxi_driver_profiles.put(
        '/internal/v1/driver/fill-with-trash',
        json={'park_id': 'park4', 'driver_profile_id': 'driver4'},
    )

    assert fill_with_trash_response.status_code == 200

    profile = mongodb.dbdrivers.find_one(
        {'park_id': 'park4', 'driver_id': 'driver4'},
    )

    assert profile['is_removed_by_request'] is True
    assert profile['is_all_data_removed'] is True
    assert profile['work_status'] == 'not_working'
    assert 'first_name' not in profile
    assert 'last_name' not in profile
    assert 'middle_name' not in profile
    assert 'license' not in profile
    assert 'license_series' not in profile
    assert 'license_number' not in profile
    assert 'license_normalized' not in profile
    assert 'driver_license_pd_id' not in profile
    assert 'email' not in profile
    assert 'phones' not in profile
    assert 'address' not in profile
    assert 'emergency_person_contacts' not in profile
    assert 'primary_state_registration_number' not in profile
    assert 'bank_accounts' not in profile
    assert 'platform_uid' not in profile
    assert 'phone_pd_ids' not in profile
    assert 'driver_license_pd_id' not in profile
    assert 'email_pd_id' not in profile
    assert 'tax_identification_number_pd_id' not in profile
    assert 'identification_pd_ids' not in profile


async def test_fill_with_trash_not_found(taxi_driver_profiles, mongodb):

    fill_with_trash_response = await taxi_driver_profiles.put(
        '/internal/v1/driver/fill_with_trash',
        params={'park_id': 'no_park', 'driver_profile_id': 'no_driver'},
    )

    assert fill_with_trash_response.status_code == 404
