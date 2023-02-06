async def check_running_circuit_ids(
        taxi_hejmdal, expected_ids, include_disabled,
):
    response = await taxi_hejmdal.get('v1/debug/running-circuits', params={})
    assert response.status_code == 200
    running_circuits = response.json()['running_circuits']

    ids = []
    for circuit in running_circuits:
        if circuit['is_disabled'] is False or include_disabled is True:
            ids.append(circuit['id'])

    assert sorted(ids) == sorted(expected_ids)


async def test_tank_branches_filtering(taxi_hejmdal):
    await taxi_hejmdal.run_task('services_component/invalidate')
    await taxi_hejmdal.run_task('tuner/initialize')

    await check_running_circuit_ids(
        taxi_hejmdal,
        expected_ids=[
            'test_circuit_id',
            'test_service1_stable_branch_host_name::rtc_memory_usage',
            #     and tank branches must be filtered
        ],
        include_disabled=False,
    )
