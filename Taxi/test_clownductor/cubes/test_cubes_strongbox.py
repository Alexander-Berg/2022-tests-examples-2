from aiohttp import web
import pytest

from clownductor.generated.service.mdb_api import plugin as mdb_plugin
from clownductor.internal.db import db_types
from clownductor.internal.tasks import cubes


def task_data(name):
    return {
        'id': 123,
        'job_id': 456,
        'name': name,
        'sleep_until': 0,
        'input_mapping': {},
        'output_mapping': {},
        'payload': {},
        'retries': 0,
        'status': 'in_progress',
        'error_message': None,
        'created_at': 0,
        'updated_at': 0,
    }


# pylint: disable=invalid-name
@pytest.mark.parametrize(
    'get_http_status, post_http_status, success',
    [
        (200, 409, True),  # already exists
        (404, 200, True),  # create new
        (404, 409, False),  # race condition, should fail and retry
        (500, 200, False),  # strongbox unavailable
        (404, 500, False),  # strongbox unavailable
    ],
)
async def test_add_group(
        web_context,
        mock_strongbox,
        get_http_status,
        post_http_status,
        success,
):  # pylint: disable=W0612
    @mock_strongbox('/v1/groups/')
    async def handler(request):  # pylint: disable=unused-argument
        if request.method == 'GET':
            status = get_http_status
        else:
            status = post_http_status

        if status == 200:
            data = {
                'yav_secret_uuid': 'sec-XXX',
                'yav_version_uuid': 'ver-YYY',
                'service_name': 'some-service',
                'env': 'unstable',
            }
            return web.json_response(data, status=status)
        return web.json_response({}, status=status)

    cube = cubes.CUBES['StrongboxCubeAddGroup'](
        web_context,
        task_data('StrongboxCubeAddGroup'),
        {
            'project': 'taxi',
            'service': 'some-service',
            'branch': 'unstable',
            'env': 'unstable',
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success == success

    if success:
        assert cube.data['payload']['yav_secret_uuid'] == 'sec-XXX'
        assert cube.data['payload']['yav_secret_version'] == 'ver-YYY'


@pytest.mark.features_on('secrets_project_prefix_naming')
async def test_add_secret_tvm(
        web_context,
        mock_strongbox,
        yav_mockserver,
        add_project,
        login_mockserver,
        staff_mockserver,
):  # pylint: disable=W0612
    @mock_strongbox('/v1/secrets/')
    async def handler(request):  # pylint: disable=unused-argument
        return web.json_response(
            {
                'yav_secret_uuid': 'sec-XXX',
                'yav_version_uuid': 'ver-YYY',
                'name': 'TVM_NAME',
            },
        )

    yav_mockserver()
    login_mockserver()
    staff_mockserver()
    await add_project('taxi-devops')

    cube = cubes.CUBES['StrongboxCubeAddTvm'](
        web_context,
        task_data('StrongboxCubeAddTvm'),
        {
            'project': 'taxi-devops',
            'service': 'some-service',
            'env': 'unstable',
            'tvm_id': '2013222',
            'tvm_secret_tmp_yav_id': 'sec-XXX',
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success
    assert cube.data['payload']['strongbox_yav_id'] == 'sec-XXX'
    assert cube.data['payload']['strongbox_name'] == 'TVM_NAME'
    assert handler.times_called == 1
    call = handler.next_call()
    assert call['request'].json == {
        'data': {
            'project': 'taxi',
            'provider_name': 'some-service',
            'secret': 'some-secret-value',
            'tvm_id': '2013222',
        },
        'env': 'unstable',
        'scope': {
            'project_name': 'taxi-devops',
            'service_name': 'some-service',
        },
        'type': 'tvm',
    }


@pytest.mark.parametrize(
    'db_type, service_type',
    [
        (db_types.DbType.Postgres, mdb_plugin.ServiceType.POSTGRES),
        (db_types.DbType.Mongo, mdb_plugin.ServiceType.MONGO),
        (db_types.DbType.Redis, mdb_plugin.ServiceType.REDIS),
    ],
)
@pytest.mark.features_on('secrets_project_prefix_naming')
async def test_add_secret_db(
        web_context,
        mock_strongbox,
        yav_mockserver,
        mdb_mockserver,
        db_type,
        service_type,
        login_mockserver,
        staff_mockserver,
        add_project,
):
    @mock_strongbox('/v1/secrets/')
    async def handler(request):  # pylint: disable=unused-argument
        return web.json_response(
            {
                'yav_secret_uuid': 'sec-XXX',
                'yav_version_uuid': 'ver-YYY',
                'name': 'TVM_NAME',
            },
        )

    def _get_secret_and_type() -> (str, dict):
        if db_type == db_types.DbType.Postgres:
            return (
                'postgresql',
                {
                    'project': 'taxi',
                    'provider_name': 'service_name',
                    'shards': [
                        {
                            'user': 'egurnovda',
                            'host': (
                                'man-zj0xk1xvjmmzzjfk.db.yandex.net,'
                                'sas-xjutiwxck3s3ifgi.db.yandex.net,'
                                'vla-27udw4m48zcufcv7.db.yandex.net'
                            ),
                            'port': '6432',
                            'db_name': 'test-db',
                            'password': 'some-secret-value',
                        },
                    ],
                },
            )
        if db_type == db_types.DbType.Mongo:
            return (
                'mongodb',
                {
                    'project': 'taxi',
                    'provider_name': 'service_name',
                    'user': 'egurnovda',
                    'host': 'man-zj0xk1xvjmmzzjfk.db.yandex.net',
                    'port': (
                        '27018,'
                        'sas-xjutiwxck3s3ifgi.db.yandex.net:27018,'
                        'vla-27udw4m48zcufcv7.db.yandex.net:27018'
                    ),
                    'db_name': 'test-db',
                    'password': 'some-secret-value',
                },
            )
        if db_type == db_types.DbType.Redis:
            return (
                'redis',
                {
                    'project': 'taxi',
                    'provider_name': 'service_name',
                    'shards': [{'name': 'unstable_test-db'}],
                    'sentinels': [
                        {
                            'host': 'man-zj0xk1xvjmmzzjfk.db.yandex.net',
                            'port': '26379',
                        },
                        {
                            'host': 'sas-xjutiwxck3s3ifgi.db.yandex.net',
                            'port': '26379',
                        },
                        {
                            'host': 'vla-27udw4m48zcufcv7.db.yandex.net',
                            'port': '26379',
                        },
                    ],
                    'password': 'some-secret-value',
                },
            )
        raise ValueError('Unknown db_type')

    yav_mockserver()
    mdb_mockserver(service_type=service_type)
    login_mockserver()
    staff_mockserver()
    await add_project('taxi-devops')

    cube = cubes.CUBES['StrongboxCubeAddDb'](
        web_context,
        task_data('StrongboxCubeAddDb'),
        {
            'cluster_id': 'mdbq9iqofu9vus91r2j9',
            'db_name': 'test-db',
            'db_type': db_type.value,
            'env': 'unstable',
            'project_name': 'taxi-devops',
            'service_name': 'service_name',
            'user_name': 'egurnovda',
            'yav_id': 'sec-XXX',
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success
    assert cube.data['payload']['strongbox_yav_id'] == 'sec-XXX'
    assert cube.data['payload']['strongbox_name'] == 'TVM_NAME'
    assert handler.times_called == 1
    call = handler.next_call()
    s_type, data = _get_secret_and_type()
    assert call['request'].json == {
        'data': data,
        'env': 'unstable',
        'scope': {
            'project_name': 'taxi-devops',
            'service_name': 'service_name',
        },
        'type': s_type,
    }
