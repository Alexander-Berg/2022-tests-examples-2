import pytest


@pytest.fixture(name='query_calculations_count')
def _query_calculations_count(pgsql):
    def call():
        cursor = pgsql['cargo_pricing'].conn.cursor()
        cursor.execute(
            """
            SELECT count(*)
            FROM cargo_pricing.calculations
            """,
        )
        return list(cursor)[0][0]

    return call


@pytest.fixture(name='create_calc')
async def _create_calc(v1_calc_creator, confirm_usage):
    async def call(is_usage_confirmed=False):
        create_resp = await v1_calc_creator.execute()
        assert create_resp.status_code == 200
        calc_id = create_resp.json()['calc_id']
        if is_usage_confirmed:
            await confirm_usage(calc_id=calc_id)

    return call


@pytest.fixture(name='get_cleanup_stats')
async def _get_cleanup_stats(taxi_cargo_pricing, taxi_cargo_pricing_monitor):
    metrics_name = 'cargo-pricing-db-cleanup'
    root_obj_name = 'deleted-calculations'

    # instead of metrics cleanup implementation in code
    # fix previous state in tests
    metric_start_state = await taxi_cargo_pricing_monitor.get_metric(
        metrics_name,
    )

    async def call(shard):
        start_value = 0
        if metric_start_state:
            root_obj = metric_start_state.get(root_obj_name, {})
            start_value = root_obj.get(shard, 0)

        metrics = await taxi_cargo_pricing_monitor.get_metric(metrics_name)
        curr_value = metrics[root_obj_name][shard]

        return curr_value - start_value

    return call


async def test_cleanup(
        create_calc,
        run_calculations_cleanup,
        query_calculations_count,
        get_cleanup_stats,
):
    # create calc #1 and confirm usage -> shouldn't be deleted
    await create_calc(is_usage_confirmed=True)
    # create calc #2 and don't confirm usage -> should be deleted
    await create_calc(is_usage_confirmed=False)
    run_calculations_cleanup.add_rule(
        delete_confirmed_calculations_after_min=9999,
    )
    await run_calculations_cleanup()
    assert query_calculations_count() == 1
    removed_calcs_stat = await get_cleanup_stats('shard0')
    assert removed_calcs_stat == 1


async def test_cleanup_with_confirmed(
        create_calc,
        run_calculations_cleanup,
        query_calculations_count,
        get_cleanup_stats,
):
    # create calc #1 and confirm usage
    await create_calc(is_usage_confirmed=True)
    # create calc #2 and don't confirm usage
    await create_calc(is_usage_confirmed=False)
    run_calculations_cleanup.add_rule(
        delete_confirmed_calculations_after_min=0,
    )
    await run_calculations_cleanup()
    assert query_calculations_count() == 0
    removed_calcs_stat = await get_cleanup_stats('shard0')
    assert removed_calcs_stat == 2


async def test_cleanup_with_non_existing_service(
        create_calc, run_calculations_cleanup, query_calculations_count,
):
    await create_calc(is_usage_confirmed=True)
    await create_calc(is_usage_confirmed=False)
    run_calculations_cleanup.add_rule(source='foo-bar')
    await run_calculations_cleanup()
    assert query_calculations_count() == 2


async def test_cleanup_with_existing_service(
        create_calc, run_calculations_cleanup, query_calculations_count,
):
    await create_calc(is_usage_confirmed=True)
    await create_calc(is_usage_confirmed=False)
    run_calculations_cleanup.add_rule(source='foo-bar')
    # in testsuite we can't get TVM service name, so use "unknown"
    run_calculations_cleanup.add_rule(source='unknown')
    await run_calculations_cleanup()
    assert query_calculations_count() == 0


async def test_cleanup_with_null_service(
        create_calc, run_calculations_cleanup, query_calculations_count,
):
    await create_calc(is_usage_confirmed=True)
    await create_calc(is_usage_confirmed=False)

    run_calculations_cleanup.add_rule(source=None)
    await run_calculations_cleanup()
    assert query_calculations_count() == 0


@pytest.fixture(name='get_shared_parts_stats')
async def _get_shared_parts_stats(
        taxi_cargo_pricing, taxi_cargo_pricing_monitor,
):
    metrics_name = 'cargo-pricing-db-shared-parts-cnt'
    root_obj_name = 'shared-parts'
    metric_start_state = await taxi_cargo_pricing_monitor.get_metric(
        metrics_name,
    )

    async def call(shard):
        start_value = 0
        if metric_start_state:
            root_obj = metric_start_state.get(root_obj_name, {})
            start_value = root_obj.get(shard, 0)

        metrics = await taxi_cargo_pricing_monitor.get_metric(metrics_name)
        curr_value = metrics[root_obj_name][shard]
        return curr_value - start_value

    return call


@pytest.mark.config(CARGO_PRICING_ENABLE_SHARED_PARTS_STATS=True)
async def test_shared_calcs_stat(
        get_shared_parts_stats,
        v2_calc_creator,
        run_calculations_cleanup,
        config_shared_calc_parts,
        taxi_cargo_pricing,
):
    await taxi_cargo_pricing.run_distlock_task('cargo-pricing-db-cleanup')
    shared_parts_stat = await get_shared_parts_stats('shard0')
    assert shared_parts_stat == 0
    calc_response = await v2_calc_creator.execute()
    assert calc_response.status_code == 200
    await taxi_cargo_pricing.run_distlock_task('cargo-pricing-db-cleanup')
    shared_parts_stat = await get_shared_parts_stats('shard0')
    assert shared_parts_stat == 2
