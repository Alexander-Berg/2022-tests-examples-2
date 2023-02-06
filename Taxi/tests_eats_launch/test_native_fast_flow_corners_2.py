import pytest

LAUNCH_URL = 'eats/v1/launch/v1/native'

HEADER_DEVICE_ID = 'X-Device-Id'

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


@pytest.mark.parametrize('method', ['get', 'post'])
async def test__ea_logout_404(
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
        mock_ea_logout_404,
        mock_core_login,
        mock_ea_login,
        method,
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

    assert mock_blackbox.times_called == 1
    assert mock_find_passport_eater.times_called == 1

    await action_login.wait_call()

    assert mock_core_login.times_called == 1
    assert mock_ea_logout_404.times_called == 1
    assert mock_ea_login.times_called == 1


@pytest.mark.experiments3(filename='exp3_eats_launch_card_transfer.json')
@pytest.mark.config(EATS_LAUNCH_CARD_TRANSFER={'allow_transfer': True})
@pytest.mark.parametrize(
    'method,expected_stq_calls,expected_stq_params,device_id,'
    + 'expected_response',
    [
        (
            'get',
            1,
            {
                'id': '123.default_login_id',
                'kwargs': {
                    'login_id': 'default_login_id',
                    'passport_uid': '123',
                    'device_id': 'chosen_device_id',
                    'eater_id': 'passport_and_session_eater_id',
                },
            },
            'chosen_device_id',
            {},
        ),
        ('get', 0, None, 'default_device_id', {}),
        (
            'post',
            1,
            {
                'id': '123.default_login_id',
                'kwargs': {
                    'login_id': 'default_login_id',
                    'passport_uid': '123',
                    'device_id': 'chosen_device_id',
                    'eater_id': 'passport_and_session_eater_id',
                },
            },
            'chosen_device_id',
            EXPECTED_POST_RESPONSE_200,
        ),
        ('post', 0, None, 'default_device_id', EXPECTED_POST_RESPONSE_200),
    ],
)
async def test__found_by_uid__fullish__authorized__login__card_transfer_exp(
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
        method,
        expected_stq_calls,
        expected_stq_params,
        device_id,
        expected_response,
):
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
            device_id=device_id,
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

    if expected_stq_calls > 0:
        await transfer_card.wait_call()

    assert stq.eats_transfer_card.times_called == expected_stq_calls

    if expected_stq_calls > 0:
        stq_call = stq.eats_transfer_card.next_call()
        kwargs = stq_call['kwargs']
        ex_kwargs = expected_stq_params['kwargs']

        assert kwargs['eater_id'] == ex_kwargs['eater_id']
        assert kwargs['device_id'] == ex_kwargs['device_id']
        assert kwargs['login_id'] == ex_kwargs['login_id']
        assert kwargs['passport_uid'] == ex_kwargs['passport_uid']
        assert stq_call['id'] == expected_stq_params['id']


@pytest.fixture(name='mock_fail_stq')
async def _mock_fail_stq(mockserver):
    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    async def _mock(request, queue_name):
        return mockserver.make_response(json={}, status=500)

    return _mock


@pytest.mark.experiments3(filename='exp3_eats_launch_card_transfer.json')
@pytest.mark.config(EATS_LAUNCH_CARD_TRANSFER={'allow_transfer': True})
@pytest.mark.parametrize(
    'method,expected_response',
    [('get', {}), ('post', EXPECTED_POST_RESPONSE_200)],
)
async def test__found_by_uid__fullish__authorized__login__card_transfer_fail(
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
        mock_fail_stq,
        mock_fail_stq_transfer_card,
        method,
        expected_response,
):
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
            device_id='chosen_device_id',
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

    await transfer_card.wait_call()

    assert stq.eats_transfer_card.times_called == 0


@pytest.mark.parametrize('method', ['get', 'post'])
@pytest.mark.parametrize('device_id', ['test_device_id', None])
async def test__forward_device_id__login(
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
        device_id,
):
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

    request_headers = make_launch_headers(
        user_ticket=USER_TICKET_SESSIONID,
        session_eater_id=common_values['passport_and_session_eater_id'],
        passport_eater_id=common_values['passport_and_session_eater_id'],
        device_id=device_id,
    )
    if device_id is None:
        del request_headers[HEADER_DEVICE_ID]

    @testpoint('action_login')
    def action_login(data):
        return data

    response = await call_native(taxi_eats_launch, method, request_headers)

    assert response.status_code == 200
    assert mock_blackbox.times_called == 1
    assert mock_find_passport_eater.times_called == 1

    await action_login.wait_call()

    assert mock_core_login.times_called == 1

    login_request_headers = mock_core_login.next_call()['request'].headers
    if device_id is None:
        assert HEADER_DEVICE_ID not in login_request_headers
    else:
        assert login_request_headers[HEADER_DEVICE_ID] == device_id


@pytest.mark.parametrize('method', ['get', 'post'])
@pytest.mark.parametrize('device_id', ['test_device_id', None])
async def test__forward_device_id__register(
        taxi_eats_launch,
        mockserver,
        make_launch_headers,
        mock_blackbox,
        mock_bb_personal_phone_store,
        mock_bb_personal_email_store,
        mock_find_by_passport_uid_not_found,
        mock_register,
        mock_ea_login,
        method,
        device_id,
):
    # flow NoByUid_NotAuthorized_Register
    mock_blackbox = await mock_blackbox(has_default_phone=True, has_email=True)

    request_headers = make_launch_headers(
        session_eater_id=None, passport_eater_id=None, device_id=device_id,
    )
    if device_id is None:
        del request_headers[HEADER_DEVICE_ID]

    response = await call_native(taxi_eats_launch, method, request_headers)
    assert response.status_code == 200

    assert mock_register.times_called == 1
    assert mock_blackbox.times_called == 1

    register_request_headers = mock_register.next_call()['request'].headers
    if device_id is None:
        assert HEADER_DEVICE_ID not in register_request_headers
    else:
        assert register_request_headers[HEADER_DEVICE_ID] == device_id
