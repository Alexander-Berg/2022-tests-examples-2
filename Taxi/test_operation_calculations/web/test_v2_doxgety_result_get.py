import pytest


@pytest.mark.pgsql('operation_calculations', files=['pg_doxgety.sql'])
@pytest.mark.config(
    OPERATION_CALCULATIONS_DOXGETY_RESTRICTIONS={
        '__default__': {
            'min_proportion': 20,
            'max_proportion': 80,
            'min_money_multiplier': 0.4,
            'max_money_multiplier': 1.5,
            'min_aa_difficulty': 0.98,
            'bonus': {},
            'bonus_per_goal': {},
            'goal': {},
            'ttest_pvalue': {'critical': {'max': 1, 'min': 0.5}},
        },
    },
)
async def test_v2_doxgety_result_get(web_app_client, mockserver):
    response = await web_app_client.get(
        f'/v2/doxgety/result', params={'task_id': 'b'},
    )
    result = await response.json()
    assert response.status == 200
    assert result == {
        'cities_result': [
            {
                'aa_difficulty': 0.98,
                'aa_difficulty_active': 0.98,
                'bonus': {'max': 6800.0, 'mean': 4498, 'min': 1900},
                'bonus_per_goal': {'max': 81.8, 'mean': 46.6, 'min': 28.9},
                'budget': 100,
                'currency': 'RUB',
                'goal': {'max': 180, 'mean': 108, 'min': 30},
                'ttest_pvalue': 0,
                'warnings': [
                    {
                        'kind': 'critical',
                        'max': 1,
                        'min': 0.5,
                        'name': 'ttest_pvalue',
                        'value': 0,
                    },
                ],
                'whitelist': '//home/taxi_ml/add_whitelist',
            },
        ],
        'whitelist': '//home/taxi_ml/add_whitelist_full',
    }
