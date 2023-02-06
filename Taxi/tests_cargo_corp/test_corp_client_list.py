import pytest

from tests_cargo_corp import utils

PHONES = ['12345678910', utils.PHONE]
LOGINS = ['yandex_login2', utils.YANDEX_LOGIN]

LOCAL_CLIENT_ID = 'some_long_id_string_of_length_32'

LOCAL_CLIENT_NAME_1 = 'local client'
LOCAL_CLIENT_NAME_2 = 'another client'

LOCAL_CLIENT = {
    'id': LOCAL_CLIENT_ID,
    'name': LOCAL_CLIENT_NAME_1,
    'is_registration_finished': False,
}
LOCAL_CLIENT_WITH_EMPLOYEE = {
    'id': LOCAL_CLIENT_ID,
    'name': LOCAL_CLIENT_NAME_1,
    'is_registration_finished': False,
    'employee': {
        'phone_pd_id': PHONES[0] + '_id',
        'yandex_login_pd_id': LOGINS[0] + '_id',
    },
}
CORP_CLIENT = {
    'id': utils.CORP_CLIENT_ID,
    'name': utils.CORP_CLIENT_NAME,
    'is_registration_finished': False,
}


@pytest.mark.parametrize(
    ['search_scope', 'search_string', 'search_phone', 'expected_json'],
    (
        pytest.param(
            None, None, None, {'corp_clients': []}, id='empty search',
        ),
        pytest.param(
            None, 'unknown_uid', None, {'corp_clients': []}, id='not found',
        ),
        pytest.param(
            None,
            utils.YANDEX_UID,
            None,
            {'corp_clients': [CORP_CLIENT, LOCAL_CLIENT]},
            id='search by yandex_uid',
        ),
        pytest.param(
            ['corp_client_id'],
            utils.YANDEX_UID,
            None,
            {'corp_clients': []},
            id='search by corp_id but write yandex_uid',
        ),
        pytest.param(
            None,
            utils.CORP_CLIENT_ID,
            None,
            {'corp_clients': [CORP_CLIENT]},
            id='search by corp_id',
        ),
        pytest.param(
            ['yandex_uid'],
            utils.CORP_CLIENT_ID,
            None,
            {'corp_clients': []},
            id='search by yandex_uid but write corp_id',
        ),
        pytest.param(
            None,
            None,
            PHONES[0],
            {'corp_clients': [LOCAL_CLIENT]},
            id='search by phone',
        ),
        pytest.param(
            None,
            utils.CORP_CLIENT_ID,
            PHONES[0],
            {'corp_clients': []},
            id='search by corp_id and phone',
        ),
        pytest.param(
            None,
            utils.CORP_CLIENT_ID,
            utils.PHONE,
            {'corp_clients': [CORP_CLIENT]},
            id='search by corp_id and phone',
        ),
        pytest.param(
            None,
            utils.YANDEX_UID,
            PHONES[0],
            {'corp_clients': [LOCAL_CLIENT]},
            id='search by yandex_uid and phone',
        ),
        pytest.param(
            None,
            utils.YANDEX_UID,
            utils.PHONE,
            {'corp_clients': [CORP_CLIENT]},
            id='search by yandex_uid and phone',
        ),
        pytest.param(
            None,
            'LOCAL CLIENT',
            None,
            {'corp_clients': [LOCAL_CLIENT]},
            id='search by name',
        ),
        pytest.param(
            None,
            'LOCAL',
            None,
            {'corp_clients': [LOCAL_CLIENT]},
            id='search by name',
        ),
        pytest.param(
            None,
            'CLIENT',
            None,
            {'corp_clients': [CORP_CLIENT, LOCAL_CLIENT]},
            id='search by name',
        ),
        pytest.param(
            None,
            'cOrP_cLiEnT',
            None,
            {'corp_clients': [CORP_CLIENT]},
            id='search by name',
        ),
        pytest.param(
            None,
            LOGINS[0],
            None,
            {'corp_clients': [LOCAL_CLIENT]},
            id='search by login',
        ),
        pytest.param(
            None,
            LOGINS[1],
            None,
            {'corp_clients': [CORP_CLIENT]},
            id='search by login',
        ),
    ),
)
async def test_clients_list(
        taxi_cargo_corp,
        mockserver,
        user_has_rights,
        register_default_user,
        prepare_multiple_clients,
        search_scope,
        search_string,
        search_phone,
        expected_json,
):
    @mockserver.json_handler('/personal/v1/phones/find')
    def _phones_store(request):
        assert request.json.keys() == {'value', 'primary_replica'}
        phone = request.json['value']
        if phone in PHONES:
            return {'id': phone + '_id', 'value': phone}
        return mockserver.make_response(
            status=404,
            json={'code': '404', 'message': 'Doc not found in mongo'},
        )

    @mockserver.json_handler('/personal/v1/yandex_logins/find')
    def _yandex_logins_store(request):
        assert request.json.keys() == {'value', 'primary_replica'}
        login = request.json['value']
        if login in LOGINS:
            return {'id': login + '_id', 'value': login}
        return mockserver.make_response(
            status=404,
            json={'code': '404', 'message': 'Doc not found in mongo'},
        )

    prepare_multiple_clients([LOCAL_CLIENT_WITH_EMPLOYEE])

    request_json = {'filter': {'multisearch': {}}}
    if search_scope:
        request_json['filter']['multisearch']['search_scope'] = search_scope
    if search_string is not None:
        request_json['filter']['multisearch']['search_string'] = search_string
    if search_phone is not None:
        request_json['filter']['search_phone'] = search_phone

    response = await taxi_cargo_corp.post(
        '/internal/cargo-corp/v1/corp-client/list', json=request_json,
    )
    assert (
        sorted(
            response.json()['corp_clients'],
            key=lambda x: x.get('name', x['id']),
        )
        == expected_json['corp_clients']
    )


async def test_clients_list_changing_names(
        taxi_cargo_corp,
        pgsql,
        mockserver,
        user_has_rights,
        register_default_user,
        prepare_multiple_clients,
):
    @mockserver.json_handler('/personal/v1/yandex_logins/find')
    def _yandex_logins_store(request):
        assert request.json.keys() == {'value', 'primary_replica'}
        login = request.json['value']
        if login in LOGINS:
            return {'id': login + '_id', 'value': login}
        return mockserver.make_response(
            status=404,
            json={'code': '404', 'message': 'Doc not found in mongo'},
        )

    prepare_multiple_clients([LOCAL_CLIENT_WITH_EMPLOYEE])

    request_json = {'filter': {'multisearch': {'search_string': 'LOCAL'}}}
    response = await taxi_cargo_corp.post(
        '/internal/cargo-corp/v1/corp-client/list', json=request_json,
    )
    assert response.json()['corp_clients'] == [LOCAL_CLIENT]

    cursor = pgsql['cargo_corp'].conn.cursor()
    cursor.execute(
        'UPDATE corp_clients.clients '
        'SET name = \'{}\' '
        'WHERE name=\'{}\' '.format(LOCAL_CLIENT_NAME_2, LOCAL_CLIENT_NAME_1),
    )
    cursor.close()
    LOCAL_CLIENT['name'] = LOCAL_CLIENT_NAME_2

    response = await taxi_cargo_corp.post(
        '/internal/cargo-corp/v1/corp-client/list', json=request_json,
    )
    assert response.json()['corp_clients'] == []

    request_json = {'filter': {'multisearch': {'search_string': 'another'}}}

    response = await taxi_cargo_corp.post(
        '/internal/cargo-corp/v1/corp-client/list', json=request_json,
    )
    assert response.json()['corp_clients'] == [LOCAL_CLIENT]
