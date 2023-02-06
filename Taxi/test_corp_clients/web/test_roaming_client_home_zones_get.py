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
    ['client_id', 'expected'],
    [
        pytest.param(
            'client_id_1',
            {
                'home_zones': [
                    {'name': 'br_privolzhskij_fo'},
                    {'name': 'br_sibirskij_fo'},
                ],
            },
        ),
        pytest.param('client_id_2', {}),
        pytest.param('client_id_3', {}),
        pytest.param('client_id_4', {'home_zones': []}),
        pytest.param('client_id_not_present', {}),
    ],
)
@pytest.mark.config(CORP_ROAMING_COUNTRY_ZONES=CORP_ROAMING_COUNTRY_ZONES)
async def test_roaming_client_home_zones_get(
        web_app_client, client_id, expected,
):
    response = await web_app_client.get(
        '/v1/roaming/client-home-zones', params={'client_id': client_id},
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == expected
