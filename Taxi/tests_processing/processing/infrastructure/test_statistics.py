async def test_statistics_handler(taxi_processing_monitor):
    metrics = await taxi_processing_monitor.get_metric('processing-ng')
    assert metrics.get('queue', {}).get('status')
