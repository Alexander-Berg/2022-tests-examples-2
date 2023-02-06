import datetime


async def test_pickup_metrics(
        taxi_eats_restapp_places, taxi_eats_restapp_places_monitor,
):
    await taxi_eats_restapp_places.run_periodic_task(
        'eats-restapp-places-' 'pickup-metrics-periodic-task-periodic',
    )
    metrics = await taxi_eats_restapp_places_monitor.get_metrics()
    assert metrics['pickup-metrics-periodic']['pickup_status_rows'] == 3
    assert metrics['pickup-metrics-periodic']['pickups_per_day'] == 2
    assert metrics['pickup-metrics-periodic']['enabled_pickups'] == 1
    assert metrics['pickup-metrics-periodic']['disabled_pickups'] == 2
    assert (
        metrics['pickup-metrics-periodic']['pickups_enabled_per_day_by_log']
        == 1
    )
    assert (
        metrics['pickup-metrics-periodic']['pickups_disabled_per_day_by_log']
        == 1
    )


async def test_pickup_daily_metrics_not_update_time(
        taxi_eats_restapp_places,
        taxi_eats_restapp_places_monitor,
        mocked_time,
):
    today = datetime.datetime.today()

    test_date = datetime.datetime(today.year, today.month, today.day, 10, 0)

    mocked_time.set(test_date)

    await taxi_eats_restapp_places.run_periodic_task(
        'eats-restapp-places-' 'pickup-metrics-periodic-task-periodic',
    )
    metrics = await taxi_eats_restapp_places_monitor.get_metrics()

    assert (
        'yesterdays_pickups' not in metrics['pickup-metrics-periodic'].keys()
    )
    assert (
        'yesterdays_pickups_enable'
        not in metrics['pickup-metrics-periodic'].keys()
    )
    assert (
        'yesterdays_pickups_disabled'
        not in metrics['pickup-metrics-periodic'].keys()
    )


async def test_pickup_daily_metrics_update_time(
        taxi_eats_restapp_places,
        taxi_eats_restapp_places_monitor,
        mocked_time,
):
    today = datetime.datetime.today()

    test_date = datetime.datetime(today.year, today.month, today.day, 21, 1)

    mocked_time.set(test_date)

    await taxi_eats_restapp_places.run_periodic_task(
        'eats-restapp-places-' 'pickup-metrics-periodic-task-periodic',
    )
    metrics = await taxi_eats_restapp_places_monitor.get_metrics()

    assert metrics['pickup-metrics-periodic']['yesterdays_pickups'] == 1
    assert (
        metrics['pickup-metrics-periodic']['yesterdays_pickups_enabled'] == 1
    )
    assert (
        metrics['pickup-metrics-periodic']['yesterdays_pickups_disabled'] == 1
    )
