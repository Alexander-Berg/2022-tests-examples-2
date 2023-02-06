import pytest

DEFAULT_YABANK_SESSION_UUID = 'session_uuid_1'
DEFAULT_YABANK_PHONE_ID = 'phone_id_1'
DEFAULT_YANDEX_BUID = 'buid_1'
DEFAULT_YANDEX_UID = 'uid_1'
DEFAULT_YANDEX_LANG = 'ru'
DEFAULT_USER_TICKET = 'user_ticket'


def _build_headers(session_uuid=DEFAULT_YABANK_SESSION_UUID):
    lang = 'en' if session_uuid == 'ok' else DEFAULT_YANDEX_LANG
    return {
        'X-YaBank-SessionUUID': session_uuid,
        'X-YaBank-PhoneID': DEFAULT_YABANK_PHONE_ID,
        'X-Yandex-BUID': DEFAULT_YANDEX_BUID,
        'X-Yandex-UID': DEFAULT_YANDEX_UID,
        'X-Ya-User-Ticket': DEFAULT_USER_TICKET,
        'X-Request-Language': lang,
    }


def _is_suggests_valid(suggests):
    assert suggests[0]['money']['amount'] == '500'
    assert suggests[0]['money']['currency'] == 'RUB'

    assert suggests[1]['money']['amount'] == '5000'
    assert suggests[1]['money']['currency'] == 'RUB'
    assert suggests[1]['plus']['amount'] == '100'
    assert suggests[1]['plus']['currency'] == 'RUB'

    return True


@pytest.mark.experiments3(filename='topup_suggest_experiments.json')
@pytest.mark.parametrize('account_status', ['ANONYMOUS', 'IDENTIFIED'])
@pytest.mark.parametrize(
    'session_uuid',
    [
        'ok',
        'default',
        'no_suggests',
        'no_hint',
        'empty',
        'disabled',
        'empty_fee_hints',
    ],
)
async def test_suggest_from_experiments(
        taxi_bank_topup,
        bank_core_client_mock,
        testpoint,
        account_status,
        session_uuid,
):
    bank_id_without_image = 'bank_id_without_image'

    @testpoint('no_bank_image')
    def checked_bank_has_no_image(data):
        assert data == bank_id_without_image

    @testpoint('translation_error')
    def skip_fee_suggest_without_translation(data):
        assert data == 'BankWithoutTranslation'

    bank_core_client_mock.set_auth_level(account_status)
    response = await taxi_bank_topup.post(
        'v1/topup/v1/get_suggests',
        headers=_build_headers(session_uuid),
        json={},
    )

    assert response.status_code == 200
    assert bank_core_client_mock.client_auth_level_handler.times_called == 1
    response_json = response.json()

    if session_uuid in [
            'ok',
            'default',
            'no_hint',
            'disabled',
            'empty_fee_hints',
    ]:
        assert _is_suggests_valid(response_json['suggests'])
    if session_uuid in ['default', 'no_suggests']:
        assert (
            response_json['hint']
            == 'Чем больше кладешь, тем можно меньше пополнять!'
        )
    if session_uuid == 'ok':
        if account_status == 'ANONYMOUS':
            assert skip_fee_suggest_without_translation.times_called == 1
            assert response_json['hints'] == {
                'Alfabank': {
                    'hint': 'Alfabank bank could charge fee',
                    'action': 'banksdk://events.action/open_sbp_instruction',
                },
                'default': {'hint': 'Default bank could charge fee'},
            }
            assert response_json['hint'] == 'Top up more, but less often'
        elif account_status == 'IDENTIFIED':
            assert checked_bank_has_no_image.times_called == 1
            assert response_json['hints'] == {
                'SberBank': {
                    'hint': 'Sber could charge fee',
                    'action': 'banksdk://events.action/open_sbp_instruction',
                    'fee_notice': {
                        'image': 'https://avatars.mdst.yandex.net/get-fintech/1401668/sberbank',
                        'title': 'Sber starts charging fee from 1 august',
                        'description': 'You can avoid fee using SBP',
                        'items': ['First hint'],
                        'button': {
                            'action': 'banksdk://topup.action/use_me2me_pull',
                            'payload': {
                                'bank_image': 'http://avatars.mdst.yandex.net/get-fintech/1401668/sberbank',
                                'account_name': 'Sber account',
                                'bank_id': '110000000111',
                            },
                            'text': 'Use account',
                        },
                    },
                },
                'GazpromBank': {
                    'hint': 'Sber could charge fee',
                    'fee_notice': {
                        'title': 'Sber starts charging fee from 1 august',
                        'description': 'You can avoid fee using SBP',
                        'button': {
                            'payload': {'bank_id': bank_id_without_image},
                            'text': 'Use account',
                        },
                    },
                },
                'default': {'hint': 'Default bank could charge fee'},
            }
    elif session_uuid == 'empty_fee_hints':
        assert 'hints' not in response_json
    else:
        assert response_json['hints'] == {
            'default': {'hint': 'Дефолт банк может брать комиссию'},
        }

    if session_uuid in ['no_suggests', 'empty']:
        assert 'suggests' not in response_json
    if session_uuid in ['no_hint', 'empty']:
        assert 'hint' not in response_json


@pytest.mark.experiments3(filename='topup_suggest_experiments.json')
@pytest.mark.parametrize('core_client_request_code', [200, 404, 500])
async def test_suggest_no_account_status_kwarg(
        taxi_bank_topup,
        bank_core_client_mock,
        testpoint,
        core_client_request_code,
):
    bank_id_without_image = 'bank_id_without_image'

    @testpoint('no_bank_image')
    def checked_bank_has_no_image(data):
        assert data == bank_id_without_image

    @testpoint('translation_error')
    def skip_fee_suggest_without_translation(data):
        assert data == 'BankWithoutTranslation'

    response = await taxi_bank_topup.post(
        'v1/topup/v1/get_suggests', headers=_build_headers('ok'), json={},
    )

    bank_core_client_mock.set_http_status_code(core_client_request_code)
    assert response.status_code == 200
    assert bank_core_client_mock.client_auth_level_handler.times_called == 1
    assert skip_fee_suggest_without_translation.times_called == 1
    response_json = response.json()
    assert response_json['hints'] == {
        'VTB': {
            'hint': 'Alfabank bank could charge fee',
            'action': 'banksdk://events.action/open_sbp_instruction',
        },
        'default': {'hint': 'Default bank could charge fee'},
    }
    assert response_json['hint'] == 'Top up more, but less often'


@pytest.mark.experiments3(filename='topup_suggest_experiments.json')
@pytest.mark.parametrize(
    'header',
    [
        'X-YaBank-SessionUUID',
        'X-YaBank-PhoneID',
        'X-Yandex-BUID',
        'X-Yandex-UID',
        'X-Ya-User-Ticket',
    ],
)
async def test_suggest_unauthorized(taxi_bank_topup, header):
    headers = _build_headers('ok')
    headers.pop(header)
    response = await taxi_bank_topup.post(
        'v1/topup/v1/get_suggests', headers=headers, json={},
    )

    assert response.status_code == 401
