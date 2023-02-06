import pytest

LAUNCH_URL = 'eats/v1/launch/v1/native'

EXPECTED_POST_RESPONSE_200 = {
    'profile': {
        'eater_uuid': 'a5f3aa68-53b7-4c98-a52a-d1551b8b3f7d',
        'passport_uid': '123',
        'personal_phone_id': 'blackbox_default_phone_id',
    },
}

EXPECTED_POST_RESPONSE_200_EAP = {
    'profile': {
        'eater_uuid': 'a5f3aa68-53b7-4c98-a52a-d1551b8b3f7d',
        'passport_uid': '123',
        'personal_phone_id': 'eap_phone_id',
    },
}

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


async def call_native(taxi_eats_launch, method, headers_values):
    if method == 'get':
        response = await taxi_eats_launch.get(
            LAUNCH_URL, headers=headers_values,
        )
        return response

    if method == 'post':
        response = await taxi_eats_launch.post(
            LAUNCH_URL, headers=headers_values,
        )
        return response

    # Unexpected method is specified.
    assert False


def make_resp_core_login(common_values, eater_id_name):
    return {
        'eater_id': common_values[eater_id_name],
        'inner_token': common_values['inner_token'],
    }


def make_req_ea_login(common_values, eater_id_name):
    return {
        'inner_session_id': common_values['inner_token'],
        'eater_id': common_values[eater_id_name],
        'eater_username': common_values[eater_id_name],
    }


def check_req_find_passport(mock_find_passport_eater, common_values):
    assert mock_find_passport_eater.times_called == 1
    assert mock_find_passport_eater.next_call()['request'].json == {
        'passport_uid': common_values['requested_passport_uid'],
    }


def check_req_core_login(mock_core_login, common_values, eater_id_name):
    assert mock_core_login.times_called == 1
    assert mock_core_login.next_call()['request'].json == make_resp_core_login(
        common_values, eater_id_name,
    )


@pytest.mark.parametrize(
    (),
    [
        pytest.param(marks=EAP_INFO_EXPERIMENT_ENABLED),
        pytest.param(marks=EAP_INFO_EXPERIMENT_DISABLED),
    ],
)
@pytest.mark.parametrize(
    'method,expected_response',
    [('get', {}), ('post', EXPECTED_POST_RESPONSE_200)],
)
async def test__found_by_uid__fullish__not_authorized__login(
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
        method,
        expected_response,
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

    response = await call_native(
        taxi_eats_launch,
        method,
        make_launch_headers(
            session_eater_id=None,
            passport_eater_id=common_values['passport_eater_id'],
        ),
    )
    assert response.status_code == 200
    assert response.json() == expected_response

    assert mock_blackbox.times_called == 1
    assert mock_bb_personal_phone_store.times_called == 1
    assert mock_bb_personal_email_store.times_called == 1

    check_req_find_passport(mock_find_passport_eater, common_values)

    await action_login.wait_call()

    check_req_core_login(mock_core_login, common_values, 'passport_eater_id')

    assert mock_ea_login.times_called == 1
    assert mock_ea_login.next_call()['request'].json == make_req_ea_login(
        common_values, 'passport_eater_id',
    )


@pytest.mark.parametrize(
    'method,eap_phone_id,eap_email_id,expected_bb_calls,expected_response',
    [
        pytest.param(
            'get', None, None, 1, {}, marks=EAP_INFO_EXPERIMENT_DISABLED,
        ),
        pytest.param(
            'get',
            'eap_phone_id',
            'eap_email_id',
            0,
            {},
            marks=EAP_INFO_EXPERIMENT_ENABLED,
        ),
        pytest.param(
            'post',
            None,
            None,
            1,
            EXPECTED_POST_RESPONSE_200,
            marks=EAP_INFO_EXPERIMENT_DISABLED,
        ),
        pytest.param(
            'post',
            'eap_phone_id',
            'eap_email_id',
            0,
            EXPECTED_POST_RESPONSE_200_EAP,
            marks=EAP_INFO_EXPERIMENT_ENABLED,
        ),
    ],
)
async def test__found_by_uid__fullish__authorized__login(
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
        eap_phone_id,
        eap_email_id,
        expected_bb_calls,
        method,
        expected_response,
):
    # flow FoundByUid_Fullish_Authorized_Login
    mock_blackbox = await mock_blackbox(has_default_phone=True, has_email=True)
    mock_find_passport_eater = await mock_find_by_passport_uid(
        make_eater(
            eater_id=common_values['passport_and_session_eater_id'],
            passport_uid=common_values['requested_passport_uid'],
            passport_uid_type=common_values['passport_uid_type_portal'],
        ),
    )

    @testpoint('action_login')
    def action_login(data):
        return data

    response = await call_native(
        taxi_eats_launch,
        method,
        make_launch_headers(
            session_eater_id=common_values['passport_and_session_eater_id'],
            passport_eater_id=common_values['passport_and_session_eater_id'],
            eap_phone_id=eap_phone_id,
            eap_email_id=eap_email_id,
        ),
    )
    assert response.status_code == 200
    assert response.json() == expected_response

    assert mock_blackbox.times_called == expected_bb_calls
    assert mock_bb_personal_phone_store.times_called == expected_bb_calls
    assert mock_bb_personal_email_store.times_called == expected_bb_calls

    check_req_find_passport(mock_find_passport_eater, common_values)

    await action_login.wait_call()

    check_req_core_login(
        mock_core_login, common_values, 'passport_and_session_eater_id',
    )

    assert mock_ea_login.times_called == 1
    assert mock_ea_login.next_call()['request'].json == make_req_ea_login(
        common_values, 'passport_and_session_eater_id',
    )


@pytest.mark.parametrize(
    (),
    [
        pytest.param(marks=EAP_INFO_EXPERIMENT_ENABLED),
        pytest.param(marks=EAP_INFO_EXPERIMENT_DISABLED),
    ],
)
@pytest.mark.parametrize(
    'method,expected_response',
    [('get', {}), ('post', EXPECTED_POST_RESPONSE_200)],
)
async def test__found_by_uid__fullish__conflicted_auth__login(
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
        mock_ea_logout,
        mock_core_login,
        mock_ea_login,
        method,
        expected_response,
):
    # flow FoundByUid_Fullish_ConflictAuth_Login
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

    response = await call_native(
        taxi_eats_launch,
        method,
        make_launch_headers(
            session_eater_id=common_values['session_eater_id'],
            passport_eater_id=common_values['passport_eater_id'],
        ),
    )
    assert response.status_code == 200
    assert response.json() == expected_response

    assert mock_blackbox.times_called == 1
    assert mock_bb_personal_phone_store.times_called == 1
    assert mock_bb_personal_email_store.times_called == 1

    check_req_find_passport(mock_find_passport_eater, common_values)

    await action_login.wait_call()

    check_req_core_login(mock_core_login, common_values, 'passport_eater_id')

    assert mock_ea_logout.times_called == 1
    assert mock_ea_logout.next_call()['request'].json == {
        'inner_session_id': common_values['inner_token'],
    }

    assert mock_ea_login.times_called == 1
    assert mock_ea_login.next_call()['request'].json == make_req_ea_login(
        common_values, 'passport_eater_id',
    )
