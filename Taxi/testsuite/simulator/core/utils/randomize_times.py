import datetime
import random


def by_interval(
        start: datetime.datetime, end: datetime.datetime,
) -> datetime.datetime:
    interval_sec = (end - start).seconds
    actual_delta_sec = random.randint(
        0, interval_sec,
    )  # including first and last

    return start + datetime.timedelta(seconds=actual_delta_sec)
