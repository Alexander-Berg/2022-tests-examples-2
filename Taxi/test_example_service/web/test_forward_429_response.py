from aiohttp import web


async def test_forward_429_resp(
        taxi_example_service_web, mock_yet_another_service,
):
    @mock_yet_another_service('/talk')
    async def handler(request):
        return web.Response(status=429)

    response = await taxi_example_service_web.get('/go_to_yas')
    assert response.status == 429
    assert handler.times_called == 1
