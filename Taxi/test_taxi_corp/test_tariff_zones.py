# pylint: disable=redefined-outer-name

import pytest


@pytest.fixture
def get_tariff_zones_mock(patch):
    @patch('taxi.clients.tariffs.TariffsClient.get_tariff_zones')
    async def _get_tariff_zones(*args, **kwargs):
        return {
            'zones': [
                {'country': 'rus', 'name': 'moscow'},
                {'country': 'rus', 'name': 'balaha'},
                {'country': 'kaz', 'name': 'astana'},
            ],
        }

    return _get_tariff_zones


@pytest.fixture
def get_client_tariff_plan_mock(patch, request):
    param = getattr(request, 'param')

    @patch(
        'taxi_corp.clients.corp_tariffs.CorpTariffsClient'
        '.get_client_tariff_plan_current',
    )
    async def _get_client_tariff_plan_current(client_id, service):
        return {
            'client_id': client_id,
            'tariff_plan_series_id': 'tariff_plan_series_id_1',
            'tariff_plan': {
                'tariff_plan_series_id': 'tariff_plan_series_id_1',
                'zones': [
                    {
                        'zone': 'moscow',
                        'tariff_series_id': 'tariff_series_id_1',
                    },
                ],
                'disable_tariff_fallback': param,
            },
        }

    return _get_client_tariff_plan_current


@pytest.mark.parametrize(
    'passport_mock, get_client_tariff_plan_mock, expected_zones',
    [
        pytest.param(
            'client1',
            False,
            [
                {'country': 'rus', 'name': 'moscow'},
                {'country': 'kaz', 'name': 'astana'},
            ],
            id='disable_tariff_fallback_is_false',
        ),
        pytest.param(
            'client1',
            True,
            [{'country': 'rus', 'name': 'moscow'}],
            id='disable_tariff_fallback_is_true',
        ),
    ],
    indirect=['passport_mock', 'get_client_tariff_plan_mock'],
)
@pytest.mark.config(CORP_TARIFF_ZONES_BLACK_LIST=['balaha'])
async def test_get_client_list(
        passport_mock,
        taxi_corp_real_auth_client,
        get_tariff_zones_mock,
        get_client_tariff_plan_mock,
        expected_zones,
):
    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/client1/tariff_zones', params={'service': 'taxi'},
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {'zones': expected_zones}
    assert get_tariff_zones_mock.calls


@pytest.mark.config(
    CORP_TARIFF_ZONES_PUBLIC_WHITE_LIST={'rus': ['moscow']},
    CORP_CARGO_TARIFF_ZONES_PUBLIC_WHITE_LIST={'kaz': ['astana']},
)
@pytest.mark.parametrize(
    'request_service, expected_zones',
    [
        pytest.param(
            None, [{'country': 'rus', 'name': 'moscow'}], id='default',
        ),
        pytest.param(
            'taxi', [{'country': 'rus', 'name': 'moscow'}], id='explicit taxi',
        ),
        pytest.param(
            'cargo', [{'country': 'kaz', 'name': 'astana'}], id='cargo',
        ),
    ],
)
async def test_get_public_list(
        taxi_corp_auth_client,
        get_tariff_zones_mock,
        request_service,
        expected_zones,
):
    params = {}
    if request_service:
        params['service'] = request_service

    response = await taxi_corp_auth_client.get(
        '/1.0/public/tariff_zones', params=params,
    )
    response_json = await response.json()

    assert response.status == 200, response_json
    assert response_json == {'zones': expected_zones}
    assert get_tariff_zones_mock.calls
