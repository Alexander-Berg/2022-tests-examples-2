import http

import pytest

from test_eats_integration_offline_orders import conftest


PLACE_1 = conftest.create_admin_place(
    id=1,
    slug='restaurant_slug_1',
    name='Ресторан "Рыба"',
    description='',
    logo_link='',
    pos_type='iiko',
    tips_link='',
    enabled=True,
    pos_token_updated_at='2022-04-19 12:00:00',
    contacts=[conftest.ADMIN_PLACE_1_CONTACTS_1],
    mark_status='error',
)
PLACE_2 = conftest.create_admin_place(
    id=2,
    slug='restaurant_slug_2',
    name='Ресторан "Мясо"',
    description='',
    logo_link='',
    pos_type='rkeeper',
    tips_link='',
    enabled=True,
)
PLACE_3 = conftest.create_admin_place(
    id=3,
    place_id='amazing_place_id',
    slug='amazing_slug',
    name='Ресторан "Ни рыба ни мясо"',
    description='',
    logo_link='',
    pos_type='iiko',
    tips_link='',
    enabled=True,
    pos_token_updated_at='',
)


def _format_place_list_response(*, places, has_more=False):
    return {'places': places, 'has_more': has_more}


@pytest.mark.parametrize(
    'params, expected_code, expected_response',
    (
        pytest.param(
            {},
            http.HTTPStatus.OK,
            _format_place_list_response(places=[PLACE_3, PLACE_1, PLACE_2]),
            id='ok-no-params',
        ),
        pytest.param(
            {'limit': 1},
            http.HTTPStatus.OK,
            _format_place_list_response(places=[PLACE_3], has_more=True),
            id='limit-1-offset-0',
        ),
        pytest.param(
            {'limit': 1, 'offset': 1},
            http.HTTPStatus.OK,
            _format_place_list_response(places=[PLACE_1], has_more=True),
            id='limit-1-offset-1',
        ),
        pytest.param(
            {'limit': 1, 'offset': 2},
            http.HTTPStatus.OK,
            _format_place_list_response(places=[PLACE_2]),
            id='limit-1-offset-2',
        ),
        pytest.param(
            {'place_id': '_2'},
            http.HTTPStatus.OK,
            _format_place_list_response(places=[PLACE_2]),
            id='filter-place-id',
        ),
        pytest.param(
            {'slug': 'rEStaurant_slug_'},
            http.HTTPStatus.OK,
            _format_place_list_response(places=[PLACE_1, PLACE_2]),
            id='filter-slug',
        ),
        pytest.param(
            {'name': 'ни рыба НИ мясо'},
            http.HTTPStatus.OK,
            _format_place_list_response(places=[PLACE_3]),
            id='filter-name',
        ),
        pytest.param(
            {'pos_types': 'rkeeper'},
            http.HTTPStatus.OK,
            _format_place_list_response(places=[PLACE_2]),
            id='filter-pos-types',
        ),
        pytest.param(
            {'pos_types': 'iiko', 'limit': 1},
            http.HTTPStatus.OK,
            _format_place_list_response(places=[PLACE_3], has_more=True),
            id='filter-pos-types-has-more',
        ),
        pytest.param(
            {'pos_types': 'iiko,rkeeper'},
            http.HTTPStatus.OK,
            _format_place_list_response(places=[PLACE_3, PLACE_1, PLACE_2]),
            id='filter-pos-types-few',
        ),
        pytest.param(
            {'pos_types': 'fake', 'limit': 1},
            http.HTTPStatus.OK,
            _format_place_list_response(places=[]),
            id='filter-pos-types-empty',
        ),
        pytest.param(
            {'place_id': 'PLACE_id_', 'limit': 1},
            http.HTTPStatus.OK,
            _format_place_list_response(places=[PLACE_1], has_more=True),
            id='filter-and-limit',
        ),
        pytest.param(
            {'place_id': 'not-exists', 'limit': 1},
            http.HTTPStatus.OK,
            _format_place_list_response(places=[]),
            id='non-existing-filter',
        ),
        pytest.param(
            {'limit': 1, 'offset': 3},
            http.HTTPStatus.OK,
            _format_place_list_response(places=[]),
            id='limit-1-offset-2',
        ),
        pytest.param(
            {'mark_status': 'error'},
            http.HTTPStatus.OK,
            _format_place_list_response(places=[PLACE_1]),
            id='mark_status_filter',
        ),
    ),
)
@pytest.mark.now('2022-05-16T10:00:30+00:00')
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'pos_tokens.sql', 'restaurants_contacts.sql'],
)
async def test_admin_place_list(
        web_app_client, params, expected_code, expected_response,
):
    response = await web_app_client.get('/admin/v1/place/list', params=params)
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
