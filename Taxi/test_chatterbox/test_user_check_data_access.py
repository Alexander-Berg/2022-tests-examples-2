import json

import pytest


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    'headers, data, expected_status',
    [
        ({'X-Ya-Service-Ticket': '123'}, {'chatterbox_id': '123'}, 401),
        (
            {
                'X-Real-IP': '123',
                'X-Yandex-UID': '123',
                'X-Ya-User-Ticket': '123',
                'X-Ya-Service-Ticket': '123',
            },
            {'park_db_id': '123'},
            400,
        ),
        (
            {
                'X-Real-IP': '123',
                'X-Yandex-UID': '123',
                'X-Ya-User-Ticket': '123',
                'X-Ya-Service-Ticket': '123',
            },
            {'chatterbox_id': '123'},
            400,
        ),
        (
            {
                'X-Real-IP': '123',
                'X-Ya-User-Ticket': '123',
                'X-Ya-Service-Ticket': '123',
            },
            {'chatterbox_id': '123', 'meta_info': {'park_db_id': '123'}},
            401,
        ),
    ],
)
async def test_wrong_request(
        cbox,
        patch_aiohttp_session,
        response_mock,
        headers,
        data,
        expected_status,
        patch_tvm_auth,
):
    patch_tvm_auth('asd', '123')

    @patch_aiohttp_session('http://blackbox.yandex-team.ru/blackbox/', 'GET')
    def _dummy_passport(method, url, *args, **kwargs):
        assert 'yandex-team.ru' in url
        return response_mock(
            text=json.dumps(
                {'users': [{'uid': {'value': '123'}, 'login': 'support_1'}]},
            ),
        )

    await cbox.post('/v1/user/check_data_access', data=data, headers=headers)
    assert cbox.status == expected_status


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    'data, expected_status, expected_access_status',
    [
        ({'chatterbox_id': '5cf94043629526419e77b82e'}, 200, 'permitted'),
        (
            {
                'chatterbox_id': '5cf94043629526419e77b82e',
                'meta_info': {'park_db_id': '123'},
            },
            200,
            'forbidden',
        ),
        (
            {
                'chatterbox_id': '7cf94043629526419e77b82e',
                'meta_info': {'park_db_id': 'some_db_id'},
            },
            200,
            'permitted',
        ),
        (
            {
                'chatterbox_id': '0cf94043629526419e77b82e',
                'meta_info': {'park_db_id': 'manually_set_park_db_id'},
            },
            200,
            'permitted',
        ),
        (
            {
                'chatterbox_id': '7cf94043629526419e77b82e',
                'meta_info': {'park_db_id': 'unknown'},
            },
            200,
            'forbidden',
        ),
        ({'chatterbox_id': '8cf94043629526419e77b82e'}, 200, 'forbidden'),
        ({'chatterbox_id': '9cf94043629526419e77b82e'}, 200, 'forbidden'),
        (
            {
                'chatterbox_id': 'acf94043629526419e77b82e',
                'meta_info': {
                    'user_phone': '+79999999999',
                    'driver_license': 'some_driver_license',
                },
            },
            200,
            'permitted',
        ),
    ],
)
async def test_data_access_check(
        cbox,
        patch_aiohttp_session,
        response_mock,
        data,
        expected_status,
        expected_access_status,
        mock_personal,
        patch_tvm_auth,
):
    patch_tvm_auth('asd', '123')

    @patch_aiohttp_session('http://blackbox.yandex-team.ru/blackbox/', 'GET')
    def _dummy_passport(method, url, *args, **kwargs):
        assert 'yandex-team.ru' in url
        return response_mock(
            text=json.dumps(
                {'users': [{'uid': {'value': '123'}, 'login': 'support_1'}]},
            ),
        )

    await cbox.post(
        '/v1/user/check_data_access',
        data=data,
        headers={
            'X-Real-IP': '123',
            'X-Yandex-UID': '123',
            'X-Ya-User-Ticket': '123',
            'X-Ya-Service-Ticket': '123',
        },
    )
    assert cbox.status == expected_status
    assert cbox.body_data == {'access_status': expected_access_status}

    assert _dummy_passport.calls


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    'headers, data, expected_status',
    [
        ({'X-Ya-Service-Ticket': '123'}, {'chatterbox_id': '123'}, 401),
        (
            {'X-Ya-Service-Ticket': '123'},
            {'chatterbox_id': '5cf94043629526419e77b82e'},
            401,
        ),
    ],
)
async def test_wrong_request_without_user_ticket(
        cbox,
        patch_aiohttp_session,
        response_mock,
        headers,
        data,
        expected_status,
        patch_tvm_auth,
):
    patch_tvm_auth('asd', '123')

    @patch_aiohttp_session('http://blackbox.yandex-team.ru/blackbox/', 'GET')
    def _dummy_passport(method, url, *args, **kwargs):
        assert 'yandex-team.ru' in url
        return response_mock(
            text=json.dumps(
                {'users': [{'uid': {'value': '123'}, 'login': 'support_1'}]},
            ),
        )

    await cbox.post('/v1/user/check_data_access', data=data, headers=headers)
    assert cbox.status == expected_status


@pytest.mark.config(
    TVM_ENABLED=True, CHATTERBOX_AUTH_WITHOUT_USER_TICKET=['asd'],
)
@pytest.mark.parametrize(
    'data, expected_status, expected_access_status',
    [
        ({'chatterbox_id': '5cf94043629526419e77b82e'}, 200, 'permitted'),
        (
            {
                'chatterbox_id': '5cf94043629526419e77b82e',
                'meta_info': {'park_db_id': '123'},
            },
            200,
            'forbidden',
        ),
    ],
)
async def test_data_access_check_without_user_ticket(
        cbox,
        patch_aiohttp_session,
        response_mock,
        data,
        expected_status,
        expected_access_status,
        mock_personal,
        patch_tvm_auth,
):
    patch_tvm_auth('asd', '123')

    @patch_aiohttp_session('http://blackbox.yandex-team.ru/blackbox/', 'GET')
    def _dummy_passport(method, url, *args, **kwargs):
        assert 'yandex-team.ru' in url
        return response_mock(
            text=json.dumps(
                {'users': [{'uid': {'value': '123'}, 'login': 'support_1'}]},
            ),
        )

    await cbox.post(
        '/v1/user/check_data_access',
        data=data,
        headers={
            'X-Real-IP': '123',
            'X-Yandex-UID': '123',
            'X-Ya-User-Ticket': '123',
            'X-Ya-Service-Ticket': '123',
        },
    )
    assert cbox.status == expected_status
    assert cbox.body_data == {'access_status': expected_access_status}

    assert _dummy_passport.calls
