import datetime


EPOCH = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)


NOW = datetime.datetime(2020, 6, 30, 10, 10, tzinfo=datetime.timezone.utc)


def time_to_string(dttm: datetime.datetime) -> str:
    dttm_str = dttm.isoformat()
    return dttm_str[:-3] + dttm_str[-2:]
