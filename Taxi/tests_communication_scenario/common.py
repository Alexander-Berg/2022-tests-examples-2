async def start(taxi_communication_scenario, request, headers=None):
    await taxi_communication_scenario.run_task('distlock/config-updater')
    await taxi_communication_scenario.invalidate_caches(
        clean_update=False, cache_names=['scenario-cache'],
    )
    result = await taxi_communication_scenario.post(
        'v1/start', json=request, headers=headers,
    )
    await taxi_communication_scenario.run_periodic_task(
        'scenario-start-worker',
    )
    return result
