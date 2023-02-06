import http

import psycopg2.extras
import pytest


IMAGE_ID = 'logo_image_id'
IMAGE_ID_FULL = f'100500/{IMAGE_ID}'
LOGO_TEMPLATE = f'$mockserver/mds_avatars/get-inplace/{IMAGE_ID_FULL}/orig'
SUCCESS_RESPONSE = {'logo_link': LOGO_TEMPLATE}


@pytest.mark.parametrize(
    ('params', 'expected_code', 'expected_response', 'is_delete_called'),
    (
        pytest.param(
            {'place_id': 'place_id__1'},
            http.HTTPStatus.OK,
            SUCCESS_RESPONSE,
            True,
            id='OK-replace',
        ),
        pytest.param(
            {'place_id': 'place_id__2'},
            http.HTTPStatus.OK,
            SUCCESS_RESPONSE,
            False,
            id='OK-new',
        ),
        pytest.param(
            {'place_id': 'not-found'},
            http.HTTPStatus.NOT_FOUND,
            {'code': 'not_found', 'message': 'place not found'},
            False,
            id='not_found',
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['restaurants.sql'],
)
async def test_admin_place_logo_add(
        web_app_client,
        patch,
        mds_s3_client,
        pgsql,
        params,
        expected_code,
        expected_response,
        is_delete_called,
):
    deleted_counter = 0

    @patch(
        'eats_integration_offline_orders.components.avatars.'
        'check_content_is_image',
    )
    def _check_content_is_image(*args, **kwargs):
        return True

    @patch(
        'eats_integration_offline_orders.components.avatars.'
        'generate_image_id',
    )
    def _generate_image_id(*args, **kwargs):
        return IMAGE_ID

    @patch('taxi.clients.mds_avatars.MDSAvatarsClient.delete')
    async def _mds_avatars_delete_mock(*args, **kwargs):
        nonlocal deleted_counter
        deleted_counter += 1
        return 200

    @patch('taxi.clients.mds_avatars.MDSAvatarsClient.upload')
    async def _mds_avatars_upload_mock(*args, **kwargs):
        return 100500, {}

    response = await web_app_client.post(
        '/admin/v1/place/logo', data=b'abc', params=params,
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
    if response.status != http.HTTPStatus.OK:
        return
    cursor = pgsql['eats_integration_offline_orders'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    cursor.execute(
        f"""
        SELECT logo_link
        FROM restaurants
        WHERE place_id = '{params['place_id']}'
        """,
    )
    row = cursor.fetchone()
    assert row['logo_link'] == IMAGE_ID_FULL
    assert is_delete_called == bool(deleted_counter)


async def test_admin_place_logo_no_image(web_app_client):
    response = await web_app_client.post(
        '/admin/v1/place/logo',
        data=b'no-image',
        params={'place_id': 'place_id'},
    )
    body = await response.json()
    assert response.status == http.HTTPStatus.BAD_REQUEST
    assert body == {
        'code': 'bad_request',
        'message': 'specified file is not image',
    }
