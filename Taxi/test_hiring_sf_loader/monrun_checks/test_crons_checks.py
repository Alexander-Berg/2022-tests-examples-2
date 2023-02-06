import pytest

from hiring_sf_loader.generated.cron import run_monrun


@pytest.mark.now('2022-01-15T08:00:00.0')
@pytest.mark.config(
    HIRING_SF_LOADER_CRONS_HEALTH_CHECK={
        '__default__': {
            'enabled': False,
            'normal_delay_upper_limit': 1,
            'critical_delay_lower_limit': 1,
        },
    },
)
async def test_crons_health__disabled():
    # arrange
    # act
    msg = await run_monrun.run(['hiring_sf_loader.monrun_checks.crons_health'])
    # assert
    assert msg == '0; '


@pytest.mark.now('2022-01-15T08:00:00.0')
async def test_crons_health__error():
    # arrange
    # act
    msg = await run_monrun.run(['hiring_sf_loader.monrun_checks.crons_health'])
    # assert
    assert msg == (
        '2; ERROR! CRITICALLY delayed crons:'
        ' the_most_important_task_ever (update process); | '
    )


@pytest.mark.now('2021-07-20T19:44:30.0')
async def test_crons_health__warning():
    # arrange
    # act
    msg = await run_monrun.run(['hiring_sf_loader.monrun_checks.crons_health'])
    # assert
    assert msg == (
        '1; WARNING! Slightly delayed crons:'
        ' the_most_important_task_ever (update process); '
    )


@pytest.mark.now('2021-07-20T19:30:00.0')
async def test_crons_health__ok():
    # arrange
    # act
    msg = await run_monrun.run(['hiring_sf_loader.monrun_checks.crons_health'])
    # assert
    assert msg == '0; '


@pytest.mark.now('2022-01-15T08:00:00.0')
@pytest.mark.pgsql(
    'hiring_sf_loader', files=['pg_hiring_sf_loader__empty.sql'],
)
async def test_crons_health__empty():
    # arrange
    # act
    msg = await run_monrun.run(['hiring_sf_loader.monrun_checks.crons_health'])
    # assert
    assert msg == '1; Unable to receive dates from taxi_hiring-sf-loader table'


@pytest.mark.now('2022-01-15T08:00:00.0')
@pytest.mark.pgsql('hiring_sf_loader', files=['pg_hiring_sf_loader__full.sql'])
@pytest.mark.config(
    HIRING_SF_LOADER_CRONS_HEALTH_CHECK={
        '__default__': {
            'enabled': True,
            'normal_delay_upper_limit': 200,
            'critical_delay_lower_limit': 400,
        },
        'custom_cron_settings': [
            {
                'name': 'task_one',
                'settings': {
                    'normal_delay_upper_limit': 1800,
                    'critical_delay_lower_limit': 3600,
                },
            },
            {
                'name': 'task_four',
                'settings': {
                    'enabled': False,
                    'normal_delay_upper_limit': 100,
                    'critical_delay_lower_limit': 240,
                },
            },
            {
                'name': 'task_five',
                'settings': {'critical_delay_lower_limit': 3600},
            },
        ],
    },
)
async def test_crons_health__use_custom_check():
    # arrange
    # act
    msg = await run_monrun.run(['hiring_sf_loader.monrun_checks.crons_health'])
    # assert
    assert msg == (
        '2; ERROR! CRITICALLY delayed crons:'
        ' task_two (update process); | '
        'WARNING! Slightly delayed crons:'
        ' task_one (update process),'
        ' task_five (update process); '
    )
