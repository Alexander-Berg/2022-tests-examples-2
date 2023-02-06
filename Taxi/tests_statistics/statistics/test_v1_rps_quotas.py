import pytest


async def make_request(taxi_statistics, *args, **kwargs):
    return await taxi_statistics.post(
        'v1/rps-quotas?service=test', json=make_body(*args, **kwargs),
    )


def make_body(
        quota,
        resource='test',
        sub_resource=None,
        limit=100,
        minimal_quota=10,
        burst=100,
        interval=1,
        max_increase_step=None,
        client_id='test_client',
        avg_usage=None,
):
    request = {
        'resource': resource,
        'sub_resource': sub_resource,
        'limit': limit,
        'minimal-quota': minimal_quota,
        'requested-quota': quota,
        'burst': burst,
        'interval': interval,
    }
    if max_increase_step is not None:
        request['max-increase-step'] = max_increase_step
    if avg_usage is not None:
        request['client-info'] = {'avg-usage': avg_usage}
    return {'requests': [request], 'client-id': client_id}


def make_response(quota, resource='test', sub_resource=None):
    tmp = {'resource': resource, 'assigned-quota': quota}
    if sub_resource:
        tmp.update({'sub_resource': sub_resource})
    return {'quotas': [tmp]}


@pytest.mark.now('2020-07-07T00:00:00Z')
async def test_simple_requests(taxi_statistics):
    response = await make_request(taxi_statistics, 40)
    assert response.status_code == 200
    assert response.json() == make_response(40)

    response = await make_request(taxi_statistics, 40)
    assert response.status_code == 200
    assert response.json() == make_response(40)

    response = await make_request(taxi_statistics, 40)
    assert response.status_code == 200
    assert response.json() == make_response(20)

    response = await make_request(taxi_statistics, 40, sub_resource='test')
    assert response.status_code == 200
    assert response.json() == make_response(40, sub_resource='test')


@pytest.mark.parametrize('interval', [1, 5, 10])
@pytest.mark.now('2020-07-07T00:00:00Z')
async def test_budget_refreshing(taxi_statistics, mocked_time, interval):
    # exhaust all the budget
    response = await make_request(taxi_statistics, 100, interval=interval)
    assert response.status_code == 200
    assert response.json() == make_response(100)

    mocked_time.sleep(0.2 * interval)

    response = await make_request(taxi_statistics, 100, interval=interval)
    assert response.status_code == 200
    assert response.json() == make_response(20)

    mocked_time.sleep(0.45 * interval)

    response = await make_request(taxi_statistics, 100, interval=interval)
    assert response.status_code == 200
    assert response.json() == make_response(45)

    mocked_time.sleep(interval)

    response = await make_request(taxi_statistics, 100, interval=interval)
    assert response.status_code == 200
    assert response.json() == make_response(100)


@pytest.mark.parametrize(
    'minimal_quota,budget,requested,assigned',
    [(20, 5, 20, 0), (20, 5, 5, 5), (20, 20, 30, 20)],
)
@pytest.mark.now('2020-07-07T00:00:00Z')
async def test_minimal_quota(
        taxi_statistics, minimal_quota, budget, requested, assigned,
):
    # take almos all the budget
    response = await make_request(taxi_statistics, 100 - budget)
    assert response.status_code == 200
    assert response.json() == make_response(100 - budget)

    response = await make_request(
        taxi_statistics, requested, minimal_quota=minimal_quota,
    )
    assert response.status_code == 200
    assert response.json() == make_response(assigned)


@pytest.mark.now('2020-07-07T00:00:00Z')
async def test_multiple_resources(taxi_statistics, mocked_time):
    body = {
        'requests': [
            {
                'service': 'test',
                'resource': 'test1',
                'limit': 100,
                'requested-quota': 50,
            },
            {
                'service': 'test',
                'resource': 'test2',
                'limit': 50,
                'requested-quota': 20,
            },
        ],
    }

    response = await taxi_statistics.post(
        'v1/rps-quotas?service=test', json=body,
    )
    assert response.status_code == 200
    quotas = {}
    for quota in response.json()['quotas']:
        quotas[quota['resource']] = quota['assigned-quota']
    assert quotas == {'test1': 50, 'test2': 20}

    mocked_time.sleep(0.2)

    body = {
        'requests': [
            {
                'service': 'test',
                'resource': 'test1',
                'limit': 100,
                'requested-quota': 100,
            },
            {
                'service': 'test',
                'resource': 'test2',
                'limit': 50,
                'requested-quota': 50,
            },
        ],
    }

    response = await taxi_statistics.post(
        'v1/rps-quotas?service=test', json=body,
    )
    assert response.status_code == 200
    for quota in response.json()['quotas']:
        quotas[quota['resource']] = quota['assigned-quota']
    assert quotas == {'test1': 70, 'test2': 40}


@pytest.mark.now('2020-07-07T00:00:00Z')
@pytest.mark.parametrize('intervals_to_burst_restore', [1, 10, 100])
@pytest.mark.parametrize('intervals_to_burst_expire', [1, 3])
async def test_burst(
        taxi_statistics,
        mocked_time,
        taxi_config,
        intervals_to_burst_restore,
        intervals_to_burst_expire,
):
    taxi_config.set_values(
        {
            'STATISTICS_LIMITERS_SETTINGS': {
                'rate_limiter': {
                    'intervals_to_burst_restore': intervals_to_burst_restore,
                    'intervals_to_burst_expire': intervals_to_burst_expire,
                },
            },
        },
    )

    # limit + burst budgets are spent
    response = await make_request(taxi_statistics, 200, burst=200)
    assert response.status_code == 200
    assert response.json() == make_response(200)

    # nothing left, usual budget and burst budget are spent
    response = await make_request(taxi_statistics, 100, burst=200)
    assert response.json() == make_response(0)

    for _ in range(6):
        mocked_time.sleep(0.2)
        # while limit is breached, burst budget doesn't restore
        response = await make_request(taxi_statistics, 150, burst=200)
        assert response.json() == make_response(20)

    mocked_time.sleep(intervals_to_burst_restore / 2)
    response = await make_request(taxi_statistics, 150, burst=200)
    assert response.json() == make_response(
        min(100, intervals_to_burst_restore / 2 * 100),
    )

    mocked_time.sleep(intervals_to_burst_restore)
    # burst budget restores
    response = await make_request(taxi_statistics, 150, burst=200)
    assert response.json() == make_response(150)

    if intervals_to_burst_expire < intervals_to_burst_restore:
        # else it doesn't work
        mocked_time.sleep(intervals_to_burst_restore)
        # budget=100, burst=1000

        response = await make_request(taxi_statistics, 150, burst=1000)
        assert response.json() == make_response(150)
        # budget=0, burst=950

        response = await make_request(taxi_statistics, 300, burst=1000)
        assert response.json() == make_response(300)
        # budget=0, burst=650

        mocked_time.sleep(intervals_to_burst_expire / 2)
        # budget=50, burst=650

        response = await make_request(taxi_statistics, 300, burst=1000)
        assert response.json() == make_response(300)
        # budget=0, burst=400

        mocked_time.sleep(intervals_to_burst_expire)
        # budget=100, burst=0; // 400 from burst expired

        response = await make_request(taxi_statistics, 300, burst=1000)
        assert response.json() == make_response(100)


@pytest.mark.parametrize('interval', [1, 10])
@pytest.mark.parametrize('limit', [100])
@pytest.mark.parametrize('max_increase_step', [1, 3, 50, 1000])
@pytest.mark.now('2020-07-07T00:00:00Z')
async def test_max_increase_step(
        taxi_statistics, mocked_time, interval, limit, max_increase_step,
):
    async def _check(expected, max_increase_step, interval):
        if limit < expected:
            expected = limit
        response = await make_request(
            taxi_statistics,
            limit,
            interval=interval,
            max_increase_step=max_increase_step,
        )
        assert response.status_code == 200
        assert response.json() == make_response(expected)

    await _check(limit, None, interval)
    await _check(0, None, interval)
    mocked_time.sleep(interval)

    await _check(max_increase_step, max_increase_step, interval)
    mocked_time.sleep(interval * 100)

    expected = 0
    for i in range(limit // max_increase_step):
        if i % 2:
            await _check(0, max_increase_step, interval)
        else:
            expected += max_increase_step
            await _check(expected, max_increase_step, interval)
        mocked_time.sleep(interval / 2)

    mocked_time.sleep(interval * 2)
    await _check(expected + max_increase_step, max_increase_step, interval)
    mocked_time.sleep(interval * 100)
    await _check(max_increase_step, max_increase_step, interval)
    await _check(0, max_increase_step, interval)


@pytest.mark.now('2020-07-07T00:00:00Z')
async def test_big_delay_overflow(taxi_statistics, mocked_time):
    response = await make_request(taxi_statistics, 100, limit=50000)
    assert response.status_code == 200
    assert response.json() == make_response(100)

    # sleep for a week
    mocked_time.sleep(7 * 24 * 60 * 60)

    response = await make_request(taxi_statistics, 100, limit=50000)
    assert response.status_code == 200
    assert response.json() == make_response(100)


@pytest.mark.now('2020-07-07T00:00:00Z')
async def test_limit_equals_1(taxi_statistics, mocked_time):
    response = await make_request(taxi_statistics, 1, limit=1, burst=1)
    assert response.status_code == 200
    assert response.json() == make_response(1)

    # budget is not refreshed until whole second passes
    for _ in range(9):
        mocked_time.sleep(0.1)
        response = await make_request(taxi_statistics, 1, limit=1, burst=1)
        assert response.status_code == 200
        assert response.json() == make_response(0)

    # pass slightly more than 0.1 second because (budget += 0.1) * 10 times
    # equals 0.9(9) in double
    mocked_time.sleep(0.10001)
    response = await make_request(taxi_statistics, 1, limit=1, burst=1)
    assert response.status_code == 200
    assert response.json() == make_response(1)


@pytest.mark.now('2020-07-07T00:00:00Z')
async def test_increase_limiter_with_host_usage(taxi_statistics, mocked_time):
    step = 10
    response = await make_request(
        taxi_statistics,
        100,
        interval=1,
        max_increase_step=step,
        client_id='client1',
        avg_usage=20,
    )
    assert response.status_code == 200
    # host1 usage is accounted and increase limit is 30 for this interval
    assert response.json() == make_response(30)

    mocked_time.sleep(1)

    response = await make_request(
        taxi_statistics,
        100,
        interval=1,
        max_increase_step=step,
        client_id='client2',
        avg_usage=30,
    )
    assert response.status_code == 200
    assert response.json() == make_response(40)


@pytest.mark.config(
    STATISTICS_LIMITERS_SETTINGS={
        'rate_limiter': {'intervals_to_burst_restore': 1},
        'settings_for_limiters': {
            'test': {
                'extra_quota_settings': {
                    'intervals_count': 3,
                    'maximum_percentage_of_limit': 80,
                },
            },
        },
    },
)
@pytest.mark.now('2020-07-07T00:00:00Z')
async def test_extra_quota_one_client(taxi_statistics, mocked_time):
    async def _check(requested, expected):
        response = await make_request(taxi_statistics, requested)
        assert response.status_code == 200
        assert response.json() == make_response(expected)

    await _check(20, 20)
    mocked_time.sleep(1)
    await _check(60, 60)
    mocked_time.sleep(1)
    await _check(30, 80)


@pytest.mark.config(
    STATISTICS_LIMITERS_SETTINGS={
        'rate_limiter': {'intervals_to_burst_restore': 1},
        'settings_for_limiters': {
            'test': {
                'extra_quota_settings': {
                    'intervals_count': 3,
                    'maximum_percentage_of_limit': 80,
                },
            },
        },
    },
)
@pytest.mark.now('2020-07-07T00:00:00Z')
async def test_extra_quota_few_clients(taxi_statistics, mocked_time):
    async def _check(requested, expected, client_id):
        response = await make_request(
            taxi_statistics, requested, client_id=client_id,
        )
        assert response.status_code == 200
        assert response.json() == make_response(expected)

    await _check(20, 20, 'client0')
    await _check(30, 30, 'client1')
    mocked_time.sleep(1)
    await _check(60, 60, 'client3')
    mocked_time.sleep(1)
    await _check(20, 26, 'client1')
