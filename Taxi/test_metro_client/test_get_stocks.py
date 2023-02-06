import json


async def test_get_stocks(mockserver, library_context, load_json):
    @mockserver.handler('/test_get_stocks')
    def _get_test_get_stocks(request):
        return mockserver.make_response(
            json.dumps(load_json('test_request_stocks.json')), 200,
        )

    @mockserver.handler('/test_get_token')
    def _get_test_get_token(request):
        return mockserver.make_response(
            json.dumps(load_json('test_token.json')), 200,
        )

    articles = ['articles'] * 251
    stocks_list = await library_context.client_metro.get_stocks(
        'place_id', articles,
    )
    assert len(stocks_list) == 2
    data = stocks_list[0].serialize()
    normalize = lambda elem, key: elem['stockDetails'][0][key]  # noqa: E731
    request_body = load_json('test_request_stocks.json')
    assert normalize(data, 'subsystemNo') == normalize(
        request_body, 'subsystemNo',
    )


async def test_get_new_stocks(mockserver, library_context, load_json):
    place_id = 'place_id'

    @mockserver.handler(f'/test_get_stocks/{place_id}')
    def _get_test_get_stocks(request):
        return mockserver.make_response(
            json.dumps(load_json('test_request_new_stocks.json')), 200,
        )

    @mockserver.handler('/test_get_token')
    def _get_test_get_token(request):
        return mockserver.make_response(
            json.dumps(load_json('test_token.json')), 200,
        )

    stocks_list = await library_context.client_metro.get_new_stocks(place_id)
    assert len(stocks_list) == 2
    assert stocks_list == load_json('answer_new_stocks.json')
