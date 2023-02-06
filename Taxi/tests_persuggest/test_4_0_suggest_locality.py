import pytest

URL = '4.0/persuggest/v1/suggest-locality'


@pytest.mark.parametrize(
    (
        'accept_language',
        'suggest_geo_lang',
        'suggest_geo_response_file',
        'expected_response_file',
    ),
    (
        pytest.param(
            'ru-RU',
            'ru',
            'suggest_geo_response.json',
            'expected_response_localized_ru.json',
            id='accept_language = ru-RU',
        ),
        pytest.param(
            'en-US',
            'en',
            'suggest_geo_response.json',
            'expected_response_localized_en.json',
            id='accept_language = en-US',
        ),
        pytest.param(
            'unknown',
            'en',
            'suggest_geo_response.json',
            'expected_response_localized_en.json',
            id='accept_language = unknown',
        ),
        pytest.param(
            'ru',
            'ru',
            'suggest_geo_response_with_countries.json',
            'expected_response_localized_ru_with_countries.json',
            id='accept_language = ru (with countries)',
        ),
    ),
)
async def test_4_0_suggest_locality_language(
        taxi_persuggest,
        mockserver,
        yamaps,
        load_json,
        accept_language,
        suggest_geo_lang,
        suggest_geo_response_file,
        expected_response_file,
):
    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        assert request.args == {
            'search_type': 'all',
            'bases': 'locality',
            'v': '7',
            'lang': suggest_geo_lang,
            'n': '5',
            'part': 'мос',
            'callback': '',
        }
        return load_json(suggest_geo_response_file)

    response = await taxi_persuggest.post(
        URL,
        {
            'part': 'мос',
            'kinds': ['locality'],
            'require_additional_fields': {
                'add_localized_name': True,
                'add_country_alpha3': True,
            },
        },
        headers={'Accept-Language': accept_language},
    )
    assert response.status_code == 200
    expected_json = load_json(expected_response_file)
    assert response.json() == expected_json


@pytest.mark.parametrize(
    (
        'taxi_persuggest_args',
        'expected_geo_request_args',
        'suggest_geo_response_file',
        'expected_response_file',
    ),
    (
        pytest.param(
            {'filters': {'countries': 'ru'}},
            {'countries': 'ru'},
            'suggest_geo_response_ru.json',
            'expected_response_ru.json',
            id='countries = ru',
        ),
        pytest.param(
            {'filters': {'countries_alpha3': ['rus']}},
            {'in': '225'},
            'suggest_geo_response_ru.json',
            'expected_response_ru.json',
            id='countries_alpha3 = ["rus"]',
        ),
        pytest.param(
            {'filters': {'countries_alpha3': ['rus', 'blr']}},
            {'in': '225,149'},
            'suggest_geo_response.json',
            'expected_response.json',
            id='countries_alpha3 = ["rus", "blr"]',
        ),
        pytest.param(
            {'filters': {'in': '225', 'countries_alpha3': ['blr']}},
            {'in': '225,149'},
            'suggest_geo_response.json',
            'expected_response.json',
            id='in = 225 and countries_alpha3 = ["blr"]',
        ),
        pytest.param(
            {'limit': 1},
            {'n': '1'},
            'suggest_geo_response_n1.json',
            'expected_response_n1.json',
            id='limit = 1',
        ),
        pytest.param(
            {'kinds': ['country', 'locality']},
            {'bases': 'country,locality'},
            'suggest_geo_response_with_countries.json',
            'expected_response_with_countries.json',
            id='kinds = country,locality',
        ),
        pytest.param(
            {'kinds': ['geobase_country', 'locality']},
            {'bases': 'geobase_country,locality'},
            'suggest_geo_response_with_countries.json',
            'expected_response_with_countries.json',
            id='kinds = geobase_country,locality',
        ),
        pytest.param(
            {
                'kinds': ['country', 'locality'],
                'require_additional_fields': {
                    'add_timezones': True,
                    'add_country_alpha3': True,
                },
            },
            {'bases': 'country,locality'},
            'suggest_geo_response_with_countries.json',
            'expected_response_with_countries_tz.json',
            id='kinds = country,locality with timezones',
        ),
    ),
)
async def test_4_0_suggest_locality_filters(
        taxi_persuggest,
        mockserver,
        yamaps,
        load_json,
        taxi_persuggest_args,
        expected_geo_request_args,
        suggest_geo_response_file,
        expected_response_file,
):
    suggest_geo_request = {
        'search_type': 'all',
        'bases': 'locality',
        'v': '7',
        'lang': 'ru',
        'n': '5',
        'part': 'мос',
        'callback': '',
    }
    suggest_geo_request.update(expected_geo_request_args)

    @mockserver.json_handler('/yamaps-suggest-geo/suggest-geo')
    def _mock_suggest_geo(request):
        assert request.args == suggest_geo_request
        return load_json(suggest_geo_response_file)

    request_body = {'part': 'мос', 'kinds': ['locality']}
    request_body.update(taxi_persuggest_args)

    response = await taxi_persuggest.post(
        URL, request_body, headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    expected_json = load_json(expected_response_file)
    assert response.json() == expected_json
