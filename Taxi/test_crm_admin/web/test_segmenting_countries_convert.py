from crm_admin.utils.segmenting import processing


async def test_countries_list(
        web_context, web_app_client, load_json, mockserver,
):
    url = '/territories/v1/countries/list'
    mocked_result = load_json('countries.json')

    @mockserver.handler(url)
    def _patched(_):
        return mockserver.make_response(json=mocked_result)

    segment_processing = processing.SegmentProcessing(web_context, 1, 1, None)

    before = ['rus', 'bel', 'Карибы']
    after = await segment_processing.convert_countries(before)

    # assert after == ['Россия', 'Бельгия', 'Карибы']
    assert after == ['Россия', 'Бельгия']
