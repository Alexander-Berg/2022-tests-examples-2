import datetime

import pytest

NOW = datetime.datetime.now().replace(microsecond=0)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
async def test_get_tariff_plan_current(
        patch, mock_corp_tariffs, taxi_corp_real_auth_client, passport_mock,
):
    mock_corp_tariffs.data.get_client_tariff_plan_response = {
        'client_id': 'client1',
        'tariff_plan_series_id': 'tariff_plan_series_id_1',
        'tariff_plan': {
            'tariff_plan_series_id': 'tariff_plan_series_id_1',
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

    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/client1/tariff_plan/current',
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert (
        response_json == mock_corp_tariffs.data.get_client_tariff_plan_response
    )


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
async def test_change_tariff_plan(
        patch, taxi_corp_real_auth_client, passport_mock,
):
    @patch(
        'taxi_corp.clients.corp_admin.'
        'CorpAdminClient.change_client_tariff_plan',
    )
    async def _change_client_tariff_plan(*args, **kwargs):
        return {}

    data = {'tariff_plan_series_id': 'tariff_plan_series_id_1'}

    response = await taxi_corp_real_auth_client.post(
        '/1.0/client/client1/tariff_plans/set', json=data,
    )
    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {}


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
async def test_get_tariff_plans(
        patch, taxi_corp_real_auth_client, passport_mock,
):
    expected = {
        'tariff_plans': [
            {
                'tariff_plan_series_id': 'tariff_plan_series_id_1',
                'description': 'tariff_plan_series_id_1',
            },
        ],
        'cooldown': 7,
        'last_changed_date': '2017-12-30T03:00:00Z',
    }

    @patch(
        'taxi_corp.clients.corp_admin.'
        'CorpAdminClient.list_available_client_tp',
    )
    async def _list_available_client_tp(*args, **kwargs):
        return expected

    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/client1/tariff_plans/available',
    )

    response_json = await response.json()
    assert response.status == 200, response_json

    assert response_json == expected
