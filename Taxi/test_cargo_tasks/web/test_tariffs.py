import pytest

CORP_CLIENT_ID = 'corp_client_id_1_______32symbols'

TRANSLATIONS_TARIFF = {
    'name.business': {'ru': 'Комфорт'},
    'name.econom': {'ru': 'Эконом'},
    'name.comfort': {'ru': 'Комфорт'},
    'name.courier': {'ru': 'Курьер'},
    'allday': {'ru': 'День'},
    'service_name.animaltransport': {'ru': 'Перевозка котэ'},
    'service_name.ski': {'ru': 'Лыжи'},
    'service_name.childchair_moscow': {'ru': 'Детское кресло'},
    'service_name.bicycle': {'ru': 'Велик'},
    'service_name.luggage': {'ru': 'Багаж'},
    'service_name.no_smoking': {'ru': 'Не курить'},
    'service_name.waiting_in_transit': {'ru': 'Ожидание в пути'},
}

TRANSLATIONS_GEOAREAS = {
    'moscow': {'ru': 'Москва'},
    'svo': {'ru': 'Шереметьево'},
    'dme': {'ru': 'Домодедово'},
    'vko': {'ru': 'Внуково'},
    'suburb': {'ru': 'За город'},
}

CORP_TARIFFS_HIDDEN_REQUIREMENTS = [
    'internal_hidden_requirement1',
    'internal_hidden_requirement2',
]

CORP_DEFAULT_TARIFF_PLANS = {
    'rus': {'tariff_plan_series_id': 'default_tariff_plan_series_id'},
}


@pytest.mark.translations(
    tariff=TRANSLATIONS_TARIFF, geoareas=TRANSLATIONS_GEOAREAS,
)
@pytest.mark.config(
    CORP_TARIFFS_HIDDEN_REQUIREMENTS=CORP_TARIFFS_HIDDEN_REQUIREMENTS,
    CORP_DEFAULT_TARIFF_PLANS=CORP_DEFAULT_TARIFF_PLANS,
)
async def test_public_tariff(web_app_client, load_json, mocked_corp_tariffs):
    mocked_corp_tariffs.set_expected_request(
        {'tariff_plan_series_id': '', 'zone_name': 'moscow'},
    )
    mocked_corp_tariffs.set_response(load_json('get_corp_tariff.json'))

    response = await web_app_client.post(
        '/v1/public/tariff',
        json={
            'client_id': CORP_CLIENT_ID,
            'zone_name': 'moscow',
            'country': 'rus',
            'locale': 'ru',
        },
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == load_json('public_tariff_response.json')


@pytest.mark.translations(
    tariff=TRANSLATIONS_TARIFF, geoareas=TRANSLATIONS_GEOAREAS,
)
@pytest.mark.config(
    CORP_TARIFFS_HIDDEN_REQUIREMENTS=CORP_TARIFFS_HIDDEN_REQUIREMENTS,
    CORP_DEFAULT_TARIFF_PLANS=CORP_DEFAULT_TARIFF_PLANS,
    CORP_CARGO_CATEGORIES={
        '__default__': {'cargo': 'name.cargo', 'courier': 'name.courier'},
    },
)
async def test_client_tariff(web_app_client, load_json, mocked_corp_tariffs):
    mocked_corp_tariffs.set_expected_request(
        {
            'client_id': CORP_CLIENT_ID,
            'zone_name': 'moscow',
            'application': 'cargo',
        },
    )
    mocked_corp_tariffs.set_response(load_json('get_corp_tariff.json'))

    response = await web_app_client.post(
        '/v1/client/tariff',
        json={
            'client_id': CORP_CLIENT_ID,
            'zone_name': 'moscow',
            'country': 'rus',
            'locale': 'ru',
        },
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json == load_json('client_tariff_response.json')
