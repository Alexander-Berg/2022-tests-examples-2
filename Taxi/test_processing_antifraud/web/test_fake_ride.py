import pytest


@pytest.mark.config(
    ANTIFRAUD_FAKE_RIDE_TRAVEL_TIME=60,
    ANTIFRAUD_SKIP_FAKE_RIDE_CHECK=['delivery'],
)
@pytest.mark.parametrize(
    'tariff_class,order_status,taxi_status,travel_time,fake',
    [
        ('econom', 'finished', 'complete', 120, False),
        ('econom', 'finished', 'canceled', 120, False),
        ('econom', 'finished', 'complete', 10, True),
        ('econom', 'finished', 'complete', 60, True),
        ('econom', 'finished', 'cancelled', 60, False),
        ('delivery', 'finished', 'complete', 10, False),
    ],
)
async def test_need_accept(
        web_processing_antifraud,
        tariff_class,
        order_status,
        taxi_status,
        travel_time,
        fake,
):
    response = await web_processing_antifraud.fake_ride.make_request(
        tariff_class=tariff_class,
        order_status=order_status,
        taxi_status=taxi_status,
        travel_time=travel_time,
    )
    assert response.status == 200

    content = await response.json()
    assert content == {'is_fake_ride': fake}


@pytest.mark.config(
    ANTIFRAUD_FAKE_RIDE_TRAVEL_TIME=100,
    PROCESSING_ANTIFRAUD_ENABLE_TOTAL_TIME_THRESHOLD=True,
    PROCESSING_ANTIFRAUD_ENABLE_TRAVEL_TIME_THRESHOLD=False,
    PROCESSING_ANTIFRAUD_TOTAL_TIME_AFTER_ASSIGNMENT_THRESHOLD=60,
)
@pytest.mark.parametrize(
    'tariff_class,order_status,taxi_status,travel_time,'
    'total_time_after_assignment,fake',
    [
        ('econom', 'finished', 'complete', 1, 120, False),
        ('econom', 'finished', 'canceled', 2, 120, False),
        ('econom', 'finished', 'complete', 103, 10, True),
        ('econom', 'finished', 'complete', 104, 60, True),
        ('econom', 'finished', 'cancelled', 105, 60, False),
    ],
)
async def test_check_total_time(
        web_processing_antifraud,
        tariff_class,
        order_status,
        taxi_status,
        travel_time,
        total_time_after_assignment,
        fake,
):
    response = await web_processing_antifraud.fake_ride.make_request(
        tariff_class=tariff_class,
        order_status=order_status,
        taxi_status=taxi_status,
        travel_time=travel_time,
        total_time_after_assignment=total_time_after_assignment,
    )
    assert response.status == 200

    content = await response.json()
    assert content == {'is_fake_ride': fake}


@pytest.mark.config(
    ANTIFRAUD_FAKE_RIDE_TRAVEL_TIME=60,
    PROCESSING_ANTIFRAUD_ENABLE_TOTAL_TIME_THRESHOLD=False,
    PROCESSING_ANTIFRAUD_ENABLE_TRAVEL_TIME_THRESHOLD=False,
    PROCESSING_ANTIFRAUD_TOTAL_TIME_AFTER_ASSIGNMENT_THRESHOLD=60,
)
@pytest.mark.parametrize(
    'tariff_class,order_status,taxi_status,travel_time,'
    'total_time_after_assignment,fake',
    [
        ('econom', 'finished', 'complete', 10, 10, False),
        ('econom', 'finished', 'complete', 60, 60, False),
    ],
)
async def test_check_disabled_total_time(
        web_processing_antifraud,
        tariff_class,
        order_status,
        taxi_status,
        travel_time,
        total_time_after_assignment,
        fake,
):
    response = await web_processing_antifraud.fake_ride.make_request(
        tariff_class=tariff_class,
        order_status=order_status,
        taxi_status=taxi_status,
        travel_time=travel_time,
        total_time_after_assignment=total_time_after_assignment,
    )
    assert response.status == 200

    content = await response.json()
    assert content == {'is_fake_ride': fake}


@pytest.mark.config(
    ANTIFRAUD_FAKE_RIDE_TRAVEL_TIME=100,
    PROCESSING_ANTIFRAUD_TOTAL_TIME_AFTER_ASSIGNMENT_THRESHOLD=60,
)
@pytest.mark.parametrize(
    'tariff_class,order_status,taxi_status,travel_time,'
    'total_time_after_assignment,travel_time_threshold_enabled,'
    'total_time_threshold_enabled,fake',
    [
        # both enabled
        ('econom', 'finished', 'complete', 99, 59, True, True, True),
        ('econom', 'finished', 'complete', 99, 61, True, True, False),
        ('econom', 'finished', 'complete', 101, 59, True, True, False),
        ('econom', 'finished', 'complete', 101, 61, True, True, False),
        # only travel enabled
        ('econom', 'finished', 'complete', 99, 59, True, False, True),
        ('econom', 'finished', 'complete', 99, 61, True, False, True),
        ('econom', 'finished', 'complete', 101, 59, True, False, False),
        ('econom', 'finished', 'complete', 101, 61, True, False, False),
        # only total enabled
        ('econom', 'finished', 'complete', 99, 59, False, True, True),
        ('econom', 'finished', 'complete', 99, 61, False, True, False),
        ('econom', 'finished', 'complete', 101, 59, False, True, True),
        ('econom', 'finished', 'complete', 101, 61, False, True, False),
        # both disabled
        ('econom', 'finished', 'complete', 99, 59, False, False, False),
        ('econom', 'finished', 'complete', 99, 61, False, False, False),
        ('econom', 'finished', 'complete', 101, 59, False, False, False),
        ('econom', 'finished', 'complete', 101, 61, False, False, False),
    ],
)
async def test_check_different_config_settings(
        web_processing_antifraud,
        taxi_config,
        tariff_class,
        order_status,
        taxi_status,
        travel_time,
        total_time_after_assignment,
        travel_time_threshold_enabled,
        total_time_threshold_enabled,
        fake,
):
    taxi_config.set_values(
        {
            'PROCESSING_ANTIFRAUD_ENABLE_TRAVEL_TIME_THRESHOLD': (
                travel_time_threshold_enabled
            ),
            'PROCESSING_ANTIFRAUD_ENABLE_TOTAL_TIME_THRESHOLD': (
                total_time_threshold_enabled
            ),
        },
    )
    response = await web_processing_antifraud.fake_ride.make_request(
        tariff_class=tariff_class,
        order_status=order_status,
        taxi_status=taxi_status,
        travel_time=travel_time,
        total_time_after_assignment=total_time_after_assignment,
    )
    assert response.status == 200

    content = await response.json()
    assert content == {'is_fake_ride': fake}
