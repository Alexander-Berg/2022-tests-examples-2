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


async def test_bad_rps_aggregation(taxi_hejmdal):
    await taxi_hejmdal.run_task('circuit_states_cache/invalidate')
    await taxi_hejmdal.run_task('services_component/invalidate')
    await taxi_hejmdal.run_task('tuner/initialize')

    await check_running_circuit_ids(
        taxi_hejmdal=taxi_hejmdal,
        expected_ids=[
            'hejmdal_dirlink::hejmdal.yandex.net::bad_rps',
            'hejmdal_dirlink::hejmdal.yandex.net/view2_GET::bad_rps',
            'hejmdal_dirlink::hejmdal.yandex.net/view_POST::bad_rps',
            'hejmdal_dirlink::hejmdal.yandex.net::timings_p95',
            'hejmdal_dirlink::hejmdal.yandex.net::timings_p98',
            'hejmdal_dirlink::hejmdal.yandex.net/view2_GET::ok_rps',
            'hejmdal_dirlink::hejmdal.yandex.net/view_POST::500_rps_low',
            'hejmdal_dirlink::500_low_rps_aggregation',
            'hejmdal_dirlink::timings_p95_aggregation',
            'hejmdal_dirlink::timings_p98_aggregation',
            'hejmdal_dirlink::bad_rps_aggregation',
            'hejmdal_dirlink::ok_rps_aggregation',
        ],
    )

    await check_running_circuit_deps(
        taxi_hejmdal=taxi_hejmdal,
        circuit_id='hejmdal_dirlink::bad_rps_aggregation',
        expected_deps=[
            'hejmdal_dirlink::hejmdal.yandex.net/view2_GET::bad_rps',
            'hejmdal_dirlink::hejmdal.yandex.net/view_POST::bad_rps',
            'hejmdal_dirlink::hejmdal.yandex.net::bad_rps',
        ],
        include_disabled=False,
    )
    await check_running_circuit_deps(
        taxi_hejmdal=taxi_hejmdal,
        circuit_id='hejmdal_dirlink::ok_rps_aggregation',
        expected_deps=[
            'hejmdal_dirlink::hejmdal.yandex.net/view2_GET::ok_rps',
        ],
        include_disabled=False,
    )
    await check_running_circuit_deps(
        taxi_hejmdal=taxi_hejmdal,
        circuit_id='hejmdal_dirlink::500_low_rps_aggregation',
        expected_deps=[
            'hejmdal_dirlink::hejmdal.yandex.net/view_POST::500_rps_low',
        ],
        include_disabled=False,
    )
    await check_running_circuit_deps(
        taxi_hejmdal=taxi_hejmdal,
        circuit_id='hejmdal_dirlink::timings_p95_aggregation',
        expected_deps=['hejmdal_dirlink::hejmdal.yandex.net::timings_p95'],
        include_disabled=False,
    )
    await check_running_circuit_deps(
        taxi_hejmdal=taxi_hejmdal,
        circuit_id='hejmdal_dirlink::timings_p98_aggregation',
        expected_deps=['hejmdal_dirlink::hejmdal.yandex.net::timings_p98'],
        include_disabled=False,
    )
