import pytest


async def test_coupons_usages_counter(taxi_coupons, testpoint, mongodb):
    series = mongodb.promocode_series.find_one({'_id': 'usages_test_series'})
    assert series['used_count'] == 0

    @testpoint('usages-counter-finish')
    def finish(_):
        series = mongodb.promocode_series.find_one(
            {'_id': 'usages_test_series'},
        )
        # promocode_usages2 - 5 usages
        # mdb_promocode_usages2 - 2 usages
        assert series['used_count'] == 7

    async with taxi_coupons.spawn_task('distlock/usages-counter-task'):
        await finish.wait_call()


@pytest.mark.config(COUPONS_ENABLE_USAGES_COUNTER=False)
@pytest.mark.skip(reason='flapping test, will be fixed in TAXIBACKEND-41551')
async def test_usages_counter_disabled(taxi_coupons, testpoint, mongodb):
    series = mongodb.promocode_series.find_one({'_id': 'usages_test_series'})
    assert series['used_count'] == 0

    @testpoint('usages-counter-finish')
    def finish(_):
        series = mongodb.promocode_series.find_one(
            {'_id': 'usages_test_series'},
        )
        assert series['used_count'] == 0

    async with taxi_coupons.spawn_task('distlock/usages-counter-task'):
        await finish.wait_call()
