async def test_update_unique_driver_id(
        db_select_orders,
        taxi_eats_performer_subventions,
        mockserver,
        make_order,
):
    order_nr_1 = 'order-nr-1'
    park_driver_profile_id_1 = 'park-driver-profile-id-1'
    order_nr_2 = 'order-nr-2'
    park_driver_profile_id_2 = 'park-driver-profile-id-2'
    order_status = 'created'

    make_order(
        eats_id=order_nr_1,
        order_status=order_status,
        park_driver_profile_id=park_driver_profile_id_1,
    )

    make_order(
        eats_id=order_nr_2,
        order_status=order_status,
        park_driver_profile_id=park_driver_profile_id_2,
    )

    unique_driver_id_1 = 'unique-driver-id-1'
    unique_driver_id_2 = 'unique-driver-id-2'

    @mockserver.json_handler(
        '/unique-drivers/v1/driver/uniques/retrieve_by_profiles',
    )
    def _mock_eats_unique_drivers(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            json={
                'uniques': [
                    {
                        'park_driver_profile_id': park_driver_profile_id_1,
                        'data': {'unique_driver_id': unique_driver_id_1},
                    },
                    {
                        'park_driver_profile_id': park_driver_profile_id_2,
                        'data': {'unique_driver_id': unique_driver_id_2},
                    },
                ],
            },
            status=200,
        )

    task_name = 'update-unique-driver-id-periodic'
    await taxi_eats_performer_subventions.run_periodic_task(task_name)

    # times_called == 2 because the data was processed in 2 coroutines
    assert _mock_eats_unique_drivers.times_called == 2

    orders = db_select_orders()
    assert len(orders) == 2

    order = db_select_orders()[0]
    assert order['eats_id'] == order_nr_1
    assert order['unique_driver_id'] == unique_driver_id_1
    assert order['park_driver_profile_id'] == park_driver_profile_id_1

    order = db_select_orders()[1]
    assert order['eats_id'] == order_nr_2
    assert order['unique_driver_id'] == unique_driver_id_2
    assert order['park_driver_profile_id'] == park_driver_profile_id_2
