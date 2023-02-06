import aiohttp.web
import pytest

CONFIG_TARIFF_GROUPS = {
    'i18n_keyset': 'opteum_scoring',
    'i18n_keys': [
        {'id': 'cargo', 'i18n_key': 'tariff_group_cargo'},
        {'id': 'child', 'i18n_key': 'tariff_group_child'},
        {'id': 'comfort', 'i18n_key': 'tariff_group_comfort'},
        {'id': 'comfortplus', 'i18n_key': 'tariff_group_comfortplus'},
        {'id': 'courier', 'i18n_key': 'tariff_group_courier'},
        {'id': 'econom', 'i18n_key': 'tariff_group_econom'},
        {'id': 'lab', 'i18n_key': 'tariff_group_lab'},
        {'id': 'med', 'i18n_key': 'tariff_group_med'},
        {'id': 'minivan', 'i18n_key': 'tariff_group_minivan'},
        {'id': 'other', 'i18n_key': 'tariff_group_other'},
        {'id': 'selfdriving', 'i18n_key': 'tariff_group_selfdriving'},
        {'id': 'vip', 'i18n_key': 'tariff_group_vip'},
        {'id': 'volunteers', 'i18n_key': 'tariff_group_volunteers'},
    ],
}


@pytest.mark.config(
    FLEET_DRIVERS_SCORING_REPORTS_TARIFF_GROUPS=CONFIG_TARIFF_GROUPS,
)
@pytest.mark.translations(
    opteum_scoring={
        'tariff_group_courier': {'ru': 'Курьер'},
        'tariff_group_econom': {'ru': 'Эконом'},
        'tariff_group_comfort': {'ru': 'Комфорт'},
        'tariff_group_comfortplus': {'ru': 'Комфорт+'},
        'tariff_group_other': {'ru': 'Остальные'},
    },
)
async def test_success(
        web_app_client, headers, mock_fleet_drivers_scoring, load_json,
):
    stub = load_json('success.json')

    @mock_fleet_drivers_scoring(
        '/v1/paid/drivers/scoring/orders-statistics/retrieve',
    )
    async def _orders_statistics_retrieve(request):
        assert request.json == stub['scoring_request']
        return aiohttp.web.json_response(stub['scoring_response'])

    response = await web_app_client.post(
        '/drivers-scoring-api/v1/paid/scoring/orders-statistics/retrieve',
        headers=headers,
        json={'request_id': 'request_id'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
