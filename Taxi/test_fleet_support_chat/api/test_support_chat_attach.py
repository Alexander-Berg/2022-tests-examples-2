import aiohttp
import aiohttp.web

IMAGE_PNG = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x01\x03\x00\x00\x00%\xdbV\xca\x00\x00\x00\x01sRGB\x01\xd9\xc9\x7f\x00'
    b'\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00'
    b'\x00\x00\x03PLTE\xff\xff\xff\xa7\xc4\x1b\xc8\x00\x00\x00\nIDATx\x9cc`'
    b'\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82'
)


async def test_success(
        web_app_client,
        mock_dac_users,
        headers,
        mock_support_chat,
        load_json,
        patch,
):
    stub = load_json('success.json')

    @mock_support_chat('/v1/chat/attach_file')
    async def _attach(request):
        return aiohttp.web.json_response(stub['support_chat_response'])

    with aiohttp.MultipartWriter('form-data') as data:
        part = data.append(IMAGE_PNG, {'Content-Type': 'image/png'})
        part.set_content_disposition(
            'form-data', name='attachment', filename='test.png',
        )

    response = await web_app_client.post(
        '/support-chat-api/v1/attach?permission=all',
        headers={
            **headers,
            'Content-Type': 'multipart/form-data; boundary=' + data.boundary,
            'X-Idempotency-Token': '1',
        },
        data=data,
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']


async def test_success_filed_validation(
        web_app_client, mock_dac_users, headers, mock_support_chat, load_json,
):
    stub = load_json('success.json')

    @mock_support_chat('/v1/chat/attach_file')
    async def _attach(request):
        return aiohttp.web.json_response(stub['support_chat_response'])

    with aiohttp.MultipartWriter('form-data') as data:
        part = data.append(
            b'image binary \x00 data', {'Content-Type': 'image/png'},
        )
        part.set_content_disposition(
            'form-data', name='attachment', filename='test.png',
        )

    response = await web_app_client.post(
        '/support-chat-api/v1/attach?permission=all',
        headers={
            **headers,
            'Content-Type': 'multipart/form-data; boundary=' + data.boundary,
            'X-Idempotency-Token': '1',
        },
        data=data,
    )

    assert response.status == 400
