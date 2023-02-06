# flake8: noqa
# pylint: disable=import-error,wildcard-import
import psycopg2
import pytest


@pytest.mark.parametrize(
    'partner_id,params,expected_code_response,expected_logins_response',
    [
        (
            1,
            {},
            200,
            [
                {'login': 'test1@yandex.ru', 'partner_id': '1'},
                {'login': 'test2@yandex.ru', 'partner_id': '2'},
            ],
        ),
        (
            1,
            {'place_ids': ['111']},
            200,
            [{'login': 'test1@yandex.ru', 'partner_id': '1'}],
        ),
        (
            1,
            {'place_ids': ['222']},
            200,
            [
                {'login': 'test1@yandex.ru', 'partner_id': '1'},
                {'login': 'test2@yandex.ru', 'partner_id': '2'},
            ],
        ),
        (
            2,
            {},
            200,
            [
                {'login': 'test2@yandex.ru', 'partner_id': '2'},
                {'login': 'test3@yandex.ru', 'partner_id': '3'},
            ],
        ),
        # no place_id
        (2, {'place_ids': ['444']}, 200, []),
        # no partner_id
        (4, {}, 200, []),
    ],
)
async def test_partner_login_list(
        taxi_eats_restapp_support_chat,
        partner_id,
        params,
        expected_code_response,
        expected_logins_response,
):
    response = await taxi_eats_restapp_support_chat.get(
        '/4.0/restapp-front/support_chat/v1/partner/login/list',
        headers={'X-YaEda-PartnerId': str(partner_id)},
        params=params,
    )
    assert response.status == expected_code_response

    logins = response.json()['logins']
    assert len(logins) == len(expected_logins_response)

    logins.sort(key=lambda x: x['login'])
    expected_logins_response.sort(key=lambda x: x['login'])
    for login, expected_login in zip(logins, expected_logins_response):
        assert login['login'] == expected_login['login']
        assert login['partner_id'] == expected_login['partner_id']
