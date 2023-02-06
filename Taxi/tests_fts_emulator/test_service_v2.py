import asyncio  # noqa: F401 C5521


async def _check_service_is_alive(fts_emulator):
    response = await fts_emulator.get('ping')
    # Status code must be checked for every request
    assert response.status_code == 200
    # Response content (even empty) must be checked for every request
    assert response.content == b''


async def test_foo(taxi_fts_emulator, mockserver, load_binary):
    @mockserver.handler('/maps-router/v2/route')
    def _router_handler(request):
        return mockserver.make_response(
            response=load_binary('maps.protobuf'),
            status=200,
            content_type='application/x-protobuf',
        )

    @mockserver.json_handler('/yagr/pipeline/test/position/store')
    def _yagr_handler(request):
        print(request)
        return mockserver.make_response('OK', status=200)

    await asyncio.sleep(10)

    await _check_service_is_alive(taxi_fts_emulator)
