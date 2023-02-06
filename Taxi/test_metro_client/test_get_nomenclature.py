import json


async def test_nomenclature_feed(mockserver, library_context, load_json):
    @mockserver.handler('/test_get_nomenclature')
    def _get_test_get_nomenclature(request):
        return mockserver.make_response(
            load_json('product_feed.json')['data'], 200,
        )

    @mockserver.handler('/test_get_stocks')
    def _get_test_get_stocks(request):
        return mockserver.make_response(
            json.dumps(load_json('test_request_stocks.json')), 200,
        )

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

    data = await library_context.client_metro.get_nomenclature(123)
    categories = data.categories.serialize()
    assert categories['412721']['id'] == 412721
    assert categories['412721']['parentId'] == '412355'
    assert categories['412721']['name'] == 'Продукты без глютена'

    offers = data.offers.serialize()
    assert offers['100009']['id'] == 100009
    assert offers['100009']['available']
    assert offers['100009']['categoryId'] == 412267
    assert offers['100009']['description'] == 'description'
    assert offers['100009']['currencyId'] == 'RUR'
    assert offers['100009']['name'] == 'Рис Metro Chef Арборио, 2 кг'
    assert (
        offers['100009']['images'][1]
        == 'https://cdn.metro-cc.ru/ru/ru_pim_564769001001_01.png?'
        'w=500&h=500&format=jpg&quality=80'
    )
    assert offers['100009']['barcodes'] == [
        '4337182053989',
        '4337182053987',
        '4337182053988',
    ]
    assert offers['100009']['weight'] == 2000
    assert offers['100009']['averageWeight'] == 2
    assert offers['100009']['composition'] == 'рис'

    assert offers['100009']['storageRequirements']['expires'] == 12 * 29
    assert offers['100009']['storageRequirements']['minimalTemperature'] == 5.0
    assert (
        offers['100009']['storageRequirements']['maximalTemperature'] == 25.0
    )

    assert offers['100009']['nutritional']['energy'] == 351.0
    assert offers['100009']['nutritional']['proteins'] == 6.9
    assert offers['100009']['nutritional']['fats'] == 1.3
    assert offers['100009']['nutritional']['carbohydrates'] == 77
    assert not offers['100009']['nutritional'].get('fatContent')

    assert offers['100009']['package']['packageType'] == 'пакет'
    assert offers['100009']['package']['packageWidth'] == 12
    assert not offers['100009']['package'].get('packageHeight')
    assert not offers['100009']['package'].get('packageDepth')
    assert not offers['100009']['package'].get('packageWeight')

    assert offers['100009']['vendor']['vendorName'] == 'METRO CHEF'
    assert offers['100009']['vendor']['vendorCountry'] == 'Россия'


async def test_nomenclature_feed_new_api_stock(
        mockserver, library_context, load_json,
):
    external_id = 123

    @mockserver.handler('/test_get_nomenclature')
    def _get_test_get_nomenclature(request):
        return mockserver.make_response(
            load_json('product_feed.json')['data'], 200,
        )

    @mockserver.handler(f'/test_get_stocks/{external_id}')
    def _get_test_get_stocks(request):
        return mockserver.make_response(
            json.dumps(load_json('test_request_new_stocks.json')), 200,
        )

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

    data = await library_context.client_metro.get_nomenclature(
        external_id, True,
    )
    result = load_json('new_stock_nomenclature_answer.json')
    assert data.serialize() == result
