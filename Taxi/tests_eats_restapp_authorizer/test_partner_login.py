# flake8: noqa
import pytest


PAYLOAD_RESPONSE_PARTNERS_INFO = {
    'id': 1,
    'name': 'test',
    'email': 'test1@yandex.ru',
    'is_blocked': False,
    'places': [111, 222],
    'is_fast_food': False,
    'country_code': '0',
    'roles': [
        {'id': 1, 'title': 'Оператор', 'slug': 'ROLE_OPERATOR'},
        {'id': 2, 'title': 'Управляющий', 'slug': 'ROLE_MANAGER'},
    ],
    'partner_id': '1',
    'timezone': 'UTC',
}


@pytest.mark.pgsql('eats_restapp_authorizer', files=('data_creds.sql',))
@pytest.mark.parametrize(
    'login, password, locale, partner_id, response_code, error_message, partners_code, partners_response',
    [
        pytest.param(
            'qwerty',
            'password_1',
            None,
            None,
            400,
            'Неверный логин или пароль',
            404,
            {},
            id='Login incorrect',
        ),
        pytest.param(
            'nananuna',
            'password_2',
            None,
            None,
            400,
            'Неверный логин или пароль',
            404,
            {},
            id='password incorrect',
        ),
        pytest.param(
            'nananuna',
            'password_1',
            None,
            None,
            400,
            'Неверный логин или пароль',
            400,
            {},
            id='partner is block',
        ),
        pytest.param(
            'nananuna',
            'password_1',
            None,
            1,
            200,
            None,
            200,
            {'payload': PAYLOAD_RESPONSE_PARTNERS_INFO},
            id='partner is ok',
        ),
        pytest.param(
            'nananuna_5',
            'password_5',
            None,
            50,
            200,
            None,
            200,
            {'payload': PAYLOAD_RESPONSE_PARTNERS_INFO},
            id='partner is ok_2',
        ),
        pytest.param(
            'qwerty',
            'password_1',
            'ru',
            None,
            400,
            'Неверный логин или пароль',
            404,
            {},
            id='Login incorrect, ru locale',
        ),
        pytest.param(
            'qwerty',
            'password_1',
            'en',
            None,
            400,
            'Incorrect login or password',
            404,
            {},
            id='Login incorrect, en locale',
        ),
    ],
)
async def test_login_partner(
        taxi_eats_restapp_authorizer,
        mockserver,
        login,
        password,
        locale,
        partner_id,
        response_code,
        error_message,
        partners_code,
        partners_response,
):
    @mockserver.json_handler('/eats-partners/internal/partners/v1/info')
    def _mock_partners(request):
        return mockserver.make_response(
            status=partners_code, json=partners_response,
        )

    headers = {'X-Eats-Restapp-Auth-Creds': password}
    if locale:
        headers['X-YaEda-Partner-Locale'] = locale
    response = await taxi_eats_restapp_authorizer.post(
        '/4.0/restapp-front/authorizer/v1/login',
        json={'login': login},
        headers=headers,
    )
    assert response.status_code == response_code
    if not error_message is None:
        assert response.json()['message'] == error_message
    if response_code == 200:
        token = response.headers['X-Eats-Restapp-Token']
        ex_id = response.headers['X-YaEda-PartnerId']
        assert token is not None
        assert len(token) > 5
        assert ex_id == str(partner_id)
