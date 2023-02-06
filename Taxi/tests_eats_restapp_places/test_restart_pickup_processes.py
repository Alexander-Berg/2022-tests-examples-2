async def test_restart_enabled(
        taxi_eats_restapp_places, taxi_eats_restapp_places_monitor,
):
    await taxi_eats_restapp_places.run_periodic_task(
        'restart-pickup-processes-periodic',
    )
    metrics = await taxi_eats_restapp_places_monitor.get_metrics()
    assert (
        metrics['restart-pickup-processes']['restarted-pickup-processes'] == 2
    )
