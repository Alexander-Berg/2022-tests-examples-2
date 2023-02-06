import copy
import json

import pytest

INVALID_SCHEMA = {'name': 'invalid', 'type': 'schema'}
TEST_SCHEMA_STR = """
{
  "blocks": [
    {
      "id": "oob",
      "type": "out_of_bounds_state"
    }
  ],
  "entry_points": [
  ],
  "name": "Test schema",
  "type": "schema",
  "out_points": [
    {
      "debug": true,
      "id": "state_out",
      "type": "bypass"
    }
  ],
  "wires": [
    {
      "from": "oob",
      "to": "state_out",
      "type": "state"
    }
  ]
}
"""
TEST_SCHEMA = json.loads(TEST_SCHEMA_STR)
TEST_SCHEMA2 = copy.deepcopy(TEST_SCHEMA)
TEST_SCHEMA2['name'] = 'Test schema 2'
TEST_TEMPLATE = copy.deepcopy(TEST_SCHEMA)
TEST_TEMPLATE['type'] = 'template'
TEST_SCHEMA_USING_TEMPLATE = {
    'name': 'Test schema using tpl',
    'type': 'schema',
    'use_template': 'template_test',
}
TEST_SCHEMA_WITH_TEST_CASE = {
    'name': 'test_name',
    'type': 'schema',
    'history_data_duration_sec': 10,
    'entry_points': [{'id': 'entry', 'type': 'data_entry_point'}],
    'out_points': [{'id': 'alert', 'type': 'state_out_point'}],
    'blocks': [
        {
            'id': 'no_data_block',
            'type': 'no_data_state',
            'no_data_duration_before_warn_sec': 60,
            'no_data_duration_before_crit_sec': 120,
            'start_state': 'Ok',
        },
    ],
    'wires': [
        {'to': 'no_data_block', 'from': 'entry', 'type': 'state'},
        {'to': 'alert', 'from': 'no_data_block', 'type': 'state'},
    ],
}


def execute_and_return_single_row(cursor, query):
    cursor.execute(query)
    return cursor.fetchall()[0]


def execute_and_return_single_val(cursor, query):
    return execute_and_return_single_row(cursor, query)[0]


async def test_circuit_schema_list(taxi_hejmdal):
    await taxi_hejmdal.run_task('tuner/initialize')

    response = await taxi_hejmdal.post('v1/circuit_schema/list')
    assert response.status_code == 200
    assert response.json() == {
        'circuit_schemas': [
            {
                'id': 'schema_ks_test',
                'type': 'schema',
                'updated': '1970-01-15T07:58:08.001+00:00',
                'description': 'KS test',
            },
            {
                'id': 'schema_oom_check',
                'type': 'schema',
                'updated': '1970-01-15T08:58:08.001+00:00',
                'description': 'Check oom indicator, crit on > 0.9',
            },
            {
                'id': 'schema_rtc_cpu_usage_v2',
                'type': 'schema',
                'updated': '1970-01-15T06:58:08.001+00:00',
                'description': 'RTC cpu usage',
            },
            {
                'id': 'schema_rtc_memory_usage_v2',
                'type': 'schema',
                'updated': '1970-01-15T06:58:08.001+00:00',
                'description': 'RTC memory usage',
            },
            {
                'id': 'schema_test',
                'type': 'schema',
                'updated': '1970-01-15T06:58:08.001+00:00',
                'description': 'test',
            },
            {
                'id': 'schema_test_delete',
                'type': 'schema',
                'updated': '1970-01-15T08:58:08.001+00:00',
                'description': 'Schema to test deletion',
            },
            {
                'id': 'schema_timings-p95',
                'type': 'schema',
                'updated': '1970-01-15T08:58:08.001+00:00',
                'description': (
                    'Inter-quartile range + anti-flap '
                    + '+ mute low rps + mute -7d iqr'
                ),
            },
            {
                'id': 'schema_timings-p98',
                'type': 'schema',
                'updated': '1970-01-15T08:58:08.001+00:00',
                'description': (
                    'Inter-quartile range + anti-flap '
                    + '+ mute low rps + mute -7d iqr'
                ),
            },
            {
                'id': 'schema_with_test_case',
                'type': 'schema',
                'updated': '1970-01-15T06:58:08.001+00:00',
                'description': 'test_schema_update_with_tests',
            },
        ],
    }


async def test_circuit_schema_retrieve(taxi_hejmdal, pgsql):
    cursor = pgsql['hejmdal'].cursor()
    iqr_json = execute_and_return_single_val(
        cursor,
        'select circuit_schema from circuit_schemas '
        + 'where id=\'schema_ks_test\'',
    )

    response = await taxi_hejmdal.post(
        'v1/circuit_schema/retrieve', params={'id': 'schema_ks_test'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'description': 'KS test',
        'type': 'schema',
        'updated': '1970-01-15T07:58:08.001+00:00',
        'circuit_schema': iqr_json,
        'custom': False,
    }

    response = await taxi_hejmdal.post(
        'v1/circuit_schema/retrieve', params={'id': 'unknown'},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'circuit schema not found',
    }


@pytest.mark.now('2019-01-01T00:00:00')
async def test_circuit_schema_create_update(taxi_hejmdal, mocked_time, pgsql):
    cursor = pgsql['hejmdal'].cursor()
    old_max_revision = execute_and_return_single_val(
        cursor, 'SELECT max(revision) from circuit_schemas',
    )

    response = await taxi_hejmdal.post(
        'v1/circuit_schema/retrieve', params={'id': 'schema_new'},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'circuit schema not found',
    }

    response = await taxi_hejmdal.put(
        'v1/circuit_schema/create',
        params={'id': 'schema_new'},
        json={
            'circuit_schema': TEST_SCHEMA,
            'type': 'schema',
            'description': 'Test schema description 1',
            'custom': False,
        },
    )
    assert response.status_code == 200
    assert response.json() == {}

    current_revision = execute_and_return_single_val(
        cursor, 'SELECT revision from circuit_schemas where id=\'schema_new\'',
    )
    assert current_revision >= old_max_revision + 1

    response = await taxi_hejmdal.post(
        'v1/circuit_schema/retrieve', params={'id': 'schema_new'},
    )
    assert response.status_code == 200
    response_json = response.json()
    # we can't mock NOW() for pgsql
    del response_json['updated']
    assert response_json == {
        'circuit_schema': TEST_SCHEMA,
        'type': 'schema',
        'description': 'Test schema description 1',
        'custom': False,
    }

    response = await taxi_hejmdal.put(
        'v1/circuit_schema/create',
        params={'id': 'schema_new'},
        json={
            'circuit_schema': TEST_SCHEMA2,
            'type': 'schema',
            'description': 'Test schema description 2',
            'custom': False,
        },
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': '409',
        'message': 'circuit schema already exists',
    }

    mocked_time.sleep(1)

    response = await taxi_hejmdal.put(
        'v1/circuit_schema/update',
        params={'id': 'schema_new'},
        json={
            'circuit_schema': TEST_SCHEMA2,
            'type': 'schema',
            'description': 'Test schema description 2',
            'custom': False,
        },
    )
    assert response.status_code == 200
    assert response.json() == {}

    current_revision = execute_and_return_single_val(
        cursor, 'SELECT revision from circuit_schemas where id=\'schema_new\'',
    )
    assert current_revision >= old_max_revision + 2

    response = await taxi_hejmdal.post(
        'v1/circuit_schema/retrieve', params={'id': 'schema_new'},
    )
    assert response.status_code == 200
    response_json = response.json()
    # we can't mock NOW() for pgsql
    del response_json['updated']
    assert response_json == {
        'circuit_schema': TEST_SCHEMA2,
        'type': 'schema',
        'description': 'Test schema description 2',
        'custom': False,
    }

    response = await taxi_hejmdal.put(
        'v1/circuit_schema/update',
        params={'id': 'schema_unknown'},
        json={
            'circuit_schema': TEST_SCHEMA2,
            'type': 'schema',
            'description': 'Test schema description 2',
            'custom': False,
        },
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'circuit schema not found',
    }


@pytest.mark.parametrize(
    'handler_path', ['v1/circuit_schema/create', 'v1/circuit_schema/update'],
)
async def test_circuit_schema_invalid(taxi_hejmdal, handler_path):
    response = await taxi_hejmdal.put(
        handler_path,
        params={'id': 'schema_new'},
        json={
            'circuit_schema': INVALID_SCHEMA,
            'type': 'schema',
            'description': 'Test schema description',
            'custom': False,
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': (
            'invalid circuit schema: Schema \'id\': required parameter '
            '\'entry_points\' is missing'
        ),
    }


async def test_circuit_schema_delete(taxi_hejmdal):
    response = await taxi_hejmdal.post(
        'v1/circuit_schema/retrieve', params={'id': 'schema_test_delete'},
    )
    assert response.status_code == 200

    response = await taxi_hejmdal.delete(
        'v1/circuit_schema/delete', params={'id': 'schema_test_delete'},
    )
    assert response.status_code == 200
    assert response.json() == {}

    response = await taxi_hejmdal.post(
        'v1/circuit_schema/retrieve', params={'id': 'schema_test_delete'},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'circuit schema not found',
    }

    response = await taxi_hejmdal.delete(
        'v1/circuit_schema/delete', params={'id': 'unknown_schema'},
    )
    assert response.status_code == 200
    assert response.json() == {}

    response = await taxi_hejmdal.delete(
        'v1/circuit_schema/delete', params={'id': 'schema_test'},
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': '409',
        'message': 'circuit schema in use',
    }


async def test_circuit_schema_template(taxi_hejmdal):
    response = await taxi_hejmdal.put(
        'v1/circuit_schema/create',
        params={'id': 'schema_new_using_tpl'},
        json={
            'circuit_schema': TEST_SCHEMA_USING_TEMPLATE,
            'type': 'schema',
            'description': 'Test schema description',
            'custom': False,
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': (
            'invalid circuit schema: schema template id \'template_test\' not '
            'found in cache'
        ),
    }

    response = await taxi_hejmdal.put(
        'v1/circuit_schema/create',
        params={'id': 'template_test'},
        json={
            'circuit_schema': TEST_TEMPLATE,
            'type': 'template',
            'description': 'Test tpl description',
            'custom': False,
        },
    )
    assert response.status_code == 200
    assert response.json() == {}

    await taxi_hejmdal.invalidate_caches(
        clean_update=True, cache_names=['schemas-cache'],
    )

    response = await taxi_hejmdal.put(
        'v1/circuit_schema/create',
        params={'id': 'schema_new_using_tpl'},
        json={
            'circuit_schema': TEST_SCHEMA_USING_TEMPLATE,
            'type': 'schema',
            'description': 'Test schema description',
            'custom': False,
        },
    )
    assert response.status_code == 200
    assert response.json() == {}

    await taxi_hejmdal.invalidate_caches(
        clean_update=True, cache_names=['schemas-cache'],
    )

    response = await taxi_hejmdal.put(
        'v1/circuit_schema/update',
        params={'id': 'schema_new_using_tpl'},
        json={
            'circuit_schema': TEST_SCHEMA_USING_TEMPLATE,
            'type': 'template',
            'description': 'Test schema description',
            'custom': False,
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'invalid circuit schema: cannot change schema type',
    }

    response = await taxi_hejmdal.delete(
        'v1/circuit_schema/delete', params={'id': 'template_test'},
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': '409',
        'message': 'circuit schema in use',
    }

    response = await taxi_hejmdal.delete(
        'v1/circuit_schema/delete', params={'id': 'schema_new_using_tpl'},
    )
    assert response.status_code == 200
    assert response.json() == {}

    await taxi_hejmdal.invalidate_caches(
        clean_update=True, cache_names=['schemas-cache'],
    )

    response = await taxi_hejmdal.delete(
        'v1/circuit_schema/delete', params={'id': 'template_test'},
    )
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.config(
    HEJMDAL_CIRCUIT_SCHEMAS_DB_SETTINGS={
        'get_by_id': {'network_timeout': 100, 'statement_timeout': 100},
        'get_changed': {'network_timeout': 200, 'statement_timeout': 200},
        'update': {'network_timeout': 200, 'statement_timeout': 200},
        'run_tests': True,
    },
)
async def test_schema_update_with_tests(taxi_hejmdal):
    response = await taxi_hejmdal.post(
        'v1/circuit_schema/retrieve', params={'id': 'schema_with_test_case'},
    )
    assert response.status_code == 200
    resp_json = response.json()
    schema = resp_json['circuit_schema']
    description = resp_json['description']

    response = await taxi_hejmdal.post('v1/test-case/list')
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json['enabled']) == 1
    assert len(resp_json['disabled']) == 1
    assert resp_json['enabled'][0]['id'] == 1
    assert (
        resp_json['enabled'][0]['description']
        == 'test_schema_update_with_tests - success'
    )
    assert resp_json['disabled'][0]['id'] == 2
    assert (
        resp_json['disabled'][0]['description']
        == 'test_schema_update_with_tests - should fail'
    )

    response = await taxi_hejmdal.put(
        'v1/circuit_schema/update',
        params={'id': 'schema_with_test_case'},
        json={
            'circuit_schema': schema,
            'type': 'schema',
            'description': description + 'NEW',
            'custom': False,
        },
    )
    assert response.status_code == 200

    response = await taxi_hejmdal.post(
        'v1/test-case/activate?id=2&do_activate=true',
    )
    assert response.status_code == 200

    response = await taxi_hejmdal.post('v1/test-case/list')
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json['enabled']) == 2

    response = await taxi_hejmdal.put(
        'v1/circuit_schema/update',
        params={'id': 'schema_with_test_case'},
        json={
            'circuit_schema': schema,
            'type': 'schema',
            'description': description + 'NEW NEW',
            'custom': False,
        },
    )
    assert response.status_code == 400
    resp_json = response.json()
    assert (
        resp_json['message']
        == 'could not save circuit schema: some tests has been failed.'
    )
