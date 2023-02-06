import datetime


def to_datetime(datetime_str):
    return datetime.datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f')


async def juggler_states_iteration(taxi_hejmdal, testpoint):
    @testpoint('juggler-states::iteration-finished')
    def task_progress(arg):
        pass

    await taxi_hejmdal.run_task('services_component/invalidate')

    async with taxi_hejmdal.spawn_task('distlock/juggler-states'):
        await task_progress.wait_call()

    await taxi_hejmdal.invalidate_caches(cache_names=['juggler-states-cache'])


async def test_juggler_states(taxi_hejmdal, testpoint, mockserver, pgsql):
    alert_description = (
        '0/1/1 (0/0) ~\n'
        'high bad rps = 12\n'
        '---\n'
        ' * Детали: https://nda.ya.ru/t/cMiaM3XQ4Qnofk\n'
        '---\n'
        ' * Grafana: https://nda.ya.ru/t/KbaxZ18C4Qnofz\n'
        ' * Golovan: https://nda.ya.ru/t/LN9amFS24QnogM\n'
        '---\n'
        'Проект: lavka\n'
        'Сервис: grocery-api\n'
        'Бранч: stable\n'
        'URL: grocery-api.lavka.yandex.net\n'
        '---\n'
        'Обратная связь: https://nda.ya.ru/t/JOGz5aQG4Qnogj\n'
        '------------------\n'
        '~ (lavka_grocery-api_stable_host)'
    )

    updated = 1635766628.9302325
    changed = 1635765983.6001961

    @mockserver.json_handler('/juggler-api/v2/checks/get_checks_state')
    def _mock_get_checks_state(request, *args, **kwargs):
        return {
            'items': [
                {
                    'host': 'test_service_stable',
                    'service': 'hejmdal-bad-rps',
                    'status': 'WARN',
                    'meta': '{}',
                    'description': alert_description,
                    'change_time': changed,
                    'aggregation_time': updated,
                    'namespace': 'taxi.lavka.prod',
                    'tags': [
                        'a_mark_taxi-monitoring',
                        'a_mark_taxi-monitoring_ns_taxi.lavka.prod',
                    ],
                    'project': 'taxi.lavka.prod',
                    'state_kind': 'ACTUAL',
                    'downtime_ids': [],
                    'mutes': [],
                },
            ],
            'limit': 100,
            'total': 1,
            'meta': {'_backend': 'vla-prod.juggler.search.yandex.net'},
            'statuses': [{'status': 'WARN', 'count': 1}],
            'response_too_large': False,
        }

    @mockserver.json_handler('/clowny-alert-manager/v1/checks/info/')
    def _mock_get_checks_info(request, *args, **kwargs):
        if request.query['check_name'] == 'hejmdal-bad-rps':
            return mockserver.make_response(
                json={
                    'source': 'hejmdal',
                    'description': 'mock description',
                    'url': (
                        'https://wiki.yandex-team.ru/taxi/backend/hejmdal/'
                        'bad-rps/'
                    ),
                },
                status=200,
            )
        return mockserver.make_response(json={}, status=404)

    # remove possible hejmdal check state from other tests
    await taxi_hejmdal.run_task('circuit_states_cache/invalidate')

    await juggler_states_iteration(taxi_hejmdal, testpoint)

    cursor = pgsql['hejmdal'].cursor()
    cursor.execute(
        'select service, host, status, changed, updated '
        'from juggler_check_states;',
    )
    query_result = cursor.fetchall()
    assert len(query_result) == 1
    item = query_result[0]
    assert item[0] == 'hejmdal-bad-rps'
    assert item[1] == 'test_service_stable'
    assert item[2] == 'WARN'
    assert item[3] == to_datetime('2021-11-01T11:26:23.000000')
    assert item[4] == to_datetime('2021-11-01T11:37:08.000000')

    response = await taxi_hejmdal.post(
        '/v1/health/service', params={'id': 1}, json={},
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert 'service_health' in resp_json
    health = resp_json['service_health']
    assert health['stats'] == {
        'total_checks': 1,
        'states': {'Warning': 1},
        'status': 'Warning',
    }
    assert health['hejmdal-bad-rps'] == {
        'check_data': {
            'changed': '2021-11-01T11:26:23+00:00',
            'description': alert_description,
            'status': 'Warning',
            'updated': '2021-11-01T11:37:08+00:00',
        },
        'info': {
            'Источник данных': 'hejmdal',
            'Детали проверки': (
                'https://wiki.yandex-team.ru/taxi/backend/hejmdal/bad-rps/'
            ),
            'description': 'mock description',
            'Канал информирования': 'Juggler',
            'Ссылка на Juggler': (
                'https://juggler.yandex-team.ru/check_details?'
                'host=test_service_stable&service=hejmdal-bad-rps'
            ),
        },
        'stats': {
            'states': {'Warning': 1},
            'status': 'Warning',
            'total_checks': 1,
        },
    }

    updated += 60 * 30  # seconds
    await juggler_states_iteration(taxi_hejmdal, testpoint)

    cursor.execute(
        'select last_update_period, update_period_ema '
        'from juggler_check_states;',
    )
    query_result = cursor.fetchall()
    assert len(query_result) == 1
    item = query_result[0]
    assert item[0] == datetime.timedelta(minutes=30)
    assert item[1] == datetime.timedelta(minutes=30)  # prev period

    updated += 60 * 30
    await juggler_states_iteration(taxi_hejmdal, testpoint)

    cursor.execute(
        'select last_update_period, update_period_ema '
        'from juggler_check_states;',
    )
    query_result = cursor.fetchall()
    assert len(query_result) == 1
    item = query_result[0]
    assert item[0] == datetime.timedelta(minutes=30)
    assert item[1] == datetime.timedelta(minutes=30)  # prev ema

    updated += 60 * 45
    await juggler_states_iteration(taxi_hejmdal, testpoint)

    cursor.execute(
        'select last_update_period, update_period_ema '
        'from juggler_check_states;',
    )
    query_result = cursor.fetchall()
    assert len(query_result) == 1
    item = query_result[0]
    assert item[0] == datetime.timedelta(minutes=45)
    assert item[1] == datetime.timedelta(minutes=30)

    updated += 60 * 45
    await juggler_states_iteration(taxi_hejmdal, testpoint)

    cursor.execute('select update_period_ema from juggler_check_states;')
    query_result = cursor.fetchall()
    assert len(query_result) == 1
    item = query_result[0]
    # some interval between 30 and 45 minutes
    assert (
        datetime.timedelta(minutes=30)
        < item[0]
        < datetime.timedelta(minutes=45)
    )
