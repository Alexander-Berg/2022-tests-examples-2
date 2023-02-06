import pytest


def get_existing_offers(pgsql):
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        cursor.execute('SELECT order_id FROM ONLY cache.offers ')
        result = cursor.fetchall()
        return [v[0] for v in result]


@pytest.mark.parametrize(
    'days,offers',
    [
        (1, []),
        (30, ['order_new']),
        (100, ['order_new', 'order_may']),
        (365, ['order_new', 'order_may', 'order_old']),
    ],
    ids=['none', 'new', 'new&may', 'all'],
)
@pytest.mark.now('2020-08-10 12:00:00.0000+03')
@pytest.mark.pgsql('pricing_data_preparer', files=['offers_cache.sql'])
async def test_cache_offers_cleanup(
        taxi_pricing_admin, pgsql, days, offers, taxi_config,
):

    taxi_config.set(PRICING_DATA_PREPARER_CACHED_OFFERS_LIFETIMES=24 * days)

    response = await taxi_pricing_admin.post(
        'service/cron', json={'task_name': 'cache-offers-cleanup'},
    )
    assert response.status_code == 200

    offers_after = get_existing_offers(pgsql)

    assert sorted(offers) == sorted(offers_after)
