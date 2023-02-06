import aiohttp.web

IMAGE_PNG = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x01\x03\x00\x00\x00%\xdbV\xca\x00\x00\x00\x01sRGB\x01\xd9\xc9\x7f\x00'
    b'\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00'
    b'\x00\x00\x03PLTE\xff\xff\xff\xa7\xc4\x1b\xc8\x00\x00\x00\nIDATx\x9cc`'
    b'\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82'
)


async def test_success(
        web_app_client, headers, mock_support_chat, load_json, patch,
):
    stub = load_json('success.json')

    @mock_support_chat('/v1/chat/chat_id/attachment/attachment_id')
    async def _attachment(request):
        assert request.query == stub['support_chat_request']
        return aiohttp.web.Response(body=IMAGE_PNG)

    response = await web_app_client.post(
        '/support-chat-api/v1/attachment',
        headers={**headers, 'X-Idempotency-Token': '1'},
        json={
            'attachment_id': 'attachment_id',
            'chat_id': 'chat_id',
            'owner': {'id': 'id', 'role': 'opteum_client'},
            'size': 'preview',
        },
    )

    assert response.status == 200
