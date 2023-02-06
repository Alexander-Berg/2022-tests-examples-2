import datetime


def to_datetime(datetime_str):
    return datetime.datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')


async def test_data_save(mockserver, taxi_hejmdal, pgsql):
    json_ts = {
        'timestamps': [
            1234267000,
            1234327000,
            1234387000,
            1234447000,
            1234507000,
            1234567000,
            1234627000,
            1234687000,
            1234747000,
        ],
        'values': [
            0.94,
            26.916,
            1.376,
            5.084,
            1.441,
            1.27,
            1.063,
            0.731,
            0.882,
        ],
    }

    json_data = [
        {'entry_point_id': 'entry1', 'timeseries': json_ts},
        {'entry_point_id': 'entry2', 'timeseries': json_ts},
    ]

    @mockserver.json_handler(
        '/solomon-sensors/api/v2/projects/taxi/sensors/data',
    )
    def _mock_solomon_sensors_data(request):
        return {
            'vector': [
                {
                    'timeseries': {
                        'alias': '',
                        'kind': 'DGAUGE',
                        'labels': {
                            'project': 'taxi',
                            'sensor': 'test-service-sensor',
                        },
                        **json_ts,
                    },
                },
            ],
        }

    await taxi_hejmdal.run_task('circuit_states_cache/invalidate')

    await taxi_hejmdal.run_task('tuner/initialize')
    response = await taxi_hejmdal.post(
        'v1/test-data/save',
        json={
            'circuit_id': 'test_circuit_id',
            'precedent_time': '1970-01-15T06:55:07.001Z',
            'target_state': 'Warning',
        },
    )

    assert response.status_code == 200
    assert response.content == b''

    response = await taxi_hejmdal.post(
        'v1/test-data/save',
        json={
            'circuit_id': 'test_circuit_id',
            'precedent_time': '1970-01-15T07:00:07.001Z',
            'target_state': 'Critical',
        },
    )

    assert response.status_code == 200
    assert response.content == b''

    response = await taxi_hejmdal.post(
        'v1/test-data/save',
        json={
            'circuit_id': 'test_circuit_id',
            'precedent_time': '1970-01-15T07:01:07.001Z',
            'target_state': 'Compute',
        },
    )

    assert response.status_code == 200
    assert response.content == b''

    cursor = pgsql['hejmdal'].cursor()
    query = (
        'select test_id, schema_id, start_time, '
        + 'precedent_time, end_time, data, meta '
        + ' from test_data order by precedent_time asc'
    )
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert len(db_res) == 3
    test_alert1 = db_res[0]
    assert len(test_alert1) == 7
    assert test_alert1[0] == 1
    assert test_alert1[1] == 'schema_test'
    assert test_alert1[2] == to_datetime('1970-01-15T06:51:07.000Z')
    assert test_alert1[3] == to_datetime('1970-01-15T06:55:07.001Z')
    assert test_alert1[4] == to_datetime('1970-01-15T06:59:07.000Z')
    assert test_alert1[5] == json_data
    meta = test_alert1[6]
    assert meta['circuit_id'] == 'test_circuit_id'
    assert meta['created'] is not None
    assert meta['source'] == 'test-data/save'

    test_alert2 = db_res[1]
    assert len(test_alert2) == 7
    assert test_alert2[0] == 2
    assert test_alert2[1] == 'schema_test'
    assert test_alert2[2] == to_datetime('1970-01-15T06:51:07.000Z')
    assert test_alert2[3] == to_datetime('1970-01-15T07:00:07.001Z')
    assert test_alert2[4] == to_datetime('1970-01-15T06:59:07.000Z')
    assert test_alert2[5] == json_data
    meta = test_alert2[6]
    assert meta['circuit_id'] == 'test_circuit_id'
    assert meta['created'] is not None
    assert meta['source'] == 'test-data/save'

    test_alert3 = db_res[2]
    assert len(test_alert3) == 7
    assert test_alert3[0] == 3
    assert test_alert3[1] == 'schema_test'
    assert test_alert3[2] == to_datetime('1970-01-15T06:51:07.000Z')
    assert test_alert3[3] == to_datetime('1970-01-15T07:01:07.001Z')
    assert test_alert3[4] == to_datetime('1970-01-15T06:59:07.000Z')
    assert test_alert3[5] == json_data
    meta = test_alert3[6]
    assert meta['circuit_id'] == 'test_circuit_id'
    assert meta['created'] is not None
    assert meta['source'] == 'test-data/save'
