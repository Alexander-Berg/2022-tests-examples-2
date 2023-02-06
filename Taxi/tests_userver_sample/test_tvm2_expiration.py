import pytest

SECONDS_IN_HOUR = 60 * 60


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_HEALTH={
        'warn-on-service-tickets-delay-hours': 2,
        'error-on-service-tickets-delay-hours': 11,
        'warn-on-public-keys-delay-hours': 48,
        'error-on-public-keys-delay-hours': 60,
    },
)
async def test_tvm2_tickets_expire(taxi_userver_sample, mocked_time):
    response = await taxi_userver_sample.get('ping')
    assert response.status_code == 200

    mocked_time.sleep(SECONDS_IN_HOUR)

    response = await taxi_userver_sample.get('ping')
    assert response.status_code == 200

    mocked_time.sleep(SECONDS_IN_HOUR * 5)

    response = await taxi_userver_sample.get('ping')
    assert response.status_code == 200

    mocked_time.sleep(SECONDS_IN_HOUR * 5)
    response = await taxi_userver_sample.get('ping')
    assert response.status_code == 500

    mocked_time.sleep(SECONDS_IN_HOUR)
    response = await taxi_userver_sample.get('ping')
    assert response.status_code == 500

    await taxi_userver_sample.invalidate_caches(clean_update=False)
    response = await taxi_userver_sample.get('ping')
    assert response.status_code == 200

    mocked_time.sleep(SECONDS_IN_HOUR * 11)
    response = await taxi_userver_sample.get('ping')
    assert response.status_code == 500


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_HEALTH={
        'warn-on-service-tickets-delay-hours': 200,
        'error-on-service-tickets-delay-hours': 1100,
        'warn-on-public-keys-delay-hours': 48,
        'error-on-public-keys-delay-hours': 60,
    },
)
async def test_tvm2_keys_expire(taxi_userver_sample, testpoint):
    delay_sec = 0

    @testpoint('tvm2-get-component-health')
    def _tp_gch(request):
        return delay_sec

    response = await taxi_userver_sample.get('ping')
    assert response.status_code == 200

    delay_sec += SECONDS_IN_HOUR

    response = await taxi_userver_sample.get('ping')
    assert response.status_code == 200

    delay_sec += SECONDS_IN_HOUR * 47

    response = await taxi_userver_sample.get('ping')
    assert response.status_code == 200

    delay_sec += SECONDS_IN_HOUR * 12
    response = await taxi_userver_sample.get('ping')
    assert response.status_code == 500

    delay_sec += SECONDS_IN_HOUR
    response = await taxi_userver_sample.get('ping')
    assert response.status_code == 500

    delay_sec = 0
    await taxi_userver_sample.invalidate_caches(clean_update=False)
    response = await taxi_userver_sample.get('ping')
    assert response.status_code == 200

    delay_sec += SECONDS_IN_HOUR * 60
    response = await taxi_userver_sample.get('ping')
    assert response.status_code == 500
