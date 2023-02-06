from aiohttp import web
import pytest

X_REAL_IP = 'test_user_ip'


@pytest.mark.parametrize(
    'image_id, expected_response',
    [
        pytest.param(
            'image_id_001',
            {
                'image_id': 'image_id_001',
                'name': 'kitten0.jpg',
                'created_by': 'test',
                'created_at': '2019-08-18T18:30:27+03:00',
                'sizes': {
                    'orig': {
                        'width': 123,
                        'height': 456,
                        'url': '$mockserver/mds_avatars/get-taxi_corp/123/image_id_001/orig',  # noqa: E501 pylint: disable=line-too-long
                    },
                },
            },
            id='all_records',
        ),
    ],
)
@pytest.mark.pgsql('corp_announcements', files=('images.sql',))
async def test_get_single_image(
        web_app_client,
        web_context,
        mockserver,
        patch,
        image_id,
        expected_response,
):
    @mockserver.json_handler('/passport-yateam/blackbox')
    async def _request(*args, **kwargs):
        return web.json_response(
            {'users': [{'uid': {'value': '3000062912'}, 'login': 'test'}]},
        )

    response = await web_app_client.get(
        '/v1/admin/image/',
        params={'image_id': image_id},
        headers={'X-Real-Ip': X_REAL_IP},
    )
    assert response.status == 200
    content = await response.json()
    assert content == expected_response


@pytest.mark.pgsql('corp_announcements', files=('images.sql',))
async def test_get_single_image_not_found(web_app_client, web_context):
    image_id = 'not_found'
    response = await web_app_client.get(
        '/v1/admin/image/',
        params={'image_id': image_id},
        headers={'X-Real-Ip': X_REAL_IP},
    )
    assert response.status == 404
    content = await response.json()
    assert content == {
        'code': 'invalid-input',
        'details': {},
        'message': 'image not found',
        'status': 'error',
    }


@pytest.mark.pgsql('corp_announcements', files=('images.sql',))
async def test_get_single_image_no_id(web_app_client, web_context):
    response = await web_app_client.get(
        '/v1/admin/image/', headers={'X-Real-Ip': X_REAL_IP},
    )
    assert response.status == 400
    content = await response.json()
    assert content == {
        'code': 'REQUEST_VALIDATION_ERROR',
        'message': 'Some parameters are invalid',
        'details': {'reason': 'image_id is required parameter'},
    }
