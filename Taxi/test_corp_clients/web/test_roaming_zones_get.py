import pytest


CORP_ROAMING_COUNTRY_ZONES = {
    'rus': [
        {'name': 'br_dalnevostochnyj_fo', 'name_ru': 'Дальневосточный ФО'},
        {'name': 'br_juzhnyj_fo', 'name_ru': 'Южный ФО'},
        {'name': 'br_privolzhskij_fo', 'name_ru': 'Приволжский ФО'},
        {'name': 'br_severo_kavkazskij_fo', 'name_ru': 'Северо-Кавказский ФО'},
        {'name': 'br_severo_zapadnyj_fo', 'name_ru': 'Северо-Западный ФО'},
        {'name': 'br_sibirskij_fo', 'name_ru': 'Сибирский ФО'},
        {'name': 'br_tsentralnyj_fo', 'name_ru': 'Центральный ФО'},
        {'name': 'br_uralskij_fo', 'name_ru': 'Уральский ФО'},
    ],
    'kaz': [{'name': 'br_atyrau', 'name_ru': 'Атырау'}],
}


@pytest.mark.parametrize(
    ['country'], [pytest.param('rus'), pytest.param('kaz')],
)
@pytest.mark.config(CORP_ROAMING_COUNTRY_ZONES=CORP_ROAMING_COUNTRY_ZONES)
async def test_roaming_zones_get(web_app_client, load_json, country):
    response = await web_app_client.get(
        '/v1/roaming/zones', params={'country': country},
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json['zones'] == load_json('expected_zones.json').get(
        country,
    )


@pytest.mark.config(CORP_ROAMING_COUNTRY_ZONES=CORP_ROAMING_COUNTRY_ZONES)
async def test_roaming_zones_get_404(web_app_client, load_json):
    response = await web_app_client.get(
        '/v1/roaming/zones', params={'country': 'isr'},
    )
    assert response.status == 404
    response_json = await response.json()
    assert response_json == {
        'message': 'Not found',
        'code': 'NOT_FOUND',
        'details': {
            'reason': 'Zones for country isr were not found in config',
        },
    }
