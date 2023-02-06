import http

import pytest

from test_eats_integration_offline_orders import conftest


def _create_request(pos_type='quick_resto'):
    return {
        'name': 'new-name',
        'address': 'new-address',
        'pos_type': pos_type,
        'pos_api_version': '1.1',
        'brand_id': 'new-brand',
        'description': 'new-description',
        'tips_link': 'new-tips-link',
    }


@pytest.mark.parametrize(
    'params, request_body, expected_code, expected_response',
    (
        pytest.param(
            {'place_id': 'place_id__1'},
            _create_request(),
            http.HTTPStatus.OK,
            conftest.create_admin_place(
                id=1,
                slug='place_id__1_slug',
                name='new-name',
                logo_link=(
                    '$mockserver/mds_avatars/get-inplace/135516/'
                    '147734d81d1de576476c6a217679e1c29f83eeb7/orig'
                ),
                description='new-description',
                tips_link='new-tips-link',
                pos_type='quick_resto',
                pos_token_updated_at='2022-04-19 12:00:00',
                pos_api_version='1.1',
                address='new-address',
                brand_id='new-brand',
                contacts=[conftest.ADMIN_PLACE_1_CONTACTS_1],
            ),
            id='ok-response',
        ),
        pytest.param(
            {'place_id': 'not-found'},
            _create_request(),
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
async def test_admin_place_edit(
        web_app_client, params, request_body, expected_code, expected_response,
):
    response = await web_app_client.patch(
        '/admin/v1/place', params=params, json=request_body,
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
