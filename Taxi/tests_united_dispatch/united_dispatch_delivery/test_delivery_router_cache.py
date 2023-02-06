import pytest


async def test_router_stats(
        exp_delivery_gamble_settings,
        exp_delivery_configs,
        create_segment,
        state_waybill_proposed,
        mock_maps,
        taxi_united_dispatch_delivery,
        taxi_united_dispatch_delivery_monitor,
):
    await taxi_united_dispatch_delivery.tests_control(reset_metrics=True)

    mock_maps.add_route(
        points=[[37.400000, 55.700000], [37.400000, 55.700000]],
        car_time=0,
        car_distance=0,
        pedestrian_time=0,
        pedestrian_distance=0,
    )
    create_segment()
    create_segment()

    await exp_delivery_gamble_settings(disable_maps_router=False)
    await exp_delivery_configs(delivery_gamble_settings=False)
    await state_waybill_proposed()

    stats = await taxi_united_dispatch_delivery_monitor.get_metric(
        'delivery-planner-router',
    )
    assert stats == {
        'client_routing_linear_router': {
            '$meta': {'solomon_children_labels': 'router_type'},
        },
        'client_routing_router': {
            'CarRouter': 1,
            'PedestrianRouter': 1,
            '$meta': {'solomon_children_labels': 'router_type'},
        },
        'custom_ud_linear_fallback': {
            '$meta': {'solomon_children_labels': 'router_type'},
        },
    }


# TODO: use invalidate caches after
# TAXICOMMON-5198
@pytest.mark.config(
    UNITED_DISPATCH_REDIS_ROUTER_CACHE_SETTINGS={
        'enabled': True,
        'redis-settings': {'max_retries': 3, 'timeout_single': 100},
        'settings': {'__default__': {'lifetime': 600}},
    },
)
async def test_redis_cache(
        exp_delivery_gamble_settings,
        exp_delivery_configs,
        create_segment,
        state_waybill_proposed,
        mock_maps,
        taxi_united_dispatch_delivery,
        taxi_united_dispatch_delivery_monitor,
        redis_store,
):
    redis_store.set(
        'router-cache::'
        + 'CarRouter-(37.400000, 55.700000)'
        + '-(37.400000, 55.700000)',
        '{"distance":0.0,"time":0}',
    )
    redis_store.set(
        'router-cache::'
        + 'PedestrianRouter-(37.400000, 55.700000)'
        + '-(37.400000, 55.700000)',
        '{"distance":0.0,"time":0}',
    )

    await taxi_united_dispatch_delivery.tests_control(reset_metrics=True)

    mock_maps.add_route(
        points=[[37.400000, 55.700000], [37.400000, 55.700000]],
        car_time=0,
        car_distance=0,
        pedestrian_time=0,
        pedestrian_distance=0,
    )
    create_segment()

    await exp_delivery_gamble_settings(disable_maps_router=False)
    await exp_delivery_configs(delivery_gamble_settings=False)
    await state_waybill_proposed()

    stats = await taxi_united_dispatch_delivery_monitor.get_metric(
        'delivery-planner-router',
    )
    assert stats == {
        'client_routing_linear_router': {
            '$meta': {'solomon_children_labels': 'router_type'},
        },
        'client_routing_router': {
            '$meta': {'solomon_children_labels': 'router_type'},
        },
        'custom_ud_linear_fallback': {
            '$meta': {'solomon_children_labels': 'router_type'},
        },
    }
