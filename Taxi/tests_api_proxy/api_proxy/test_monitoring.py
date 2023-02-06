import json

import pytest

TEST_TEAM = {
    'description': (
        'Группа разработки инфраструктуры пользовательских продуктов'
    ),
    'staff_groups': [
        'yandex_distproducts_browserdev_mobile_taxi_9720_dep95813',
    ],
}
MONITORING_TEAMS_SETTINGS = {
    'aggregation-interval': 60,
    'min-events': 0,
    'error-threshold': 50,
}
JUGGLER_RESPONSE = {
    'accepted_events': 1,
    'events': [{'code': 200}],
    'success': True,
}


@pytest.mark.config(DEV_TEAMS={'tes\nt\'-\\ \tteam/': TEST_TEAM})
@pytest.mark.parametrize(
    'task, service, ok_desc',
    [
        ('handlers-juggler-push', 'handlers', 'no bad handlers'),
        ('resources-juggler-push', 'resources', 'no bad resources'),
        (
            'handlers_configs-juggler-push',
            'handlers_configs',
            'all taxi-configs exist and qos ok',
        ),
    ],
)
@pytest.mark.suspend_periodic_tasks(
    'resources-juggler-push',
    'handlers-juggler-push',
    'handlers_configs-juggler-push',
)
async def test_basic_ok(taxi_api_proxy, mockserver, task, service, ok_desc):
    @mockserver.json_handler('/juggler/events')
    def events_handler(req):
        data = json.loads(req.get_data())
        assert len(data['events']) == 1
        assert data['events'][0] == {
            'description': f'OK: {ok_desc}',
            'instance': '',
            'service': f'autogen_tes%0At%27-%5C%20%09team%2F_{service}',
            'status': 'OK',
        }
        return JUGGLER_RESPONSE

    await taxi_api_proxy.run_periodic_task(task)
    assert events_handler.times_called == 1


@pytest.mark.config(
    MONITORING_TEAMS_SETTINGS=MONITORING_TEAMS_SETTINGS,
    DEV_TEAMS={'tes\nt\'-\\ \tteam/': TEST_TEAM},
)
@pytest.mark.parametrize('error', [None, 500, 'timeout'])
@pytest.mark.suspend_periodic_tasks(
    'handlers-juggler-push',
    'handlers_configs-juggler-push',
    'resources-juggler-push',
)
async def test_upstream_500(
        taxi_api_proxy, endpoints, resources, error, mockserver, load_yaml,
):
    @mockserver.json_handler('/juggler/events')
    def events_handler(req):
        data = json.loads(req.get_data())
        assert len(data['events']) == 1
        event = data['events'][0]
        if error is None:
            assert event['status'] == 'OK'
            if 'handlers' in event['service']:
                assert event['description'] == 'OK: no bad handlers'
                return JUGGLER_RESPONSE
            if 'resources' in event['service']:
                assert event['description'] == 'OK: no bad resources'
                return JUGGLER_RESPONSE
            assert 0
        else:
            assert event['status'] == 'CRIT'
            if 'handlers' in event['service']:
                assert event['description'] == 'CRIT: /ep: 100.0%'
                return JUGGLER_RESPONSE
            if 'resources' in event['service']:
                assert (
                    event['description'] == 'CRIT: resource-upstream: 100.0%'
                )
                return JUGGLER_RESPONSE
            assert 0
        return {}

    dev_team_name = 'tes\nt\'-\\ \tteam/'
    handle_upstream = await _setup_config(
        endpoints, resources, mockserver, load_yaml, dev_team_name, error,
    )

    response = await taxi_api_proxy.post(
        '/ep?', json={'enable-fail-policy': False, 'foo': 'FOO'},
    )
    code = response.status_code
    assert (error is not None and code == 500) or (code == 200)

    await taxi_api_proxy.run_periodic_task('handlers-juggler-push')
    await taxi_api_proxy.run_periodic_task('resources-juggler-push')
    assert handle_upstream.times_called == 1
    assert events_handler.times_called == 2


@pytest.mark.config(
    MONITORING_TEAMS_SETTINGS=MONITORING_TEAMS_SETTINGS,
    DEV_TEAMS={'test-team': TEST_TEAM},
)
@pytest.mark.parametrize(
    'error,expect_fail',
    [(None, False), (500, True), ('timeout', True), (404, False)],
)
@pytest.mark.suspend_periodic_tasks(
    'handlers-juggler-push',
    'handlers_configs-juggler-push',
    'resources-juggler-push',
)
async def test_catch_with_failpolicy(
        taxi_api_proxy,
        endpoints,
        resources,
        error,
        expect_fail,
        mockserver,
        load_yaml,
):
    @mockserver.json_handler('/juggler/events')
    def events_handler(req):
        data = json.loads(req.get_data())
        assert len(data['events']) == 1
        event = data['events'][0]
        if 'handlers' in event['service']:
            assert event['description'] == 'OK: no bad handlers'
            assert event['status'] == 'OK'
            return JUGGLER_RESPONSE
        if 'resources' in event['service']:
            if expect_fail:
                assert (
                    event['description'] == 'CRIT: resource-upstream: 100.0%'
                )
                assert event['status'] == 'CRIT'
            else:
                assert event['description'] == 'OK: no bad resources'
                assert event['status'] == 'OK'
            return JUGGLER_RESPONSE
        assert 0
        return {}

    dev_team_name = 'test-team'
    handle_upstream = await _setup_config(
        endpoints, resources, mockserver, load_yaml, dev_team_name, error,
    )

    response = await taxi_api_proxy.post(
        '/ep?', json={'enable-fail-policy': True, 'foo': 'FOO'},
    )
    assert response.status_code == 200

    await taxi_api_proxy.run_periodic_task('handlers-juggler-push')
    await taxi_api_proxy.run_periodic_task('resources-juggler-push')
    assert handle_upstream.times_called == 1
    assert events_handler.times_called == 2


@pytest.mark.config(
    MONITORING_TEAMS_SETTINGS=MONITORING_TEAMS_SETTINGS,
    DEV_TEAMS={'test-team': TEST_TEAM},
)
@pytest.mark.parametrize('error', [False, True])
@pytest.mark.suspend_periodic_tasks(
    'handlers-juggler-push',
    'handlers_configs-juggler-push',
    'resources-juggler-push',
)
async def test_fired_by_internal_error(
        taxi_api_proxy, endpoints, resources, error, mockserver, load_yaml,
):
    @mockserver.json_handler('/juggler/events')
    def events_handler(req):
        data = json.loads(req.get_data())
        assert len(data['events']) == 1
        event = data['events'][0]
        if 'resources' in event['service']:
            assert event['description'] == 'OK: no bad resources'
            assert event['status'] == 'OK'
            return JUGGLER_RESPONSE
        if 'handlers' in event['service']:
            if error:
                assert event['description'] == 'CRIT: /ep: 100.0%'
                assert event['status'] == 'CRIT'
            else:
                assert event['description'] == 'OK: no bad handlers'
                assert event['status'] == 'OK'
            return JUGGLER_RESPONSE
        assert 0
        return {}

    dev_team_name = 'test-team'
    handle_upstream = await _setup_config(
        endpoints, resources, mockserver, load_yaml, dev_team_name, None,
    )
    request = {'enable-fail-policy': False}
    if not error:
        request['foo'] = 'FOO'

    response = await taxi_api_proxy.post('/ep?', json=request)
    code = response.status_code
    assert (error and code == 500) or (code == 200)

    await taxi_api_proxy.run_periodic_task('handlers-juggler-push')
    await taxi_api_proxy.run_periodic_task('resources-juggler-push')
    assert handle_upstream.times_called == 1
    assert events_handler.times_called == 2


@pytest.mark.config(
    MONITORING_TEAMS_SETTINGS={
        'aggregation-interval': 60,
        'min-events': 6,
        'error-threshold': 50,
    },
    DEV_TEAMS={'test-team': TEST_TEAM},
)
@pytest.mark.parametrize(
    'delay, triggered',
    [
        (0, True),
        pytest.param(
            10, True, marks=pytest.mark.skip(reason='broken on segment edge'),
        ),
        (11, False),
    ],
)
@pytest.mark.suspend_periodic_tasks(
    'handlers-juggler-push',
    'handlers_configs-juggler-push',
    'resources-juggler-push',
)
async def test_live_min_events(
        delay,
        triggered,
        taxi_api_proxy,
        endpoints,
        resources,
        mockserver,
        load_yaml,
        mocked_time,
):
    @mockserver.json_handler('/juggler/events')
    def events_handler(req):
        data = json.loads(req.get_data())
        assert len(data['events']) == 1
        event = data['events'][0]
        if triggered:
            assert event['status'] == 'CRIT'
            if 'resources' in event['service']:
                assert (
                    event['description'] == 'CRIT: resource-upstream: 100.0%'
                )
                return JUGGLER_RESPONSE
            if 'handlers' in event['service']:
                assert event['description'] == 'CRIT: /ep: 100.0%'
                return JUGGLER_RESPONSE
            assert 0
        else:
            assert event['status'] == 'OK'
            if 'resources' in event['service']:
                assert event['description'] == 'OK: no bad resources'
                return JUGGLER_RESPONSE
            if 'handlers' in event['service']:
                assert event['description'] == 'OK: no bad handlers'
                return JUGGLER_RESPONSE
            assert 0
        return {}

    dev_team_name = 'test-team'
    handle_upstream = await _setup_config(
        endpoints, resources, mockserver, load_yaml, dev_team_name, 500,
    )

    for _ in range(6):
        response = await taxi_api_proxy.post(
            '/ep?', json={'enable-fail-policy': False, 'foo': 'FOO'},
        )
        assert response.status_code == 500
        mocked_time.sleep(delay)
    assert handle_upstream.times_called == 6

    # actual 'sleep' here
    await taxi_api_proxy.tests_control(invalidate_caches=False)

    await taxi_api_proxy.run_periodic_task('handlers-juggler-push')
    await taxi_api_proxy.run_periodic_task('resources-juggler-push')
    assert events_handler.times_called == 2


@pytest.mark.config(
    MONITORING_TEAMS_SETTINGS={
        'aggregation-interval': 10,
        'min-events': 1,
        'error-threshold': 51,
    },
    DEV_TEAMS={'test-team': TEST_TEAM},
)
@pytest.mark.parametrize('delay, triggered', [(9, False), (11, True)])
@pytest.mark.suspend_periodic_tasks(
    'handlers-juggler-push',
    'handlers_configs-juggler-push',
    'resources-juggler-push',
)
async def test_live_threshold(
        delay,
        triggered,
        taxi_api_proxy,
        endpoints,
        resources,
        mockserver,
        load_yaml,
        mocked_time,
):
    @mockserver.json_handler('/juggler/events')
    def events_handler(req):
        data = json.loads(req.get_data())
        assert len(data['events']) == 1
        event = data['events'][0]
        if triggered:
            assert event['status'] == 'CRIT'
            assert event['description'] == 'CRIT: /ep: 100.0%'
        else:
            assert event['status'] == 'OK'
            assert event['description'] == 'OK: no bad handlers'
        return JUGGLER_RESPONSE

    dev_team_name = 'test-team'
    await _setup_config(
        endpoints, resources, mockserver, load_yaml, dev_team_name, None,
    )

    response = await taxi_api_proxy.post(
        '/ep?', json={'enable-fail-policy': False, 'foo': 'FOO'},
    )
    assert response.status_code == 200
    mocked_time.sleep(delay)
    response = await taxi_api_proxy.post('/ep?', json={})
    assert response.status_code == 500
    await taxi_api_proxy.run_periodic_task('handlers-juggler-push')
    assert events_handler.times_called == 1


@pytest.mark.config(
    MONITORING_TEAMS_SETTINGS=MONITORING_TEAMS_SETTINGS,
    DEV_TEAMS={'test-team': TEST_TEAM, 'other-team': TEST_TEAM},
)
@pytest.mark.suspend_periodic_tasks(
    'handlers-juggler-push',
    'handlers_configs-juggler-push',
    'resources-juggler-push',
)
async def test_other_team(
        taxi_api_proxy, endpoints, resources, mockserver, load_yaml,
):
    @mockserver.json_handler('/juggler/events')
    def events_handler(req):
        data = json.loads(req.get_data())
        assert len(data['events']) == 2
        for event in data['events']:
            if event['service'] == 'autogen_test-team_resources':
                assert event['status'] == 'CRIT'
                assert (
                    event['description'] == 'CRIT: resource-upstream: 100.0%'
                )
                return JUGGLER_RESPONSE
            if event['service'] == 'autogen_test-team_handlers':
                assert event['status'] == 'CRIT'
                assert event['description'] == 'CRIT: /ep: 100.0%'
                return JUGGLER_RESPONSE
            if event['service'] == 'autogen_other-team_resources':
                assert event['status'] == 'OK'
                assert event['description'] == 'OK: no bad resources'
                return JUGGLER_RESPONSE
            if event['service'] == 'autogen_other-team_handlers':
                assert event['status'] == 'OK'
                assert event['description'] == 'OK: no bad handlers'
                return JUGGLER_RESPONSE
        assert 0
        return {}

    mock = await _setup_config(
        endpoints, resources, mockserver, load_yaml, 'test-team', 500,
    )

    response = await taxi_api_proxy.post(
        '/ep?', json={'enable-fail-policy': False, 'foo': 'FOO'},
    )
    assert response.status_code == 500
    assert mock.times_called == 1
    await taxi_api_proxy.run_periodic_task('handlers-juggler-push')
    await taxi_api_proxy.run_periodic_task('resources-juggler-push')
    assert events_handler.times_called == 2


@pytest.mark.config(
    MONITORING_TEAMS_SETTINGS={
        'aggregation-interval': 60,
        'min-events': 0,
        'error-threshold': 9,
    },
    DEV_TEAMS={'test-team': TEST_TEAM},
)
@pytest.mark.suspend_periodic_tasks(
    'handlers-juggler-push',
    'handlers_configs-juggler-push',
    'resources-juggler-push',
)
async def test_shows_percentage_correctly(
        taxi_api_proxy,
        endpoints,
        resources,
        mockserver,
        load_yaml,
        mocked_time,
):
    @mockserver.json_handler('/juggler/events')
    def events_handler(req):
        data = json.loads(req.get_data())
        assert len(data['events']) == 1
        event = data['events'][0]
        if not errors:
            assert event['status'] == 'OK'
            assert event['description'] == 'OK: no bad handlers'
        else:
            assert event['status'] == 'CRIT'
            assert (
                event['description']
                == f'CRIT: /ep: {round(100*errors / (errors+10), 1)}%'
            )
        return JUGGLER_RESPONSE

    dev_team_name = 'test-team'
    await _setup_config(
        endpoints, resources, mockserver, load_yaml, dev_team_name, None,
    )

    for _ in range(10):
        response = await taxi_api_proxy.post(
            '/ep?', json={'enable-fail-policy': False, 'foo': 'FOO'},
        )
        assert response.status_code == 200
        mocked_time.sleep(1)
    errors = 0
    await taxi_api_proxy.run_periodic_task('handlers-juggler-push')

    for n_try in range(1, 41):
        response = await taxi_api_proxy.post('/ep?', json={})
        assert response.status_code == 500
        errors = n_try
        await taxi_api_proxy.run_periodic_task('handlers-juggler-push')

    assert events_handler.times_called == 41


@pytest.mark.config(DEV_TEAMS={'test-team': TEST_TEAM})
@pytest.mark.parametrize(
    'url, method, expected_code',
    [('/ep', 'post', 200), ('/pe', 'post', 404), ('/ep', 'patch', 405)],
)
@pytest.mark.suspend_periodic_tasks(
    'handlers-juggler-push',
    'handlers_configs-juggler-push',
    'resources-juggler-push',
)
async def test_wrong_params(
        taxi_api_proxy,
        endpoints,
        resources,
        mockserver,
        load_yaml,
        url,
        method,
        expected_code,
):
    @mockserver.json_handler('/juggler/events')
    def events_handler(req):
        data = json.loads(req.get_data())
        assert len(data['events']) == 1
        event = data['events'][0]
        assert event['status'] == 'OK'
        assert event['description'] == 'OK: no bad handlers'
        return JUGGLER_RESPONSE

    dev_team_name = 'test-team'
    await _setup_config(
        endpoints, resources, mockserver, load_yaml, dev_team_name, None,
    )
    method = getattr(taxi_api_proxy, method)
    response = await method(
        url, json={'enable-fail-policy': False, 'foo': 'FOO'},
    )
    assert response.status_code == expected_code
    await taxi_api_proxy.run_periodic_task('handlers-juggler-push')
    assert events_handler.times_called == 1


@pytest.mark.config(
    DEV_TEAMS={'test-team': TEST_TEAM, 'other-team': TEST_TEAM},
)
@pytest.mark.parametrize(
    'config_exist, dev_team, status, description',
    [
        (True, 'test-team', 'OK', 'OK: all taxi-configs exist and qos ok'),
        (
            False,
            'test-team',
            'CRIT',
            'CRIT: your missed configs: ep-with-cfg[FOO]. '
            'Missed configs: FOO',
        ),
        (False, 'other-team', 'WARN', 'WARN: Missed configs: FOO'),
    ],
)
@pytest.mark.suspend_periodic_tasks(
    'handlers-juggler-push',
    'handlers_configs-juggler-push',
    'resources-juggler-push',
)
async def test_missed_taxi_configs(
        taxi_api_proxy,
        endpoints,
        taxi_config,
        load_yaml,
        config_exist,
        dev_team,
        status,
        description,
        mockserver,
):
    @mockserver.json_handler('/juggler/events')
    def events_handler(req):
        data = json.loads(req.get_data())
        for event in data['events']:
            if event['service'] == f'autogen_{dev_team}_handlers_configs':
                assert event['status'] == status
                assert event['description'] == description
                return JUGGLER_RESPONSE
        assert 0
        return {}

    taxi_config.set(BAR='bar')
    if config_exist:
        taxi_config.set(FOO='FOO')
    await taxi_api_proxy.invalidate_caches()

    await endpoints.safely_create_endpoint(
        '/ep_with_cfg',
        endpoint_id='ep-with-cfg',
        post_handler=load_yaml('endpoint_with_taxi_config.yaml'),
        dev_team='test-team',
    )
    await taxi_api_proxy.run_periodic_task('handlers_configs-juggler-push')
    assert events_handler.times_called == 1


async def _setup_config(
        endpoints, resources, mockserver, load_yaml, dev_team_name, error,
):
    @mockserver.json_handler('/upstream-url')
    def handle_upstream(request):
        if error == 'timeout':
            raise mockserver.TimeoutError()
        if isinstance(error, int):
            return mockserver.make_response(status=error)
        return {'bar': 'BAR'}

    await resources.safely_create_resource(
        resource_id='resource-upstream',
        url=mockserver.url('upstream-url'),
        method='post',
        dev_team=dev_team_name,
        max_retries=1,
    )
    await endpoints.safely_create_endpoint(
        path='/ep',
        endpoint_id='just-ep',
        post_handler=load_yaml('endpoint.yaml'),
        dev_team=dev_team_name,
    )
    return handle_upstream
