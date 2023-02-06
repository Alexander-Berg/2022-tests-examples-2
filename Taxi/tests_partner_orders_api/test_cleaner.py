import datetime

import pytest

JOB_NAME = 'cleanup_partner_orders_api_psql_orders'


def get_orders_count(psql):
    cursor = psql.cursor()
    cursor.execute(
        'SELECT COUNT(*) FROM partner_orders_api.order_price_details '
        'UNION ALL '
        'SELECT COUNT(*) FROM partner_orders_api.price_details_items;',
    )
    return list(r[0] for r in cursor)


@pytest.mark.pgsql(
    'partner_orders_api', files=['order_price_details_insert.sql'],
)
@pytest.mark.config(
    PARTNER_ORDERS_API_PSQL_CLEANUP_ENABLED=True,
    PARTNER_ORDERS_API_PSQL_CLEANUP_TTLS_V2={'price_detail': 1},
)
async def test_partner_orders_api_cleanup(
        taxi_partner_orders_api, pgsql, mocked_time,
):
    db = pgsql['partner_orders_api']
    timestamp = datetime.datetime.now()
    mocked_time.set(timestamp)
    await taxi_partner_orders_api.tests_control(invalidate_caches=False)
    await taxi_partner_orders_api.run_task('distlock/psql-cleaner')
    assert get_orders_count(db) == [2, 3]

    timestamp += datetime.timedelta(minutes=31)
    mocked_time.set(timestamp)
    await taxi_partner_orders_api.tests_control(invalidate_caches=False)
    await taxi_partner_orders_api.run_task('distlock/psql-cleaner')
    assert get_orders_count(db) == [2, 3]

    timestamp += datetime.timedelta(minutes=30)
    mocked_time.set(timestamp)
    await taxi_partner_orders_api.tests_control(invalidate_caches=False)
    await taxi_partner_orders_api.run_task('distlock/psql-cleaner')
    assert get_orders_count(db) == [1, 1]

    timestamp += datetime.timedelta(minutes=60)
    mocked_time.set(timestamp)
    await taxi_partner_orders_api.tests_control(invalidate_caches=False)
    await taxi_partner_orders_api.run_task('distlock/psql-cleaner')
    assert get_orders_count(db) == [0, 0]
