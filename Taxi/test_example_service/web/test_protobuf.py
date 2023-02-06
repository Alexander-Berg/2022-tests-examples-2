from aiohttp import web

from example_service_proto import request_pb2
from example_service_proto.proto import response_pb2
from yandex.maps.proto.search import address_pb2


async def test_server(web_app_client):
    response = await web_app_client.post(
        '/protobuf',
        data=request_pb2.TestRequest(first=1, second=2).SerializeToString(),
        headers={'Content-Type': 'application/protobuf'},
    )
    assert response.status == 200
    assert response.content_type == 'application/protobuf'
    data = response_pb2.TestResponse.FromString(  # pylint: disable=no-member
        await response.read(),
    )
    assert data.sum == 3


async def test_client(web_context, mock_yet_another_service):
    @mock_yet_another_service('/yamaps-proxy', raw_request=True)
    async def handler(request):
        address = address_pb2.Address.FromString(  # pylint: disable=no-member
            await request.read(),
        )
        assert address.formatted_address == 'bacbac'
        new_address = address_pb2.Address(formatted_address='heyho')
        return web.Response(
            body=new_address.SerializeToString(),
            content_type='application/protobuf',
        )

    client = web_context.clients.yet_another_service

    response = await client.yamaps_proxy_post(
        body=address_pb2.Address(formatted_address='bacbac'),
    )

    assert response.status == 200
    assert response.body.formatted_address == 'heyho'
    assert handler.times_called == 1
