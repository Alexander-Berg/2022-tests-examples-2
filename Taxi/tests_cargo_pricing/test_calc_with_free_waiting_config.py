async def test_calc_with_changed_free_waiting_by_config(
        v1_calc_creator, taxi_config, taxi_cargo_pricing,
):
    taxi_requirements = [{}, {'door_to_door': True, 'cargo_type': 'van'}]
    source_free_waitings = [120, 600]
    destination_free_waitings = [180, 600]
    taxi_config.set_values(
        {
            'CARGO_TARIFFS_FREE_WAITING': {
                'moscow': {
                    'cargocorp': {
                        'source': {
                            'free_waiting_time': source_free_waitings[0],
                            'free_waiting_time_with_door_to_door': (
                                source_free_waitings[1]
                            ),
                        },
                        'destination': {
                            'free_waiting_time': destination_free_waitings[0],
                            'free_waiting_time_with_door_to_door': (
                                destination_free_waitings[1]
                            ),
                        },
                    },
                },
            },
        },
    )
    for i in range(2):
        source_free_waiting = source_free_waitings[i]
        destination_free_waiting = destination_free_waitings[i]
        free_waiting_time = {
            'pickup': source_free_waiting,
            'dropoff': destination_free_waiting,
            'return': destination_free_waiting,
        }
        v1_calc_creator.payload['taxi_requirements'] = taxi_requirements[i]
        await taxi_cargo_pricing.invalidate_caches()
        response = await v1_calc_creator.execute()
        assert response.status_code == 200
        resp = response.json()
        paid_waiting = 0
        paid_waiting_in_destination = 0
        for waypoint in resp['details']['waypoints']:
            waiting = waypoint['waiting']
            free_waiting = free_waiting_time[waypoint['type']]
            assert free_waiting == int(waiting['free_waiting_time'])
            waypoint_paid_waiting = max(
                0, int(waiting['total_waiting']) - free_waiting,
            )
            assert waypoint_paid_waiting == int(waiting['paid_waiting'])
            if waypoint['type'] == 'pickup':
                paid_waiting += waypoint_paid_waiting
            else:
                paid_waiting_in_destination += waypoint_paid_waiting
        assert int(resp['details']['paid_waiting_time']) == paid_waiting
        assert (
            int(resp['details']['paid_waiting_in_destination_time'])
            == paid_waiting_in_destination
        )
