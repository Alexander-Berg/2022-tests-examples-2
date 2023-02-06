import datetime

import pytest


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


async def delete_custom_check(taxi_hejmdal, pgsql):
    cursor = pgsql['hejmdal'].cursor()
    query = """
        update custom_checks
        set deleted = true,
            revision=default
        where id=1;"""
    cursor.execute(query)
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


async def test_custom_check_sql(taxi_hejmdal, pgsql):
    await taxi_hejmdal.run_task('tuner/initialize')
    await taxi_hejmdal.run_task('services_component/invalidate')
    await taxi_hejmdal.invalidate_caches(
        clean_update=False, cache_names=['custom-checks-cache'],
    )

    # Check custom_check is loaded from db
    await check_running_circuit_ids(
        taxi_hejmdal, expected_ids=['custom-check-1'],
    )

    # Check custom_check is deleted
    await delete_custom_check(taxi_hejmdal, pgsql)
    await check_running_circuit_ids(taxi_hejmdal, expected_ids=[])


async def test_custom_check_api(taxi_hejmdal, pgsql, mockserver):
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
                        'labels': {},
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
        taxi_hejmdal, expected_ids=['custom-check-1'],
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
                        'host!=\'cluster|Man|Sas|Vla|Myt|Iva\'})'
                    ),
                },
            },
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
        taxi_hejmdal, expected_ids=['custom-check-1', 'custom-check-2'],
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
                    'host!=\'cluster|Man|Sas|Vla|Myt|Iva\'})'
                ),
            },
        },
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
        'recipients': [],
        'ticket': ticket,
    }
    # Updated params values after cache validation
    await taxi_hejmdal.invalidate_caches(
        clean_update=False, cache_names=['schemas-cache'],
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
        'recipients': [],
        'ticket': ticket,
    }

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
    await delete_custom_check(taxi_hejmdal, pgsql)
    await check_running_circuit_ids(taxi_hejmdal, expected_ids=[])


async def test_custom_check_constrains(taxi_hejmdal, pgsql, mockserver):
    ticket = f'{TICKETS_QUEUE}-1'

    # Check unique constrains
    response = await taxi_hejmdal.post(
        'v1/custom_checks',
        headers={'X-YaTaxi-Draft-Tickets': ticket},
        json={
            'name': 'test_custom_check_name',
            'service_id': 1,
            'preset_id': 'template_test',
            'params': {
                'window_sec': 1,
                'min_samples': 1,
                'lower_time_ms': 0,
                'upper_time_ms': 1,
                'fixed_upper_bound': 1,
            },
            'flows': {},
            'recipients': [],
        },
    )
    assert response.status_code == 400

    # Check name constrains
    response = await taxi_hejmdal.post(
        'v1/custom_checks',
        headers={'X-YaTaxi-Draft-Tickets': ticket},
        json={
            'name': 'name with whitespace',
            'service_id': 1,
            'preset_id': 'template_test',
            'params': {
                'window_sec': 1,
                'min_samples': 1,
                'lower_time_ms': 0,
                'upper_time_ms': 1,
                'fixed_upper_bound': 1,
            },
            'flows': {},
            'recipients': [],
        },
    )
    assert response.status_code == 400

    response = await taxi_hejmdal.post(
        'v1/custom_checks',
        headers={'X-YaTaxi-Draft-Tickets': ticket},
        json={
            'name': 'name_with_+_symbol',
            'service_id': 1,
            'preset_id': 'template_test',
            'params': {
                'window_sec': 1,
                'min_samples': 1,
                'lower_time_ms': 0,
                'upper_time_ms': 1,
                'fixed_upper_bound': 1,
            },
            'flows': {},
            'recipients': [],
        },
    )
    assert response.status_code == 400

    # Check flow constrains: all entry points
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
                'some_name': {
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
            'recipients': [],
        },
    )
    assert response.status_code == 400

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
                        'labels': {},
                        'timestamps': [1632827220000],
                        'values': [23.0],
                    },
                },
                {
                    'timeseries': {
                        'alias': '',
                        'kind': 'DGAUGE',
                        'type': 'DGAUGE',
                        'labels': {},
                        'timestamps': [1632827220000],
                        'values': [8.0],
                    },
                },
            ],
        }

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
            'recipients': [],
        },
    )
    assert response.status_code == 400

    # Test cleanup
    await delete_custom_check(taxi_hejmdal, pgsql)
    await check_running_circuit_ids(taxi_hejmdal, expected_ids=[])


async def test_custom_check_presets_api(taxi_hejmdal, pgsql):
    await taxi_hejmdal.run_task('tuner/initialize')
    await taxi_hejmdal.run_task('services_component/invalidate')

    # Get preset
    response = await taxi_hejmdal.get('v1/custom_checks/presets/list')
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json == {
        'preset_list': [
            {
                'id': 'template_test',
                'name': 'Custom check template: threshold',
            },
        ],
    }

    # Get preset by id
    response = await taxi_hejmdal.get(
        'v1/custom_checks/presets?id=template_test',
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json == {
        'description': 'Schema template for testing',
        'name': 'Custom check template: threshold',
        'params': {
            'type': 'object',
            'required': [
                'window_sec',
                'min_samples',
                'lower_time_ms',
                'upper_time_ms',
                'fixed_upper_bound',
            ],
            'properties': {
                'alert_format': {
                    'type': 'string',
                    'default': (
                        'Значение метрики превысило пороговое значение:'
                        ' {value:.1f} > {bound:.1f}'
                    ),
                },
                'fixed_upper_bound': {'type': 'number'},
                'lower_time_ms': {'type': 'number'},
                'min_samples': {'type': 'number'},
                'upper_time_ms': {'type': 'number'},
                'window_sec': {'type': 'number'},
            },
        },
    }

    # Test cleanup
    await delete_custom_check(taxi_hejmdal, pgsql)
    await check_running_circuit_ids(taxi_hejmdal, expected_ids=[])


async def test_custom_check_test_tool_api(taxi_hejmdal, pgsql, mockserver):
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
                        'labels': {
                            'cluster': 'production_uservices',
                            'project': 'taxi',
                            'sensor': 'surge-stats.count_missing_places.1m',
                            'application': 'eats-surge-resolver',
                            'service': 'uservices',
                            'group': 'eda_eats-surge-resolver_stable',
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
                },
            ],
        }

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
                    'program': (
                        'series_sum({project=\'taxi\', '
                        'cluster=\'production_uservices\', '
                        'service=\'uservices\', '
                        'application=\'eats-surge-resolver\', '
                        'sensor=\'surge-stats.count_missing_places.1m\', '
                        'group=\'eda_eats-surge-resolver_stable\')'
                    ),
                },
            },
            'alert_details': 'Some alert details.',
            'from': '2021-10-04T12:00:00.000Z',
            'to': '2021-10-04T12:10:00.000Z',
        },
    )
    assert response.status_code == 200
    resp_json = response.json()
    # 10 points returned, but min_samples = 4.
    # So the 1st, 2nd and 3rd states had not been pushed out.
    assert len(resp_json['metric']['state_points']) == 7
    for state_point in resp_json['metric']['state_points']:
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

    # Test cleanup
    await delete_custom_check(taxi_hejmdal, pgsql)
    await check_running_circuit_ids(taxi_hejmdal, expected_ids=[])


@pytest.mark.config(
    HEJMDAL_CUSTOM_CHECKS_SETTINGS=HEJMDAL_CUSTOM_CHECKS_SETTINGS,
)
async def test_custom_check_draft_api(taxi_hejmdal, pgsql, mockserver):
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
                        'labels': {},
                        'timestamps': [1632827220000],
                        'values': [23.0],
                    },
                },
            ],
        }

    @mockserver.json_handler('/clowny-alert-manager/v1/alerts/upsert/')
    def _mock_alert_manager_upsert(upsert_request):
        return {}

    @mockserver.json_handler('/clowny-alert-manager/v1/alerts/remove/')
    def _mock_alert_manager_remove(remove_request):
        return {}

    ticket = f'{TICKETS_QUEUE}-1'

    flows = {
        'usage': {
            'project': 'taxi',
            'program': (
                'series_sum({project=\'taxi\', '
                'cluster=\'production_uservices\', '
                'service=\'uservices\', '
                'application=\'eats-surge-resolver\', '
                'sensor=\'surge-stats.count_missing_places.1m\', '
                'group=\'eda_eats-surge-resolver_stable\', '
                'host!=\'cluster|Man|Sas|Vla|Myt|Iva\'})'
            ),
        },
    }

    params = {
        'window_sec': 1,
        'min_samples': 1,
        'lower_time_ms': 0,
        'upper_time_ms': 1,
        'fixed_upper_bound': 1,
    }

    custom_check_without_ticket = {
        'name': 'unique_custom_check_name',
        'description': 'custom check for testing CRUD api',
        'preset_id': 'template_test',
        'service_id': 1,
        'params': params,
        'flows': flows,
        'recipients': ['alklev'],
    }

    custom_check = {
        'name': 'unique_custom_check_name',
        'description': 'custom check for testing CRUD api',
        'preset_id': 'template_test',
        'service_id': 1,
        'params': params,
        'flows': flows,
        'recipients': ['alklev'],
        'ticket': ticket,
    }

    updated_custom_check = {
        'name': 'unique_custom_check_name',
        'description': 'UPDATED custom check for testing CRUD api',
        'preset_id': 'template_test',
        'service_id': 1,
        'params': params,
        'flows': flows,
        'recipients': ['alklev', 'victorshch'],
        'ticket': ticket,
    }

    custom_check_existed_name = {
        'name': 'test_custom_check_name',
        'description': 'custom check for testing CRUD api',
        'preset_id': 'template_test',
        'service_id': 1,
        'params': params,
        'flows': flows,
        'recipients': [],
    }

    custom_check_aggregate_issue = {
        'name': 'unique_custom_check_name',
        'description': 'custom check for testing CRUD api',
        'preset_id': 'template_test',
        'service_id': 2,
        'params': params,
        'flows': flows,
        'recipients': ['alklev'],
    }

    await taxi_hejmdal.run_task('tuner/initialize')
    await taxi_hejmdal.run_task('services_component/invalidate')

    # Check if can create custom check: custom-name-already-exists
    response = await taxi_hejmdal.post(
        'v1/custom_checks/check-draft', json=custom_check_existed_name,
    )
    assert response.status_code == 400
    resp_json = response.json()
    assert resp_json['code'] == 'custom-name-already-exists'

    # Check if can create custom check: unable-to-create-aggregate
    response = await taxi_hejmdal.post(
        'v1/custom_checks/check-draft', json=custom_check_aggregate_issue,
    )
    assert response.status_code == 400
    resp_json = response.json()
    assert resp_json['code'] == 'unable-to-create-aggregate'

    # Check if can create custom check: Ok
    response = await taxi_hejmdal.post(
        'v1/custom_checks/check-draft', json=custom_check_without_ticket,
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['data'] == custom_check_without_ticket
    assert 'tickets' in resp_json
    assert 'create_data' in resp_json['tickets']
    assert resp_json['tickets']['create_data']['ticket_queue'] == TICKETS_QUEUE

    # Create custom check
    response = await taxi_hejmdal.post(
        'v1/custom_checks/',
        headers={'X-YaTaxi-Draft-Tickets': ticket},
        json=resp_json['data'],
    )
    assert response.status_code == 200

    # Invalidate cache to receive custom_check schema
    await taxi_hejmdal.invalidate_caches(
        clean_update=False, cache_names=['schemas-cache'],
    )

    # Check if can update custom check: custom-name-already-exists
    response = await taxi_hejmdal.put(
        'v1/custom_checks/check-draft?id=2',
        headers={'X-YaTaxi-Draft-Tickets': ticket},
        json=custom_check_existed_name,
    )
    assert response.status_code == 400
    resp_json = response.json()
    assert resp_json['code'] == 'custom-name-already-exists'

    # Check if can update custom check: custom-check-is-not-found
    response = await taxi_hejmdal.put(
        'v1/custom_checks/check-draft?id=3',
        headers={'X-YaTaxi-Draft-Tickets': ticket},
        json=updated_custom_check,
    )
    assert response.status_code == 404
    resp_json = response.json()
    assert resp_json['code'] == 'custom-check-is-not-found'

    # Check if can update custom check: Ok
    response = await taxi_hejmdal.put(
        'v1/custom_checks/check-draft?id=2',
        headers={'X-YaTaxi-Draft-Tickets': ticket},
        json=updated_custom_check,
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['data'] == updated_custom_check
    assert resp_json['diff']['current'] == custom_check
    assert resp_json['diff']['new'] == updated_custom_check

    # Update custom check
    response = await taxi_hejmdal.put(
        'v1/custom_checks?id=2',
        headers={'X-YaTaxi-Draft-Tickets': ticket},
        json=resp_json['data'],
    )
    assert response.status_code == 200

    # Check if can delete custom check: custom-check-is-not-found
    response = await taxi_hejmdal.delete(
        'v1/custom_checks/check-draft?id=3', json=updated_custom_check,
    )
    assert response.status_code == 404
    resp_json = response.json()
    assert resp_json['code'] == 'custom-check-is-not-found'

    # Check if can delete custom check: Ok
    response = await taxi_hejmdal.delete(
        'v1/custom_checks/check-draft?id=2', json=updated_custom_check,
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['data'] == {}
    assert resp_json['diff']['current'] == updated_custom_check
    assert resp_json['diff']['new'] == {}

    # Delete custom check
    response = await taxi_hejmdal.delete(
        'v1/custom_checks?id=2', json=resp_json['data'],
    )
    assert response.status_code == 200

    # Test cleanup
    await delete_custom_check(taxi_hejmdal, pgsql)
    await check_running_circuit_ids(taxi_hejmdal, expected_ids=[])
