import pytest

from eats_integration_shooter.generated.cron import run_cron

CRON_SETTINGS = ['eats_integration_shooter.crontasks.health_ping', '-t', '0']


@pytest.mark.config(
    EATS_INTEGRATION_SHOOTER_HEALTH_CHECK_PARTNERS_SETTINGS={
        'health_ping': {'enabled': False},
    },
)
async def test_should_not_start_if_disabled(cron_context, cron_runner, stq):
    await run_cron.main(CRON_SETTINGS)
    assert stq.eats_integration_shooter_health_ping.times_called == 0


@pytest.mark.config(
    EATS_INTEGRATION_SHOOTER_HEALTH_CHECK_PARTNERS_SETTINGS={
        'health_ping': {'enabled': True, 'place_groups': []},
    },
)
async def test_should_not_start_if_place_groups_is_empty(
        cron_context, cron_runner, stq,
):
    await run_cron.main(CRON_SETTINGS)
    assert stq.eats_integration_shooter_health_ping.times_called == 0


@pytest.mark.config(
    EATS_INTEGRATION_SHOOTER_HEALTH_CHECK_PARTNERS_SETTINGS={
        'health_ping': {
            'enabled': True,
            'place_groups': ['place_group_id_1', 'place_group_id_2'],
        },
    },
)
async def test_correct_run(cron_context, cron_runner, stq):
    await run_cron.main(CRON_SETTINGS)
    assert stq.eats_integration_shooter_health_ping.times_called == 2
