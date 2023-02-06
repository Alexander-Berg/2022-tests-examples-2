import pytest


async def test_no_parameters(web_app_client, load_json, personal_mock):
    response = await web_app_client.get('/v1/clients/list')
    assert response.status == 200
    response_json = await response.json()
    expected_clients = load_json('expected_clients.json')
    assert response_json == {
        'clients': [client for client in expected_clients.values()],
        'skip': 0,
        'limit': 50,
        'amount': 7,
        'sort_field': 'name',
        'sort_direction': 1,
    }


async def test_with_parameters(web_app_client, load_json, personal_mock):
    response = await web_app_client.get(
        '/v1/clients/list',
        params={
            'skip': 1,
            'limit': 2,
            'sort_field': 'email',
            'sort_direction': -1,
        },
    )
    assert response.status == 200
    response_json = await response.json()
    expected_clients = load_json('expected_clients.json')
    assert response_json == {
        'clients': [
            expected_clients['client_id_7'],
            expected_clients['client_id_6'],
        ],
        'skip': 1,
        'limit': 2,
        'amount': 7,
        'sort_field': 'email',
        'sort_direction': -1,
    }


@pytest.mark.parametrize(
    'search, expected_client_id',
    [
        # fmt: off
        pytest.param(
            'client_id_1',
            'client_id_1',
            id='search by id',
        ),
        pytest.param(
            'corp_client_2',
            'client_id_2',
            id='search by name',
        ),
        pytest.param(
            'email@ya.ru',
            'client_id_1',
            id='search by email',
        ),
        pytest.param(
            '101/12',
            'client_id_1',
            id='search by contract',
        ),
        pytest.param(
            '100002',
            'client_id_2',
            id='search by billing_id',
        ),
        # fmt: on
    ],
)
async def test_search(
        web_app_client, load_json, personal_mock, search, expected_client_id,
):
    response = await web_app_client.get(
        '/v1/clients/list', params={'search': search},
    )
    assert response.status == 200
    response_json = await response.json()
    expected_clients = load_json('expected_clients.json')
    assert response_json == {
        'clients': [expected_clients[expected_client_id]],
        'skip': 0,
        'limit': 50,
        'amount': 1,
        'sort_field': 'name',
        'sort_direction': 1,
        'search': search,
    }


async def test_get_trial(web_app_client, load_json, personal_mock):
    response = await web_app_client.get(
        '/v1/clients/list', params={'is_trial': 'true'},
    )
    assert response.status == 200
    response_json = await response.json()
    expected_clients = load_json('expected_clients.json')
    assert response_json == {
        'clients': [expected_clients['client_id_2']],
        'skip': 0,
        'limit': 50,
        'amount': 1,
        'sort_field': 'name',
        'sort_direction': 1,
    }


async def test_get_non_trial(web_app_client, load_json, personal_mock):
    response = await web_app_client.get(
        '/v1/clients/list', params={'is_trial': 'false'},
    )
    assert response.status == 200
    response_json = await response.json()
    expected_clients = load_json('expected_clients.json')
    assert response_json == {
        'clients': [
            expected_clients['client_id_1'],
            expected_clients['client_id_3'],
            expected_clients['client_id_4'],
            expected_clients['client_id_5'],
            expected_clients['client_id_6'],
            expected_clients['client_id_7'],
        ],
        'skip': 0,
        'limit': 50,
        'amount': 6,
        'sort_field': 'name',
        'sort_direction': 1,
    }


async def test_empty_list(
        web_app_client, load_json, personal_mock, mockserver,
):
    @mockserver.json_handler('personal/v1/emails/find')
    def _find_email(request):
        return {'value': request.json['value'], 'id': 'invalid'}

    @mockserver.json_handler('personal/v1/yandex_logins/find')
    def _find_login(request):
        return {'value': request.json['value'], 'id': 'invalid'}

    search = 'client_name6'
    response = await web_app_client.get(
        '/v1/clients/list', params={'search': search},
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == {
        'clients': [],
        'skip': 0,
        'limit': 50,
        'amount': 0,
        'sort_field': 'name',
        'sort_direction': 1,
        'search': 'client_name6',
    }
