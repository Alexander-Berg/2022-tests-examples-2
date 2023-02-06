import pytest


@pytest.mark.pgsql('eats_partners', files=['fill_data.sql'])
async def test_periodic_statistic(
        taxi_eats_partners, taxi_eats_partners_monitor, pgsql,
):
    await taxi_eats_partners.run_task('active-partners-statistic-task')
    metrics = await taxi_eats_partners_monitor.get_metric(
        'periodic-active-partners-statistic',
    )
    expected_result = {
        'active_partners': {'for_last_minute': 2, 'for_24_hours': 4},
    }
    assert metrics == expected_result

    cursor = pgsql['eats_partners'].cursor()
    cursor.execute(
        f"""UPDATE eats_partners.last_activity
            SET last_activity_at = NOW() - INTERVAL '5 DAYS'
            WHERE partner_id = 1""",
    )

    await taxi_eats_partners.run_task('active-partners-statistic-task')
    metrics = await taxi_eats_partners_monitor.get_metric(
        'periodic-active-partners-statistic',
    )
    expected_result = {
        'active_partners': {'for_last_minute': 1, 'for_24_hours': 3},
    }
    assert metrics == expected_result
