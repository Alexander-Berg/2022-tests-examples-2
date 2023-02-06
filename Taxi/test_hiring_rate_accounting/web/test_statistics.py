import datetime
import uuid

import dateutil.parser as date_util


async def test_proper_statistics(update, load_json, get_statistics):
    # create a record
    update_query = load_json('update_with_limit.json')
    update_query['request_id'] = uuid.uuid4().hex
    await update(update_query)

    stat_query = load_json('statistics.json')
    date = str(
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc),
    )
    stat_query['counters'][0]['from_date'] = date

    # ensure that record exists & has proper values
    statistics = await get_statistics(stat_query)
    counters = statistics['statistics']['counters'][0]
    assert counters['from_timestamp'] == _calculate_datetime(date, stat_query)
    assert counters['count'] == 1


def _calculate_value(multiplicity: int, value: int) -> int:
    while value % multiplicity != 0:
        value -= 1
    return value


def parse_date(date_str: str) -> datetime.datetime:
    return date_util.parse(date_str)


def _calculate_datetime(incoming_date: str, query: dict) -> int:
    query = query['counters'][0]
    date = parse_date(incoming_date).replace(microsecond=0)
    day, hour, minute = date.day, date.hour, date.minute
    if query['unit'] == 'minutes':
        minute = _calculate_value(query['value'], date.minute)
    elif query['unit'] == 'hours':
        hour = _calculate_value(query['value'], date.hour)
        minute = 0
    elif query['unit'] == 'days':
        day = _calculate_value(query['value'], date.day) or 1
        hour = minute = 0
    return int(
        datetime.datetime(
            date.year, date.month, day, hour, minute,
        ).timestamp(),
    )
