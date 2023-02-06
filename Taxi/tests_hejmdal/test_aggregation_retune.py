async def switch_mod(taxi_hejmdal, pgsql, mod_id, disable):
    cursor = pgsql['hejmdal'].cursor()
    query = (
        'update spec_template_mods set mod_data = \'{{"disable": {}}}\', '
        'revision = default, updated = default where id = {};'.format(
            str(disable).lower(), mod_id,
        )
    )
    cursor.execute(query)
    await taxi_hejmdal.invalidate_caches(
        clean_update=False, cache_names=['spec-template-mod-cache'],
    )
    await taxi_hejmdal.run_task('tuner/retune')


async def check_running_circuit_ids(taxi_hejmdal, expected_ids):
    response = await taxi_hejmdal.get('v1/debug/running-circuits', params={})
    assert response.status_code == 200
    running_circuits = response.json()['running_circuits']

    ids = [circuit['id'] for circuit in running_circuits]
    assert sorted(ids) == sorted(expected_ids)


async def check_running_circuit_deps(
        taxi_hejmdal, circuit_id, expected_deps, include_disabled,
):
    response = await taxi_hejmdal.get(
        'v1/debug/running-circuits',
        params={
            'circuit_id': circuit_id,
            'include_disabled': include_disabled,
        },
    )
    assert response.status_code == 200
    running_circuits = response.json()['running_circuits']
    assert len(running_circuits) == 1
    circuit_deps = running_circuits[0]['dependencies']
    assert sorted(circuit_deps) == sorted(expected_deps)


async def check_mod_usage(taxi_hejmdal, mod_id, usage_count):
    response = await taxi_hejmdal.post(
        '/v1/mod/retrieve', params={'mod_id': mod_id},
    )
    assert response.status_code == 200
    assert response.json()['usage_count'] == usage_count


async def test_retune_aggregation_disable_enable_disable_circuit(
        taxi_hejmdal, pgsql,
):
    await taxi_hejmdal.run_task('circuit_states_cache/invalidate')
    await taxi_hejmdal.run_task('services_component/invalidate')
    await taxi_hejmdal.run_task('tuner/initialize')

    await check_running_circuit_ids(
        taxi_hejmdal,
        expected_ids=[
            'host_name_1_prestable::rtc_cpu_usage',
            'host_name_2_stable::rtc_cpu_usage',
            'host_name_2_testing::rtc_cpu_usage_testing',
            'test_branch_stable_1::test_domain_name_1_yandex_net::timings_p95',
            'test_branch_stable_1::test_domain_name_1_yandex_net::timings_p98',
            'test_branch_stable_2::test_domain_name_2_yandex_net::timings_p95',
            'test_branch_stable_2::test_domain_name_2_yandex_net::timings_p98',
            'test_branch_stable_1::rtc_cpu_timings',
            'test_branch_stable_2::rtc_cpu_timings',
            'test_circuit_id',
        ],
    )
    await check_mod_usage(taxi_hejmdal, mod_id=1, usage_count=1)

    # Turn circuit on
    await switch_mod(taxi_hejmdal, pgsql, mod_id=1, disable=False)
    await check_running_circuit_ids(
        taxi_hejmdal,
        expected_ids=[
            'host_name_1_stable::rtc_cpu_usage',
            'host_name_1_prestable::rtc_cpu_usage',
            'host_name_2_stable::rtc_cpu_usage',
            'host_name_2_testing::rtc_cpu_usage_testing',
            'test_branch_stable_1::test_domain_name_1_yandex_net::timings_p95',
            'test_branch_stable_1::test_domain_name_1_yandex_net::timings_p98',
            'test_branch_stable_2::test_domain_name_2_yandex_net::timings_p95',
            'test_branch_stable_2::test_domain_name_2_yandex_net::timings_p98',
            'test_branch_stable_1::rtc_cpu_timings',
            'test_branch_stable_2::rtc_cpu_timings',
            'test_circuit_id',
        ],
    )
    await check_mod_usage(taxi_hejmdal, mod_id=1, usage_count=1)

    # Turn circuit off again
    await switch_mod(taxi_hejmdal, pgsql, mod_id=1, disable=True)
    await check_running_circuit_ids(
        taxi_hejmdal,
        expected_ids=[
            'host_name_1_prestable::rtc_cpu_usage',
            'host_name_2_stable::rtc_cpu_usage',
            'host_name_2_testing::rtc_cpu_usage_testing',
            'test_branch_stable_1::test_domain_name_1_yandex_net::timings_p95',
            'test_branch_stable_1::test_domain_name_1_yandex_net::timings_p98',
            'test_branch_stable_2::test_domain_name_2_yandex_net::timings_p95',
            'test_branch_stable_2::test_domain_name_2_yandex_net::timings_p98',
            'test_branch_stable_1::rtc_cpu_timings',
            'test_branch_stable_2::rtc_cpu_timings',
            'test_circuit_id',
        ],
    )
    await check_mod_usage(taxi_hejmdal, mod_id=1, usage_count=1)


async def test_retune_aggregation_enable_disable_enable_circuit(
        taxi_hejmdal, pgsql,
):
    # Turn circuit on
    await switch_mod(taxi_hejmdal, pgsql, mod_id=1, disable=False)

    await taxi_hejmdal.run_task('circuit_states_cache/invalidate')
    await taxi_hejmdal.run_task('services_component/invalidate')
    await taxi_hejmdal.run_task('tuner/initialize')

    await check_running_circuit_ids(
        taxi_hejmdal,
        expected_ids=[
            'host_name_1_stable::rtc_cpu_usage',
            'host_name_1_prestable::rtc_cpu_usage',
            'host_name_2_stable::rtc_cpu_usage',
            'host_name_2_testing::rtc_cpu_usage_testing',
            'test_branch_stable_1::test_domain_name_1_yandex_net::timings_p95',
            'test_branch_stable_1::test_domain_name_1_yandex_net::timings_p98',
            'test_branch_stable_2::test_domain_name_2_yandex_net::timings_p95',
            'test_branch_stable_2::test_domain_name_2_yandex_net::timings_p98',
            'test_branch_stable_1::rtc_cpu_timings',
            'test_branch_stable_2::rtc_cpu_timings',
            'test_circuit_id',
        ],
    )
    await check_mod_usage(taxi_hejmdal, mod_id=1, usage_count=1)

    # Turn circuit off
    await switch_mod(taxi_hejmdal, pgsql, mod_id=1, disable=True)
    await check_running_circuit_ids(
        taxi_hejmdal,
        expected_ids=[
            'host_name_1_prestable::rtc_cpu_usage',
            'host_name_2_stable::rtc_cpu_usage',
            'host_name_2_testing::rtc_cpu_usage_testing',
            'test_branch_stable_1::test_domain_name_1_yandex_net::timings_p95',
            'test_branch_stable_1::test_domain_name_1_yandex_net::timings_p98',
            'test_branch_stable_2::test_domain_name_2_yandex_net::timings_p95',
            'test_branch_stable_2::test_domain_name_2_yandex_net::timings_p98',
            'test_branch_stable_1::rtc_cpu_timings',
            'test_branch_stable_2::rtc_cpu_timings',
            'test_circuit_id',
        ],
    )
    await check_mod_usage(taxi_hejmdal, mod_id=1, usage_count=1)

    # Turn circuit on
    await switch_mod(taxi_hejmdal, pgsql, mod_id=1, disable=False)
    await check_running_circuit_ids(
        taxi_hejmdal,
        expected_ids=[
            'host_name_1_stable::rtc_cpu_usage',
            'host_name_1_prestable::rtc_cpu_usage',
            'host_name_2_stable::rtc_cpu_usage',
            'host_name_2_testing::rtc_cpu_usage_testing',
            'test_branch_stable_1::test_domain_name_1_yandex_net::timings_p95',
            'test_branch_stable_1::test_domain_name_1_yandex_net::timings_p98',
            'test_branch_stable_2::test_domain_name_2_yandex_net::timings_p95',
            'test_branch_stable_2::test_domain_name_2_yandex_net::timings_p98',
            'test_branch_stable_1::rtc_cpu_timings',
            'test_branch_stable_2::rtc_cpu_timings',
            'test_circuit_id',
        ],
    )
    await check_mod_usage(taxi_hejmdal, mod_id=1, usage_count=1)


async def test_retune_aggregation_deps_disable_enable_disable_circuit(
        taxi_hejmdal, pgsql,
):
    await taxi_hejmdal.run_task('circuit_states_cache/invalidate')
    await taxi_hejmdal.run_task('services_component/invalidate')
    await taxi_hejmdal.run_task('tuner/initialize')

    await check_running_circuit_deps(
        taxi_hejmdal,
        circuit_id='test_branch_stable_1::rtc_cpu_timings',
        expected_deps=[
            'host_name_1_prestable::rtc_cpu_usage',
            'test_branch_stable_1::test_domain_name_1_yandex_net::timings_p95',
            'test_branch_stable_1::test_domain_name_1_yandex_net::timings_p98',
        ],
        include_disabled=False,
    )

    await check_running_circuit_deps(
        taxi_hejmdal,
        circuit_id='test_branch_stable_1::rtc_cpu_timings',
        expected_deps=[
            'host_name_1_stable::rtc_cpu_usage',
            'host_name_1_prestable::rtc_cpu_usage',
            'test_branch_stable_1::test_domain_name_1_yandex_net::timings_p95',
            'test_branch_stable_1::test_domain_name_1_yandex_net::timings_p98',
        ],
        include_disabled=True,
    )

    await check_running_circuit_deps(
        taxi_hejmdal,
        circuit_id='test_branch_stable_2::rtc_cpu_timings',
        expected_deps=[
            'host_name_2_stable::rtc_cpu_usage',
            'test_branch_stable_2::test_domain_name_2_yandex_net::timings_p95',
            'test_branch_stable_2::test_domain_name_2_yandex_net::timings_p98',
        ],
        include_disabled=False,
    )

    await check_running_circuit_deps(
        taxi_hejmdal,
        circuit_id='test_branch_stable_2::rtc_cpu_timings',
        expected_deps=[
            'host_name_2_stable::rtc_cpu_usage',
            'test_branch_stable_2::test_domain_name_2_yandex_net::timings_p95',
            'test_branch_stable_2::test_domain_name_2_yandex_net::timings_p98',
        ],
        include_disabled=True,
    )

    # Turn circuit on
    await switch_mod(taxi_hejmdal, pgsql, mod_id=1, disable=False)

    await check_running_circuit_deps(
        taxi_hejmdal,
        circuit_id='test_branch_stable_1::rtc_cpu_timings',
        expected_deps=[
            'host_name_1_stable::rtc_cpu_usage',
            'host_name_1_prestable::rtc_cpu_usage',
            'test_branch_stable_1::test_domain_name_1_yandex_net::timings_p95',
            'test_branch_stable_1::test_domain_name_1_yandex_net::timings_p98',
        ],
        include_disabled=False,
    )

    await check_running_circuit_deps(
        taxi_hejmdal,
        circuit_id='test_branch_stable_1::rtc_cpu_timings',
        expected_deps=[
            'host_name_1_stable::rtc_cpu_usage',
            'host_name_1_prestable::rtc_cpu_usage',
            'test_branch_stable_1::test_domain_name_1_yandex_net::timings_p95',
            'test_branch_stable_1::test_domain_name_1_yandex_net::timings_p98',
        ],
        include_disabled=True,
    )

    await check_running_circuit_deps(
        taxi_hejmdal,
        circuit_id='test_branch_stable_2::rtc_cpu_timings',
        expected_deps=[
            'host_name_2_stable::rtc_cpu_usage',
            'test_branch_stable_2::test_domain_name_2_yandex_net::timings_p95',
            'test_branch_stable_2::test_domain_name_2_yandex_net::timings_p98',
        ],
        include_disabled=False,
    )

    await check_running_circuit_deps(
        taxi_hejmdal,
        circuit_id='test_branch_stable_2::rtc_cpu_timings',
        expected_deps=[
            'host_name_2_stable::rtc_cpu_usage',
            'test_branch_stable_2::test_domain_name_2_yandex_net::timings_p95',
            'test_branch_stable_2::test_domain_name_2_yandex_net::timings_p98',
        ],
        include_disabled=True,
    )

    # Turn circuit off again
    await switch_mod(taxi_hejmdal, pgsql, mod_id=1, disable=True)

    await check_running_circuit_deps(
        taxi_hejmdal,
        circuit_id='test_branch_stable_1::rtc_cpu_timings',
        expected_deps=[
            'host_name_1_prestable::rtc_cpu_usage',
            'test_branch_stable_1::test_domain_name_1_yandex_net::timings_p95',
            'test_branch_stable_1::test_domain_name_1_yandex_net::timings_p98',
        ],
        include_disabled=False,
    )

    await check_running_circuit_deps(
        taxi_hejmdal,
        circuit_id='test_branch_stable_1::rtc_cpu_timings',
        expected_deps=[
            'host_name_1_stable::rtc_cpu_usage',
            'host_name_1_prestable::rtc_cpu_usage',
            'test_branch_stable_1::test_domain_name_1_yandex_net::timings_p95',
            'test_branch_stable_1::test_domain_name_1_yandex_net::timings_p98',
        ],
        include_disabled=True,
    )

    await check_running_circuit_deps(
        taxi_hejmdal,
        circuit_id='test_branch_stable_2::rtc_cpu_timings',
        expected_deps=[
            'host_name_2_stable::rtc_cpu_usage',
            'test_branch_stable_2::test_domain_name_2_yandex_net::timings_p95',
            'test_branch_stable_2::test_domain_name_2_yandex_net::timings_p98',
        ],
        include_disabled=False,
    )

    await check_running_circuit_deps(
        taxi_hejmdal,
        circuit_id='test_branch_stable_2::rtc_cpu_timings',
        expected_deps=[
            'host_name_2_stable::rtc_cpu_usage',
            'test_branch_stable_2::test_domain_name_2_yandex_net::timings_p95',
            'test_branch_stable_2::test_domain_name_2_yandex_net::timings_p98',
        ],
        include_disabled=True,
    )
