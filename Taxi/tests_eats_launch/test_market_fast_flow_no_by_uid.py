import pytest

LAUNCH_URL = 'eats/v1/launch/v1/market'

EAP_INFO_EXPERIMENT_ENABLED = pytest.mark.experiments3(
    name='eats_launch_use_eap_personal_info',
    consumers=['eats-launch/use-eap-personal-info'],
    default_value={'enabled': True},
    is_config=True,
)

EAP_INFO_EXPERIMENT_DISABLED = pytest.mark.experiments3(
    name='eats_launch_use_eap_personal_info',
    consumers=['eats-launch/use-eap-personal-info'],
    default_value={'enabled': False},
    is_config=True,
)


@pytest.mark.parametrize(
    (),
    [
        pytest.param(marks=EAP_INFO_EXPERIMENT_ENABLED),
        pytest.param(marks=EAP_INFO_EXPERIMENT_DISABLED),
    ],
)
@pytest.mark.parametrize('has_phone', [True, False])
async def test__no_by_uid__authorized__logout_register(
        taxi_eats_launch,
        common_values,
        mockserver,
        make_launch_headers,
        mock_blackbox,
        mock_bb_personal_phone_store,
        mock_bb_personal_email_store,
        mock_find_by_passport_uid_not_found,
        mock_ea_logout,
        mock_register,
        make_register_request,
        mock_ea_login,
        has_phone,
):
    # flow NoByUid_Authorized_LogoutRegister
    mock_blackbox = await mock_blackbox(
        has_default_phone=has_phone, has_email=True,
    )

    response = await taxi_eats_launch.post(
        LAUNCH_URL,
        headers=make_launch_headers(
            session_eater_id=common_values['session_eater_id'],
            passport_eater_id=None,
        ),
    )
    assert response.status_code == 200

    assert mock_blackbox.times_called == 1
    assert mock_bb_personal_phone_store.times_called == has_phone
    assert mock_bb_personal_email_store.times_called == 1

    assert mock_find_by_passport_uid_not_found.times_called == 1
    assert mock_find_by_passport_uid_not_found.next_call()['request'].json == {
        'passport_uid': common_values['requested_passport_uid'],
    }

    assert mock_ea_logout.times_called == 1
    assert mock_ea_logout.next_call()['request'].json == {
        'inner_session_id': common_values['inner_token'],
    }

    assert mock_register.times_called == 1
    assert mock_register.next_call()['request'].json == make_register_request(
        has_phone=has_phone, has_email=True,
    )

    assert mock_ea_login.times_called == 1
    assert mock_ea_login.next_call()['request'].json == {
        'inner_session_id': common_values['inner_token'],
        'eater_id': 'registered_eater_id',
        'eater_username': 'registered_eater_id',
    }


@pytest.mark.parametrize(
    (),
    [
        pytest.param(marks=EAP_INFO_EXPERIMENT_ENABLED),
        pytest.param(marks=EAP_INFO_EXPERIMENT_DISABLED),
    ],
)
@pytest.mark.parametrize('has_default_phone', [True, False])
@pytest.mark.parametrize('has_secured_phone', [True, False])
async def test__no_by_uid__not_authorized__register(
        taxi_eats_launch,
        common_values,
        mockserver,
        make_launch_headers,
        mock_blackbox,
        mock_bb_personal_phone_store,
        mock_bb_personal_email_store,
        mock_find_by_passport_uid_not_found,
        mock_register,
        make_register_request,
        mock_ea_login,
        has_default_phone,
        has_secured_phone,
):
    # flow NoByUid_NotAuthorized_Register
    mock_blackbox = await mock_blackbox(
        has_default_phone=has_default_phone,
        has_secured_phone=has_secured_phone,
        has_email=True,
    )

    response = await taxi_eats_launch.post(
        LAUNCH_URL,
        headers=make_launch_headers(
            session_eater_id=None, passport_eater_id=None,
        ),
    )
    assert response.status_code == 200

    assert mock_blackbox.times_called == 1
    assert mock_bb_personal_phone_store.times_called == (
        has_default_phone or has_secured_phone
    )
    assert mock_bb_personal_email_store.times_called == 1

    assert mock_find_by_passport_uid_not_found.times_called == 1
    assert mock_find_by_passport_uid_not_found.next_call()['request'].json == {
        'passport_uid': common_values['requested_passport_uid'],
    }

    assert mock_register.times_called == 1
    assert mock_register.next_call()['request'].json == make_register_request(
        has_phone=(has_default_phone or has_secured_phone),
        has_email=True,
        is_secured_phone=has_secured_phone,
    )

    assert mock_ea_login.times_called == 1
    assert mock_ea_login.next_call()['request'].json == {
        'inner_session_id': common_values['inner_token'],
        'eater_id': common_values['registered_eater_id'],
        'eater_username': common_values['registered_eater_id'],
    }
