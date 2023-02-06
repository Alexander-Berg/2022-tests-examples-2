# mongo
async def test_cities_full_list(web_app_client, load_json, mongo):
    await mongo.cities.insert_many(
        [
            {'_id': 'Череповец', 'country': 'rus'},
            {'_id': 'Санкт-Петербург', 'country': 'rus'},
            {'_id': 'Кишинев', 'country': 'mda'},
            {'_id': 'Нью-Йорк', 'country': 'usa'},
        ],
    )

    response = await web_app_client.get('/v1/dictionaries/cities')

    assert response.status == 200
    response_data = await response.json()

    assert response_data == [
        {'label': 'Череповец', 'value': 'Череповец'},
        {'label': 'Санкт-Петербург', 'value': 'Санкт-Петербург'},
        {'label': 'Кишинев', 'value': 'Кишинев'},
        {'label': 'Нью-Йорк', 'value': 'Нью-Йорк'},
    ]


async def test_filtered_cities(web_app_client, load_json, mongo):
    await mongo.cities.insert_many(
        [
            {'_id': 'Череповец', 'country': 'rus'},
            {'_id': 'Санкт-Петербург', 'country': 'rus'},
            {'_id': 'Кишинев', 'country': 'mda'},
            {'_id': 'Нью-Йорк', 'country': 'usa'},
        ],
    )

    response = await web_app_client.get(
        '/v1/dictionaries/cities?countries=rus,usa',
    )

    assert response.status == 200
    response_data = await response.json()

    assert response_data == [
        {'label': 'Череповец', 'value': 'Череповец'},
        {'label': 'Санкт-Петербург', 'value': 'Санкт-Петербург'},
        {'label': 'Нью-Йорк', 'value': 'Нью-Йорк'},
    ]


async def test_countries_list(web_app_client, load_json, mockserver):
    url = '/territories/v1/countries/list'
    mocked_result = load_json('countries.json')

    @mockserver.handler(url)
    def _patched(_):
        return mockserver.make_response(json=mocked_result)

    response = await web_app_client.get('/v1/dictionaries/countries')

    assert response.status == 200
    response_data: list = await response.json()
    assert {'label': 'Россия', 'value': 'rus'} in response_data
    assert {'label': 'Узбекистан', 'value': 'uzb'} in response_data
