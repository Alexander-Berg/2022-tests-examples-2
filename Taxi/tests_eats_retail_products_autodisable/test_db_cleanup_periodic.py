import pytest

from tests_eats_retail_products_autodisable import models


PERIODIC_NAME = 'db-cleanup'
MOCK_NOW = '2021-09-20T15:00:00+03:00'
OLD_UNAVAILABLE_UNTIL = '2021-09-20T14:00:00+03:00'
UNAVAILABLE_UNTIL_IN_FUTURE = '2021-09-20T16:00:00+03:00'
PLACE_ID_1 = 1
ORIGIN_ID_1 = 'item_origin_1'
ORIGIN_ID_2 = 'item_origin_2'
ALGORITHM_NAME = 'threshold'


@pytest.mark.now(MOCK_NOW)
async def test_db_cleanup(
        enable_periodic_in_config,
        get_autodisabled_products_from_db,
        save_autodisabled_products_to_db,
        taxi_eats_retail_products_autodisable,
        testpoint,
        to_utc_datetime,
):
    enable_periodic_in_config(PERIODIC_NAME)

    @testpoint('db-cleanup-finished')
    def periodic_end_run(param):
        pass

    # set 2 autodisabled products - origin_id=1 has old force_unavailable_until
    # so it will be deleted, origin_id=2 has force_unavailable_until in future
    # so it will stay
    autodisabled_products = gen_autodisabled_products(to_utc_datetime)
    save_autodisabled_products_to_db(autodisabled_products)

    await taxi_eats_retail_products_autodisable.run_distlock_task(
        PERIODIC_NAME,
    )
    assert periodic_end_run.times_called == 1

    assert get_autodisabled_products_from_db() == [autodisabled_products[1]]


async def test_periodic_metrics(verify_periodic_metrics):
    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)


def gen_autodisabled_products(to_utc_datetime):
    return [
        # will be deleted since force_unavailable_until < now
        models.AutodisabledProduct(
            place_id=PLACE_ID_1,
            origin_id=ORIGIN_ID_1,
            force_unavailable_until=to_utc_datetime(OLD_UNAVAILABLE_UNTIL),
            algorithm_name=ALGORITHM_NAME,
            last_disabled_at=to_utc_datetime(MOCK_NOW),
        ),
        # won't be deleted since force_unavailable_until > now
        models.AutodisabledProduct(
            place_id=PLACE_ID_1,
            origin_id=ORIGIN_ID_2,
            force_unavailable_until=to_utc_datetime(
                UNAVAILABLE_UNTIL_IN_FUTURE,
            ),
            algorithm_name=ALGORITHM_NAME,
            last_disabled_at=to_utc_datetime(MOCK_NOW),
        ),
    ]
