async def test_monitor(taxi_arcadia_userver_test_monitor):
    metrics = await taxi_arcadia_userver_test_monitor.get_metrics()
    assert '$version' in metrics
