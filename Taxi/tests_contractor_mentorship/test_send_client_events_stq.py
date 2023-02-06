async def test_send_client_events_for_many_drivers(stq_runner, mockserver):
    @mockserver.json_handler('/client-events/bulk-push', prefix=True)
    def handler(request):
        return {'items': []}

    await stq_runner.contractor_mentorship_send_client_events.call(
        task_id='123', args=[[{'park_id': '1', 'driver_profile_id': '2'}]],
    )
    assert handler.times_called == 1


async def test_send_client_events_no_drivers(stq_runner, mockserver):
    @mockserver.json_handler('/client-events/bulk-push', prefix=True)
    def handler(request, name):
        return {}

    await stq_runner.contractor_mentorship_send_client_events.call(
        task_id='123', args=[[]],
    )
    assert handler.times_called == 0
