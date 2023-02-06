import re

import pytest

from taxi.clients import passport
from taxi.clients import passport_internal


@pytest.mark.parametrize(
    'company_name, login',
    [
        ('ООО Петрушка', 'corp-petrushka'),
        ('LTD Petrushka 77', 'corp-petrushka77'),
        ('ООО ооо ltd LTD', 'corp-oooltd'),
        ('ООО АСД', 'corp-asd'),
        (
            'ЗАО Эти прекрасные и сказочные булочки',
            'corp-etiprekrasnyeiskazoc',
        ),
        ('ООО 2е Петрушки', 'corp-2epetrushki'),
        ('ООО 43', 'corp-43'),
        ('ООО Underscore_company', 'corp-underscorecompany'),
    ],
)
async def test_suggest_login(
        taxi_corp_admin_client, company_name, login, patch,
):
    @patch('taxi.clients.passport.PassportClient.get_info_by_login')
    async def _get_info_by_login(*args, **kwargs):
        raise passport.InvalidLoginError()

    post = {'company_name': company_name}

    response = await taxi_corp_admin_client.post(
        '/v1/suggest/login', json=post,
    )
    data = await response.json()

    assert response.status == 200
    assert len(data['login']) <= 30
    assert data['login'][-5:].isdigit()
    assert data['login'][:-5] == login

    calls = _get_info_by_login.calls
    assert len(calls) == 1
    assert calls[0]['args'] == ()
    assert calls[0]['kwargs']['login'] == data['login']


async def test_suggest_login_not_found(taxi_corp_admin_client, patch):
    @patch('taxi.clients.passport.PassportClient.get_info_by_login')
    async def _get_info_by_login(*args, **kwargs):
        return {'uid': '12345'}

    response = await taxi_corp_admin_client.post(
        '/v1/suggest/login', json={'company_name': 'Petrushka'},
    )
    resp_data = await response.json()

    assert response.status == 500
    assert resp_data == {
        'details': {},
        'message': 'suggest login error',
        'status': 'error',
        'code': 'suggest login error',
    }


async def test_suggest_login_error(taxi_corp_admin_client, patch):
    @patch('taxi.clients.passport.PassportClient.get_info_by_login')
    async def _get_info_by_login(*args, **kwargs):
        raise passport.PassportError()

    response = await taxi_corp_admin_client.post(
        '/v1/suggest/login', json={'company_name': 'Petrushka'},
    )
    assert response.status == 500


async def test_register(taxi_corp_admin_client, patch):
    @patch('taxi.clients.passport_internal.PassportClient.register')
    async def _register(*args, **kwargs):
        return {'status': 'ok', 'uid': '12345'}

    login = 'petrushka12345'

    response = await taxi_corp_admin_client.post(
        '/v1/register',
        json={'login': login},
        headers={'X-Yandex-Uid': '1120000000092474'},
    )
    resp_data = await response.json()

    assert response.status == 200
    assert list(resp_data.keys()) == ['login', 'password']
    assert login == resp_data['login']
    assert re.match(r'^\w{8}$', resp_data['password'])

    calls = _register.calls
    assert len(calls) == 1
    assert calls[0]['args'] == ()
    assert calls[0]['kwargs']['login'] == resp_data['login']
    assert calls[0]['kwargs']['password'] == resp_data['password']


async def test_register_error(taxi_corp_admin_client, patch):
    @patch('taxi.clients.passport_internal.PassportClient.register')
    async def _register(*args, **kwargs):
        raise passport_internal.PassportError(errors=['login.notavailable'])

    response = await taxi_corp_admin_client.post(
        '/v1/register',
        json={'login': 'login'},
        headers={'X-Yandex-Uid': '1120000000092474'},
    )
    resp_data = await response.json()

    assert response.status == 400
    assert resp_data == {
        'details': {},
        'status': 'error',
        'message': 'passport errors: [\'login.notavailable\']',
        'code': 'passport errors',
    }
