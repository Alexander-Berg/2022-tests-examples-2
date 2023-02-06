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
    'arm': [{'name': 'br_erevan', 'name_ru': 'Ереван'}],
}


@pytest.mark.parametrize(
    ['client_id', 'request_data', 'expected'],
    [
        pytest.param(
            'client_id_1',
            {
                'home_zones': [
                    {'name': 'br_privolzhskij_fo'},
                    {'name': 'br_sibirskij_fo'},
                    {'name': 'br_uralskij_fo'},
                ],
            },
            [
                {'name': 'br_privolzhskij_fo'},
                {'name': 'br_sibirskij_fo'},
                {'name': 'br_uralskij_fo'},
            ],
            id='add one zone',
        ),
        pytest.param(
            'client_id_1',
            {'home_zones': [{'name': 'br_privolzhskij_fo'}]},
            [{'name': 'br_privolzhskij_fo'}],
            id='remove one zone',
        ),
        pytest.param(
            'client_id_2',
            {'home_zones': [{'name': 'br_privolzhskij_fo'}]},
            [{'name': 'br_privolzhskij_fo'}],
            id='add zones field',
        ),
        pytest.param(
            'client_id_1', {'home_zones': []}, [], id='clear zones field',
        ),
        pytest.param('client_id_1', {}, None, id='remove zones field'),
        pytest.param(
            'client_id_3',
            {'home_zones': [{'name': 'br_erevan'}]},
            [{'name': 'br_erevan'}],
            id='initially null',
        ),
        pytest.param(
            'client_id_4',
            {'home_zones': []},
            [],
            id='zones field stays empty',
        ),
    ],
)
@pytest.mark.config(CORP_ROAMING_COUNTRY_ZONES=CORP_ROAMING_COUNTRY_ZONES)
async def test_roaming_client_home_zones_update(
        web_app_client, db, client_id, request_data, expected,
):
    response = await web_app_client.post(
        '/v1/roaming/client-home-zones',
        params={'client_id': client_id},
        json=request_data,
    )
    assert response.status == 200
    client_home_zones = await db.secondary.corp_client_roaming_zones.find_one(
        {'client_id': client_id}, projection=['zones'],
    )
    assert client_home_zones.get('zones') == expected


@pytest.mark.config(CORP_ROAMING_COUNTRY_ZONES=CORP_ROAMING_COUNTRY_ZONES)
async def test_roaming_client_home_zones_update_400(web_app_client):
    response = await web_app_client.post(
        '/v1/roaming/client-home-zones',
        params={'client_id': 'client_id_1'},
        json={
            'home_zones': [
                {'name': 'br_privolzhskij_fo'},
                {'name': 'wrong'},
                {'name': 'wrong2'},
            ],
            'country': 'rus',
        },
    )
    assert response.status == 400
    response_json = await response.json()
    assert response_json == {
        'message': 'Request error',
        'code': 'REQUEST_ERROR',
        'details': {
            'reason': (
                'Zones (wrong, wrong2) are not in the list'
                ' of available country ("rus") zones'
            ),
        },
    }
