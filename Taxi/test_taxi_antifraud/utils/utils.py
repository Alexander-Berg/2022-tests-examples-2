import datetime

from taxi.util import dates as dates_utils


def _fake_datetime_to_datetime(dtm):
    return datetime.datetime.fromtimestamp(dtm.timestamp())


def convert_datetimes(rows, fields):
    for row in rows:
        for field in fields:
            if field in row:
                if isinstance(row[field], str):
                    row[field] = dates_utils.parse_timestring(
                        row[field], timezone='UTC',
                    )
                else:
                    row[field] = _fake_datetime_to_datetime(row[field])

    return rows


def del_fields(rows, fields):
    for row in rows:
        for field in fields:
            if field in row:
                del row[field]
    return rows


def check_dict_is_subdict(dict_, subdict):
    for key, value in subdict.items():
        assert key in dict_
        assert value == dict_[key]
