import datetime
import uuid

import dateutil.parser as date_util


async def test_remove_old_records(
        load_json, update, get_statistics, run_remove_old_records,
):
    await run_remove_old_records()
    query = load_json('update_with_from_date.json')
    query['request_id'] = uuid.uuid4().hex
    date = query['counters'][0]['from_date']

    # send request with an old date
    await update(query)

    stat_query = load_json('statistics.json')

    # ensure that record from first request exists
    statistics = await get_statistics(stat_query)
    counter = statistics['statistics']['counters'][0]
    assert counter['from_timestamp'] == _calculate_timestamp(date, query)
    assert counter['count'] == 1

    # run cron which deletes records older than 60 days
    await run_remove_old_records()

    # ensure that cron has already deleted the record
    statistics = await get_statistics(stat_query)
    counter = statistics['statistics']['counters'][0]
    assert counter['from_timestamp'] == _calculate_timestamp(date, query)
    assert counter['count'] == 0


async def test_not_remove_not_old_records(
        load_json, update, get_statistics, run_remove_old_records,
):
    date = str(date_in_allowed_past())

    query = load_json('update_with_from_date.json')
    query['counters'][0]['from_date'] = date
    query['request_id'] = uuid.uuid4().hex

    # send request with a date which is
    # just an hour from being marked as old
    await update(query)

    stat_query = load_json('statistics.json')
    stat_query['counters'][0]['from_date'] = date

    # ensure that record from first request exists
    statistics = await get_statistics(stat_query)
    counter = statistics['statistics']['counters'][0]
    assert counter['from_timestamp'] == _calculate_timestamp(date, query)
    assert counter['count'] == 1

    # run cron which deletes records older than 60 days
    await run_remove_old_records()

    # ensure that cron did not delete the record
    statistics = await get_statistics(stat_query)
    counter = statistics['statistics']['counters'][0]
    assert counter['from_timestamp'] == _calculate_timestamp(date, query)
    assert counter['count'] == 1


def date_in_past() -> datetime.datetime:
    date = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc,
    ) - datetime.timedelta(days=60)
    return date


def date_in_allowed_past() -> datetime.datetime:
    date = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc,
    ) - datetime.timedelta(days=59, hours=23)
    return date


def _calculate_value(multiplicity: int, value: int) -> int:
    while value % multiplicity != 0:
        value -= 1
    return value


def parse_date(date_str: str) -> datetime.datetime:
    return date_util.parse(date_str)


def _calculate_timestamp(incoming_date: str, query: dict) -> int:
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
