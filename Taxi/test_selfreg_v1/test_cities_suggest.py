import pytest

HEADERS = {'Accept-Language': 'ru_RU'}

CITIES_TRANSLATIONS = {
    'Москва': {'ru': 'Москва Локализованная'},
    'Московская область': {'ru': 'Мособласть Локализованная'},
    'Санкт-Петербург': {'ru': 'Питер Локализованный'},
    'Хельсинки': {'ru': 'Хельсинки Локализованные'},
    'Таллин': {'ru': 'Таллин Локализованный'},
    'Минск': {'ru': 'Минск Локализованный'},
    'Гомель': {'ru': 'Гомель Локализованный'},
}

CITIES_TRANSLATIONS_INCOMPLETE = {'Москва': {'en': 'Moscow', 'ru': ''}}

CITY_MOSCOW = {'id': 'Москва', 'text': 'Москва Локализованная'}
CITY_PITER = {'id': 'Санкт-Петербург', 'text': 'Питер Локализованный'}
CITY_MOSCOW_OBLAST = {
    'id': 'Московская область',
    'text': 'Мособласть Локализованная',
}
CITY_HELSINKI = {'id': 'Хельсинки', 'text': 'Хельсинки Локализованные'}
CITY_TALINN = {'id': 'Таллин', 'text': 'Таллин Локализованный'}
CITY_MINSK = {'id': 'Минск', 'text': 'Минск Локализованный'}
CITY_GOMEL = {'id': 'Гомель', 'text': 'Гомель Локализованный'}

# mypy demands type annotation here
RESPONSE_EMPTY: dict = {'cities': []}

RESPONSE_ALL_CITIES = {
    'cities': [
        CITY_MOSCOW,
        CITY_MOSCOW_OBLAST,
        CITY_PITER,
        CITY_HELSINKI,
        CITY_TALINN,
        CITY_MINSK,
        CITY_GOMEL,
    ],
}

RESPONSE_CITIES_RUS = {'cities': [CITY_MOSCOW, CITY_MOSCOW_OBLAST, CITY_PITER]}


@pytest.mark.translations(cities=CITIES_TRANSLATIONS_INCOMPLETE)
@pytest.mark.parametrize(
    'acceptlang, partial_translations',
    [('ru-RU', False), ('ru_RU', False), ('en-US', True), ('en_US', True)],
)
async def test_cities_suggest_translations_fallback(
        taxi_selfreg, acceptlang, partial_translations,
):
    params = {'country': 'RU', 'token': 'token_no_city'}
    response = await taxi_selfreg.get(
        '/selfreg/v1/cities/suggest',
        params=params,
        headers={'Accept-Language': acceptlang},
    )

    assert response.status == 200
    resp_body = await response.json()
    resp_cities = {city['id']: city['text'] for city in resp_body['cities']}
    if partial_translations:
        assert resp_cities == {
            'Москва': 'Moscow',
            'Московская область': 'Московская область',
            'Санкт-Петербург': 'Санкт-Петербург',
        }
    else:
        assert resp_cities == {
            'Москва': 'Москва',
            'Московская область': 'Московская область',
            'Санкт-Петербург': 'Санкт-Петербург',
        }


@pytest.mark.translations(cities=CITIES_TRANSLATIONS)
@pytest.mark.parametrize(
    'filter_str, country, expect_response',
    [
        ('', None, RESPONSE_CITIES_RUS),
        ('', 'RU', RESPONSE_CITIES_RUS),
        ('', 'FI', {'cities': [CITY_HELSINKI]}),
        ('', 'fi', {'cities': [CITY_HELSINKI]}),
        ('м', None, {'cities': [CITY_MOSCOW, CITY_MOSCOW_OBLAST, CITY_MINSK]}),
        ('Мос', None, {'cities': [CITY_MOSCOW, CITY_MOSCOW_OBLAST]}),
        ('МОС', None, {'cities': [CITY_MOSCOW, CITY_MOSCOW_OBLAST]}),
        ('Москва', None, {'cities': [CITY_MOSCOW]}),
        ('Москва ', None, {'cities': [CITY_MOSCOW]}),
        ('Москваa', None, RESPONSE_EMPTY),
        ('Хель', None, {'cities': [CITY_HELSINKI]}),
    ],
)
async def test_cities_suggest_ok(
        taxi_selfreg, filter_str, country, expect_response,
):
    params = {'filter': filter_str, 'token': 'token_msk'}
    if country:
        params['country'] = country

    response = await taxi_selfreg.get(
        '/selfreg/v1/cities/suggest', params=params, headers=HEADERS,
    )

    assert response.status == 200
    resp_body = await response.json()
    response_cities_sorted = sorted(resp_body['cities'], key=lambda k: k['id'])
    expect_cities_sorted = sorted(
        expect_response['cities'], key=lambda k: k['id'],
    )
    assert response_cities_sorted == expect_cities_sorted


@pytest.mark.translations(cities=CITIES_TRANSLATIONS)
@pytest.mark.parametrize('token', ['token_no_city', 'token_bad_city'])
async def test_cities_suggest_no_country(taxi_selfreg, token):
    params = {'token': token}

    response = await taxi_selfreg.get(
        '/selfreg/v1/cities/suggest', params=params, headers=HEADERS,
    )

    assert response.status == 200
    resp_body = await response.json()
    response_cities_sorted = sorted(resp_body['cities'], key=lambda k: k['id'])
    expect_cities_sorted = sorted(
        RESPONSE_ALL_CITIES['cities'], key=lambda k: k['id'],
    )
    assert response_cities_sorted == expect_cities_sorted
