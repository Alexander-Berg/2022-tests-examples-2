import copy
import typing

import pytest

from api_4_0_middleware import mw as api_4_0_mw


BACKEND_REQUIRED_HEADERS = {
    'X-Yandex-UID': '42',
    'X-YaTaxi-UserId': '1212',
    'X-Yandex-Login': 'tesla-suxx',
    'X-Ya-User-Ticket': 'test_ticket',
}
BACKEND_BASE_RESPONSE = {
    'yandex_uid': '42',
    'yandex_login': 'tesla-suxx',
    'yandex_taxi_userid': '1212',
    'user_ticket': 'test_ticket',
    'flags': {
        'has_phonish': False,
        'has_ya_plus': False,
        'no_login': False,
        'phone_confirm_required': False,
        'has_plus_cashback': False,
        'account_type': 'unknown',
    },
    'personal': {},
    'app_vars': {},
}


def make_response(
        extra: typing.Optional[dict] = None,
        extra_flags: typing.Optional[dict] = None,
        extra_personal: typing.Optional[dict] = None,
):
    response: typing.Dict[str, typing.Any] = copy.deepcopy(
        BACKEND_BASE_RESPONSE,
    )
    response.update(extra or {})
    response['flags'].update(extra_flags or {})
    response['personal'].update(extra_personal or {})
    return response


@pytest.fixture(name='client')
def yas_fixture(web_context):
    return web_context.clients.yet_another_service


@pytest.mark.parametrize(
    'request_headers,response_body',
    [
        (
            {
                **BACKEND_REQUIRED_HEADERS,
                'X-YaTaxi-PhoneId': '3434',
                'X-YaTaxi-Pass-Flags': 'phonish,ya-plus',
                'X-Request-Language': 'ruRU',
                'X-Request-Application': 'key1=val1,key2=val2,incorrect',
            },
            make_response(
                extra={
                    'locale': 'ruRU',
                    'yandex_taxi_phoneid': '3434',
                    'app_vars': {'key1': 'val1', 'key2': 'val2'},
                },
                extra_flags={
                    'account_type': 'phonish',
                    'has_phonish': True,
                    'has_ya_plus': True,
                },
            ),
        ),
        ({}, {'reason': 'NOT AUTHORIZED'}),
    ],
)
async def test_server_pass_not_authorized(
        web_app_client, request_headers, response_body,
):
    response = await web_app_client.get(
        '/api-4-0/pass-not-authorized-echo', headers=request_headers,
    )
    assert response.status == 200
    assert await response.json() == response_body


@pytest.mark.parametrize(
    'request_headers,response_body,status',
    [
        (BACKEND_REQUIRED_HEADERS, BACKEND_BASE_RESPONSE, 200),
        (
            {
                **BACKEND_REQUIRED_HEADERS,
                'X-YaTaxi-PhoneId': '3434',
                'X-YaTaxi-Pass-Flags': 'phonish,ya-plus',
                'X-Request-Language': 'ruRU',
                'X-Request-Application': 'key1=val1,key2=val2,incorrect',
            },
            make_response(
                extra={
                    'locale': 'ruRU',
                    'yandex_taxi_phoneid': '3434',
                    'app_vars': {'key1': 'val1', 'key2': 'val2'},
                },
                extra_flags={
                    'account_type': 'phonish',
                    'has_phonish': True,
                    'has_ya_plus': True,
                    'no_login': False,
                },
            ),
            200,
        ),
        (
            {},
            {'code': 'not-authorized', 'message': 'Request not authorized'},
            401,
        ),
        (
            {
                **BACKEND_REQUIRED_HEADERS,
                'X-YaTaxi-Pass-Flags': 'phonish,portal,no-login',
            },
            make_response(
                extra_flags={
                    'account_type': 'portal',
                    'has_phonish': True,
                    'no_login': True,
                },
            ),
            200,
        ),
        (
            {**BACKEND_REQUIRED_HEADERS, 'X-YaTaxi-Pass-Flags': 'pdd'},
            make_response(extra_flags={'account_type': 'pdd'}),
            200,
        ),
    ],
)
async def test_server_with_strict_check(
        web_app_client, request_headers, response_body, status,
):
    response = await web_app_client.get(
        '/api-4-0/closed-echo', headers=request_headers,
    )
    assert response.status == status
    assert await response.json() == response_body


async def test_client_pass(client, mock_yet_another_service):
    headers = {
        **BACKEND_REQUIRED_HEADERS,
        'X-YaTaxi-PhoneId': '3434',
        'X-YaTaxi-Pass-Flags': 'phonish,ya-plus',
        'X-Request-Language': 'ruRU',
        'X-Request-Application': 'key1=val1,key2=val2',
        'X-YaTaxi-Bound-Uids': '1,2,3',
        'X-YaTaxi-Bound-UserIds': '4,5,6',
        'X-YaTaxi-User': 'personal_phone_id=123',
        'X-Login-Id': '343',
        'X-Remote-IP': '127.0.0.1',
    }

    @mock_yet_another_service('/pong')
    async def pong_handler(request):
        for key, value in headers.items():
            assert request.headers[key] == value
        return None

    response = await client.pong(
        api_4_0_auth_context=api_4_0_mw.parse_auth_context(headers),
    )

    assert response.status == 200
    assert response.body is None

    assert pong_handler.times_called == 1
