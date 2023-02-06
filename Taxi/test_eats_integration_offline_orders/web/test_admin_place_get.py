import http

import pytest

from test_eats_integration_offline_orders import conftest


@pytest.mark.parametrize(
    'params, expected_code, expected_response',
    (
        pytest.param(
            {'place_id': 'place_id__1'},
            http.HTTPStatus.OK,
            conftest.create_admin_place(
                id=1,
                slug='place_id__1_slug',
                name='Самый тестовый ресторан',
                logo_link=(
                    '$mockserver/mds_avatars/get-inplace/135516/'
                    '147734d81d1de576476c6a217679e1c29f83eeb7/orig'
                ),
                description=(
                    'Он настолько тестовый, что его можно только тестировать'
                ),
                tips_link='some_tips_link',
                pos_token_updated_at='2022-04-19 12:00:00',
                contacts=[conftest.ADMIN_PLACE_1_CONTACTS_1],
            ),
            id='ok-response',
        ),
        pytest.param(
            {'place_id': 'place_id__2'},
            http.HTTPStatus.OK,
            conftest.create_admin_place(
                id=2,
                slug='restaurant_slug_2',
                name='Ресторан "Мясо"',
                pos_token_updated_at='',
            ),
            id='ok-response-no-iiko',
        ),
        pytest.param(
            {'place_id': 'place_id__4'},
            http.HTTPStatus.OK,
            conftest.create_admin_place(
                id=4,
                slug='restaurant_slug_4',
                name='Кафе "У меня нет фантазии"',
                pos_type='rkeeper',
                enabled=True,
            ),
            id='ok-response-rkeeper',
        ),
        pytest.param(
            {'place_id': '100000'},
            http.HTTPStatus.NOT_FOUND,
            {'message': 'place not found', 'code': 'not_found'},
            id='not-found',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'pos_tokens.sql', 'restaurants_contacts.sql'],
)
@pytest.mark.now('2022-05-16T10:00:30+00:00')
async def test_admin_place_get(
        web_app_client, params, expected_code, expected_response,
):
    response = await web_app_client.get('/admin/v1/place', params=params)
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
