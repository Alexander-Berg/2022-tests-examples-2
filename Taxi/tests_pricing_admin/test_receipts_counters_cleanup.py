import pytest


def get_existing_counters(pgsql):
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        cursor.execute('SELECT order_id FROM receipts.receipts_counters')
        result = cursor.fetchall()
        return [v[0] for v in result]


@pytest.mark.parametrize(
    'days,counters',
    [
        (1, []),
        (30, ['receipt_new']),
        (100, ['receipt_new', 'receipt_may']),
        (365, ['receipt_new', 'receipt_may', 'receipt_old']),
    ],
    ids=['none', 'new', 'new&may', 'all'],
)
@pytest.mark.now('2020-08-10 12:00:00.0000+03')
@pytest.mark.pgsql('pricing_data_preparer', files=['receipts_counters.sql'])
async def test_receipts_counters_cleanup(
        taxi_pricing_admin, pgsql, days, counters, taxi_config,
):

    taxi_config.set(PRICING_ADMIN_RECEIPTS_COUNTERS_LIFETIMES=24 * days)

    response = await taxi_pricing_admin.post(
        'service/cron', json={'task_name': 'receipts-counters-cleanup'},
    )
    assert response.status_code == 200

    counters_after = get_existing_counters(pgsql)

    assert sorted(counters) == sorted(counters_after)
