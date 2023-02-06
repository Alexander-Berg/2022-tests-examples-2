# pylint: disable=redefined-outer-name
import pytest

from eats_corp_orders.generated.cron import run_cron


@pytest.mark.now('2022-02-22T23:30:00+0000')
@pytest.mark.config(
    EATS_CORP_ORDERS_FREE_USER_CODES_SETTINGS={'free_after': 3600},
)
async def test_delete_codes(check_codes_db, load_json):
    await run_cron.main(
        ['eats_corp_orders.crontasks.free_user_codes', '-t', '0'],
    )

    check_codes_db(load_json('expected.json'))
