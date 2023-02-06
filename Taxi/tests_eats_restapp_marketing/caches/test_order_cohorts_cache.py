import pytest


@pytest.mark.yt(
    static_table_data=['yt_empty_order_cohorts_summary_table.yaml'],
)
@pytest.mark.config(
    EATS_RESTAPP_MARKETING_ADVERT_ORDERS_STATS={
        'download_statistics': {
            'cluster': 'yt-local',
            'order_statisics': '//home/testsuite/orders',
            'task_period': 60,
            'batch_size': 1000,
            'order_cohorts_summary': '//home/testsuite/order_cohorts_summary',
        },
    },
)
async def test_cache_update_succeeded_on_empty_table(
        taxi_eats_restapp_marketing, yt_apply, testpoint,
):
    @testpoint('order-cohorts-cache_update_succeeded')
    def cache_update_succeeded(data):
        pass

    @testpoint('order-cohorts-cache_update_failed')
    def cache_update_failed(data):
        pass

    await taxi_eats_restapp_marketing.invalidate_caches(clean_update=False)

    assert cache_update_succeeded.times_called > 1
    assert cache_update_failed.times_called == 0
