import operator

import pytest

GEOAREAS_TRANSLATIONS = {
    'kaz': {'ru': 'Казахстан'},
    'rus': {'ru': 'Россия'},
    'zvenigorod': {'ru': 'Звенигород'},
    'mytishchi': {'ru': 'Мытищи'},
    'vladimir': {'ru': 'Владимир'},
}

ZVENIGOROD = {
    'country': 'rus',
    'name': 'zvenigorod',
    'time_zone': 'Europe/Moscow',
    'translation': 'Звенигород',
}
BELGRADE = {
    'country': 'rus',
    'name': 'belgrade',
    'time_zone': 'Europe/Belgrade',
}
ASTANA = {
    'country': 'kaz',
    'name': 'astana',
    'time_zone': 'Asia/Omsk',
    'currency': 'KZT',
}
MYTISHCHI = {
    'country': 'rus',
    'name': 'mytishchi',
    'time_zone': 'Europe/Moscow',
    'translation': 'Мытищи',
    'currency': 'RUB',
}
VLADIMIR = {
    'country': 'rus',
    'name': 'vladimir',
    'time_zone': 'Europe/Moscow',
    'translation': 'Владимир',
    'currency': 'RUB',
}
ABIDJAN = {
    'country': 'civ',
    'name': 'abidjan',
    'time_zone': 'Africa/Abidjan',
    'translation': 'Абиджан',
}


@pytest.mark.translations(geoareas=GEOAREAS_TRANSLATIONS)
@pytest.mark.parametrize(
    ['params', 'expected_zones', 'test_id'],
    [
        pytest.param(
            dict(),
            [ASTANA, BELGRADE, MYTISHCHI, VLADIMIR, ZVENIGOROD],
            'No filtration',
        ),
        pytest.param(
            dict(city_ids='Astana,Belgrade'),
            [ASTANA, BELGRADE],
            'Filter by citites',
        ),
        pytest.param(
            dict(city_ids='Moscow'),
            [MYTISHCHI, VLADIMIR],
            'Multiple home zones for one city id',
        ),
        pytest.param(dict(country='kaz'), [ASTANA], 'Filter by country'),
        pytest.param(
            dict(country='rus', city_ids='Belgrade,Moscow'),
            [BELGRADE, MYTISHCHI, VLADIMIR],
            'Filter by country and cities',
        ),
        pytest.param(
            dict(country='rus', city_ids='Atlantis'), [], 'Non existent city',
        ),
        pytest.param(
            dict(city_ids='Astana,Belgrade,Atlantis'),
            [ASTANA, BELGRADE],
            'Filter by citites, one non existent',
        ),
        pytest.param(
            dict(country='rus', city_ids='Astana'), [], 'City not in country',
        ),
        pytest.param(
            dict(zone_names='zvenigorod,mytishchi'),
            [MYTISHCHI, ZVENIGOROD],
            'Filter by zone',
        ),
        pytest.param(dict(zone_names='a'), [], 'Non existent zone'),
        pytest.param(
            dict(zone_names='a,mytishchi'),
            [MYTISHCHI],
            'Filter by zones, one non existent',
        ),
        pytest.param(
            dict(country='civ', zone_names='zvenigorod'),
            [],
            'Zone not in country',
        ),
        pytest.param(
            dict(city_ids='Astana', zone_names='zvenigorod'),
            [],
            'Zone not in city',
        ),
    ],
)
@pytest.mark.parametrize(
    'exp_name',
    [
        pytest.param(
            'fallback_enabled',
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_enabled.json',
                )
            ),
        ),
        pytest.param(
            'fallback_disabled',
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_disabled.json',
                )
            ),
        ),
    ],
)
async def test_get_list(
        web_app_client,
        cache_shield,
        tariffs_context,
        mock_individual_tariffs,
        load_json,
        params,
        expected_zones,
        test_id,
        exp_name,
):
    if exp_name == 'fallback_disabled':
        tariffs_context.set_tariffs_list_response(
            load_json('individual_tariff_responses.json')[test_id],
        )
    params.update({'locale': 'ru'})

    response = await web_app_client.get('/v1/tariff_zones', params=params)
    data = await response.json()

    assert response.status == 200, data

    zones = data['zones']
    zones.sort(key=operator.itemgetter('name'))
    assert zones == expected_zones


@pytest.mark.parametrize(
    'exp_name',
    [
        pytest.param(
            'fallback_enabled',
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_enabled.json',
                )
            ),
        ),
        pytest.param(
            'fallback_disabled',
            marks=(
                pytest.mark.client_experiments3(
                    file_with_default_response='exp3_fallback_disabled.json',
                )
            ),
        ),
    ],
)
async def test_get_list_bad_locale(
        web_app_client,
        cache_shield,
        tariffs_context,
        mock_individual_tariffs,
        exp_name,
):
    response = await web_app_client.get('/v1/tariff_zones?locale=rur')
    data = await response.json()
    assert response.status == 400, data
    assert data == {
        'code': 'unsupported-locale',
        'message': 'rur not in ru, en, hy, ka, kk, uk, az, ro, zh, ky, lv',
    }
