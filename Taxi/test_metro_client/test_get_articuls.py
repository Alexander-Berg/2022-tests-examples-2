async def test_nomenclature_feed(mockserver, library_context, load_json):
    @mockserver.handler('/test_get_nomenclature')
    def _get_test_get_nomenclature(request):
        return mockserver.make_response(
            load_json('product_feed.json')['data'], 200,
        )

    data = await library_context.client_metro.get_articuls_from_feed()
    assert data == [100009, 118546]
