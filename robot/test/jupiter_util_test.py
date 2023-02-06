import datetime
import robot.jupiter.library.python.jupiter_util as jupiter_util
import time
import os


def tz_shifter(tz):
    def decorator(func):
        def wrapper():
            old_tz = os.getenv("TZ")
            os.putenv("TZ", tz)
            time.tzset()

            func()

            if old_tz:
                os.putenv("TZ", old_tz)
            else:
                os.unsetenv("TZ")
            time.tzset()

        return wrapper
    return decorator


def check_state_from_timestamp():
    state = jupiter_util.get_state_from_timestamp(1565016000)
    assert state == "20190805-174000", "Invalid state from timestamp convertation"


def check_state_to_timestamp():
    timestamp = jupiter_util.state_to_timestamp("20190805-174000")
    assert timestamp == 1565016000, "Invalid state to timestamp convertation"


def check_state_to_datetime():
    state = "20190805-174000"
    dt_util = jupiter_util.state_to_datetime(state)
    dt_local = datetime.datetime.fromtimestamp(jupiter_util.state_to_timestamp(state))
    # check to avoid comparsion of offset-naive and offset-aware datetimes error
    assert dt_util == dt_local, "Inconsistent state to datetime/timestamp convertation"


@tz_shifter(":UTC")
def test_state_from_timestamp_utc():
    check_state_from_timestamp()


@tz_shifter(":Europe/Moscow")
def test_state_from_timestamp_msk():
    check_state_from_timestamp()


@tz_shifter(":UTC")
def test_state_to_timestamp_utc():
    check_state_to_timestamp()


@tz_shifter(":Europe/Moscow")
def test_state_to_timestamp_msk():
    check_state_to_timestamp()


@tz_shifter(":UTC")
def test_state_to_datetime_utc():
    check_state_to_datetime()


@tz_shifter(":Europe/Moscow")
def test_state_to_datetime_msk():
    check_state_to_datetime()
