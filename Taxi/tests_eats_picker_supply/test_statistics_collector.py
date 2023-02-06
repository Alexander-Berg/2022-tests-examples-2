import pytest


@pytest.mark.config(
    EATS_PICKER_SUPPLY_STATISTIC_SETTINGS={'period_seconds': 1},
)
async def test_statistics_collector_pickers_count(
        taxi_eats_picker_supply,
        taxi_eats_picker_supply_monitor,
        create_picker,
):
    for i in range(1, 100):
        create_picker(picker_id=i)

    await taxi_eats_picker_supply.run_task('supply-statistics-collector-task')

    metrics = await taxi_eats_picker_supply_monitor.get_metric(
        'supply-statistics-collector',
    )

    assert metrics['pickers_count'] == 99
