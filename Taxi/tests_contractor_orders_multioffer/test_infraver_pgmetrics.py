import pytest


@pytest.mark.pgsql(
    'contractor_orders_multioffer', files=['multioffer_internal_state.sql'],
)
async def test_return_all(taxi_contractor_orders_multioffer, testpoint):
    @testpoint('pg-table-stats_finished')
    def task_progress(arg):
        assert arg['multioffer']['tables']['multioffer_drivers']['$meta'] == {
            'solomon_label': 'table_name',
        }

    async with taxi_contractor_orders_multioffer.spawn_task(
            'distlock/pg-table-stats',
    ):
        await task_progress.wait_call()
