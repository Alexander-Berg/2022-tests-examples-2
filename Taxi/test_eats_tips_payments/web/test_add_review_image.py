from aiohttp import web
import pytest


@pytest.mark.parametrize(
    (
        'image_content',
        'image_name',
        'review_id',
        'ext_api_status',
        'ext_api_response',
        'expected_status',
        'expected_result',
    ),
    [
        (
            b'123',
            'image_name',
            1,
            400,
            {
                'code': 'image_not_valid',
                'message': 'file must be a valid image',
            },
            400,
            {
                'code': 'image_not_valid',
                'message': 'file must be a valid image',
            },
        ),
        (
            b'123',
            'image_name',
            1,
            401,
            {'code': 'not_authorized', 'message': 'auth token is missing'},
            401,
            {'code': 'not_authorized', 'message': 'auth token is missing'},
        ),
        (
            b'123',
            'image_name',
            1,
            404,
            {
                'code': 'review_not_found',
                'message': 'review with specified id is not exists',
            },
            404,
            {
                'code': 'review_not_found',
                'message': 'review with specified id is not exists',
            },
        ),
        (b'123', 'image_name', 1, 200, None, 200, None),
    ],
)
async def test_add_review(
        taxi_eats_tips_payments_web,
        mock_chaevieprosto,
        image_content,
        image_name,
        review_id,
        ext_api_status,
        ext_api_response,
        expected_status,
        expected_result,
):
    @mock_chaevieprosto('/review/image')
    async def _mock_waiter(request):
        assert request.headers.get('X-API-Key') == 'some_token'
        if ext_api_response:
            return web.json_response(ext_api_response, status=ext_api_status)
        return web.Response(status=ext_api_status)

    response = await taxi_eats_tips_payments_web.post(
        '/v1/users/waiters/review_image',
        params={'review_id': review_id},
        headers={'X-File-Name': image_name} if image_name else None,
        data=image_content,
    )
    assert response.status == expected_status
    if ext_api_status != 200:
        content = await response.json()
        assert content == expected_result
