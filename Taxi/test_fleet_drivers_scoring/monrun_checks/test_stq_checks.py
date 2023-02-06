import pytest

# pylint: disable=redefined-outer-name
from fleet_drivers_scoring.generated.cron import run_monrun


@pytest.mark.pgsql('fleet_drivers_scoring', files=['gen_stq_checks.sql'])
@pytest.mark.now('2020-05-17T10:00+00:01')
async def test_errors():
    msg = await run_monrun.run(
        ['fleet_drivers_scoring.monrun_checks.stq_checks_do_not_fail_much'],
    )
    assert msg == '2; Too many stqs is not done'


@pytest.mark.pgsql('fleet_drivers_scoring', files=['gen_stq_checks.sql'])
@pytest.mark.now('2020-05-17T10:01+00')
@pytest.mark.config(
    FLEET_DRIVERS_SCORING_MONRUN_THRESHOLDS={
        'yt_updates': {
            'orders': {'warn_hours': 30, 'crit_hours': 36},
            'quality_metrics': {'warn_hours': 30, 'crit_hours': 36},
            'ratings': {'warn_hours': 30, 'crit_hours': 36},
            'high_speed_driving': {'warn_hours': 30, 'crit_hours': 36},
            'passenger_tags': {'warn_hours': 30, 'crit_hours': 36},
            'driving_style': {'warn_hours': 30, 'crit_hours': 36},
        },
        'stq_checks': {
            'minutes_to_check': 10,
            'percentage_fails_to_crit': 80,
            'percentage_fails_to_warn': 60,
            'min_number_checks_to_trigger': 0,
        },
    },
)
async def test_warn():
    msg = await run_monrun.run(
        ['fleet_drivers_scoring.monrun_checks.stq_checks_do_not_fail_much'],
    )
    assert msg == '1; Many stqs is not done'


@pytest.mark.pgsql('fleet_drivers_scoring', files=['gen_stq_checks_old.sql'])
@pytest.mark.now('2020-05-17T10:01+00')
@pytest.mark.config(
    FLEET_DRIVERS_SCORING_MONRUN_THRESHOLDS={
        'yt_updates': {
            'orders': {'warn_hours': 30, 'crit_hours': 36},
            'quality_metrics': {'warn_hours': 30, 'crit_hours': 36},
            'ratings': {'warn_hours': 30, 'crit_hours': 36},
            'high_speed_driving': {'warn_hours': 30, 'crit_hours': 36},
            'passenger_tags': {'warn_hours': 30, 'crit_hours': 36},
            'driving_style': {'warn_hours': 30, 'crit_hours': 36},
        },
        'stq_checks': {
            'minutes_to_check': 10,
            'percentage_fails_to_crit': 1,
            'percentage_fails_to_warn': 1,
            'min_number_checks_to_trigger': 0,
        },
    },
)
async def test_old_errors_not_affect():
    msg = await run_monrun.run(
        ['fleet_drivers_scoring.monrun_checks.stq_checks_do_not_fail_much'],
    )
    assert msg == '0; Check done'


async def test_empty_checks_ok():
    msg = await run_monrun.run(
        ['fleet_drivers_scoring.monrun_checks.stq_checks_do_not_fail_much'],
    )
    assert msg == '0; Check done'


@pytest.mark.pgsql('fleet_drivers_scoring', files=['gen_stq_checks.sql'])
@pytest.mark.now('2020-05-17T10:01+00')
@pytest.mark.config(
    FLEET_DRIVERS_SCORING_MONRUN_THRESHOLDS={
        'yt_updates': {
            'orders': {'warn_hours': 30, 'crit_hours': 36},
            'quality_metrics': {'warn_hours': 30, 'crit_hours': 36},
            'ratings': {'warn_hours': 30, 'crit_hours': 36},
            'high_speed_driving': {'warn_hours': 30, 'crit_hours': 36},
            'passenger_tags': {'warn_hours': 30, 'crit_hours': 36},
            'driving_style': {'warn_hours': 30, 'crit_hours': 36},
        },
        'stq_checks': {
            'minutes_to_check': 10,
            'percentage_fails_to_crit': 0,
            'percentage_fails_to_warn': 0,
            'min_number_checks_to_trigger': 10,
        },
    },
)
async def test_min_checks_to_check():
    msg = await run_monrun.run(
        ['fleet_drivers_scoring.monrun_checks.stq_checks_do_not_fail_much'],
    )
    assert msg == '0; Too little checks to test'


@pytest.mark.pgsql(
    'fleet_drivers_scoring', files=['with_status_meta_info.sql'],
)
@pytest.mark.now('2020-05-17T10:01+00')
@pytest.mark.config(
    FLEET_DRIVERS_SCORING_MONRUN_THRESHOLDS={
        'stq_checks': {
            'minutes_to_check': 10,
            'percentage_fails_to_crit': 55,
            'percentage_fails_to_warn': 45,
            'min_number_checks_to_trigger': 0,
        },
    },
)
async def test_status_meta_info():
    msg = await run_monrun.run(
        ['fleet_drivers_scoring.monrun_checks.stq_checks_do_not_fail_much'],
    )
    assert msg == '1; Many stqs is not done'
