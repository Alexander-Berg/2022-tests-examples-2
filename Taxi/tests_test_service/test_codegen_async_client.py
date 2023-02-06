import asyncio
import time


#  ->  test-service       ->  _handler       ->  test-service    ->  test
async def test_contents_no_content_type(taxi_test_service, mockserver):
    @mockserver.json_handler('/test-service/codegen/async-client')
    async def _handler(request):
        await asyncio.sleep(1)
        return mockserver.make_response()

    t_1 = time.time()

    response = await taxi_test_service.get('/codegen/async-client')
    assert _handler.times_called == 20
    assert response.status_code == 200

    t_2 = time.time()
    assert t_2 - t_1 < 10
