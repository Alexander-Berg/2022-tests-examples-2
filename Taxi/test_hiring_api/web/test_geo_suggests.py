import pytest

OK_STATUS = 200


@pytest.mark.config(HIRING_API_CITIES_RU_LOCALES=['ru', 'kz'])
@pytest.mark.parametrize(
    ('params', 'response_name'),
    [
        ({'locale': 'en'}, 'en'),
        ({'locale': 'ru'}, 'ru'),
        ({}, 'en'),
        ({'locale': 'kz'}, 'ru'),
        ({'locale': 'jp'}, 'en'),
    ],
)
async def test_cities_suggests(
        taxi_hiring_api_web,
        mock_gambling_territories,
        load_json,
        params,
        response_name,
):
    # arrange
    mock_gambling_territories(
        load_json('gambling_territories_response.json'), OK_STATUS,
    )
    expected_response = load_json('expected_responses.json')[response_name]

    # act
    response = await taxi_hiring_api_web.post(
        '/v1/suggests/cities', params=params,
    )

    # assert
    assert response.status == expected_response['status']
    response_body = await response.json()
    assert response_body == expected_response['data']


@pytest.mark.usefixtures('timeout_gambling_territories')
async def test_cities_suggest_gambling_fail(taxi_hiring_api_web):
    response = await taxi_hiring_api_web.post('/v1/suggests/cities', params={})

    assert response.status == 400


@pytest.mark.translations(
    territories_suggests={
        'tariffs.key1': {'ru': 'Ключ 1', 'kz': 'Кілт 1', 'en': 'Key 1'},
        'tariffs.key2': {'ru': 'Ключ 2', 'kz': 'Кілт 2', 'en': 'Key 2'},
        'tariffs.key3': {'ru': 'Ключ 3', 'kz': 'Кілт 3', 'en': 'Key 3'},
        'tariffs.key_no_kz': {'ru': 'Ключ без КЗ', 'en': 'Key no KZ'},
        'employment_type.some': {'ru': 'Сом', 'en': 'Some'},
        'employment_type.other': {'ru': 'Лещ', 'en': 'Other'},
    },
)
@pytest.mark.parametrize(
    ('params', 'response_name'),
    [
        ({'id': 'some_territory'}, 'some_en'),
        ({'id': 'some_territory', 'locale': 'en'}, 'some_en'),
        ({'id': 'some_territory', 'locale': 'ru'}, 'some_ru'),
        ({'id': 'some_territory', 'locale': 'kz'}, 'some_kz'),
        ({'id': 'other_territory', 'locale': 'en'}, 'other_en'),
        ({'id': 'other_territory', 'locale': 'ru'}, 'other_ru'),
        ({'id': 'not_found'}, 'not_found'),
    ],
)
@pytest.mark.usefixtures('mock_gambling_get_territory')
async def test_city_info_suggests(
        taxi_hiring_api_web, load_json, params, response_name,
):
    expected_response = load_json('expected_responses.json')[response_name]
    response = await taxi_hiring_api_web.get(
        f'/v1/suggests/city-info', params=params,
    )

    assert response.status == expected_response['status']

    if response.status == 200:
        response_body = await response.json()
        assert response_body == expected_response['data']


@pytest.mark.usefixtures('timeout_gambling_territories')
async def test_city_info_suggests_gambling_fail(taxi_hiring_api_web):
    response = await taxi_hiring_api_web.get(
        '/v1/suggests/city-info', params={'id': 'some'},
    )

    assert response.status == 400
