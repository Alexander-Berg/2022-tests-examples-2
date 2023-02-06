import pytest


@pytest.mark.now('2017-09-05T01:16:00+0')
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
async def test_simple(cron_runner, get_ride_subs_cache):
    await cron_runner.ride_subs_order_cache_cleaner()

    assert get_ride_subs_cache() == {
        'cache': [['order2', 10]],
        'user': [['portal_uid', 'yataxi', 'order4']],
        'paid_order': [['order6', '5.0000']],
    }
