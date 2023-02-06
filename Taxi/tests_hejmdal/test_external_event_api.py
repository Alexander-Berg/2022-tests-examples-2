async def test_start_event(taxi_hejmdal, pgsql):
    await taxi_hejmdal.run_task('services_component/invalidate')
    response = await taxi_hejmdal.post(
        '/v1/external-event/start',
        json={
            'event_type': 'drills',
            'datacenters': ['vla'],
            'projects': ['Taxi', 'Lavka'],
        },
    )
    assert response.status_code == 200
    cursor = pgsql['hejmdal'].cursor()
    cursor.execute(
        'select event_type, event_data from external_events '
        'where link = \'drillslavkataxivla\'',
    )
    query_result = cursor.fetchall()
    assert query_result[0] == (
        'drills',
        {'datacenters': ['vla'], 'project_ids': [1, 2, 3]},
    )

    response = await taxi_hejmdal.post(
        '/v1/external-event/start',
        json={'event_type': 'deploy', 'service_id': 9999, 'env': 'testing'},
    )
    assert response.status_code == 200
    cursor.execute(
        'select event_type, event_data from external_events '
        'where link = \'deploy9999testing\'',
    )
    query_result = cursor.fetchall()
    assert query_result[0] == (
        'deploy',
        {'env': 'testing', 'service_id': 9999},
    )


async def test_start_event_conflict(taxi_hejmdal):
    await taxi_hejmdal.run_task('services_component/invalidate')
    response = await taxi_hejmdal.post(
        '/v1/external-event/start',
        json={
            'event_type': 'drills',
            'datacenters': ['iva'],
            'projects': ['Taxi', 'Lavka'],
        },
    )
    assert response.status_code == 409
    response_json = response.json()
    assert (
        response_json['message']
        == 'Conflict with not finished event, link: drillslavkataxiiva'
    )

    response = await taxi_hejmdal.post(
        '/v1/external-event/start',
        json={'event_type': 'deploy', 'service_id': 999, 'env': 'testing'},
    )
    assert response.status_code == 409
    response_json = response.json()
    assert (
        response_json['message']
        == 'Conflict with not finished event, link: deploy999testing'
    )


async def test_start_event_unknown_project(taxi_hejmdal):
    await taxi_hejmdal.run_task('services_component/invalidate')
    response = await taxi_hejmdal.post(
        '/v1/external-event/start',
        json={
            'event_type': 'drills',
            'datacenters': ['vla'],
            'projects': ['Tuxi'],
        },
    )
    assert response.status_code == 400
    response_json = response.json()
    assert response_json['message'] == (
        'Unknown business unit project: tuxi, check config: '
        'HEJMDAL_BU_TO_CLOWNDUCTOR_PROJECTS'
    )


async def test_start_event_unknown_service(taxi_hejmdal):
    await taxi_hejmdal.run_task('services_component/invalidate')
    response = await taxi_hejmdal.post(
        '/v1/external-event/start',
        json={'event_type': 'deploy', 'service_id': 123, 'env': 'testing'},
    )
    assert response.status_code == 400
    response_json = response.json()
    assert (
        response_json['message']
        == 'ExternalEvent: unknown service id 123 for deploy event'
    )


async def test_start_event_unknown_type(taxi_hejmdal):
    await taxi_hejmdal.run_task('services_component/invalidate')
    response = await taxi_hejmdal.post(
        '/v1/external-event/start',
        json={
            'event_type': 'fake_type',
            'datacenters': ['vla'],
            'projects': ['Taxi'],
        },
    )
    assert response.status_code == 400


async def test_start_event_bad_deadline(taxi_hejmdal):
    await taxi_hejmdal.run_task('services_component/invalidate')
    response = await taxi_hejmdal.post(
        '/v1/external-event/start',
        json={
            'event_type': 'drills',
            'datacenters': ['vla'],
            'projects': ['Taxi'],
            'deadline': '1970-01-01T03:00:00+03:00',
        },
    )
    assert response.status_code == 400
    response_json = response.json()
    assert response_json['message'] == 'deadline must be greater than now + 1m'


async def test_finish_event(taxi_hejmdal):
    await taxi_hejmdal.run_task('services_component/invalidate')
    response = await taxi_hejmdal.post(
        '/v1/external-event/finish',
        json={
            'event_type': 'drills',
            'datacenters': ['iva'],
            'projects': ['taxi', 'lavka'],
        },
    )
    assert response.status_code == 200

    response = await taxi_hejmdal.post(
        '/v1/external-event/finish',
        json={'event_type': 'deploy', 'service_id': 999, 'env': 'testing'},
    )
    assert response.status_code == 200


async def test_finish_event_not_found(taxi_hejmdal):
    await taxi_hejmdal.run_task('services_component/invalidate')
    response = await taxi_hejmdal.post(
        '/v1/external-event/finish',
        json={
            'event_type': 'drills',
            'datacenters': ['vla'],
            'projects': ['taxi', 'lavka'],
        },
    )
    assert response.status_code == 404
    response_json = response.json()
    assert (
        response_json['message']
        == 'There\'s no started event with link: drillslavkataxivla'
    )

    response = await taxi_hejmdal.post(
        '/v1/external-event/finish',
        json={'event_type': 'deploy', 'service_id': 123, 'env': 'testing'},
    )
    assert response.status_code == 404
    response_json = response.json()
    assert (
        response_json['message']
        == 'There\'s no started event with link: deploy123testing'
    )


async def test_finish_event_unknown_type(taxi_hejmdal):
    await taxi_hejmdal.run_task('services_component/invalidate')
    response = await taxi_hejmdal.post(
        '/v1/external-event/finish',
        json={
            'event_type': 'fake_type',
            'datacenters': ['vla'],
            'projects': ['Taxi'],
        },
    )
    assert response.status_code == 400
