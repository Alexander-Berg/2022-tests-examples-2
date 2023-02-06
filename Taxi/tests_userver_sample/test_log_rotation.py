import signal


TEST_RETRIES_COUNT = 15


async def test_log_rotation(taxi_userver_sample, userver_sample_send_signal):
    for _ in range(TEST_RETRIES_COUNT):
        await userver_sample_send_signal(signal.SIGUSR1)
        response = await taxi_userver_sample.get('ping')
        assert response.status_code == 200
