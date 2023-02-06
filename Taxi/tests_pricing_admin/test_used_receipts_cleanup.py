import pytest


def get_receipts(pgsql):
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        cursor.execute('SELECT order_id FROM ONLY receipts.custom_receipts')
        result = cursor.fetchall()
        return [v[0] for v in result]


@pytest.mark.parametrize(
    'days, receipts, unused_warning',
    [
        (
            1,
            ['receipt_old_unused', 'receipt_new_unused', 'receipt_may_unused'],
            ['receipt_old_unused', 'receipt_new_unused', 'receipt_may_unused'],
        ),
        (
            30,
            [
                'receipt_new_used',
                'receipt_old_unused',
                'receipt_new_unused',
                'receipt_may_unused',
            ],
            ['receipt_old_unused', 'receipt_may_unused'],
        ),
        (
            100,
            [
                'receipt_new_used',
                'receipt_may_used',
                'receipt_old_unused',
                'receipt_new_unused',
                'receipt_may_unused',
            ],
            ['receipt_old_unused'],
        ),
        (
            365,
            [
                'receipt_new_used',
                'receipt_may_used',
                'receipt_old_used',
                'receipt_old_unused',
                'receipt_new_unused',
                'receipt_may_unused',
            ],
            [],
        ),
    ],
    ids=['none', 'new', 'new&may', 'all'],
)
@pytest.mark.now('2020-08-10 12:00:00.0000+03')
@pytest.mark.pgsql('pricing_data_preparer', files=['custom_receipts.sql'])
async def test_used_receipts_cleanup(
        taxi_pricing_admin,
        pgsql,
        days,
        receipts,
        unused_warning,
        taxi_config,
        testpoint,
):

    taxi_config.set(PRICING_ADMIN_USED_RECEIPTS_LIFETIMES=24 * days)

    unused = []

    @testpoint('unused_receipt_testpoint')
    def unused_receipt_testpoint(data):
        unused.append(data)

    response = await taxi_pricing_admin.post(
        'service/cron', json={'task_name': 'used-receipts-cleanup'},
    )
    assert response.status_code == 200

    receipts_after = get_receipts(pgsql)

    assert sorted(receipts) == sorted(receipts_after)
    assert unused == unused_warning
