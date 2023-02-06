from aiohttp import web
import flatbuffers

from example_service_fbs.fbs import TestRequest
from example_service_fbs.fbs import TestResponse
from example_service_fbs.fbs import Tree
from fbs.handlers.v1.route import Route
from userver_sample.autogen.fbs import TestPostRequest
from userver_sample.autogen.fbs import TestPostResponse


async def test_server(web_app_client):
    builder = flatbuffers.Builder(1024)
    Tree.TreeStart(builder)
    Tree.TreeAddHeight(builder, 1.0)
    first_tree = Tree.TreeEnd(builder)
    Tree.TreeStart(builder)
    Tree.TreeAddHeight(builder, 2.0)
    second_tree = Tree.TreeEnd(builder)
    TestRequest.TestRequestStart(builder)
    TestRequest.TestRequestAddFirst(builder, first_tree)
    TestRequest.TestRequestAddSecond(builder, second_tree)
    request = TestRequest.TestRequestEnd(builder)
    builder.Finish(request)

    response = await web_app_client.post(
        '/flatbuffer',
        data=builder.Output(),
        headers={'Content-Type': 'application/flatbuffer'},
    )
    assert response.status == 200
    assert response.content_type == 'application/flatbuffer'
    data = TestResponse.TestResponse.GetRootAsTestResponse(
        bytearray(await response.read()), 0,
    )
    assert data.Sum() == 3.0


async def test_client(web_context, mock_yet_another_service):
    @mock_yet_another_service(
        '/userver-sample-flatbuffer-proxy', raw_request=True,
    )
    async def handler(request):
        request_data = (
            TestPostRequest.TestPostRequest.GetRootAsTestPostRequest(
                bytearray(await request.read()), 0,
            )
        )
        assert request_data.Arg1() == 10
        assert request_data.Arg2() == 20
        builder = flatbuffers.Builder(1024)
        TestPostResponse.TestPostResponseStart(builder)
        TestPostResponse.TestPostResponseAddSum(
            builder, request_data.Arg1() + request_data.Arg2(),
        )
        response = TestPostResponse.TestPostResponseEnd(builder)
        builder.Finish(response)

        return web.Response(
            body=builder.Output(), content_type='application/flatbuffer',
        )

    client = web_context.clients.yet_another_service

    builder = flatbuffers.Builder(1024)
    TestPostRequest.TestPostRequestStart(builder)
    TestPostRequest.TestPostRequestAddArg1(builder, 10)
    TestPostRequest.TestPostRequestAddArg2(builder, 20)
    request = TestPostRequest.TestPostRequestEnd(builder)
    builder.Finish(request)

    response = await client.userver_sample_flatbuffer_proxy_post(
        body=builder.Output(),
    )

    assert response.status == 200
    assert response.body.Sum() == 30
    assert handler.times_called == 1


async def test_route_calc(web_context, mock_route_calc):
    @mock_route_calc('/v1/route')
    async def handler(request):
        builder = flatbuffers.Builder(1024)
        Route.RouteStart(builder)
        Route.RouteAddBlocked(builder, False)
        response = Route.RouteEnd(builder)
        builder.Finish(response)

        return web.Response(
            body=builder.Output(), content_type='application/x-flatbuffers',
        )

    client = web_context.clients.route_calc

    response = await client.v1_route_post()
    assert response.status == 200
    assert response.body.Blocked() is False
    assert handler.times_called == 1
