import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from cargo_sf_plugins import *  # noqa: F403 F401

from tests_cargo_sf import const

OAUTH_RESPONSE = {
    'access_token': 'token_from_sf',
    'instance_url': (
        'https://yandexdelivery--testing.sandbox.my.salesforce.com'
    ),
    'id': (
        'https://test.salesforce.com/id/00D1j0000008hfNEAQ/00509000009P3YoAAK'
    ),
    'token_type': 'Bearer',
    'issued_at': '1643151066030',
    'signature': 'XXXXXXXXX',
}

AMO_OAUTH_REQUEST = {
    'client_id': 'client_id',
    'client_secret': 'client_secret',
    'grant_type': 'authorization_code',
    'redirect_uri': 'http://cargo-sf.taxi.tst.yandex.net/api/v1/amocrm/auth',
    'code': 'auth_code_from_amo',
}

AMO_REFRESH_REQUEST = {
    'client_id': 'client_id',
    'client_secret': 'client_secret',
    'grant_type': 'refresh_token',
    'redirect_uri': 'http://cargo-sf.taxi.yandex.net/api/v1/amocrm/auth',
    'refresh_token': 'refresh_token_from_amo',
}

AMO_OAUTH_RESPONSE = {
    'token_type': 'Bearer',
    'expires_in': 86400,
    'access_token': 'new_access_token_from_amo',
    'refresh_token': 'new_refresh_token_from_amo',
}

AMO_OAUTH_BAD_RESPONSE = {
    'hint': 'Authorization code has expired',
    'title': 'Некорректный запрос',
    'type': 'https://developers.amocrm.ru/v3/errors/OAuthProblemJson',
    'status': 401,
    'detail': 'В запросе отсутствует ряд параметров или параметры невалидны',
}

AMO_GOOD_COMPLEX_RESPONSE = [
    {
        'id': 15198335,
        'contact_id': 19663157,
        'company_id': 19663155,
        'request_id': ['qweasd'],
        'merged': False,
    },
]

AMO_BAD_COMPLEX_RESPONSE = {
    'validation-errors': [
        {
            'request_id': 'qweasd',
            'errors': [
                {
                    'code': 'InvalidType',
                    'path': '_embedded.contacts.0.responsible_user_id',
                    'detail': 'This value should be of type int.',
                },
                {
                    'code': 'NotSupportedChoice',
                    'path': '_embedded.contacts.0.responsible_user_id',
                    'detail': 'The value you selected is not a valid choice.',
                },
            ],
        },
    ],
    'title': 'Bad Request',
    'type': 'https://httpstatus.es/400',
    'status': 400,
    'detail': 'Request validation failed',
}


@pytest.fixture(name='create_auth_token_record', autouse=True)
def _create_auth_token_record(pgsql):
    cursor = pgsql['cargo_sf'].conn.cursor()

    cursor.execute(
        f"""
        INSERT INTO
            cargo_sf.salesforce_auth_token (
                id, auth_token, updated_at
            ) VALUES
            (1,
            'dbZz5B2NcPBPzyAquzaoDtN6/m03mTe3qX3jexRbviC0EY62gI+OgHAc9xC4S/iO',
            '{const.TOKEN_JUST_UPDATED_TIME}');
    """,
    )

    cursor.close()


@pytest.fixture(name='mock_auth')
def _mock_auth(mockserver):
    @mockserver.json_handler('external_salesforce/services/oauth2/token')
    def mock(request):
        assert (
            request.headers['Content-Type']
            == 'application/x-www-form-urlencoded'
        )
        assert request.form == {
            'grant_type': 'password',
            'client_id': 'client_id',
            'client_secret': 'consumer_secret',
            'username': 'username',
            'password': 'passwordpersonal_token',
        }
        return mockserver.make_response(status=200, json=OAUTH_RESPONSE)

    return mock


@pytest.fixture(name='create_amo_auth_token_record', autouse=True)
def _create_amo_auth_token_record(pgsql):
    cursor = pgsql['cargo_sf'].conn.cursor()

    cursor.execute(
        f"""
        INSERT INTO cargo_sf.amo_auth_token (
            id, access_token, refresh_token
        ) VALUES (
            1,
            'Rj44tvOZQtKDqQCinnTSFAiK3C9M3x6tXKoeBAV61swbZHwmEmTFtBT/C0nlXX+e',
            'uRyPZSAX1f5vT5kHrOb2zSSYAe9uuojAlaT3wjFi93LUDjJdZSqCW4f6mbzWeq3w'
        );
    """,
    )

    cursor.close()


@pytest.fixture(name='update_bad_amo_auth_token_record')
def _update_bad_amo_auth_token_record(pgsql):
    cursor = pgsql['cargo_sf'].conn.cursor()

    cursor.execute(
        f"""
        UPDATE cargo_sf.amo_auth_token
        SET access_token = 'tl5KavqOvHWdCW6ZxTvt4dBCKutH'
        'Eyk5GQlNU4XohNbqvgP4Q8VeowfN+6sS589j',
        refresh_token = 'uRyPZSAX1f5vT5kHrOb2zSSYAe9uuojA'
        'laT3wjFi93LUDjJdZSqCW4f6mbzWeq3w'
        WHERE id = 1;
    """,
    )

    cursor.close()


@pytest.fixture(name='mock_amo_auth')
def _mock_amo_auth(mockserver):
    @mockserver.json_handler('/amocrm-cargo/oauth2/access_token')
    def mock(request):
        if request.json == AMO_OAUTH_REQUEST:
            return mockserver.make_response(
                status=200, json=AMO_OAUTH_RESPONSE,
            )
        if request.json == AMO_REFRESH_REQUEST:
            return mockserver.make_response(
                status=200, json=AMO_OAUTH_RESPONSE,
            )
        return mockserver.make_response(
            status=400, json=AMO_OAUTH_BAD_RESPONSE,
        )

    return mock


@pytest.fixture(name='mock_amo_users')
def _mock_amo_users(mockserver, load_json):
    @mockserver.json_handler('/amocrm-cargo/api/v4/users')
    def mock(request):
        return mockserver.make_response(
            status=200,
            json=load_json(
                f'amo_user_list_response_page{request.query["page"]}.json',
            ),
        )

    return mock


@pytest.fixture(name='mock_amo_leads')
def _mock_amo_leads(mockserver, load_json):
    @mockserver.json_handler('/amocrm-cargo/api/v4/leads')
    def mock(request):
        if request.method == 'GET':
            if (
                    request.query_string
                    == b'limit=250&with=contacts&query=external_event_id204'
            ):
                return mockserver.make_response(status=204, json={})

            if (
                    request.headers['Authorization']
                    == 'Bearer bad_access_token_from_amo'
            ):
                return mockserver.make_response(
                    status=401, json=AMO_OAUTH_BAD_RESPONSE,
                )
        return mockserver.make_response(
            status=200, json=load_json('amo_lead_list_response.json'),
        )

    return mock


@pytest.fixture(name='mock_amo_companies')
def _mock_amo_companies(mockserver, load_json):
    @mockserver.json_handler('/amocrm-cargo/api/v4/companies')
    def mock(request):
        return mockserver.make_response(
            status=200, json=load_json('amo_company_list_response.json'),
        )

    return mock


@pytest.fixture(name='mock_amo_contacts')
def _mock_amo_contacts(mockserver, load_json):
    @mockserver.json_handler('/amocrm-cargo/api/v4/contacts')
    def mock(request):
        return mockserver.make_response(
            status=200, json=load_json('amo_contact_list_response.json'),
        )

    return mock


@pytest.fixture(name='mock_amo_lead_link')
def _mock_amo_lead_link(mockserver, load_json):
    @mockserver.json_handler('/amocrm-cargo/api/v4/leads/link')
    def mock(request):
        return mockserver.make_response(
            status=200,
            json={
                '_links': {'self': {'href': ''}},
                '_embedded': {
                    'links': [
                        {
                            'entity_id': 2809483,
                            'entity_type': 'leads',
                            'to_entity_id': 3997525,
                            'to_entity_type': 'contacts',
                            'metadata': None,
                        },
                        {
                            'entity_id': 2809483,
                            'entity_type': 'leads',
                            'to_entity_id': 3997523,
                            'to_entity_type': 'companies',
                            'metadata': None,
                        },
                    ],
                },
            },
        )

    return mock


@pytest.fixture(name='mock_amo_create_task')
def _mock_amo_create_task(mockserver, load_json):
    @mockserver.json_handler('/amocrm-cargo/api/v4/tasks')
    def mock(request):
        if request.json[0]['text'] == 'some_invalid_data':
            return mockserver.make_response(
                status=400, json=AMO_OAUTH_BAD_RESPONSE,
            )
        return mockserver.make_response(
            status=200,
            json={
                '_links': {'self': {'href': 'https://'}},
                '_embedded': {
                    'tasks': [
                        {
                            'id': 295869,
                            'request_id': '0',
                            '_links': {'self': {'href': 'https://'}},
                        },
                    ],
                },
            },
        )

    return mock


@pytest.fixture(name='mock_amo_create_note')
def _mock_amo_create_note(mockserver, load_json):
    @mockserver.json_handler('/amocrm-cargo/api/v4/leads/notes')
    def mock(request):
        if request.json[0]['entity_id'] == 9001:
            # mock some data error
            return mockserver.make_response(
                status=400, json=AMO_OAUTH_BAD_RESPONSE,
            )
        return mockserver.make_response(status=200, json={'_embedded': {}})

    return mock


@pytest.fixture(name='mock_startrek')
def _mock_startrek(mockserver, load_json):
    @mockserver.json_handler('/startrek/v2/issues')
    def mock(request):
        return mockserver.make_response(
            status=201, json={'id': 'id', 'self': 'self', 'key': 'key'},
        )

    return mock


@pytest.fixture(name='mock_cargo_crm')
def _mock_cargo_crm(mockserver, load_json):
    @mockserver.json_handler(
        '/cargo-crm/internal/cargo-crm/flow/manager/ticket/init',
    )
    def mock(request):
        return mockserver.make_response(
            status=request.json['status'], json=request.json['json'],
        )

    return mock


@pytest.fixture(name='mock_amo_create_lead_note')
def _mock_amo_create_lead_note(mockserver, load_json):
    @mockserver.json_handler('/amocrm-cargo/api/v4/leads/notes')
    def mock(request):
        return mockserver.make_response(
            status=200,
            json={
                '_links': {'self': {'href': 'https://'}},
                '_embedded': {'notes': [{'id': 295869}]},
            },
        )

    return mock


@pytest.fixture(name='mock_amo_complex')
def _mock_amo_complex(mockserver):
    @mockserver.json_handler('/amocrm-cargo/api/v4/leads/complex')
    def mock(request):
        if request.json == [{}]:
            return mockserver.make_response(
                status=400, json=AMO_BAD_COMPLEX_RESPONSE,
            )
        return mockserver.make_response(
            status=200, json=AMO_GOOD_COMPLEX_RESPONSE,
        )

    return mock
