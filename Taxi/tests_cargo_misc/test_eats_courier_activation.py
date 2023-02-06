DEFAULT_COURIER_ID = 'courier_id_1'


def get_courier_profile(courier_id=DEFAULT_COURIER_ID):
    _id = {'courier_id': courier_id}
    data = {'external_ids': {'eats': 'courier_dbid-1'}}
    return {
        'park_id': 'park1',
        'courier_app': 'taximeter',
        'transport_type': 'pedestrian',
        'first_name': 'first_name',
        'middle_name': 'middle_name',
        'last_name': 'last_name',
        'phone': '+70000000001',
        'orders_provider': 'eda',
        'work_status': 'working',
        **_id,
        'data': data,
    }


async def test_sample_tasks(
        stq_runner, driver_profiles, mockserver, testpoint,
):
    @mockserver.json_handler('/client-events/push')
    def _mock_client_events(request):
        return mockserver.make_response(status=200, json={'version': '777'})

    @testpoint('GetChannel')
    def _get_channel_testpoint(data):
        assert data == f'contractor:park1_driver1'

    driver_profiles.set_profiles(
        [get_courier_profile(courier_id=DEFAULT_COURIER_ID)],
    )

    await stq_runner.eats_courier_activation.call(
        task_id='task_id_1', kwargs={'courierId': DEFAULT_COURIER_ID},
    )

    assert _mock_client_events.times_called == 1
    assert _get_channel_testpoint.times_called == 1
