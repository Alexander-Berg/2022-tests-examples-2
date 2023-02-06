import dataclasses

import pytest


PERSONAL_MAP = {'+71234567890': 'ab234cdea', '+71234567891': 'ab234cdeb'}

USER_API_MAP = {'ab234cdea': 'bcd120', 'ab234cdeb': 'bcd121'}

HEADERS = {'Accept-Language': 'ru', 'MessageUniqueId': '12345abcd'}
URL = '/vtb/v1/user/register'


@dataclasses.dataclass
class User:
    maas_user_id: str
    phone_id: str
    personal_phone_id: str
    access_key_hash: str


@pytest.fixture(name='personal')
def _mock_personal(mockserver):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _phone_store(request):
        assert request.json['validate']

        phone = request.json['value']

        if phone == '+7invalid890':
            return mockserver.make_response(
                json={
                    'code': 'phone_format_error',
                    'message': 'Phone format error',
                },
                status=400,
            )

        assert phone in PERSONAL_MAP
        personal_id = PERSONAL_MAP[phone]

        return mockserver.make_response(
            json={'id': personal_id, 'value': phone},
        )


@pytest.fixture(name='user_api')
def _mock_user_api(mockserver, load_json):
    @mockserver.json_handler('/user-api/user_phones')
    def _user_phones(request):
        personal_id = request.json['personal_phone_id']
        assert personal_id in USER_API_MAP
        assert request.json['type'] == 'yandex'
        phone_id = USER_API_MAP[personal_id]
        response_body = load_json('user_phones_response.json')
        response_body['id'] = phone_id
        return mockserver.make_response(json=response_body)


def get_user_from_db(pgsql, maas_user_id: str) -> User:
    cursor = pgsql['maas'].cursor()
    cursor.execute(
        f'SELECT * FROM maas.users WHERE maas_user_id = \'{maas_user_id}\';',
    )
    row = cursor.fetchone()
    return User(
        maas_user_id=row[0],
        phone_id=row[1],
        personal_phone_id=row[2],
        access_key_hash=row[3],
    )


@pytest.mark.parametrize(
    (),
    (
        pytest.param(id='Create new user'),
        pytest.param(
            id='User already exists',
            marks=pytest.mark.pgsql('maas', files=['users.sql']),
        ),
    ),
)
async def test_success(taxi_maas, personal, user_api, pgsql):
    maas_user_id = 'abcd-abcd-0'
    request_body = {
        'phone': '71234567890',
        'maas_user_id': maas_user_id,
        'hash_key': 'dba1-abda',
    }
    response = await taxi_maas.post(URL, headers=HEADERS, json=request_body)
    assert response.status == 200
    assert response.json() == {}
    user = get_user_from_db(pgsql, maas_user_id)
    assert user.maas_user_id == maas_user_id
    assert user.phone_id == 'bcd120'
    assert user.personal_phone_id == 'ab234cdea'
    assert user.access_key_hash == 'dba1-abda'


@pytest.mark.pgsql('maas', files=['users.sql'])
@pytest.mark.parametrize(
    ('phone', 'maas_user_id'),
    (
        pytest.param('81234567890', 'abcd-abcd-0', id='Wrong phone format'),
        pytest.param('7invalid890', 'abcd-abcd-0', id='Wrong phone format'),
        pytest.param(
            '71234567890', 'abcd-abcd-1', id='Inconsistent maas_user_id',
        ),
        pytest.param('71234567891', 'abcd-abcd-0', id='Inconsistent phone'),
    ),
)
async def test_problem(
        taxi_maas, personal, user_api, phone: str, maas_user_id: str,
):
    request_body = {'phone': phone, 'maas_user_id': maas_user_id}
    response = await taxi_maas.post(URL, headers=HEADERS, json=request_body)
    assert response.status == 422
    response_body = response.json()
    if phone in ('81234567890', '7invalid890'):
        assert response_body['errorCode'] == '10'
    elif phone == '71234567890':
        assert response_body['errorCode'] == '39'
    elif phone == '71234567891':
        assert response_body['errorCode'] == '32'
