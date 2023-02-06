import pytest

LAUNCH_URL = 'eats/v1/launch/v1/native'

# Generated using ya tool:
#   ya tool tvm unittest user --default 123
USER_TICKET_BAD_SCOPE = (
    '3:user:CA0Q__________9_Gg4KAgh7EHsg0oXYzAQoAQ:K_hTF-XxAQHCyHody_d4iTmu'
    'lv-T7dMOB2iCrnPERj28bF5mjcww2T0pOW3-0ZIgyB-fh6rF1b9zggH4V1TmcIamvqT-iH'
    'E_8aepc-WAsh3I66OSlwEPkWzHhQvoEtirnFexZrht_27bysrhFfu-I5egBEXW3OzdT81w'
    'RZB6Ad4'
)

# Generated using ya tool:
#   ya tool tvm unittest user --default 123 --scopes bb:sessionid
USER_TICKET_SESSIONID = (
    '3:user:CA0Q__________9_GhwKAgh7EHsaDGJiOnNlc3Npb25pZCDShdjMBCgB:HN8EHfy'
    'MxAbCu5Go7O9cxEp99oTxxwRdBhQucMEouC6Xo73r469KlWu9kwtBWaEqee66ddH9hc0F1j'
    'r_l5fxxT1lVZBIT2uhsX9Ex9cguScMONZ8_H8SyxpipQ7jaOu5obTRjZLAYqriRdq775hV-'
    'T2b5sBtppv0piQfpiAwrRw'
)

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


@pytest.mark.config(TVM_USER_TICKETS_ENABLED=False)
async def test_noargs(taxi_eats_launch, common_values, mockserver):
    response = await taxi_eats_launch.get(
        LAUNCH_URL,
        headers={'X-Ya-Service-Ticket': common_values['mock_service_ticket']},
    )
    assert response.status_code == 403
    assert response.json() == {
        'code': '403',
        'message': 'missing or empty X-Yandex-UID header',
    }


async def test_post_noargs(taxi_eats_launch, common_values, mockserver):
    response = await taxi_eats_launch.post(
        LAUNCH_URL,
        headers={'X-Ya-Service-Ticket': common_values['mock_service_ticket']},
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Missing X-Eats-Session in header',
    }


@pytest.mark.config(TVM_USER_TICKETS_ENABLED=False)
async def test_no_uid(taxi_eats_launch, common_values, mockserver):
    response = await taxi_eats_launch.get(
        LAUNCH_URL,
        headers={
            'X-YaTaxi-Pass-Flags': common_values['pass_flags_portal'],
            'X-YaTaxi-User': '',
            'X-Eats-Session': common_values['inner_token'],
            'X-Remote-IP': '127.0.0.1',
            'X-Ya-Service-Ticket': common_values['mock_service_ticket'],
        },
    )
    assert response.status_code == 403
    assert response.json() == {
        'code': '403',
        'message': 'missing or empty X-Yandex-UID header',
    }


async def test_post_no_uid(taxi_eats_launch, common_values, mockserver):
    response = await taxi_eats_launch.post(
        LAUNCH_URL,
        headers={
            'X-YaTaxi-Pass-Flags': common_values['pass_flags_portal'],
            'X-YaTaxi-User': '',
            'X-Eats-Session': common_values['inner_token'],
            'X-Remote-IP': '127.0.0.1',
            'X-Ya-Service-Ticket': common_values['mock_service_ticket'],
        },
    )
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.parametrize(
    (),
    [
        pytest.param(marks=EAP_INFO_EXPERIMENT_ENABLED),
        pytest.param(marks=EAP_INFO_EXPERIMENT_DISABLED),
    ],
)
async def test_post_no_user_ticket(
        taxi_eats_launch, common_values, mockserver,
):
    response = await taxi_eats_launch.post(
        LAUNCH_URL,
        headers={
            'X-YaTaxi-Pass-Flags': common_values['pass_flags_portal'],
            'X-YaTaxi-User': '',
            'X-Eats-Session': common_values['inner_token'],
            'X-Remote-IP': '127.0.0.1',
            'X-Ya-Service-Ticket': common_values['mock_service_ticket'],
            'X-Yandex-UID': '123',
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Missing TVM user ticket',
    }


@pytest.mark.parametrize('method', ['get', 'post'])
async def test_launch_by_phonish(
        taxi_eats_launch,
        common_values,
        mockserver,
        make_launch_headers,
        method,
):
    response = await call_native(
        taxi_eats_launch,
        method,
        make_launch_headers(
            session_eater_id=None,
            passport_eater_id=None,
            pass_flags=common_values['pass_flags_phonish'],
        ),
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'PHONISH_FORBIDDEN',
        'message': 'Launch by phonish is forbidden.',
    }


@pytest.mark.parametrize(
    (),
    [
        pytest.param(marks=EAP_INFO_EXPERIMENT_ENABLED),
        pytest.param(marks=EAP_INFO_EXPERIMENT_DISABLED),
    ],
)
async def test_user_ticket_bad_scope(
        taxi_eats_launch, mockserver, make_launch_headers,
):
    response = await taxi_eats_launch.get(
        LAUNCH_URL,
        headers=make_launch_headers(
            session_eater_id=None,
            passport_eater_id=None,
            user_ticket=USER_TICKET_BAD_SCOPE,
        ),
    )
    assert response.status_code == 403
    assert response.json()['code'] == '403'


@pytest.mark.parametrize(
    'method,is_card_transfer_allowed,expected_stq_calls,expected_stq_params,'
    + 'eap_phone_id,eap_email_id,expected_bb_calls,expected_response',
    [
        pytest.param(
            'get',
            True,
            1,
            {
                'id': '123.default_login_id',
                'kwargs': {
                    'login_id': 'default_login_id',
                    'passport_uid': '123',
                    'device_id': 'default_device_id',
                    'eater_id': 'passport_and_session_eater_id',
                },
            },
            None,
            None,
            1,
            {},
            marks=EAP_INFO_EXPERIMENT_DISABLED,
        ),
        pytest.param(
            'get',
            True,
            1,
            {
                'id': '123.default_login_id',
                'kwargs': {
                    'login_id': 'default_login_id',
                    'passport_uid': '123',
                    'device_id': 'default_device_id',
                    'eater_id': 'passport_and_session_eater_id',
                },
            },
            'eap_phone_id',
            'eap_email_id',
            0,
            {},
            marks=EAP_INFO_EXPERIMENT_ENABLED,
        ),
        pytest.param(
            'get',
            False,
            0,
            None,
            None,
            None,
            1,
            {},
            marks=EAP_INFO_EXPERIMENT_DISABLED,
        ),
        pytest.param(
            'get',
            False,
            0,
            None,
            'eap_phone_id',
            'eap_email_id',
            0,
            {},
            marks=EAP_INFO_EXPERIMENT_ENABLED,
        ),
        pytest.param(
            'post',
            True,
            1,
            {
                'id': '123.default_login_id',
                'kwargs': {
                    'login_id': 'default_login_id',
                    'passport_uid': '123',
                    'device_id': 'default_device_id',
                    'eater_id': 'passport_and_session_eater_id',
                },
            },
            None,
            None,
            1,
            EXPECTED_POST_RESPONSE_200,
            marks=EAP_INFO_EXPERIMENT_DISABLED,
        ),
        pytest.param(
            'post',
            True,
            1,
            {
                'id': '123.default_login_id',
                'kwargs': {
                    'login_id': 'default_login_id',
                    'passport_uid': '123',
                    'device_id': 'default_device_id',
                    'eater_id': 'passport_and_session_eater_id',
                },
            },
            'eap_phone_id',
            'eap_email_id',
            0,
            EXPECTED_POST_RESPONSE_200_EAP,
            marks=EAP_INFO_EXPERIMENT_ENABLED,
        ),
        pytest.param(
            'post',
            False,
            0,
            None,
            None,
            None,
            1,
            EXPECTED_POST_RESPONSE_200,
            marks=EAP_INFO_EXPERIMENT_DISABLED,
        ),
        pytest.param(
            'post',
            False,
            0,
            None,
            'eap_phone_id',
            'eap_email_id',
            0,
            EXPECTED_POST_RESPONSE_200_EAP,
            marks=EAP_INFO_EXPERIMENT_ENABLED,
        ),
    ],
)
async def test__found_by_uid__fullish__authorized__login__userticket_sessionid(
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
        stq,
        taxi_config,
        eap_phone_id,
        eap_email_id,
        expected_bb_calls,
        method,
        is_card_transfer_allowed,
        expected_stq_calls,
        expected_stq_params,
        expected_response,
):
    taxi_config.set_values(
        {
            'EATS_LAUNCH_CARD_TRANSFER': {
                'allow_transfer': is_card_transfer_allowed,
            },
        },
    )
    await taxi_eats_launch.invalidate_caches()

    # flow FoundByUid_Fullish_Authorized_Login
    mock_blackbox = await mock_blackbox(
        has_default_phone=True,
        has_email=True,
        user_ticket=USER_TICKET_SESSIONID,
    )
    mock_find_passport_eater = await mock_find_by_passport_uid(
        make_eater(
            eater_id=common_values['passport_and_session_eater_id'],
            passport_uid=common_values['requested_passport_uid'],
            passport_uid_type=common_values['passport_uid_type_portal'],
            personal_phone_id='personal_phone_id',
        ),
    )

    @testpoint('action_login')
    def action_login(data):
        return data

    @testpoint('transfer_card')
    def transfer_card(data):
        return data

    response = await call_native(
        taxi_eats_launch,
        method,
        make_launch_headers(
            user_ticket=USER_TICKET_SESSIONID,
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

    assert mock_find_passport_eater.times_called == 1
    assert mock_find_passport_eater.next_call()['request'].json == {
        'passport_uid': common_values['requested_passport_uid'],
    }

    await action_login.wait_call()

    assert mock_core_login.times_called == 1
    assert mock_core_login.next_call()['request'].json == {
        'eater_id': common_values['passport_and_session_eater_id'],
        'inner_token': common_values['inner_token'],
    }

    assert mock_ea_login.times_called == 1
    assert mock_ea_login.next_call()['request'].json == {
        'inner_session_id': common_values['inner_token'],
        'eater_id': common_values['passport_and_session_eater_id'],
        'eater_username': common_values['passport_and_session_eater_id'],
    }

    if expected_stq_calls > 0:
        await transfer_card.wait_call()

    assert stq.eats_transfer_card.times_called == expected_stq_calls
    # TODO Destroy ifs from test!!!
    if is_card_transfer_allowed:
        stq_call = stq.eats_transfer_card.next_call()
        kwargs = stq_call['kwargs']
        ex_kwargs = expected_stq_params['kwargs']

        assert kwargs['eater_id'] == ex_kwargs['eater_id']
        assert kwargs['device_id'] == ex_kwargs['device_id']
        assert kwargs['login_id'] == ex_kwargs['login_id']
        assert kwargs['passport_uid'] == ex_kwargs['passport_uid']
        assert stq_call['id'] == expected_stq_params['id']


@pytest.mark.parametrize(
    'expected_bb_calls',
    [
        pytest.param(0, marks=EAP_INFO_EXPERIMENT_ENABLED),
        pytest.param(1, marks=EAP_INFO_EXPERIMENT_DISABLED),
    ],
)
@pytest.mark.parametrize('method', ['get', 'post'])
async def test__found_by_uid__fullish__authorized__login__eater_banned(
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
        expected_bb_calls,
        method,
):
    # flow FoundByUid_Fullish_Authorized_Login
    mock_blackbox = await mock_blackbox(has_default_phone=True, has_email=True)
    mock_find_passport_eater = await mock_find_by_passport_uid(
        make_eater(
            eater_id=common_values['passport_and_session_eater_id'],
            passport_uid=common_values['requested_passport_uid'],
            passport_uid_type=common_values['passport_uid_type_portal'],
            personal_phone_id='personal_phone_id_1',
            banned_at='2019-12-31T10:59:59+03:00',
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
        ),
    )

    assert response.status_code == 403
    assert response.json() == {
        'code': 'USER_IS_BANNED',
        'message': 'User is banned',
    }

    assert mock_blackbox.times_called == expected_bb_calls
    assert mock_bb_personal_phone_store.times_called == expected_bb_calls
    assert mock_bb_personal_email_store.times_called == expected_bb_calls

    assert mock_find_passport_eater.times_called == 1
    assert mock_find_passport_eater.next_call()['request'].json == {
        'passport_uid': common_values['requested_passport_uid'],
    }

    await action_login.wait_call()

    assert mock_core_login.times_called == 1
    assert mock_core_login.next_call()['request'].json == {
        'eater_id': common_values['passport_and_session_eater_id'],
        'inner_token': common_values['inner_token'],
    }


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
async def test__found_by_uid__fullish__authorized__login__by_pdd(
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
            pass_flags=common_values['pass_flags_pdd'],
            eap_phone_id=eap_phone_id,
            eap_email_id=eap_email_id,
        ),
    )

    assert response.status_code == 200
    assert response.json() == expected_response

    assert mock_blackbox.times_called == expected_bb_calls
    assert mock_bb_personal_phone_store.times_called == expected_bb_calls
    assert mock_bb_personal_email_store.times_called == expected_bb_calls

    assert mock_find_passport_eater.times_called == 1
    assert mock_find_passport_eater.next_call()['request'].json == {
        'passport_uid': common_values['requested_passport_uid'],
    }

    await action_login.wait_call()

    assert mock_core_login.times_called == 1
    assert mock_core_login.next_call()['request'].json == {
        'eater_id': common_values['passport_and_session_eater_id'],
        'inner_token': common_values['inner_token'],
    }

    assert mock_ea_login.times_called == 1
    assert mock_ea_login.next_call()['request'].json == {
        'inner_session_id': common_values['inner_token'],
        'eater_id': common_values['passport_and_session_eater_id'],
        'eater_username': common_values['passport_and_session_eater_id'],
    }


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
async def test_invalid_requested_passport_eater_id(
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
            passport_eater_id='invalid_eater_id',
            pass_flags=common_values['pass_flags_pdd'],
        ),
    )

    assert response.status_code == 200
    assert response.json() == expected_response

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
        'eater_id': common_values['passport_and_session_eater_id'],
        'inner_token': common_values['inner_token'],
    }

    assert mock_ea_login.times_called == 1
    assert mock_ea_login.next_call()['request'].json == {
        'inner_session_id': common_values['inner_token'],
        'eater_id': common_values['passport_and_session_eater_id'],
        'eater_username': common_values['passport_and_session_eater_id'],
    }


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
async def test_not_found_requested_passport_eater_id(
        taxi_eats_launch,
        common_values,
        mockserver,
        make_launch_headers,
        make_eater,
        mock_blackbox,
        mock_bb_personal_phone_store,
        mock_bb_personal_email_store,
        mock_find_by_passport_uid_not_found,
        mock_register,
        make_register_request,
        mock_ea_login,
        method,
        expected_response,
):
    # flow NoByUid_NotAuthorized_Register
    mock_blackbox = await mock_blackbox(has_default_phone=True, has_email=True)

    response = await call_native(
        taxi_eats_launch,
        method,
        make_launch_headers(
            session_eater_id=None, passport_eater_id='invalid_eater_id',
        ),
    )

    assert response.status_code == 200
    assert response.json() == expected_response

    assert mock_blackbox.times_called == 1
    assert mock_bb_personal_phone_store.times_called == 1
    assert mock_bb_personal_email_store.times_called == 1

    assert mock_find_by_passport_uid_not_found.times_called == 1
    assert mock_find_by_passport_uid_not_found.next_call()['request'].json == {
        'passport_uid': common_values['requested_passport_uid'],
    }

    assert mock_register.times_called == 1
    assert mock_register.next_call()['request'].json == make_register_request(
        has_phone=True, has_email=True,
    )

    assert mock_ea_login.times_called == 1
    assert mock_ea_login.next_call()['request'].json == {
        'inner_session_id': common_values['inner_token'],
        'eater_id': common_values['registered_eater_id'],
        'eater_username': common_values['registered_eater_id'],
    }


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
async def test_not_found_requested_session_eater_id(
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
        mock_ea_logout,
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
            session_eater_id='invalid_eater_id',
            passport_eater_id=common_values['passport_eater_id'],
        ),
    )

    assert response.status_code == 200
    assert response.json() == expected_response

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

    assert mock_ea_logout.times_called == 1
    assert mock_ea_logout.next_call()['request'].json == {
        'inner_session_id': common_values['inner_token'],
    }
