import datetime as dt

import pytest

from taxi_takeout.tasks import helpers
from taxi_takeout.tasks.users.models import PhoneConfirmation


@pytest.mark.now('2019-01-21T12:00:00')
@pytest.mark.config(
    TAKEOUT_PHONE_CONFIRM_MAX_DAYS_SIZE=10, ORDERS_HISTORY_MAX_SIZE_DAYS=2,
)
@pytest.mark.parametrize(
    'pc_created, pc_last_confirmed, expected',
    [
        (
            dt.datetime(2019, 1, 17),
            dt.datetime(2019, 1, 20),
            helpers.DateInterval(
                dt.datetime(2019, 1, 17), dt.datetime(2019, 1, 21, 12),
            ),
        ),
        (
            dt.datetime(2019, 1, 2),
            dt.datetime(2019, 1, 8),
            helpers.DateInterval(
                dt.datetime(2019, 1, 2), dt.datetime(2019, 1, 8),
            ),
        ),
        (
            dt.datetime(2019, 1, 20),
            None,
            helpers.DateInterval(
                dt.datetime(2019, 1, 19, 12), dt.datetime(2019, 1, 21, 12),
            ),
        ),
        (dt.datetime(2019, 1, 2), None, None),
    ],
)
async def test_interval(pc_created, pc_last_confirmed, expected, taxi_config):
    phone_confirm = PhoneConfirmation(
        created=pc_created,
        last_confirmed=pc_last_confirmed,
        updated=None,
        uid=None,
        uid_type=None,
        phone_id=None,
        bound_portal_uid=None,
    )
    interval = helpers.get_order_interval(
        phone_confirm,
        taxi_config.get('TAKEOUT_PHONE_CONFIRM_MAX_DAYS_SIZE'),
        taxi_config.get('ORDERS_HISTORY_MAX_SIZE_DAYS'),
    )

    assert interval == expected
