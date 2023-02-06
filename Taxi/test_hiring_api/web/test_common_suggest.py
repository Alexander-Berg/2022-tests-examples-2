import pytest


COUNTRIES_TRANSLATIONS = {
    'country_license.civ': {
        'mixed': 'Côte d’Ivoire',
        'ru': 'Кот-д\'Ивуар',
        'en': 'Côte d’Ivoire',
    },
    'country_license.ago': {'ru': 'Ангола', 'en': 'Angola', 'mixed': 'Ангола'},
    'country_license.cmr': {
        'ru': 'Камерун',
        'mixed': 'Cameroon',
        'en': 'Cameroon',
    },
    'country_license.zmb': {'mixed': 'Замбия', 'en': 'Zambia', 'ru': 'Замбия'},
    'skipped': {'en': 'Should skip'},
}


@pytest.mark.translations(hiring_suggests=COUNTRIES_TRANSLATIONS)
@pytest.mark.parametrize(
    'params, expected',
    [
        ('local_en', 'en'),
        ('local_ru', 'ru'),
        ('local_mixed', 'mixed'),
        ('local_empty', 'en'),
        ('name_empty', 'name_empty'),
    ],
)
async def test_common_suggest(
        taxi_hiring_api_web, load_json, params, expected,
):
    # arrange
    query_params = load_json('request_params.json')[params]
    expected_response = load_json('expected_responses.json')[expected]

    # act
    response = await taxi_hiring_api_web.get(
        '/v1/suggests/common', params=query_params,
    )

    # assert
    assert response.status == expected_response['status']
    response_body = await response.json()
    assert response_body == expected_response['data']
