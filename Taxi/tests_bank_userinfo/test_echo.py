import pytest

AUTH_HEADERS = {
    'X-YaBank-SessionUUID': 'test_yabank_session_uuid',
    'X-YaBank-PhoneID': 'test_yabank_phone_id',
    'X-Yandex-BUID': 'test_yandex_buid',
    'X-Yandex-UID': 'test_yandex_uid',
    'X-Ya-User-Ticket': 'test_user_ticket',
    'X-Request-Application': 'app_name=sdk_example',
    'X-Request-Language': 'ru',
    'User-Agent': 'UA',
    'Referer': 'ya.ru',
    'X-Remote-IP': '127.0.0.1',
    'X-YaBank-Yandex-Team-Login': 'kozlov-alex',
    'X-YaBank-AuthorizedByAuthproxy': 'yes',
    'X-YaBank-ColorTheme': 'LIGHT',
    'X-YaBank-SessionStatus': 'ok',
    'X-YaBank-ChannelType': 'WEB',
    'X-Yandex-Auth-Status': 'VALID',
    'X-YaTaxi-Pass-Flags': 'phonish,portal',
}

NOT_NULLABLE_HEADERS = {
    'X-Remote-IP',
    'X-Request-Application',
    'X-Request-Language',
    'X-YaTaxi-Pass-Flags',
}


@pytest.mark.parametrize('header_to_remove', AUTH_HEADERS.keys())
async def test_echo(taxi_bank_userinfo, header_to_remove):
    if header_to_remove == 'User-Agent':
        return

    expected_headers = AUTH_HEADERS.copy()
    expected_headers.pop(header_to_remove)
    response = await taxi_bank_userinfo.post(
        'v1/userinfo/v1/echo', json={}, headers=expected_headers,
    )
    assert response.status == 200
    json = response.json()
    if header_to_remove in NOT_NULLABLE_HEADERS:
        expected_headers[header_to_remove] = ''
    if header_to_remove == 'X-YaBank-ChannelType':
        expected_headers[header_to_remove] = 'SDK'
    assert json == expected_headers


def production_patch_config(config, config_vars):
    config_vars['non_production'] = False


@pytest.mark.uservice_oneshot(config_hooks=[production_patch_config])
async def test_production_env(taxi_bank_userinfo):
    response = await taxi_bank_userinfo.post('v1/userinfo/v1/echo', json={})

    assert response.status_code == 404
