import pytest


AUTH_HEADERS_LIST = [
    {'X-YaBank-SessionUUID': 'test_yabank_session_uuid'},
    {'X-YaBank-PhoneID': 'test_yabank_phone_id'},
    {'X-Yandex-BUID': 'test_yandex_buid'},
    {'X-Yandex-UID': 'test_yandex_uid'},
    {'X-Ya-User-Ticket': 'test_user_ticket'},
]


def _build_headers(exclude_headers=None, channel_type=None):
    all_headers = {
        'X-Request-Application': 'app_brand=yataxi,app_name=web,app_ver1=2',
        'X-Request-Language': 'en',
    }
    for header in AUTH_HEADERS_LIST:
        all_headers.update(header)

    if channel_type:
        all_headers.update({'X-YaBank-ChannelType': channel_type})

    if not exclude_headers:
        return all_headers

    for header_to_exclude in exclude_headers:
        all_headers.pop(header_to_exclude, None)

    return all_headers


@pytest.mark.parametrize('channel_type', ['WEB', 'SDK', None])
async def test_bank_authproxy(taxi_userver_sample, channel_type):
    response = await taxi_userver_sample.get(
        'test_bank_authproxy',
        headers=_build_headers(channel_type=channel_type),
    )
    assert response.status_code == 200
    assert response.json() == {
        'yandex_uid': 'test_yandex_uid',
        'ya_bank_phone_id': 'test_yabank_phone_id',
        'ya_bank_session_uuid': 'test_yabank_session_uuid',
        'ya_user_ticket': 'test_user_ticket',
        'yandex_buid': 'test_yandex_buid',
        'locale': 'en',
        'app_name': 'web',
        'app_version': '2',
        'channel_type': channel_type or 'SDK',
    }


@pytest.mark.parametrize('excluded_header', AUTH_HEADERS_LIST)
async def test_bank_authproxy_401(taxi_userver_sample, excluded_header):
    response = await taxi_userver_sample.get(
        'test_bank_authproxy', headers=_build_headers(excluded_header),
    )
    assert response.status_code == 401
