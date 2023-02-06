import pytest


@pytest.mark.pgsql('eats_receipts', files=['failed_stq.sql'])
async def test_db_metrics_collector(taxi_eats_receipts, testpoint):
    @testpoint('eats_receipts_db_metrics_collected')
    def task_finished(data):
        return data

    await taxi_eats_receipts.invalidate_caches(clean_update=True)
    await taxi_eats_receipts.run_periodic_task(
        'eats_receipts_collect_statistics',
    )

    response = await task_finished.wait_call()
    assert response['data']['ofd_timeouts'] == 2
    assert response['data']['payture_timeouts'] == 1
    assert response['data']['average_receipt_delay'] == 240
