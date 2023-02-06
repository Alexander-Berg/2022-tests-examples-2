import pytest

from clownductor.internal.db import db_types
from clownductor.internal.tasks import cubes


@pytest.mark.config(
    CLOWNDUCTOR_MDB_VERSION_SETTINGS={
        '__default__': {'pg': '12', 'mongo': '4.2', 'redis': '5.0'},
    },
)
@pytest.mark.features_on('set_limit_test_pg_mdb_clusters')
@pytest.mark.parametrize(
    'db_type, taxi_con_limit, taxiro_con_limit, env, expected',
    [
        pytest.param(None, 140, 10, 'stable', 'pg_create_request.json'),
        pytest.param(
            db_types.DbType.Postgres.value,
            140,
            10,
            'stable',
            'pg_create_request.json',
        ),
        pytest.param(
            db_types.DbType.Mongo.value,
            None,
            None,
            'stable',
            'mongo_create_request.json',
        ),
        pytest.param(
            db_types.DbType.Redis.value,
            None,
            None,
            'stable',
            'redis_create_request.json',
        ),
        pytest.param(
            db_types.DbType.Postgres.value,
            140,
            10,
            'unstable',
            'pg_create_request_unstable.json',
            marks=pytest.mark.config(
                CLOWNDUCTOR_DB_CONNECTIONS_LIMIT_SETTINGS={
                    'minimum_connections': 100,
                    'per_core': 150,
                    'mdb_reserved': 90,
                    'for_ro_user': 10,
                },
            ),
        ),
    ],
)
async def test_create_cluster(
        patch,
        web_context,
        task_data,
        yav_mockserver,
        mdb_mockserver,
        load_json,
        db_type,
        taxi_con_limit,
        taxiro_con_limit,
        env,
        expected,
):
    @patch(
        'clownductor.generated.service.mdb_api.plugin.'
        'get_random_regions_without_man',
    )
    def _get_random_regions_without_man():
        return [{'zoneId': 'sas'}, {'zoneId': 'sas'}, {'zoneId': 'vla'}]

    yav_mockserver()
    mock = mdb_mockserver('test-db')

    cube = cubes.CUBES['MDBCubeCreateCluster'](
        web_context,
        task_data(
            'MDBCubeCreateCluster',
            input_mapping={
                'folder_id': 'folder_id',
                'name': 'service',
                'disk_size': 'disk_size',
                'flavor': 'flavor',
                'environment': 'env',
                'password_id': 'password_id',
                'ro_password_id': 'ro_password_id',
                'version': None,
            },
        ),
        {
            'folder_id': '123',
            'service': 'test-db',
            'disk_size': 10,
            'flavor': 's2.nano',
            'env': env,
            'password_id': 'sec-XXX',
            'ro_password_id': 'sec-XXX',
            'db_type': db_type,
        },
        [],
        None,
    )
    await cube.update()
    assert cube.success
    assert cube.data['payload'] == {
        'operation_id': 'mdbq9ue8i0gdv0grghrj',
        'db_name': 'test_db',
        'user_name': 'taxi',
        'ro_user_name': 'taxiro',
    }

    assert mock.times_called == 2
    iam_call = mock.next_call()
    assert iam_call['request'].json == {
        'yandexPassportOauthToken': 'mdb_oauth',
    }
    create_call = mock.next_call()
    assert not mock.has_calls
    create_json = create_call['request'].json
    expected_json = load_json(expected)
    assert create_json == expected_json


def _set_name_env(json: dict, env: str):
    json['name'] = env + '_' + json['name']
    if env == 'stable':
        json['environment'] = 'PRODUCTION'
