import pytest

LAUNCH_URL = 'eats/v1/launch/v1/market'

EATS_EATERS_EXPERIMENT_ENABLED_READING = pytest.mark.experiments3(
    name='eats_launch_use_eats_eaters',
    consumers=['eats-launch/use-eats-eaters'],
    default_value={'enabled_reading': True, 'enabled_writing': False},
    is_config=True,
)

EATS_EATERS_EXPERIMENT_DISABLED = pytest.mark.experiments3(
    name='eats_launch_use_eats_eaters',
    consumers=['eats-launch/use-eats-eaters'],
    default_value={'enabled_reading': False, 'enabled_writing': False},
    is_config=True,
)


@EATS_EATERS_EXPERIMENT_ENABLED_READING
async def test_eats_eaters_exp_use_ee(
        taxi_eats_launch,
        common_values,
        mockserver,
        testpoint,
        make_launch_headers,
        make_eater,
        mock_blackbox,
        mock_bb_personal_phone_store,
        mock_bb_personal_email_store,
        mock_ee_find_by_passport_uid,
        mock_core_login,
        mock_ea_login,
):
    # flow FoundByUid_Fullish_NotAuthorized_Login
    mock_blackbox = await mock_blackbox(has_default_phone=True, has_email=True)
    mock_ee_find_passport_eater = await mock_ee_find_by_passport_uid(
        make_eater(
            eater_id=common_values['passport_eater_id'],
            passport_uid=common_values['requested_passport_uid'],
            passport_uid_type=common_values['passport_uid_type_portal'],
        ),
    )

    @testpoint('action_login')
    def action_login(data):
        return data

    response = await taxi_eats_launch.post(
        LAUNCH_URL,
        headers=make_launch_headers(
            session_eater_id=None,
            passport_eater_id=common_values['passport_eater_id'],
        ),
    )
    assert response.status_code == 200

    assert mock_blackbox.times_called == 1
    assert mock_bb_personal_phone_store.times_called == 1
    assert mock_bb_personal_email_store.times_called == 1

    assert mock_ee_find_passport_eater.times_called == 1
    assert mock_ee_find_passport_eater.next_call()['request'].json == {
        'passport_uid': common_values['requested_passport_uid'],
    }

    await action_login.wait_call()

    assert mock_core_login.times_called == 1
    assert mock_core_login.next_call()['request'].json == {
        'eater_id': common_values['passport_eater_id'],
        'inner_token': common_values['inner_token'],
    }

    assert mock_ea_login.times_called == 1
    assert mock_ea_login.next_call()['request'].json == {
        'inner_session_id': common_values['inner_token'],
        'eater_id': common_values['passport_eater_id'],
        'eater_username': common_values['passport_eater_id'],
    }


@EATS_EATERS_EXPERIMENT_DISABLED
async def test_eats_eaters_exp_use_core(
        taxi_eats_launch,
        common_values,
        mockserver,
        testpoint,
        make_launch_headers,
        make_eater,
        mock_blackbox,
        mock_bb_personal_phone_store,
        mock_bb_personal_email_store,
        mock_find_by_passport_uid,
        mock_core_login,
        mock_ea_login,
):
    # flow FoundByUid_Fullish_NotAuthorized_Login
    mock_blackbox = await mock_blackbox(has_default_phone=True, has_email=True)
    mock_find_passport_eater = await mock_find_by_passport_uid(
        make_eater(
            eater_id=common_values['passport_eater_id'],
            passport_uid=common_values['requested_passport_uid'],
            passport_uid_type=common_values['passport_uid_type_portal'],
        ),
    )

    @testpoint('action_login')
    def action_login(data):
        return data

    response = await taxi_eats_launch.post(
        LAUNCH_URL,
        headers=make_launch_headers(
            session_eater_id=None,
            passport_eater_id=common_values['passport_eater_id'],
        ),
    )
    assert response.status_code == 200

    assert mock_blackbox.times_called == 1
    assert mock_bb_personal_phone_store.times_called == 1
    assert mock_bb_personal_email_store.times_called == 1

    assert mock_find_passport_eater.times_called == 1
    assert mock_find_passport_eater.next_call()['request'].json == {
        'passport_uid': common_values['requested_passport_uid'],
    }

    await action_login.wait_call()

    assert mock_core_login.times_called == 1
    assert mock_core_login.next_call()['request'].json == {
        'eater_id': common_values['passport_eater_id'],
        'inner_token': common_values['inner_token'],
    }

    assert mock_ea_login.times_called == 1
    assert mock_ea_login.next_call()['request'].json == {
        'inner_session_id': common_values['inner_token'],
        'eater_id': common_values['passport_eater_id'],
        'eater_username': common_values['passport_eater_id'],
    }
