import pytest

from atlas_backend.generated.cron import run_cron


@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['calc_alternative_types.sql'],
)
async def test_update_calc_alternative_types(
        clickhouse_client_mock, web_app_client, patch,
):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute')
    async def _execute(*args, **kwargs):
        return [
            ('altpin',),
            ('explicit_antisurge',),
            ('combo_inner',),
            ('perfect_chain',),
        ]

    await run_cron.main(
        ['atlas_backend.crontasks.update_calc_alternative_types', '-t', '0'],
    )

    response = await web_app_client.get('/api/v1/calc-alternative-types')
    assert response.status == 200
    actual_result = await response.json()
    assert actual_result == {
        'calc_alternative_types': [
            {'type_id': 'combo_outer', 'name': 'combo_outer'},
            {'type_id': 'altpin', 'name': 'altpin'},
            {'type_id': 'explicit_antisurge', 'name': 'explicit_antisurge'},
            {'type_id': 'combo_inner', 'name': 'combo_inner'},
            {'type_id': 'perfect_chain', 'name': 'perfect_chain'},
        ],
    }
