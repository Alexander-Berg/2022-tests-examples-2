import pytest


@pytest.mark.config(
    OPERATION_CALCULATIONS_DOXGETY_SETTINGS={
        'money_multiplier': 0.8,
        'budget_table': '//home',
    },
)
@pytest.mark.parametrize(
    'params,expected_result',
    (
        pytest.param(
            {
                'cities_config': [
                    {'tariff_zones': ['moscow'], 'proportion': 50},
                    {'tariff_zones': ['moscow', 'himki'], 'proportion': 100},
                    {'tariff_zones': ['moscow', 'spb'], 'proportion': 50},
                    {'tariff_zones': ['spb'], 'proportion': 50},
                ],
            },
            [
                {
                    'budget': 400.0,
                    'proportion': 50,
                    'tariff_zones': ['moscow'],
                },
                {
                    'budget': 850.0,
                    'proportion': 100,
                    'tariff_zones': ['moscow', 'himki'],
                },
                {
                    'tariff_zones': ['moscow', 'spb'],
                    'proportion': 50,
                    'not_found': ['spb'],
                    'budget': 400.0,
                },
                {
                    'tariff_zones': ['spb'],
                    'proportion': 50,
                    'not_found': ['spb'],
                    'budget': 0.0,
                },
            ],
        ),
        pytest.param(
            {
                'cities_config': [
                    {'tariff_zones': ['moscow'], 'proportion': 50},
                ],
                'money_multiplier': 0.71,
            },
            [{'budget': 400.0, 'proportion': 50, 'tariff_zones': ['moscow']}],
        ),
    ),
)
async def test_v1_doxgety_budget_post(
        web_app_client, patch, open_file, params, expected_result,
):
    @patch('yt.clickhouse.execute')
    def _execute(*args, **kwargs):
        return [
            {
                'tariff_zone': 'moscow',
                'money_multiplier': 0.8,
                'sum_bonus': 200,
                'budget_conversion': 4,
            },
            {
                'tariff_zone': 'himki',
                'money_multiplier': 0.8,
                'sum_bonus': 100,
                'budget_conversion': 0.5,
            },
        ]

    response = await web_app_client.post(f'/v1/doxgety/budget/', json=params)
    assert response.status == 200
    result = await response.json()
    assert result == expected_result
