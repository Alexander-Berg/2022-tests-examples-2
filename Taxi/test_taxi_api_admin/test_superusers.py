import pytest


@pytest.mark.now('2020-06-10T20:00:00')
async def test_get_superusers(taxi_api_admin_client):
    response = await taxi_api_admin_client.post(
        '/v1/superusers/retrieve/', json={},
    )
    assert response.status == 200
    data = await response.json()
    assert data == {
        'users': [
            {'login': 'test_login_1', 'ticket': 'ticket-1'},
            {
                'login': 'test_login_2',
                'time_end': '2020-06-10T23:00:00+0300',
                'ticket': 'ticket-2',
            },
            {'login': 'superuser', 'ticket': 'ticket-4'},
        ],
    }


@pytest.mark.parametrize(
    'login, duration, code, expected, reason',
    [
        (
            'test_empty_reason',
            1,
            400,
            {
                'code': 'invalid-input',
                'details': {'': ['\'reason\' is a required property']},
                'message': 'Invalid input',
                'status': 'error',
            },
            None,
        ),
        (
            'test_login_1',
            1,
            200,
            {
                'login': 'test_login_1',
                'time_end': '2020-06-10T23:01:00+0300',
                'ticket': 'ticket-1',
                'reason': 'reason_login_1',
            },
            'reason_login_1',
        ),
        (
            'test_login_2',
            60,
            200,
            {
                'login': 'test_login_2',
                'time_end': '2020-06-11T00:00:00+0300',
                'ticket': 'ticket-2',
                'reason': 'reason_login_2',
            },
            'reason_login_2',
        ),
        (
            'test_login_3',
            60,
            200,
            {
                'login': 'test_login_3',
                'time_end': '2020-06-11T00:00:00+0300',
                'ticket': 'TAXISUPERUSER-100',
                'reason': 'reason_login_3',
            },
            'reason_login_3',
        ),
        (
            'not_found_user',
            12,
            404,
            {'details': 'not found user: not_found_user', 'code': 'NOT_FOUND'},
            'reason_non_existing_user',
        ),
    ],
)
@pytest.mark.now('2020-06-10T20:00:00')
async def test_set_superuser(
        taxi_api_admin_client, login, duration, code, expected, reason,
):
    data = {'login': login}
    if duration is not None:
        data['duration'] = duration
    if reason is not None:
        data['reason'] = reason
    response = await taxi_api_admin_client.post(
        '/v1/superusers/set/', json=data,
    )
    assert response.status == code
    content = await response.json()
    assert content == expected


@pytest.mark.parametrize(
    'login, code, expected, reason',
    [
        (
            'test_empty_reason',
            400,
            {
                'code': 'invalid-input',
                'details': {'': ['\'reason\' is a required property']},
                'message': 'Invalid input',
                'status': 'error',
            },
            None,
        ),
        (
            'test_login_1',
            200,
            {
                'login': 'test_login_1',
                'ticket': 'ticket-1',
                'time_end': '2020-06-10T23:00:00+0300',
            },
            'some reason',
        ),
        (
            'test_login_2',
            200,
            {
                'login': 'test_login_2',
                'time_end': '2020-06-10T23:00:00+0300',
                'ticket': 'ticket-2',
            },
            'whatever reason',
        ),
        (
            'not_found_user',
            404,
            {'code': 'NOT_FOUND', 'details': 'not found user: not_found_user'},
            'weird reason',
        ),
    ],
)
@pytest.mark.now('2020-06-10T20:00:00')
async def test_superusers_unset(
        taxi_api_admin_client, login, code, expected, reason, patch,
):
    @patch('taxi.clients.idm.IdmApiClient._request')
    async def _request(url, **kwargs):
        data = {}
        if 'api/v1/roles/' in url:
            data = {
                'errors': 1,
                'errors_ids': [
                    {
                        'id': 9220419,
                        'message': 'Роль находится в состоянии Отозвана',
                    },
                ],
                'successes': 1,
                'successes_ids': [{'id': 19062346}],
            }
        return data

    data = {'login': login}
    if reason is not None:
        data['reason'] = reason
    response = await taxi_api_admin_client.post(
        '/v1/superusers/unset/', json=data,
    )
    assert response.status == code
    content = await response.json()
    assert content == expected
    if code == 200:
        assert len(_request.calls) == 1
