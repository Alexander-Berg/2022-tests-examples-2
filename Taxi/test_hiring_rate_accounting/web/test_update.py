import datetime
import uuid


async def test_increment_counter(update, load_json):
    # create a record with 3 different counters
    query = load_json('update.json')
    query['request_id'] = uuid.uuid4().hex
    response, response_body = await update(query)
    assert response.status == 200

    # ensure that all the counters were creted
    assert len(response_body['statistics']['counters']) == 3

    # ensure that pause is calculated correctly
    assert response_body['statistics']['pause'] == 0.0

    # ensure idempotency works
    response, response_body = await update(query)
    assert response.status == 400
    assert response_body['code'] == 'BAD_REQUEST_ID'


async def test_increment_counter_with_limit(update, load_json):
    # create a counter with limit
    query = load_json('update_with_limit.json')
    for i in range(2):
        query['request_id'] = uuid.uuid4().hex
        response, response_body = await update(query)
        assert response.status == 200
        pause = response_body['statistics']['pause']
        if i == 0:
            # ensure that after one request pause is calculated correctly
            assert pause == 0.0
        else:
            # ensure that after second request pause is
            # still calculated correctly
            second = datetime.datetime.utcnow().second
            real_pause = 60 - second
            assert real_pause - 1 <= pause <= real_pause + 1


async def test_increment_limit(update, load_json):
    # create a counter with limit
    query = load_json('update_with_limit.json')
    for i in range(5):
        query['request_id'] = uuid.uuid4().hex
        # increment limit at each request
        query['counters'][0]['limit'] = i + 1
        response, response_body = await update(query)
        assert response.status == 200
        pause = response_body['statistics']['pause']

        # ensure that after each request pause is calculated correctly
        assert pause == 0.0


async def test_increment_two_counters_with_limits(update, load_json):
    # create a record with two counters,
    # each limited by 1 request in period
    query = load_json('update_with_two_limits.json')
    for i in range(2):
        query['request_id'] = uuid.uuid4().hex
        response, response_body = await update(query)
        assert response.status == 200
        pause = response_body['statistics']['pause']
        if i == 0:
            # ensure that after one request pause is calculated correctly
            assert pause == 0.0
        else:
            # ensure that after reaching the limit,
            # pause is equal to the maximum among all counters
            real_pause = find_one_day_pause()
            assert real_pause - 1 <= pause <= real_pause + 1


def find_one_day_pause() -> float:
    start = calculate_datetime()
    next_day = start + datetime.timedelta(days=1)
    now = datetime.datetime.utcnow()
    return next_day.timestamp() - now.timestamp()


def calculate_value(multiplicity: int, value: int) -> int:
    while value % multiplicity != 0:
        value -= 1
    return value


def calculate_datetime() -> datetime.datetime:
    date = datetime.datetime.utcnow()
    date = date.replace(microsecond=0)
    day = calculate_value(1, date.day) or 1
    hour = minute = 0

    return datetime.datetime(date.year, date.month, day, hour, minute)


async def test_increment_and_decrement(update, get_statistics, load_json):
    # create a record with two counters,
    # each limited by 1 request in period
    query = load_json('update_with_two_limits.json')
    for i in range(2):
        query['request_id'] = uuid.uuid4().hex
        response, response_body = await update(query)
        assert response.status == 200
        pause = response_body['statistics']['pause']
        if i == 0:
            # ensure that after one request pause is calculated correctly
            assert pause == 0.0
        else:
            # ensure that after reaching the limit,
            # pause is equal to the maximum among all counters
            real_pause = find_one_day_pause()
            assert real_pause - 1 <= pause <= real_pause + 1

    # Decrease counters
    query['value'] = -5
    query['request_id'] = uuid.uuid4().hex
    response, response_body = await update(query)
    assert response.status == 200
    pause = response_body['statistics']['pause']
    assert pause == 0.0

    # The counter can't fall below zero, so we must receive 0
    stat_query = load_json('statistics.json')
    date = str(
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc),
    )
    stat_query['counters'][0]['from_date'] = date
    statistics = await get_statistics(stat_query)
    counters = statistics['statistics']['counters'][0]
    assert counters['count'] == 0
