# pylint: disable=redefined-outer-name

import datetime

import pytest

NOW = datetime.datetime.now().replace(microsecond=0)

TARIFF_ZONES = {
    'zones': [
        {'country': 'rus', 'name': 'moscow', 'translation': 'Москва'},
        {'country': 'rus', 'name': 'spb', 'translation': 'Санкт-Петербург'},
        {'country': 'rus', 'name': 'balaha', 'translation': 'Балаха'},
        {'country': 'kaz', 'name': 'astana', 'translation': 'Астана'},
    ],
}

TARIFFS = {
    'tariffs': [
        {'categories_names': ['econom', 'business'], 'home_zone': 'moscow'},
        {'categories_names': ['econom'], 'home_zone': 'spb'},
        {'categories_names': ['econom'], 'home_zone': 'balaha'},
        {'categories_names': ['econom'], 'home_zone': 'astana'},
    ],
}

TRANSLATIONS = {
    'name.business': {'ru': 'Комфорт'},
    'allday': {'ru': 'День'},
    'service_name.animaltransport': {'ru': 'Перевозка котэ'},
    'service_name.ski': {'ru': 'Лыжи'},
    'service_name.childchair_moscow': {'ru': 'Детское кресло'},
    'service_name.bicycle': {'ru': 'Велик'},
    'service_name.luggage': {'ru': 'Багаж'},
    'service_name.no_smoking': {'ru': 'Не курить'},
    'service_name.waiting_in_transit': {'ru': 'Ожидание в пути'},
}


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
@pytest.mark.translations(
    tariff=TRANSLATIONS,
    geoareas={
        'moscow': {'ru': 'Москва'},
        'svo': {'ru': 'Шереметьево'},
        'dme': {'ru': 'Домодедово'},
        'vko': {'ru': 'Внуково'},
        'suburb': {'ru': 'За город'},
    },
)
@pytest.mark.config(
    CORP_TARIFFS_HIDDEN_REQUIREMENTS=[
        'internal_hidden_requirement1',
        'internal_hidden_requirement2',
    ],
)
async def test_get_one(
        load_json,
        taxi_corp_real_auth_client,
        mock_corp_tariffs,
        passport_mock,
        mock_tariffs,
):
    mock_corp_tariffs.data.get_client_tariff_response = load_json(
        'get_corp_tariff.json',
    )
    mock_tariffs.data.get_tariffs_response = TARIFFS
    mock_tariffs.data.get_tariff_zones_response = TARIFF_ZONES
    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/client1/tariff',
        params={'zone_name': 'moscow', 'service': 'taxi'},
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    expected_data = load_json('get_one_response.json')
    assert response_json == expected_data

    # check corp-tariffs requests
    call = mock_corp_tariffs.get_client_tariff_current.next_call()
    assert call['request'].query == {
        'client_id': 'client1',
        'zone_name': 'moscow',
        'application': 'taxi',
    }
    assert not mock_corp_tariffs.get_client_tariff_current.has_calls


@pytest.mark.parametrize(
    'tariff_plan_series_id, is_error, status_code, expected',
    [
        pytest.param(
            'tariff_plan_1',
            False,
            200,
            'get_one_response.json',
            id='existing tariff plan',
        ),
        pytest.param(
            'nonexisting_tp',
            True,
            400,
            {
                'code': 'INVALID_TARIFF_PLAN_SERIES_ID',
                'errors': [
                    {
                        'code': 'INVALID_TARIFF_PLAN_SERIES_ID',
                        'text': 'tariff_plan_series_id is invalid',
                    },
                ],
                'message': 'tariff_plan_series_id is invalid',
            },
            id='nonexisting tariff plan',
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
@pytest.mark.translations(
    tariff=TRANSLATIONS,
    geoareas={
        'moscow': {'ru': 'Москва'},
        'svo': {'ru': 'Шереметьево'},
        'dme': {'ru': 'Домодедово'},
        'vko': {'ru': 'Внуково'},
        'suburb': {'ru': 'За город'},
    },
)
@pytest.mark.config(
    CORP_TARIFFS_HIDDEN_REQUIREMENTS=[
        'internal_hidden_requirement1',
        'internal_hidden_requirement2',
    ],
    CORP_AVAILABLE_TARIFF_PLANS_TO_CHOOSE={
        'rus': [
            {
                'name': 'main',
                'combination': [
                    {
                        'description_key': 'tariff_plan_series_id_1',
                        'tariff_plan_series_id': 'tariff_plan_1',
                    },
                    {
                        'description_key': 'tariff_plan_series_id_8',
                        'tariff_plan_series_id': 'tariff_plan_2',
                    },
                ],
            },
        ],
    },
    CORP_ROAMING_TARIFF_PLANS_MAP={
        'rus': [
            {
                'description': 'very_testing_tp',
                'roaming_tariff_plan_series_id': (
                    'default_tariff_plan_series_id'
                ),
                'tariff_plan_series_id': 'tariff_plan_1',
            },
        ],
    },
)
async def test_get_one_tariff_plan_series_id(
        load_json,
        taxi_corp_real_auth_client,
        mock_corp_tariffs,
        passport_mock,
        mock_tariffs,
        tariff_plan_series_id,
        is_error,
        expected,
        status_code,
):

    mock_corp_tariffs.data.get_client_tariff_response = load_json(
        'get_corp_tariff.json',
    )
    mock_corp_tariffs.data.get_client_tariff_plan_response = {
        'client_id': 'client1',
        'tariff_plan_series_id': 'tariff_plan_1',
        'tariff_plan': {
            'tariff_plan_series_id': 'tariff_plan_1',
            'zones': [
                {'zone': 'moscow', 'tariff_series_id': 'tariff_series_id_1'},
            ],
            'disable_tariff_fallback': False,
            'application_multipliers': [
                {'application': 'callcenter', 'multiplier': 2},
                {'application': 'corpweb', 'multiplier': 3},
            ],
        },
    }
    mock_tariffs.data.get_tariffs_response = TARIFFS
    mock_tariffs.data.get_tariff_zones_response = TARIFF_ZONES
    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/client1/tariff',
        params={
            'zone_name': 'moscow',
            'service': 'taxi',
            'tariff_plan_series_id': tariff_plan_series_id,
        },
    )
    response_json = await response.json()
    assert response.status == status_code, response_json
    if is_error:
        expected_data = expected
    else:
        expected_data = load_json(expected)
    assert response_json == expected_data

    # check corp-tariffs requests
    if not is_error:
        call = mock_corp_tariffs.get_client_tariff_current.next_call()
        assert call['request'].query == {
            'client_id': 'client1',
            'zone_name': 'moscow',
            'application': 'taxi',
            'tariff_plan_series_id': 'tariff_plan_1',
        }
    assert not mock_corp_tariffs.get_tariff_current.has_calls


@pytest.mark.now(NOW.isoformat())
@pytest.mark.translations(
    tariff=TRANSLATIONS,
    geoareas={
        'moscow': {'ru': 'Москва'},
        'svo': {'ru': 'Шереметьево'},
        'dme': {'ru': 'Домодедово'},
        'vko': {'ru': 'Внуково'},
        'suburb': {'ru': 'За город'},
    },
)
@pytest.mark.config(
    CORP_DEFAULT_TARIFF_PLANS={
        'rus': {'tariff_plan_series_id': 'default_tariff_plan_series_id'},
    },
)
@pytest.mark.config(
    CORP_TARIFFS_HIDDEN_REQUIREMENTS=[
        'internal_hidden_requirement1',
        'internal_hidden_requirement2',
    ],
)
async def test_get_public_one(
        load_json, taxi_corp_real_auth_client, mock_corp_tariffs,
):
    mock_corp_tariffs.data.get_tariff_response = load_json(
        'get_corp_tariff.json',
    )
    response = await taxi_corp_real_auth_client.get(
        '/1.0/public/tariff?zone_name=moscow&country=rus',
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == load_json('get_one_response.json')

    # check corp-tariffs requests
    call = mock_corp_tariffs.get_tariff_current.next_call()
    assert call['request'].query == {
        'tariff_plan_series_id': 'default_tariff_plan_series_id',
        'zone_name': 'moscow',
    }
    assert not mock_corp_tariffs.get_tariff_current.has_calls


@pytest.mark.config(
    CORP_TARIFF_ZONES_PUBLIC_WHITE_LIST={
        'rus': ['moscow', 'spb'],
        'kaz': ['astana'],
    },
    CORP_DEFAULT_CATEGORIES={'rus': ['econom', 'business'], 'kaz': ['econom']},
)
@pytest.mark.translations(
    tariff={
        'name.econom': {'ru': 'Эконом'},
        'name.comfort': {'ru': 'Комфорт'},
    },
)
@pytest.mark.parametrize(
    'country, expected',
    [
        pytest.param(
            'rus',
            {
                'tariffs': [
                    {
                        'country': 'rus',
                        'home_zone': 'moscow',
                        'home_zone_translate': 'Москва',
                        'categories': [
                            {'name': 'econom', 'name_translate': 'Эконом'},
                            {'name': 'business', 'name_translate': 'Комфорт'},
                        ],
                    },
                    {
                        'country': 'rus',
                        'home_zone': 'spb',
                        'home_zone_translate': 'Санкт-Петербург',
                        'categories': [
                            {'name': 'econom', 'name_translate': 'Эконом'},
                        ],
                    },
                ],
            },
            id='rus',
        ),
        pytest.param(
            'kaz',
            {
                'tariffs': [
                    {
                        'country': 'kaz',
                        'home_zone': 'astana',
                        'home_zone_translate': 'Астана',
                        'categories': [
                            {'name': 'econom', 'name_translate': 'Эконом'},
                        ],
                    },
                ],
            },
            id='kaz',
        ),
    ],
)
async def test_get_public_list(
        taxi_corp_auth_client, mock_tariffs, country, expected,
):
    mock_tariffs.data.get_tariff_zones_response = TARIFF_ZONES
    mock_tariffs.data.get_tariffs_response = TARIFFS
    response = await taxi_corp_auth_client.get(
        '/1.0/public/tariffs', params={'country': country},
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == expected

    # check tariffs requests
    tariff_zones_call = mock_tariffs.get_tariff_zones.next_call()
    assert tariff_zones_call['request'].query == {'locale': 'ru'}
    assert not mock_tariffs.get_tariff_zones.has_calls

    tariffs_call = mock_tariffs.get_tariffs.next_call()
    assert tariffs_call['request'].query == {}
    assert not mock_tariffs.get_tariffs.has_calls


@pytest.mark.config(
    CORP_TARIFF_ZONES_BLACK_LIST=['balaha'],
    CORP_DEFAULT_CATEGORIES={'rus': ['econom', 'business'], 'kaz': ['econom']},
    CORP_AVAILABLE_TARIFF_PLANS_TO_CHOOSE={
        'rus': [
            {
                'name': 'main',
                'combination': [
                    {
                        'description_key': 'tariff_plan_series_id_1',
                        'tariff_plan_series_id': 'tariff_plan_series_id_1',
                    },
                    {
                        'description_key': 'tariff_plan_series_id_8',
                        'tariff_plan_series_id': 'tariff_plan_2',
                    },
                ],
            },
        ],
    },
)
@pytest.mark.translations(
    tariff={
        'name.econom': {'ru': 'Эконом'},
        'name.comfort': {'ru': 'Комфорт'},
    },
)
@pytest.mark.parametrize(
    'disable_tariff_fallback, expected, tariff_plan_series_id, status_code',
    [
        pytest.param(
            False,
            {
                'tariffs': [
                    {
                        'country': 'rus',
                        'home_zone': 'moscow',
                        'home_zone_translate': 'Москва',
                        'categories': [
                            {'name': 'econom', 'name_translate': 'Эконом'},
                            {'name': 'business', 'name_translate': 'Комфорт'},
                        ],
                    },
                    {
                        'country': 'rus',
                        'home_zone': 'spb',
                        'home_zone_translate': 'Санкт-Петербург',
                        'categories': [
                            {'name': 'econom', 'name_translate': 'Эконом'},
                        ],
                    },
                ],
            },
            None,
            200,
            id='disable_tariff_fallback_false',
        ),
        pytest.param(
            True,
            {
                'tariffs': [
                    {
                        'country': 'rus',
                        'home_zone': 'moscow',
                        'home_zone_translate': 'Москва',
                        'categories': [
                            {'name': 'econom', 'name_translate': 'Эконом'},
                            {'name': 'business', 'name_translate': 'Комфорт'},
                        ],
                    },
                ],
            },
            None,
            200,
            id='disable_tariff_fallback_true',
        ),
        pytest.param(
            True,
            {
                'tariffs': [
                    {
                        'country': 'rus',
                        'home_zone': 'spb',
                        'home_zone_translate': 'Санкт-Петербург',
                        'categories': [
                            {'name': 'econom', 'name_translate': 'Эконом'},
                        ],
                    },
                ],
            },
            'tariff_plan_series_id_1',
            200,
            id='with_tariff_plan_series_id',
        ),
        pytest.param(
            True,
            {
                'errors': [
                    {
                        'text': 'tariff_plan_series_id is invalid',
                        'code': 'INVALID_TARIFF_PLAN_SERIES_ID',
                    },
                ],
                'message': 'tariff_plan_series_id is invalid',
                'code': 'INVALID_TARIFF_PLAN_SERIES_ID',
            },
            'wrong_tariff_plan_series_id',
            400,
            id='with_invalid_tariff_plan_series_id',
        ),
    ],
)
async def test_get_list(
        taxi_corp_auth_client,
        mock_corp_tariffs,
        mock_tariffs,
        disable_tariff_fallback,
        expected,
        patch,
        tariff_plan_series_id,
        status_code,
):
    mock_tariffs.data.get_tariff_zones_response = TARIFF_ZONES
    mock_tariffs.data.get_tariffs_response = TARIFFS
    mock_corp_tariffs.data.get_client_tariff_plan_response = {
        'client_id': 'client1',
        'tariff_plan_series_id': 'tariff_plan_series_id_1',
        'tariff_plan': {
            'tariff_plan_series_id': 'tariff_plan_series_id_1',
            'zones': [
                {'zone': 'moscow', 'tariff_series_id': 'tariff_series_id_1'},
            ],
            'disable_tariff_fallback': disable_tariff_fallback,
            'application_multipliers': [
                {'application': 'callcenter', 'multiplier': 2},
                {'application': 'corpweb', 'multiplier': 3},
            ],
        },
    }

    @patch('taxi_corp.clients.corp_admin.CorpAdminClient.tariff_plans_current')
    async def _tariff_plans_current(*args, **kwargs):
        return {
            'tariff_plan_series_id': tariff_plan_series_id,
            'zones': [
                {'zone': 'spb', 'tariff_series_id': 'tariff_series_id_1'},
            ],
            'disable_tariff_fallback': disable_tariff_fallback,
            'application_multipliers': [
                {'application': 'callcenter', 'multiplier': 2},
                {'application': 'corpweb', 'multiplier': 3},
            ],
        }

    params = {}
    if tariff_plan_series_id:
        params['tariff_plan_series_id'] = tariff_plan_series_id
    response = await taxi_corp_auth_client.get(
        '/1.0/client/client1/tariffs', params=params,
    )
    response_json = await response.json()
    assert response.status == status_code, response_json
    assert response_json == expected

    # check corp-tariffs requests
    call = mock_corp_tariffs.get_client_tariff_plan_current.next_call()
    assert call['request'].query == {'client_id': 'client1', 'service': 'taxi'}
    assert not mock_corp_tariffs.get_client_tariff_plan_current.has_calls

    # check tariffs requests
    tariff_zones_call = mock_tariffs.get_tariff_zones.next_call()
    assert tariff_zones_call['request'].query == {'locale': 'ru'}
    assert not mock_tariffs.get_tariff_zones.has_calls

    tariffs_call = mock_tariffs.get_tariffs.next_call()
    assert tariffs_call['request'].query == {}
    assert not mock_tariffs.get_tariffs.has_calls
