import pytest

from taxi_corp.clients import taxi_corp_announcements

ANNOUNCEMENT_ID = 'qwerty'
ANNOUNCEMENT_DICT = {
    'announcement_id': ANNOUNCEMENT_ID,
    'announcement_type': 'news',
    'title': 'title',
    'text': 'text',
    'status': 'not_read',
}

TEST_CORP_ANNOUNCEMENTS_PARAMS = dict(
    argnames=['passport_mock', 'expected_uid'],
    argvalues=[
        pytest.param('client1', 'client1_uid', id='test_client'),
        pytest.param('manager1', 'manager1_uid', id='test_admin'),
        pytest.param('dep_manager1', 'dep_manager1_uid', id='test_manager'),
        pytest.param('secretary1', 'secretary1_uid', id='test_secretary'),
    ],
)


@pytest.mark.parametrize(
    **TEST_CORP_ANNOUNCEMENTS_PARAMS, indirect=['passport_mock'],
)
async def test_announcements_list(
        taxi_corp_real_auth_client, passport_mock, expected_uid, patch,
):
    @patch('taxi.clients.passport.get_passport_info')
    async def _get_passport_info(*args):
        return {'uid': expected_uid, 'login': expected_uid, 'is_staff': False}

    @patch(
        'taxi_corp.clients.taxi_corp_announcements.'
        'CorpAnnouncementsClient.get_announcements_list',
    )
    async def _response(client_id, yandex_uid, **kwargs):
        assert client_id == 'client1'
        assert yandex_uid == expected_uid
        return {'announcements': [ANNOUNCEMENT_DICT]}

    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/client1/announcements',
    )

    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {'announcements': [ANNOUNCEMENT_DICT]}


@pytest.mark.parametrize(
    **TEST_CORP_ANNOUNCEMENTS_PARAMS, indirect=['passport_mock'],
)
async def test_promos_list(
        taxi_corp_real_auth_client, passport_mock, expected_uid, patch,
):
    @patch('taxi.clients.passport.get_passport_info')
    async def _get_passport_info(*args):
        return {'uid': expected_uid, 'login': expected_uid, 'is_staff': False}

    @patch(
        'taxi_corp.clients.taxi_corp_announcements.'
        'CorpAnnouncementsClient.get_promos_list',
    )
    async def _response(client_id, yandex_uid, **kwargs):
        assert client_id == 'client1'
        assert yandex_uid == expected_uid
        return {'announcements': [ANNOUNCEMENT_DICT]}

    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/client1/announcements/promos',
    )

    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {'announcements': [ANNOUNCEMENT_DICT]}


@pytest.mark.parametrize(
    **TEST_CORP_ANNOUNCEMENTS_PARAMS, indirect=['passport_mock'],
)
async def test_announcement(
        taxi_corp_real_auth_client, passport_mock, expected_uid, patch,
):
    @patch('taxi.clients.passport.get_passport_info')
    async def _get_passport_info(*args):
        return {'uid': expected_uid, 'login': expected_uid, 'is_staff': False}

    @patch(
        'taxi_corp.clients.taxi_corp_announcements.'
        'CorpAnnouncementsClient.get_announcement',
    )
    async def _response(client_id, yandex_uid, announcement_id, **kwargs):
        assert client_id == 'client1'
        assert yandex_uid == expected_uid
        assert announcement_id == ANNOUNCEMENT_ID
        return ANNOUNCEMENT_DICT

    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/client1/announcement',
        params={'announcement_id': ANNOUNCEMENT_ID},
    )

    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == ANNOUNCEMENT_DICT


@pytest.mark.parametrize(
    **TEST_CORP_ANNOUNCEMENTS_PARAMS, indirect=['passport_mock'],
)
async def test_announcement_mark_read(
        taxi_corp_real_auth_client, passport_mock, expected_uid, patch,
):
    @patch('taxi.clients.passport.get_passport_info')
    async def _get_passport_info(*args):
        return {'uid': expected_uid, 'login': expected_uid, 'is_staff': False}

    @patch(
        'taxi_corp.clients.taxi_corp_announcements.'
        'CorpAnnouncementsClient.announcement_mark_read',
    )
    async def _response(client_id, yandex_uid, announcement_id, **kwargs):
        assert client_id == 'client1'
        assert yandex_uid == expected_uid
        assert announcement_id == ANNOUNCEMENT_ID
        return {}

    response = await taxi_corp_real_auth_client.post(
        '/1.0/client/client1/announcement/read',
        json={'announcement_id': ANNOUNCEMENT_ID},
    )

    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {}


@pytest.mark.parametrize(
    **TEST_CORP_ANNOUNCEMENTS_PARAMS, indirect=['passport_mock'],
)
async def test_announcement_cta_mark_clicked(
        taxi_corp_real_auth_client, passport_mock, expected_uid, patch,
):
    @patch('taxi.clients.passport.get_passport_info')
    async def _get_passport_info(*args):
        return {'uid': expected_uid, 'login': expected_uid, 'is_staff': False}

    @patch(
        'taxi_corp.clients.taxi_corp_announcements.'
        'CorpAnnouncementsClient.announcement_cta_mark_clicked',
    )
    async def _response(client_id, yandex_uid, announcement_id, **kwargs):
        assert client_id == 'client1'
        assert yandex_uid == expected_uid
        assert announcement_id == ANNOUNCEMENT_ID
        return {}

    response = await taxi_corp_real_auth_client.post(
        '/1.0/client/client1/announcement/cta_mark_clicked',
        json={'announcement_id': ANNOUNCEMENT_ID},
    )

    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {}


@pytest.mark.parametrize(
    ['passport_mock', 'json', 'service_response', 'error_code', 'error'],
    [
        pytest.param(
            'client1',
            {},
            {},
            400,
            {
                'errors': [
                    {
                        'text': '\'announcement_id\' is a required property',
                        'code': 'GENERAL',
                    },
                ],
                'message': 'Invalid input',
                'code': 'REQUEST_VALIDATION_ERROR',
                'details': {
                    'fields': [
                        {
                            'message': (
                                '\'announcement_id\' is a required property'
                            ),
                            'code': 'REQUEST_VALIDATION_ERROR',
                            'path': [],
                        },
                    ],
                },
            },
            id='no_announcement_id',
        ),
        pytest.param(
            'client1',
            {'announcement_id': '12345'},
            None,
            500,
            {
                'code': 'CORP_ANNOUNCEMENTS',
                'errors': [
                    {
                        'code': 'CORP_ANNOUNCEMENTS',
                        'text': 'error.corp_announcements_unexpected_error',
                    },
                ],
                'message': 'error.corp_announcements_unexpected_error',
            },
            id='unexpected_error',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_announcement_fail(
        taxi_corp_real_auth_client,
        patch,
        passport_mock,
        json,
        service_response,
        error_code,
        error,
):
    @patch('taxi.clients.passport.get_passport_info')
    async def _get_passport_info(*args):
        return {'uid': 'client1_uid', 'login': 'login', 'is_staff': False}

    @patch(
        'taxi_corp.clients.taxi_corp_announcements.'
        'CorpAnnouncementsClient._request',
    )
    async def _response(*args, **kwargs):
        if service_response is not None:
            return service_response
        raise taxi_corp_announcements.ClientError()

    response = await taxi_corp_real_auth_client.post(
        '/1.0/client/client1/announcement/read', json=json,
    )

    response_json = await response.json()
    assert response.status == error_code, response_json
    assert response_json == error
