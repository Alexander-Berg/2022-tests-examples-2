import json


async def test_get_prices(mockserver, library_context, load_json):
    @mockserver.handler('/test_get_prices')
    def _get_test_get_prices(request):
        return mockserver.make_response(
            json.dumps(load_json('test_request_prices.json')), 200,
        )

    @mockserver.handler('/test_get_token')
    def _get_test_get_token(request):
        return mockserver.make_response(
            json.dumps(load_json('test_token.json')), 200,
        )

    articles = ['articles'] * 251
    prices_list = await library_context.client_metro.get_prices(
        'place_id', articles,
    )
    assert len(prices_list) == 18
    prices = prices_list[0].serialize()
    request_body = load_json('test_request_prices.json')
    assert prices == request_body[0]


async def test_get_prices_new_method(mockserver, library_context, load_json):
    @mockserver.handler('/test_get_prices')
    def _get_test_get_prices(request):
        return mockserver.make_response(
            json.dumps(load_json('test_request_prices_new_method.json')), 200,
        )

    @mockserver.handler('/test_get_token')
    def _get_test_get_token(request):
        return mockserver.make_response(
            json.dumps(load_json('test_token.json')), 200,
        )

    articles = ['articles'] * 251
    prices_list = await library_context.client_metro.get_prices(
        'place_id', articles,
    )
    assert len(prices_list) == 20
    prices = prices_list[0].serialize()
    request_body = load_json('test_request_prices_new_method_parsed.json')
    assert prices == request_body[0]
