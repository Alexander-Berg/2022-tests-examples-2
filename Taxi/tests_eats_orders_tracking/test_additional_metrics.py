import pytest

TRACKING_URL = '/eats/v1/eats-orders-tracking/v1/tracking'
MOCK_DATETIME = '2020-10-28T18:20:00.00+00:00'


@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking',
    files=['fill_tracked_order_payload.sql', 'fill_courier_with_claim.sql'],
)
async def test_eda_static_courier_info_metric(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        taxi_eats_orders_tracking_monitor,
):
    statistics_before = await taxi_eats_orders_tracking_monitor.get_metric(
        'courier-info',
    )
    await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )
    statistics_after = await taxi_eats_orders_tracking_monitor.get_metric(
        'courier-info',
    )
    assert statistics_after['no-info'] - statistics_before['no-info'] == 1
    assert (
        statistics_after['grocery-no-info']
        - statistics_before['grocery-no-info']
        == 1
    )
    # заказ с номером 000000-000001 не имеет статической информации о курьере
    # заказ с номером 000000-000005 лавка не имеет статической
    # информации о курьере (постфикс -grocery)
    # заказ с номером 000000-000000 имеет статическую информацию о курьере
    # заказ с номером 000000-000002 marketplace
    # заказ с номером 000000-000003 pickup
    # заказ с номером 000000-000004 отсутствие taken_at
