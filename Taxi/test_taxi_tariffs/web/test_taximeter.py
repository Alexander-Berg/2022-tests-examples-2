# pylint:disable=invalid-name
# pylint:disable=redefined-outer-name
import json

import pytest

params = [
    pytest.param(
        '05156a5d865a429a960ddb4dde20e735:5caeed9d1bc8d21af5a07a24-'
        '4e4a0806458d46a5827baefc5989d68d-54eaaebc146441bc8f8d8e0df54a6bff',
        'tariff31_moscow_econom_decoupling1.json',
        True,
        id='decoupling moscow_econom tariff policy',
    ),
    pytest.param(
        '05156a5d865a429a960ddb4dde20e735:5caeed9d1bc8d21af5a07a24-'
        '3193b516dab44747add7d9ce463e541f-b85f3e94abcc42cbbc96c4f9f39b199d',
        'tariff31_moscow_econom_decoupling2.json',
        True,
        id='decoupling moscow_econom tariff plan policy',
    ),
    pytest.param(
        'surge--59d3027127a542989074e7cdfe6122a5:5caeed9d1bc8d21af5a07a24-'
        '14a6b044fcd64e028425126c8140e6a7-1d5ccf18b9b140eab7767c0f3b8426d1'
        '--minimal_2-distance_3-time_4-hidden_1-surcharge_5-multiplier_6-sp_7',
        'tariff31_decoupling_surge_moscow_mkk.json',
        True,
        id='decoupling surge moscow_mkk',
    ),
    pytest.param(
        '9f22bb7f4c7c49a484689a2a0bf4dd18:5caeeda81bc8d21af5a07a27-'
        'a67a51a9c2a84605998d5ed135012709-750cb8a9a9734b6f8aabead7375516fa',
        'tariff31_belgrade_decoupling.json',
        True,
        id='decoupling belgrade custom corp tariff',
    ),
    pytest.param(
        '05156a5d865a429a960ddb4dde20e735',
        'tariff31_moscow_econom.json',
        False,
        id='simple moscow_econom',
    ),
    pytest.param(
        '59d3027127a542989074e7cdfe6122a5',
        'tariff31_moscow_mkk.json',
        False,
        id='simple moscow_mkk',
    ),
    pytest.param(
        '096520342f6e4765991e21de17d980bf',
        'tariff31_belgrade.json',
        False,
        id='simple belgrade',
    ),
    pytest.param(
        'surge--05156a5d865a429a960ddb4dde20e735--minimal_2-distance_3-'
        'time_4-hidden_1-surcharge_5-multiplier_6-sp_7',
        'tariff31_surge_moscow_econom.json',
        False,
        id='surge moscow_econom',
    ),
    pytest.param(
        'surge--59d3027127a542989074e7cdfe6122a5--minimal_2-distance_3-'
        'time_4-hidden_1-surcharge_5-multiplier_6-sp_7',
        'tariff31_surge_moscow_mkk.json',
        False,
        id='surge moscow_mkk',
    ),
    pytest.param(
        'surge--096520342f6e4765991e21de17d980bf--minimal_2-distance_3-'
        'time_4-hidden_1-surcharge_5-multiplier_6-sp_7',
        'tariff31_surge_belgrade.json',
        False,
        id='surge belgrade',
    ),
    pytest.param(
        'surge--eb42d18920cd4e79b79661dcabd8d9da--minimal_2-distance_3-'
        'time_4-hidden_1-surcharge_5-multiplier_6-sp_7',
        'tariff31_surge_smolensk.json',
        False,
        id='surge smolensk',
    ),
    pytest.param(
        'surge--eb42d18920cd4e79b79661dcabd8d9da--minimal_2-distance_3-'
        'requirement_hourly_rental.1hours',
        'tariff_31_tariff_requirement_smolensk.json',
        False,
        id='surge smolensk',
    ),
]


@pytest.fixture
def mock_corp_tariffs(mockserver, load_json):
    corp_tariffs_data = load_json('mock_corp_tariffs.json')
    corp_tariffs = {
        corp_tariff['tariff']['id']: corp_tariff
        for corp_tariff in corp_tariffs_data
    }

    @mockserver.json_handler(r'/corp-tariffs/v1/tariff', regex=True)
    def _get_tariff(request):

        tariff_id = request.query['id']
        corp_tariff = corp_tariffs.get(tariff_id)
        if corp_tariff:
            return corp_tariff

        return mockserver.make_response(
            response=json.dumps(
                {
                    'code': '404',
                    'message': 'corp tariff {} not found'.format(tariff_id),
                    'details': {},
                },
            ),
            status=404,
        )

    return _get_tariff


@pytest.mark.config(
    ENABLE_DRIVER_CHANGE_COST=True,
    CLEAN_SURGE_TO_WAITING_PRICE_APPLIANCE={
        '__default__': False,
        'smolensk': True,
    },
    USE_MINIMAL_ZERO_COST_BY_REQUIREMENT={
        '__default__': False,
        'hourly_rental.1hours': True,
    },
    USE_WAITING_IN_TRANSIT_ZERO_COST_BY_REQUIREMENT={
        '__default__': False,
        'hourly_rental.1hours': True,
    },
    CORP_CATEGORIES={
        '__default__': {'econom': 'name.econom', 'mkk': 'name.mkk'},
    },
)
@pytest.mark.parametrize(
    'category_id, expected_filename, is_decoupling', params,
)
async def test_get_tariffs(
        load_json,
        web_app_client,
        mock_corp_tariffs,
        cache_shield,
        category_id,
        expected_filename,
        is_decoupling,
):
    expected = load_json(expected_filename)

    response = await web_app_client.get(
        '/v1/taximeter/get_tariffs?id={}'.format(category_id),
    )

    data = await response.json()

    assert response.status == 200, data
    assert expected == data

    assert mock_corp_tariffs.has_calls == is_decoupling


@pytest.mark.filldb(tariff_settings='new_format')
@pytest.mark.config(
    ENABLE_DRIVER_CHANGE_COST=True,
    CLEAN_SURGE_TO_WAITING_PRICE_APPLIANCE={
        '__default__': False,
        'smolensk': True,
    },
    USE_MINIMAL_ZERO_COST_BY_REQUIREMENT={
        '__default__': False,
        'hourly_rental.1hours': True,
    },
    USE_WAITING_IN_TRANSIT_ZERO_COST_BY_REQUIREMENT={
        '__default__': False,
        'hourly_rental.1hours': True,
    },
    CORP_CATEGORIES={
        '__default__': {'econom': 'name.econom', 'mkk': 'name.mkk'},
    },
)
@pytest.mark.parametrize(
    'category_id, expected_filename, is_decoupling', params,
)
async def test_get_tariffs_new_format(
        load_json,
        web_app_client,
        mock_corp_tariffs,
        cache_shield,
        category_id,
        expected_filename,
        is_decoupling,
):
    expected = load_json(expected_filename)

    response = await web_app_client.get(
        '/v1/taximeter/get_tariffs?id={}'.format(category_id),
    )

    data = await response.json()

    assert response.status == 200, data
    assert expected == data

    assert mock_corp_tariffs.has_calls == is_decoupling


@pytest.mark.config(
    ENABLE_DRIVER_CHANGE_COST=True,
    CLEAN_SURGE_TO_WAITING_PRICE_APPLIANCE={
        '__default__': False,
        'smolensk': True,
    },
    USE_MINIMAL_ZERO_COST_BY_REQUIREMENT={'__default__': True},
    USE_WAITING_IN_TRANSIT_ZERO_COST_BY_REQUIREMENT={'__default__': True},
    CORP_CATEGORIES={
        '__default__': {'econom': 'name.econom', 'mkk': 'name.mkk'},
    },
)
async def test_get_tariffs_step_by_step(
        load_json, web_app_client, mock_corp_tariffs,
):
    for param in params:
        category_id, expected_filename, _ = param.values
        expected = load_json(expected_filename)

        response = await web_app_client.get(
            '/v1/taximeter/get_tariffs?id={}'.format(category_id),
        )

        data = await response.json()

        assert response.status == 200, data
        assert expected == data


@pytest.mark.parametrize(
    'category_id, is_decoupling',
    [
        pytest.param('category_id', False, id='unknown driver tariff'),
        pytest.param(
            'category_id:corp_tariff_id', True, id='unknown corp tariff',
        ),
    ],
)
async def test_get_tariffs_404(
        web_app_client,
        cache_shield,
        mock_corp_tariffs,
        category_id,
        is_decoupling,
):
    response = await web_app_client.get(
        '/v1/taximeter/get_tariffs?id={}'.format(category_id),
    )

    response_json = await response.json()
    assert response.status == 404, response_json
    assert response_json == {
        'code': 'not-found',
        'message': 'can not find docs with ids: [\'{}\']'.format(category_id),
    }

    assert mock_corp_tariffs.has_calls == is_decoupling
