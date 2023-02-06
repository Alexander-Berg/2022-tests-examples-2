import pytest


@pytest.mark.parametrize('place_id', [None, '420'])
async def test_attach_file(
        taxi_eats_restapp_support_chat, place_id, mockserver,
):
    headers = {'X-YaEda-PartnerId': '13', 'Content-Type': 'image/png'}
    parameters = {
        'service': 'restapp',
        'filename': 'some.png',
        'idempotency_token': 'unique',
    }
    if place_id:
        parameters['restapp_place_id'] = place_id
    parameters_string = '&'.join(
        ['{}={}'.format(k, v) for k, v in parameters.items()],
    )
    body = b'filedata'

    @mockserver.json_handler(
        '/protocol-py3/4.0/support_chat/v1/realtime/attach_file',
    )
    def _mock_support_chat(request):
        assert request.headers['X-YaEda-PartnerId'] == (
            place_id or 'partner_13'
        )
        assert request.args == parameters
        assert request.get_data() == body
        return mockserver.make_response(
            status=200, json={'attachment_id': 'attach_id'},
        )

    response = await taxi_eats_restapp_support_chat.post(
        '/4.0/support_chat/v1/realtime/attach_file?{}'.format(
            parameters_string,
        ),
        headers=headers,
        data=body,
    )

    assert response.status == 200
    assert response.json()['attachment_id'] == 'attach_id'


@pytest.mark.parametrize('place_id', [None, '420'])
async def test_download_file(
        taxi_eats_restapp_support_chat, place_id, mockserver,
):
    headers = {'X-YaEda-PartnerId': '13'}
    parameters = {'service': 'restapp'}
    if place_id:
        parameters['restapp_place_id'] = place_id
    parameters_string = '&'.join(
        ['{}={}'.format(k, v) for k, v in parameters.items()],
    )
    body = b'filedata'

    @mockserver.handler(
        '/protocol-py3/4.0/support_chat/v1'
        '/realtime/chat_id/download_file/attach_id',
    )
    def _mock_support_chat(request):
        assert request.headers['X-YaEda-PartnerId'] == (
            place_id or 'partner_13'
        )
        assert request.args == parameters
        return mockserver.make_response(status=200, response=body)

    response = await taxi_eats_restapp_support_chat.get(
        '/4.0/support_chat/v1'
        '/realtime/chat_id/download_file/attach_id?{}'.format(
            parameters_string,
        ),
        headers=headers,
        data=body,
    )

    assert response.status == 200
    assert response.content == body
