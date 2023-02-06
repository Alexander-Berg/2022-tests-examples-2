# flake8: noqa
# pylint: disable=import-error,wildcard-import


async def test_metrics(taxi_market_shops_monitor):
    stats = await taxi_market_shops_monitor.get_metric('cache')
    assert stats['shops-storage-cache']['current-documents-count'] == 11

    stats = await taxi_market_shops_monitor.get_metric('shops-storage-cache')
    assert stats['data-version'] == 123
