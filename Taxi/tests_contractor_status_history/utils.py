import datetime

from dateutil import parser
import pytz


def parse_date_str(date_str):
    return parser.parse(date_str).astimezone(pytz.UTC)


def date_str_to_sec(date_str):
    return int(parse_date_str(date_str).timestamp())


def date_from_ms(stamp):
    return datetime.datetime.fromtimestamp(stamp / 1000.0, pytz.UTC)


async def reset_arch_status(
        taxi_contractor_status_history, mocked_time, testpoint, now_tp,
):
    to_day = now_tp.toordinal()
    from_day = to_day - 15

    @testpoint('table-arch-state-checker-tp')
    def _checker_testpoint(data):
        pass

    # resetting statuses for all tables
    for day in range(from_day, to_day):
        mocked_time.set(datetime.datetime.fromordinal(day))
        await taxi_contractor_status_history.enable_testpoints()
        _checker_testpoint.flush()
        await taxi_contractor_status_history.run_periodic_task(
            'tables-arch-checker',
        )
        await _checker_testpoint.wait_call()
