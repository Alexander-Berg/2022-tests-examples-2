import pytest


TEST_UID = 100
TEST_UID_STR = '100'
TEST_DISPLAY_NAME = 'Козьма Прутков'
TEST_AVATAR_ID = '123'
TEST_AVATAR_STR = 'https://avatars.mds.yandex.net/get-yapic/{}/40x40'.format(
    TEST_AVATAR_ID,
)
TEST_HEADERS = {'X-Yandex-UID': TEST_UID_STR, 'X-Remote-IP': '1.2.3.4'}
TEST_LOGIN = 'kozmaprutkov'


@pytest.fixture(name='mock_check_client')
async def _mock_check_client(mockserver):
    async def do_mock_check_client(
            uid=TEST_UID_STR,
            client_state='API_ENABLED',
            client_role='CLIENT',
            has_shared_wallet=False,
            fails=False,
    ):
        @mockserver.json_handler('/direct-internal/clients/checkClientState')
        async def _do_mock_check_client(request):
            assert request.json['uid'] == int(uid)

            if fails:
                return mockserver.make_response(status=500)

            data = {
                'success': True,
                'client_state': client_state,
                'client_role': client_role,
            }
            if client_state != 'NOT_EXISTS':
                data['has_shared_wallet'] = has_shared_wallet
            if client_state == 'CAN_NOT_BE_CREATED':
                data['can_not_be_created_reason'] = 'LOGIN_CANNOT_BE_PDD'

            return data

        return _do_mock_check_client

    return do_mock_check_client


@pytest.mark.parametrize(
    'client_state, client_role, expected_status',
    [
        pytest.param('API_ENABLED', 'CLIENT', 'ok', id='enabled, client'),
        pytest.param(
            'API_ENABLED',
            'AGENCY',
            'need_another_account',
            id='enabled, not client',
        ),
        pytest.param(
            'NOT_EXISTS', None, 'need_register', id='not exists, no role',
        ),
        pytest.param(
            'NOT_EXISTS', 'CLIENT', 'need_register', id='not exists, client',
        ),
        pytest.param('API_DISABLED', 'CLIENT', 'need_register', id='disabled'),
        pytest.param(
            'API_DISABLED',
            'AGENCY',
            'need_another_account',
            id='disabled, not client',
        ),
        pytest.param(
            'API_BLOCKED',
            'CLIENT',
            'need_another_account',
            id='api_blocked, client',
        ),
        pytest.param(
            'BLOCKED', 'CLIENT', 'need_another_account', id='blocked, client',
        ),
        pytest.param(
            'BLOCKED',
            'AGENCY',
            'need_another_account',
            id='blocked, not client',
        ),
        pytest.param(
            'CAN_NOT_BE_CREATED',
            None,
            'need_another_account',
            id='cannot be created',
        ),
    ],
)
async def test_check_client(
        taxi_eats_restapp_marketing,
        mock_blackbox_userinfo,
        mock_check_client,
        client_state,
        client_role,
        expected_status,
):
    bb_handler = await mock_blackbox_userinfo()
    direct_handler = await mock_check_client(
        client_state=client_state, client_role=client_role,
    )

    response = await taxi_eats_restapp_marketing.post(
        f'/4.0/restapp-front/marketing/v1/check-partner', headers=TEST_HEADERS,
    )

    assert bb_handler.times_called == 1
    assert direct_handler.times_called == 1

    assert response.status == 200
    assert response.json() == {
        'yandex_uid': TEST_UID,
        'status': expected_status,
        'display_name': TEST_DISPLAY_NAME,
        'login': TEST_LOGIN,
        'avatar': TEST_AVATAR_STR,
    }


async def test_not_found_in_bb(
        taxi_eats_restapp_marketing, mock_blackbox_userinfo, mock_check_client,
):
    bb_handler = await mock_blackbox_userinfo(not_found=True)
    direct_handler = await mock_check_client()

    response = await taxi_eats_restapp_marketing.post(
        f'/4.0/restapp-front/marketing/v1/check-partner', headers=TEST_HEADERS,
    )

    assert bb_handler.times_called == 1
    assert direct_handler.times_called == 1

    assert response.status == 200
    assert response.json() == {
        'yandex_uid': 0,
        'status': 'ok',
        'display_name': '',
        'login': '',
    }


@pytest.mark.parametrize(
    'bb_fails, direct_fails, expected_response',
    [
        pytest.param(
            True,
            False,
            {'yandex_uid': 0, 'status': 'ok', 'display_name': '', 'login': ''},
            id='bb fails',
        ),
        pytest.param(
            False,
            True,
            {
                'yandex_uid': TEST_UID,
                'status': 'need_another_account',
                'display_name': TEST_DISPLAY_NAME,
                'login': TEST_LOGIN,
                'avatar': TEST_AVATAR_STR,
            },
            id='direct fails',
        ),
        pytest.param(
            True,
            True,
            {
                'yandex_uid': 0,
                'status': 'need_another_account',
                'display_name': '',
                'login': '',
            },
            id='both fail',
        ),
    ],
)
async def test_bb_fails(
        taxi_eats_restapp_marketing,
        mock_blackbox_userinfo,
        mock_check_client,
        bb_fails,
        direct_fails,
        expected_response,
):
    bb_handler = await mock_blackbox_userinfo(fails=bb_fails)
    direct_handler = await mock_check_client(fails=direct_fails)

    response = await taxi_eats_restapp_marketing.post(
        f'/4.0/restapp-front/marketing/v1/check-partner', headers=TEST_HEADERS,
    )

    if bb_fails:
        assert bb_handler.times_called == 3
    else:
        assert bb_handler.times_called == 1

    assert direct_handler.times_called == 1

    assert response.status == 200
    assert response.json() == expected_response
