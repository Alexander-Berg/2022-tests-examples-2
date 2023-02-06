import pytest


HANDLE_PATH = '/4.0/invites/v1/activate'

CLUB_NAME = 'yandex_go'

NUM_CODES = 5
CODE_LENGTH = 10


def encode_application_header(
        application, brand, app_version, platform_version,
):
    app_ver = app_version.split('.')
    platform_ver = platform_version.split('.')

    params = [f'app_name={application}', f'app_brand={brand}']

    for index, ver_part in enumerate(app_ver):
        params.append(f'app_ver{index+1}={ver_part}')

    for index, ver_part in enumerate(platform_ver):
        params.append(f'platform_ver{index+1}={ver_part}')

    return ','.join(params)


def pa_headers(
        yandex_uid='123456789',
        phone_id='abcdefgh',
        application='android',
        brand='yataxi',
        app_version='1.100.0',
        platform_version='5.0.0',
):
    headers = {
        'X-Yandex-Login': 'user',
        'X-Yandex-Uid': yandex_uid,
        'X-YaTaxi-Pass-Flags': 'phonish,portal',
        'X-Request-Application': encode_application_header(
            application, brand, app_version, platform_version,
        ),
    }

    if phone_id:
        headers['X-YaTaxi-PhoneId'] = phone_id

    return headers


@pytest.mark.parametrize(
    'request_body, has_phone_id, expected_code',
    [
        pytest.param({}, True, 400, id='empty request body'),
        pytest.param(
            {'param': 'value'}, True, 400, id='missing required param',
        ),
        pytest.param({'code': 'abacaba'}, False, 401, id='missing phone_id'),
    ],
)
async def test_bad_request(
        taxi_invites, request_body, has_phone_id, expected_code,
):
    if has_phone_id:
        headers = pa_headers()
    else:
        headers = pa_headers(phone_id=None)

    response = await taxi_invites.post(
        HANDLE_PATH, headers=headers, json=request_body,
    )
    assert response.status_code == expected_code


@pytest.mark.parametrize('app_version', ['1.5', '1.5.3', '2'])
@pytest.mark.parametrize('platform_version', ['4.5', '4.5.7', '5'])
@pytest.mark.parametrize(
    'expected_code',
    [
        pytest.param(
            'outdated_app',
            marks=pytest.mark.config(
                INVITES_CLIENT_VERSION_REQUIREMENTS={
                    CLUB_NAME: {'android': {'min_app_version': ''}},
                },
            ),
        ),
        pytest.param(
            'outdated_os',
            marks=pytest.mark.config(
                INVITES_CLIENT_VERSION_REQUIREMENTS={
                    CLUB_NAME: {'android': {'min_os_version': 'wrong_format'}},
                },
            ),
        ),
        pytest.param(
            'outdated_os',
            marks=pytest.mark.config(
                INVITES_CLIENT_VERSION_REQUIREMENTS={
                    CLUB_NAME: {
                        'android': {
                            'min_app_version': '1.0.0',
                            'min_os_version': '',
                        },
                    },
                },
            ),
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_texts.json')
@pytest.mark.now('2020-01-10T00:00:00+0300')
async def test_broken_version_config(
        taxi_invites, app_version, platform_version, expected_code,
):
    phone_id = 'not_member'
    invite_code = 'yandex_go_elite_member__not_used'

    headers = pa_headers(
        phone_id=phone_id,
        application='android',
        app_version=app_version,
        platform_version=platform_version,
    )
    request = {'code': invite_code}
    response = await taxi_invites.post(
        HANDLE_PATH, headers=headers, json=request,
    )
    assert response.status_code == 200

    response_json = response.json()
    assert response_json['code'] == expected_code


@pytest.mark.parametrize(
    'phone_id, is_yandex_go_member',
    [
        ('not_member', False),
        ('yandex_go_member', True),
        ('yandex_go_elite_member', True),
        ('yet_another_club_member', False),
    ],
)
@pytest.mark.parametrize(
    'invite_code, code_exists, code_used',
    [
        pytest.param('invalid_code', False, None, id='code_does_not_exist'),
        pytest.param(
            'yandex_go_elite_member__yandex_go_member',
            True,
            True,
            id='code_already_used',
        ),
        pytest.param(
            'yandex_go_elite_member__not_used',
            True,
            False,
            id='code_not_used',
        ),
    ],
)
@pytest.mark.parametrize(
    'app_version, app_supported',
    [('1.0.0', False), ('1', False), ('1.5', True), ('1.5.3', True)],
)
@pytest.mark.parametrize(
    'platform_version, platform_supported',
    [('4.0.4', False), ('4.2', False), ('4.5.0', True), ('5', True)],
)
@pytest.mark.config(
    INVITES_CLIENT_VERSION_REQUIREMENTS={
        CLUB_NAME: {
            'android': {'min_app_version': '1.5.0', 'min_os_version': '4.5.0'},
        },
    },
    INVITE_CODES_CREATION_PARAMS={
        'num_codes': NUM_CODES,
        'code_length': CODE_LENGTH,
        'alphabet': 'abcdefg012345',
    },
)
@pytest.mark.experiments3(filename='exp3_texts.json')
@pytest.mark.now('2020-01-10T00:00:00+0300')
async def test_main(
        taxi_invites,
        invites_db,
        load_json,
        phone_id,
        is_yandex_go_member,
        invite_code,
        code_exists,
        code_used,
        app_version,
        platform_version,
        app_supported,
        platform_supported,
        stq,
):
    assert (
        invites_db.user_is_club_member(phone_id, CLUB_NAME)
        is is_yandex_go_member
    )
    assert invites_db.invite_code_exists(invite_code) is code_exists
    if code_exists:
        assert invites_db.invite_code_is_used(invite_code) is code_used

    if is_yandex_go_member:
        if code_exists:
            if code_used and invites_db.invite_code_is_used(
                    invite_code, phone_id=phone_id,
            ):
                expected_code = 'code_activated'
            else:
                expected_code = 'code_redundant'
        else:
            expected_code = 'code_invalid'
    else:
        if not code_exists:
            expected_code = 'code_invalid'
        elif code_used:
            expected_code = 'code_used'
        elif not app_supported:
            expected_code = 'outdated_app'
        elif not platform_supported:
            expected_code = 'outdated_os'
        else:
            # code not used and all requirements are met
            expected_code = 'code_activated'

    expected_info = load_json('codes_info.json')[expected_code]

    headers = pa_headers(
        phone_id=phone_id,
        application='android',
        app_version=app_version,
        platform_version=platform_version,
    )
    request = {'code': invite_code}
    response = await taxi_invites.post(
        HANDLE_PATH, headers=headers, json=request,
    )
    assert response.status_code == 200

    response_json = response.json()
    assert response_json == {'code': expected_code, 'info': expected_info}

    if expected_code == 'code_activated':
        assert invites_db.user_is_club_member(phone_id, CLUB_NAME)
        assert invites_db.invite_code_is_used(invite_code, phone_id=phone_id)

        if not is_yandex_go_member:
            # new user created with new invite codes
            assert stq.invites_member_set_club_tag.times_called == 1
            save_call = stq.invites_member_set_club_tag.next_call()
            assert save_call['kwargs']['phone_id'] == phone_id
            assert save_call['kwargs']['club_id'] == invites_db.get_club_id(
                CLUB_NAME,
            )

            user_codes = invites_db.get_user_invite_codes(CLUB_NAME, phone_id)
            assert len(user_codes) == NUM_CODES
            assert all(
                [len(code['code']) == CODE_LENGTH for code in user_codes],
            )
