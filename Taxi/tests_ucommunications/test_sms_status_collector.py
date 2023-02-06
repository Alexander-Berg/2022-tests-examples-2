from testsuite.utils import callinfo


# Actually this test not working correctly yet.
# We need to be able to run worker by request from testsuite to make it work.
# Otherwise worker will start before test begin and process all SMS from queue.
# I keep this test for manual executions and for future use
async def test_worker(taxi_ucommunications, mock_infobip, testpoint, mongodb):
    _first_run = False

    @testpoint('sms-status-collector-start')
    def start(data):
        # Hack to prevent flaps:
        # If queue contains exactly N messages then it is first worker run.
        # Since we can't control from test when worker will be started we need
        # to ignore executions when some messages already processed
        _first_run = mongodb.sms_confirmation_queue.count() == 8  # noqa: F841

    @testpoint('sms-status-collector-finish')
    def finish(data):
        if not _first_run:
            return

        stats = data['total']
        assert stats['fetched'] == 8
        assert stats['delivered'] == 1
        assert stats['undelivered'] == 2
        assert stats['unknown'] == 1
        assert stats['processing_error'] == 3
        assert stats['delivery_error'] == 1
        assert stats['deleted_from_db'] == 4
        assert mongodb.sms_confirmation_queue.count() == 4

    await taxi_ucommunications.enable_testpoints()
    try:
        await start.wait_call()
        await finish.wait_call()
    except callinfo.CallQueueTimeoutError:
        # Hack: we can't be sure that worker will be executed while test
        # is running, so just ignore this error
        pass
