import datetime


TICKETS_QUEUE = 'TEST-DIAGNOSTICS'
DB_TIMEOUTS = {'network_timeout_ms': 100, 'statement_timeout_ms': 100}
HEJMDAL_CUSTOM_CHECKS_SETTINGS = {
    'read_custom_check_control': DB_TIMEOUTS,
    'write_custom_check_control': DB_TIMEOUTS,
    'tickets_queue': TICKETS_QUEUE,
}


def to_datetime(datetime_str):
    return datetime.datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S%z')


async def update_custom_check(taxi_hejmdal, pgsql):
    cursor = pgsql['hejmdal'].cursor()
    query = """
        update custom_checks
        set
            name='test_custom_check_name_updated',
            flows=$${
                "usage": {
                    "project": "taxi",
                    "program": "series_sum({
                        project='taxi',
                        cluster='production_uservices',
                        service='uservices',
                        application='eats-surge-resolver',
                        sensor='surge-stats.count_missing_places.1m',
                        group='test-group_stable|test-group_pre_stable',
                        host='test-host-2.yp-c.yandex.net'})"
                }
            }$$::jsonb,
            revision=default
        where id=1;"""
    cursor.execute(query)
    await taxi_hejmdal.invalidate_caches(
        clean_update=False, cache_names=['custom-checks-cache'],
    )
    await taxi_hejmdal.run_task('tuner/retune')


async def delete_custom_check(taxi_hejmdal, pgsql, check_id=1):
    cursor = pgsql['hejmdal'].cursor()
    query = """
        update custom_checks
        set deleted = true,
            revision=default
        where id={};"""
    cursor.execute(query.format(check_id))
    await taxi_hejmdal.invalidate_caches(
        clean_update=False,
        cache_names=['custom-checks-cache', 'schemas-cache'],
    )
    await taxi_hejmdal.run_task('tuner/retune')


async def check_running_circuit_ids(taxi_hejmdal, expected_ids):
    response = await taxi_hejmdal.get('v1/debug/running-circuits', params={})
    assert response.status_code == 200
    running_circuits = response.json()['running_circuits']

    ids = [circuit['id'] for circuit in running_circuits]
    assert sorted(ids) == sorted(expected_ids)


async def test_custom_check_group_by_label_sql(taxi_hejmdal, pgsql):
    await taxi_hejmdal.run_task('tuner/initialize')
    await taxi_hejmdal.run_task('services_component/invalidate')
    await taxi_hejmdal.invalidate_caches(
        clean_update=False, cache_names=['custom-checks-cache'],
    )

    # Check custom_check is loaded from db
    await check_running_circuit_ids(
        taxi_hejmdal,
        expected_ids=['custom-check-1-man', 'custom-check-1-vla'],
    )

    # Check custom_check is deleted
    await delete_custom_check(taxi_hejmdal, pgsql, check_id=1)
    await delete_custom_check(taxi_hejmdal, pgsql, check_id=2)
    await check_running_circuit_ids(taxi_hejmdal, expected_ids=[])


async def test_custom_check_group_by_label_api(
        taxi_hejmdal, pgsql, mockserver,
):
    @mockserver.json_handler(
        '/solomon-sensors/api/v2/projects/taxi/sensors/data',
    )
    def _mock_solomon_sensors_data(solomon_request, *args, **kwargs):
        return {
            'vector': [
                {
                    'timeseries': {
                        'alias': '',
                        'kind': 'DGAUGE',
                        'type': 'DGAUGE',
                        'labels': {'ctype': 'testing', 'host': 'man'},
                        'timestamps': [1632827220000],
                        'values': [23.0],
                    },
                },
                {
                    'timeseries': {
                        'alias': '',
                        'kind': 'DGAUGE',
                        'type': 'DGAUGE',
                        'labels': {'ctype': 'stable', 'host': 'sas'},
                        'timestamps': [1632827220000],
                        'values': [23.0],
                    },
                },
            ],
        }

    ticket = f'{TICKETS_QUEUE}-1'

    await taxi_hejmdal.run_task('tuner/initialize')
    await taxi_hejmdal.run_task('services_component/invalidate')

    # Get custom checks
    response = await taxi_hejmdal.get('v1/custom_checks/list')
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json['custom_check_list']) == 1
    await check_running_circuit_ids(
        taxi_hejmdal,
        expected_ids=['custom-check-1-man', 'custom-check-1-vla'],
    )

    # Create custom check
    response = await taxi_hejmdal.post(
        'v1/custom_checks',
        headers={'X-YaTaxi-Draft-Tickets': ticket},
        json={
            'name': 'crud_api_test',
            'description': 'custom check for testing CRUD api',
            'preset_id': 'template_test',
            'params': {
                'window_sec': 1,
                'min_samples': 1,
                'lower_time_ms': 0,
                'upper_time_ms': 1,
                'fixed_upper_bound': 1,
            },
            'flows': {
                'usage': {
                    'project': 'taxi',
                    'program': (
                        'series_sum({project=\'taxi\', '
                        'cluster=\'production_uservices\', '
                        'service=\'uservices\', '
                        'application=\'eats-surge-resolver\', '
                        'sensor=\'surge-stats.count_missing_places.1m\', '
                        'group=\'eda_eats-surge-resolver_stable\', '
                        'ctype=\'*\'})'
                    ),
                },
            },
            'group_by_labels': ['ctype'],
            'recipients': [],
        },
    )
    assert response.status_code == 200

    # Get custom checks
    response = await taxi_hejmdal.get('v1/custom_checks/list')
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json['custom_check_list']) == 2
    for custom_check in resp_json['custom_check_list']:
        if custom_check['id'] == 1:
            assert custom_check['name'] == 'test_custom_check_name'
            assert custom_check['description'] == 'TEST custom check'
            assert custom_check['updated'] is not None
        elif custom_check['id'] == 2:
            assert custom_check['name'] == 'crud_api_test'
            assert (
                custom_check['description']
                == 'custom check for testing CRUD api'
            )
            assert custom_check['updated'] is not None
        else:
            assert False

    await taxi_hejmdal.invalidate_caches(
        clean_update=False,
        cache_names=['custom-checks-cache', 'schemas-cache'],
    )
    await taxi_hejmdal.run_task('tuner/retune')
    await check_running_circuit_ids(
        taxi_hejmdal,
        expected_ids=[
            'custom-check-1-man',
            'custom-check-1-vla',
            'custom-check-2-testing',
            'custom-check-2-stable',
        ],
    )

    # Get custom checks by service id
    response = await taxi_hejmdal.get('v1/custom_checks/list?service_id=1')
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json['custom_check_list']) == 1

    # Get custom checks by id
    response = await taxi_hejmdal.get('v1/custom_checks?id=2')
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json == {
        'name': 'crud_api_test',
        'description': 'custom check for testing CRUD api',
        'preset_id': 'template_test',
        'params': {
            'window_sec': 1,
            'min_samples': 1,
            'lower_time_ms': 0,
            'upper_time_ms': 1,
            'fixed_upper_bound': 1,
        },
        'flows': {
            'usage': {
                'project': 'taxi',
                'program': (
                    'series_sum({project=\'taxi\', '
                    'cluster=\'production_uservices\', '
                    'service=\'uservices\', '
                    'application=\'eats-surge-resolver\', '
                    'sensor=\'surge-stats.count_missing_places.1m\', '
                    'group=\'eda_eats-surge-resolver_stable\', '
                    'ctype=\'*\'})'
                ),
            },
        },
        'group_by_labels': ['ctype'],
        'recipients': [],
        'ticket': ticket,
    }

    # Update custom check
    response = await taxi_hejmdal.put(
        'v1/custom_checks?id=2',
        headers={'X-YaTaxi-Draft-Tickets': ticket},
        json={
            'name': 'crud_api_test',
            'description': 'UPDATED: custom check for testing CRUD api',
            'service_id': 1,
            'preset_id': 'template_test',
            'params': {
                'window_sec': 5,
                'min_samples': 1,
                'lower_time_ms': 0,
                'upper_time_ms': 0,
                'fixed_upper_bound': 5000,
            },
            'flows': {
                'usage': {
                    'project': 'taxi',
                    'program': (
                        'series_sum({project=\'taxi\', '
                        'cluster=\'production_uservices\', '
                        'service=\'uservices\', '
                        'application=\'eats-surge-resolver\', '
                        'sensor=\'surge-stats.count_missing_places.1m\', '
                        'group=\'eda_eats-surge-resolver_stable\', '
                        'host!=\'cluster\'})'
                    ),
                },
            },
            'group_by_labels': ['host'],
            'recipients': [],
            'ticket': ticket,
        },
    )
    assert response.status_code == 200

    # Get custom checks by service id
    response = await taxi_hejmdal.get('v1/custom_checks/list?service_id=1')
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json['custom_check_list']) == 2

    # Get custom checks by id
    # Previous params values before cache validation
    response = await taxi_hejmdal.get('v1/custom_checks?id=2')
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json == {
        'name': 'crud_api_test',
        'description': 'UPDATED: custom check for testing CRUD api',
        'service_id': 1,
        'preset_id': 'template_test',
        'params': {
            'window_sec': 1,
            'min_samples': 1,
            'lower_time_ms': 0,
            'upper_time_ms': 1,
            'fixed_upper_bound': 1,
        },
        'flows': {
            'usage': {
                'project': 'taxi',
                'program': (
                    'series_sum({project=\'taxi\', '
                    'cluster=\'production_uservices\', '
                    'service=\'uservices\', '
                    'application=\'eats-surge-resolver\', '
                    'sensor=\'surge-stats.count_missing_places.1m\', '
                    'group=\'eda_eats-surge-resolver_stable\', '
                    'host!=\'cluster\'})'
                ),
            },
        },
        'group_by_labels': ['host'],
        'recipients': [],
        'ticket': ticket,
    }
    # Updated params values after cache validation
    await taxi_hejmdal.invalidate_caches(
        clean_update=False,
        cache_names=['custom-checks-cache', 'schemas-cache'],
    )
    response = await taxi_hejmdal.get('v1/custom_checks?id=2')
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json == {
        'name': 'crud_api_test',
        'description': 'UPDATED: custom check for testing CRUD api',
        'service_id': 1,
        'preset_id': 'template_test',
        'params': {
            'window_sec': 5,
            'min_samples': 1,
            'lower_time_ms': 0,
            'upper_time_ms': 0,
            'fixed_upper_bound': 5000,
        },
        'flows': {
            'usage': {
                'project': 'taxi',
                'program': (
                    'series_sum({project=\'taxi\', '
                    'cluster=\'production_uservices\', '
                    'service=\'uservices\', '
                    'application=\'eats-surge-resolver\', '
                    'sensor=\'surge-stats.count_missing_places.1m\', '
                    'group=\'eda_eats-surge-resolver_stable\', '
                    'host!=\'cluster\'})'
                ),
            },
        },
        'group_by_labels': ['host'],
        'recipients': [],
        'ticket': ticket,
    }

    await taxi_hejmdal.invalidate_caches(
        clean_update=True,
        cache_names=['custom-checks-cache', 'schemas-cache'],
    )
    await taxi_hejmdal.run_task('tuner/retune')
    # TODO fix DIAGNOSTICS-1718
    # await check_running_circuit_ids(
    #     taxi_hejmdal,
    #     expected_ids=[
    #         'custom-check-1-man',
    #         'custom-check-1-vla',
    #         'custom-check-2-sas',
    #         'custom-check-2-man',
    #     ],
    # )

    # Delete custom check
    response = await taxi_hejmdal.delete('v1/custom_checks?id=2')
    assert response.status_code == 200
    response = await taxi_hejmdal.get('v1/custom_checks?id=2')
    assert response.status_code == 404
    response = await taxi_hejmdal.delete('v1/custom_checks?id=2')
    assert response.status_code == 404
    response = await taxi_hejmdal.get('v1/custom_checks/list')
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json['custom_check_list']) == 1

    # Test cleanup
    await delete_custom_check(taxi_hejmdal, pgsql, check_id=1)
    await delete_custom_check(taxi_hejmdal, pgsql, check_id=2)
    await check_running_circuit_ids(taxi_hejmdal, expected_ids=[])


async def test_custom_check_group_by_label_constrains(
        taxi_hejmdal, pgsql, mockserver,
):
    ticket = f'{TICKETS_QUEUE}-1'

    # Check flow constrains: single line
    @mockserver.json_handler(
        '/solomon-sensors/api/v2/projects/taxi/sensors/data',
    )
    def _mock_wrong_solomon_sensors_data(solomon_request, *args, **kwargs):
        return {
            'vector': [
                {
                    'timeseries': {
                        'alias': '',
                        'kind': 'DGAUGE',
                        'type': 'DGAUGE',
                        'labels': {'host': 'man', 'ctype': 'testing'},
                        'timestamps': [1632827220000],
                        'values': [23.0],
                    },
                },
                {
                    'timeseries': {
                        'alias': '',
                        'kind': 'DGAUGE',
                        'type': 'DGAUGE',
                        'labels': {'host': 'sas', 'ctype': 'stable'},
                        'timestamps': [1632827220000],
                        'values': [8.0],
                    },
                },
                {
                    'timeseries': {
                        'alias': '',
                        'kind': 'DGAUGE',
                        'type': 'DGAUGE',
                        'labels': {'host': 'sas'},
                        'timestamps': [1632827220000],
                        'values': [8.0],
                    },
                },
            ],
        }

    # Check supporting only one group by label
    response = await taxi_hejmdal.post(
        'v1/custom_checks',
        headers={'X-YaTaxi-Draft-Tickets': ticket},
        json={
            'name': 'crud_api_test',
            'service_id': 1,
            'preset_id': 'template_test',
            'params': {
                'window_sec': 1,
                'min_samples': 1,
                'lower_time_ms': 0,
                'upper_time_ms': 1,
                'fixed_upper_bound': 1,
            },
            'flows': {
                'usage': {
                    'project': 'taxi',
                    'program': (
                        '{project=\'taxi\','
                        'cluster=\'production_uservices\','
                        'service=\'uservices\','
                        'application=\'eats-surge-resolver\','
                        'sensor=\'surge-stats.count_missing_places.1m\','
                        'group=\'eda_eats-surge-resolver_stable\'}'
                    ),
                },
            },
            'group_by_labels': ['ctype', 'host'],
            'recipients': [],
        },
    )
    assert response.status_code == 400
    resp_json = response.json()
    assert resp_json['message'] == (
        'ExtractAndValidateCustomCheckTimeLines: only one group by labels '
        'supported, but 2 are created'
    )

    # Check one timeline for unique group by label
    response = await taxi_hejmdal.post(
        'v1/custom_checks',
        headers={'X-YaTaxi-Draft-Tickets': ticket},
        json={
            'name': 'crud_api_test',
            'service_id': 1,
            'preset_id': 'template_test',
            'params': {
                'window_sec': 1,
                'min_samples': 1,
                'lower_time_ms': 0,
                'upper_time_ms': 1,
                'fixed_upper_bound': 1,
            },
            'flows': {
                'usage': {
                    'project': 'taxi',
                    'program': (
                        '{project=\'taxi\','
                        'cluster=\'production_uservices\','
                        'service=\'uservices\','
                        'application=\'eats-surge-resolver\','
                        'sensor=\'surge-stats.count_missing_places.1m\','
                        'group=\'eda_eats-surge-resolver_stable\'}'
                    ),
                },
            },
            'group_by_labels': ['host'],
            'recipients': [],
        },
    )
    assert response.status_code == 400
    resp_json = response.json()
    assert resp_json['message'] == (
        'ExtractAndValidateCustomCheckTimeLines: custom check flow has more '
        'then one timeline for unique group by label value host'
    )

    # Check all timelines has group by label
    response = await taxi_hejmdal.post(
        'v1/custom_checks',
        headers={'X-YaTaxi-Draft-Tickets': ticket},
        json={
            'name': 'crud_api_test',
            'service_id': 1,
            'preset_id': 'template_test',
            'params': {
                'window_sec': 1,
                'min_samples': 1,
                'lower_time_ms': 0,
                'upper_time_ms': 1,
                'fixed_upper_bound': 1,
            },
            'flows': {
                'usage': {
                    'project': 'taxi',
                    'program': (
                        '{project=\'taxi\','
                        'cluster=\'production_uservices\','
                        'service=\'uservices\','
                        'application=\'eats-surge-resolver\','
                        'sensor=\'surge-stats.count_missing_places.1m\','
                        'group=\'eda_eats-surge-resolver_stable\'}'
                    ),
                },
            },
            'group_by_labels': ['ctype'],
            'recipients': [],
        },
    )
    assert response.status_code == 400
    resp_json = response.json()
    assert resp_json['message'] == (
        'ExtractAndValidateCustomCheckTimeLines: custom check flow timeline '
        'has no value for group by label ctype'
    )

    # Test cleanup
    await delete_custom_check(taxi_hejmdal, pgsql)
    await check_running_circuit_ids(taxi_hejmdal, expected_ids=[])


async def test_custom_check_group_by_label_retune(
        taxi_hejmdal, pgsql, mockserver,
):
    @mockserver.json_handler(
        '/solomon-sensors/api/v2/projects/taxi/sensors/data',
    )
    def _mock_solomon_sensors_data(solomon_request, *args, **kwargs):
        return {
            'vector': [
                {
                    'timeseries': {
                        'alias': '',
                        'kind': 'DGAUGE',
                        'type': 'DGAUGE',
                        'labels': {'host': 'sas'},
                        'timestamps': [1632827220000],
                        'values': [23.0],
                    },
                },
                {
                    'timeseries': {
                        'alias': '',
                        'kind': 'DGAUGE',
                        'type': 'DGAUGE',
                        'labels': {'host': 'myt'},
                        'timestamps': [1632827220000],
                        'values': [23.0],
                    },
                },
            ],
        }

    await taxi_hejmdal.run_task('tuner/initialize')
    await taxi_hejmdal.run_task('services_component/invalidate')

    # Get custom checks
    response = await taxi_hejmdal.get('v1/custom_checks/list')
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json['custom_check_list']) == 1
    await check_running_circuit_ids(
        taxi_hejmdal,
        expected_ids=['custom-check-1-man', 'custom-check-1-vla'],
    )

    # Get custom checks by id
    response = await taxi_hejmdal.get('v1/custom_checks?id=1')
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json == {
        'name': 'test_custom_check_name',
        'description': 'TEST custom check',
        'preset_id': 'template_test',
        'params': {
            'window_sec': 5,
            'min_samples': 60,
            'lower_time_ms': 0,
            'upper_time_ms': 5000,
            'fixed_upper_bound': 100,
        },
        'flows': {
            'usage': {
                'project': 'taxi',
                'program': (
                    'series_sum({project=\'taxi\', '
                    'cluster=\'production_uservices\', '
                    'service=\'uservices\', '
                    'application=\'eats-surge-resolver\', '
                    'sensor=\'surge-stats.count_missing_places.1m\', '
                    'group=\'test-group_stable|test-group_pre_stable\', '
                    'host=\'*\'})'
                ),
            },
        },
        'group_by_labels': ['host'],
        'recipients': [],
        'ticket': '',
        'service_id': 1,
    }

    # Updated params values after cache validation and retune
    await taxi_hejmdal.run_task('distlock/custom_check_manager')
    await taxi_hejmdal.invalidate_caches(
        clean_update=False,
        cache_names=['custom-checks-cache', 'schemas-cache'],
    )
    await taxi_hejmdal.run_task('tuner/retune')

    # Get custom checks after update
    response = await taxi_hejmdal.get('v1/custom_checks/list')
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json['custom_check_list']) == 1
    await check_running_circuit_ids(
        taxi_hejmdal,
        expected_ids=['custom-check-1-sas', 'custom-check-1-myt'],
    )

    # Get custom checks by id after update
    response = await taxi_hejmdal.get('v1/custom_checks?id=1')
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json == {
        'name': 'test_custom_check_name',
        'description': 'TEST custom check',
        'preset_id': 'template_test',
        'params': {
            'window_sec': 5,
            'min_samples': 60,
            'lower_time_ms': 0,
            'upper_time_ms': 5000,
            'fixed_upper_bound': 100,
        },
        'flows': {
            'usage': {
                'project': 'taxi',
                'program': (
                    'series_sum({project=\'taxi\', '
                    'cluster=\'production_uservices\', '
                    'service=\'uservices\', '
                    'application=\'eats-surge-resolver\', '
                    'sensor=\'surge-stats.count_missing_places.1m\', '
                    'group=\'test-group_stable|test-group_pre_stable\', '
                    'host=\'*\'})'
                ),
            },
        },
        'group_by_labels': ['host'],
        'recipients': [],
        'ticket': '',
        'service_id': 1,
    }

    # Test cleanup
    await delete_custom_check(taxi_hejmdal, pgsql)
    await check_running_circuit_ids(taxi_hejmdal, expected_ids=[])


async def test_custom_check_test_group_by_label_tool_api(
        taxi_hejmdal, pgsql, mockserver,
):
    sas_time_series = {
        'timeseries': {
            'alias': '',
            'kind': 'DGAUGE',
            'type': 'DGAUGE',
            'labels': {
                'cluster': 'production_uservices',
                'project': 'taxi',
                'sensor': 'surge-stats.count_missing_places.1m',
                'application': 'eats-surge-resolver',
                'service': 'uservices',
                'group': 'eda_eats-surge-resolver_stable',
                'host': 'Sas',
            },
            'timestamps': [
                1633348800000,  # 12:00
                1633348860000,  # 12:01
                1633348920000,  # 12:02
                1633348980000,  # 12:03
                1633349040000,  # 12:04
                1633349100000,  # 12:05
                1633349160000,  # 12:06
                1633349220000,  # 12:07
                1633349280000,  # 12:08
                1633349340000,  # 12:09
            ],
            'values': [
                10.0,  # NoData
                10.0,  # NoData
                10.0,  # NoData
                10.0,  # Ok
                30.0,  # Ok
                30.0,  # Ok
                30.0,  # Ok
                30.0,  # Warning
                30.0,  # Warning
                30.0,  # Warning
            ],
        },
    }
    vla_time_series = {
        'timeseries': {
            'alias': '',
            'kind': 'DGAUGE',
            'type': 'DGAUGE',
            'labels': {
                'cluster': 'production_uservices',
                'project': 'taxi',
                'sensor': 'surge-stats.count_missing_places.1m',
                'application': 'eats-surge-resolver',
                'service': 'uservices',
                'group': 'eda_eats-surge-resolver_stable',
                'host': 'Vla',
            },
            'timestamps': [
                1633348800000,  # 12:00
                1633348860000,  # 12:01
                1633348920000,  # 12:02
                1633348980000,  # 12:03
                1633349040000,  # 12:04
                1633349100000,  # 12:05
                1633349160000,  # 12:06
                1633349220000,  # 12:07
                1633349280000,  # 12:08
                1633349340000,  # 12:09
            ],
            'values': [
                10.0,  # NoData
                10.0,  # NoData
                10.0,  # NoData
                10.0,  # Ok
                10.0,  # Ok
                10.0,  # Ok
                50.0,  # Ok
                50.0,  # Ok
                50.0,  # Ok
                50.0,  # Warning
            ],
        },
    }

    @mockserver.json_handler(
        '/solomon-sensors/api/v2/projects/taxi/sensors/data',
    )
    def _mock_solomon_sensors_data(solomon_request, *args, **kwargs):
        if (
                solomon_request.json.get('program')
                == '{project=\'taxi\', host=\'Sas\'}'
        ):
            return {'vector': [sas_time_series]}
        if (
                solomon_request.json.get('program')
                == '{project=\'taxi\', host=\'Vla\'}'
        ):
            return {'vector': [vla_time_series]}
        return {'vector': [sas_time_series, vla_time_series]}

    await taxi_hejmdal.run_task('tuner/initialize')
    await taxi_hejmdal.run_task('services_component/invalidate')

    # Test custom check
    response = await taxi_hejmdal.post(
        'v1/custom_checks/test',
        json={
            'preset_id': 'template_test',
            'params': {
                'window_sec': 300,
                'min_samples': 4,
                'lower_time_ms': 0,
                'upper_time_ms': 1000,
                'fixed_upper_bound': 20,
            },
            'flows': {
                'usage': {
                    'project': 'taxi',
                    'program': '{project=\'taxi\', host=\'Sas|Vla\'}',
                },
            },
            'group_by_labels': ['host'],
            'alert_details': 'Some alert details.',
            'from': '2021-10-04T12:00:00.000Z',
            'to': '2021-10-04T12:10:00.000Z',
        },
    )
    assert response.status_code == 200
    resp_json = response.json()
    # 10 points returned, but min_samples = 4.
    # So the 1st, 2nd and 3rd states had not been pushed out.

    # Sas host
    assert len(resp_json['Sas']['state_points']) == 7
    for state_point in resp_json['Sas']['state_points']:
        if state_point['state'] == 'Ok':
            assert to_datetime(state_point['time']) > to_datetime(
                '2021-10-04T12:02:00+00:00',
            )
            assert to_datetime(state_point['time']) < to_datetime(
                '2021-10-04T12:07:00+00:00',
            )
        if state_point['state'] == 'Warning':
            assert to_datetime(state_point['time']) >= to_datetime(
                '2021-10-04T12:07:00+00:00',
            )
            assert (
                state_point['description']
                == 'Значение метрики превысило пороговое значение: 30.0 > 20.0'
            )

    # Vla host
    assert len(resp_json['Vla']['state_points']) == 7
    for state_point in resp_json['Vla']['state_points']:
        if state_point['state'] == 'Ok':
            assert to_datetime(state_point['time']) > to_datetime(
                '2021-10-04T12:02:00+00:00',
            )
            assert to_datetime(state_point['time']) < to_datetime(
                '2021-10-04T12:09:00+00:00',
            )
        if state_point['state'] == 'Warning':
            assert to_datetime(state_point['time']) >= to_datetime(
                '2021-10-04T12:09:00+00:00',
            )
            assert (
                state_point['description']
                == 'Значение метрики превысило пороговое значение: 50.0 > 20.0'
            )

    # Test cleanup
    await delete_custom_check(taxi_hejmdal, pgsql)
    await check_running_circuit_ids(taxi_hejmdal, expected_ids=[])
