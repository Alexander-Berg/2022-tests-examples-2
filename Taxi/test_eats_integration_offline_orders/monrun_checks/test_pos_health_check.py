import pytest

from eats_integration_offline_orders.generated.cron import run_monrun
from eats_integration_offline_orders.monrun_checks import pos_health_check


ERROR_LINK = pos_health_check.ERROR_PLACES_URL


@pytest.mark.now('2022-05-15T12:30:00.0+03:00')
@pytest.mark.parametrize(
    'expected',
    (
        pytest.param(
            f'2; {ERROR_LINK}',
            id='not checked restaurants',
            marks=[
                pytest.mark.config(
                    EI_OFFLINE_ORDERS_HEALTH_CHECK_SETTINGS={
                        'unhealthy_threshold_seconds': 60,
                    },
                ),
            ],
        ),
        pytest.param(
            '0; Check done',
            id='all closed',
            marks=[
                pytest.mark.config(
                    EI_OFFLINE_ORDERS_HEALTH_CHECK_SETTINGS={
                        'unhealthy_threshold_seconds': 3600,
                    },
                ),
            ],
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['restaurants.sql'],
)
async def test_pos_health_check(expected):
    message = await run_monrun.run(
        ['eats_integration_offline_orders.monrun_checks.pos_health_check'],
    )
    assert message == expected
