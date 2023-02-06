import pytest

from eats_integration_offline_orders.generated.cron import run_monrun
from eats_integration_offline_orders.monrun_checks import orders_closed_check

ORDERS_LINK_TEMPLATE = orders_closed_check.ERRORS_ORDERS_LINK
URL_DATE = '2022-05-15%2012%3A25%3A00%2B03%3A00'


@pytest.mark.now('2022-05-15T12:30:00.0+03:00')
@pytest.mark.parametrize(
    'expected',
    (
        pytest.param(
            f'2; {ORDERS_LINK_TEMPLATE.format(URL_DATE)}',
            id='not closed',
            marks=[
                pytest.mark.config(
                    EI_OFFLINE_ORDERS_MONRUN_ORDERS_CLOSED_SETTINGS={
                        'min_non_closed_time_seconds': 60,
                        'max_non_closed_time_seconds': 300,
                    },
                ),
            ],
        ),
        pytest.param(
            '0; Check done',
            id='all closed',
            marks=[
                pytest.mark.config(
                    EI_OFFLINE_ORDERS_MONRUN_ORDERS_CLOSED_SETTINGS={
                        'min_non_closed_time_seconds': 600,
                        'max_non_closed_time_seconds': 700,
                    },
                ),
            ],
        ),
    ),
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'tables.sql', 'orders.sql'],
)
async def test_plus_invoices_checks(expected):
    message = await run_monrun.run(
        ['eats_integration_offline_orders.monrun_checks.orders_closed_check'],
    )
    assert message == expected
