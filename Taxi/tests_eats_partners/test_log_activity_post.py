import pytz

PARTNERS_REQUEST = (123, 1000, 4000, 2000, 3000, 3000, 234, 678, 4000, 3000, 1)
PARTNERS_ANSWER = (1, 123, 234, 678, 1000, 2000, 3000, 4000)


def get_sql_data(pgsql):
    cursor = pgsql['eats_partners'].cursor()
    cursor.execute(
        'SELECT partner_id,last_activity_at'
        ' FROM eats_partners.last_activity'
        ' ORDER BY partner_id',
    )
    return [
        {'partner_id': result[0], 'last_activity_at': result[1]}
        for result in list(cursor)
    ]


async def test_log_activity_post_simple(taxi_eats_partners, pgsql):
    for partner_id in PARTNERS_REQUEST:
        response = await taxi_eats_partners.post(
            '/internal/partners/v1/log-activity',
            json={},
            params={'partner_id': partner_id},
        )
        assert response.status_code == 200

    sql_data = get_sql_data(pgsql)
    assert len(PARTNERS_ANSWER) == len(sql_data)
    for idx, partner_id in enumerate(PARTNERS_ANSWER):
        assert partner_id == sql_data[idx]['partner_id']


async def test_log_activity_post_cache(
        taxi_eats_partners, pgsql, mocked_time, testpoint,
):
    @testpoint('mock_pg_now')
    def mock_pg_now(val):
        pass

    time1 = pytz.utc.localize(mocked_time.now())

    response = await taxi_eats_partners.post(
        '/internal/partners/v1/log-activity',
        json={},
        params={'partner_id': 100},
    )
    assert response.status_code == 200
    assert time1 == get_sql_data(pgsql)[0]['last_activity_at']

    mocked_time.sleep(10)
    time2 = pytz.utc.localize(mocked_time.now())
    response = await taxi_eats_partners.post(
        '/internal/partners/v1/log-activity',
        json={},
        params={'partner_id': 100},
    )
    assert response.status_code == 200
    assert time1 != time2
    assert time1 == get_sql_data(pgsql)[0]['last_activity_at']

    mocked_time.sleep(601)
    time3 = pytz.utc.localize(mocked_time.now())
    response = await taxi_eats_partners.post(
        '/internal/partners/v1/log-activity',
        json={},
        params={'partner_id': 100},
    )
    assert response.status_code == 200
    assert time3 == get_sql_data(pgsql)[0]['last_activity_at']
    assert mock_pg_now.has_calls


async def test_last_activity_cache_metrics(
        taxi_eats_partners, taxi_eats_partners_monitor, mocked_time,
):
    async def do_log_activity():
        response = await taxi_eats_partners.post(
            '/internal/partners/v1/log-activity',
            json={},
            params={'partner_id': 100},
        )
        assert response.status_code == 200

    metric_name = 'last-activity-cache'

    # in previous tests log-activity handle has been called a few times
    # so metrics will be > 0 already
    init_values = await taxi_eats_partners_monitor.get_metric(metric_name)
    expected_result = {
        'hits': init_values['hits'],
        'misses': init_values['misses'],
        'stale': init_values['stale'],
    }

    await do_log_activity()
    expected_result['misses'] += 1
    metrics = await taxi_eats_partners_monitor.get_metric(metric_name)
    assert metrics == expected_result

    await do_log_activity()
    metrics = await taxi_eats_partners_monitor.get_metric(metric_name)
    expected_result['hits'] += 1
    assert metrics == expected_result

    mocked_time.sleep(1000)
    await do_log_activity()
    metrics = await taxi_eats_partners_monitor.get_metric(metric_name)
    expected_result['stale'] += 1
    assert metrics == expected_result
