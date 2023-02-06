import datetime

import dateutil.parser

MAX_RPS_FOR_AUTOGEN_RATELIMIT = 2
MILLISECONDS_IN_SECOND = 1000
MS_TO_RESTORE_TOKEN = MILLISECONDS_IN_SECOND / MAX_RPS_FOR_AUTOGEN_RATELIMIT


async def request_200(taxi_userver_sample):
    response = await taxi_userver_sample.get('/autogen/ratelimit')
    assert response.status_code == 200
    assert response.json() == {'message': 'FINE'}


async def hit_rate_limit(taxi_userver_sample):
    response = await taxi_userver_sample.get('/autogen/ratelimit')
    assert response.status_code == 429
    assert response.json() == {'code': '429', 'message': 'Too Many Requests'}


async def request_and_hit_rate_limit(taxi_userver_sample):
    for _ in range(MAX_RPS_FOR_AUTOGEN_RATELIMIT):
        await request_200(taxi_userver_sample)

    await hit_rate_limit(taxi_userver_sample)


async def test_ratelimit(taxi_userver_sample, mocked_time):
    now = dateutil.parser.parse('2019-09-19T14:03:00+00:00')
    mocked_time.set(now)
    await request_and_hit_rate_limit(taxi_userver_sample)

    now += datetime.timedelta(seconds=1)
    mocked_time.set(now)
    await request_and_hit_rate_limit(taxi_userver_sample)

    now += datetime.timedelta(seconds=10)
    mocked_time.set(now)
    await request_and_hit_rate_limit(taxi_userver_sample)

    now += datetime.timedelta(milliseconds=MS_TO_RESTORE_TOKEN - 1)
    mocked_time.set(now)
    await hit_rate_limit(taxi_userver_sample)

    now += datetime.timedelta(milliseconds=2)
    mocked_time.set(now)
    await request_200(taxi_userver_sample)
    await hit_rate_limit(taxi_userver_sample)
