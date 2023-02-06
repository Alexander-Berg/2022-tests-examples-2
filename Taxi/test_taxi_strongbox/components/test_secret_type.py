# pylint: disable=inconsistent-return-statements,unused-variable
import contextlib
import copy

import pytest

from taxi_strongbox.components import secret_type as st
from taxi_strongbox.components.sessions import vault_session as vs
from taxi_strongbox.generated.service.strongbox_schemas import plugin as ssp


@pytest.mark.parametrize(
    ['type_name', 'data', 'expected_parsed', 'expected_rendered'],
    [
        (
            'oracle',
            {
                'project': 'lavka',
                'provider_name': 'random_name',
                'shards': [
                    {
                        'dsn': (
                            '(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)'
                            '(HOST=tt1.oebs.yandex.net)))'
                        ),
                        'user': 'test_user',
                        'password': 'asd331dd&22',
                    },
                    {
                        'dsn': (
                            '(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)'
                            '(HOST=tt2.oebs.yandex.net)))'
                        ),
                        'user': 'another_test_user',
                        'password': 'asd331dd&22',
                    },
                ],
            },
            st.ParseResult(
                'ORACLE_LAVKA_RANDOM_NAME',
                [
                    vs.SecretValue('project', 'lavka'),
                    vs.SecretValue('provider_name', 'random_name'),
                    vs.SecretValue(
                        'shards.0.dsn',
                        '(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)'
                        '(HOST=tt1.oebs.yandex.net)))',
                    ),
                    vs.SecretValue('shards.0.password', 'asd331dd&22'),
                    vs.SecretValue('shards.0.user', 'test_user'),
                    vs.SecretValue(
                        'shards.1.dsn',
                        '(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)'
                        '(HOST=tt2.oebs.yandex.net)))',
                    ),
                    vs.SecretValue('shards.1.password', 'asd331dd&22'),
                    vs.SecretValue('shards.1.user', 'another_test_user'),
                ],
            ),
            '"random_name":[{"dsn":"(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)'
            '(HOST=tt1.oebs.yandex.net)))","user":"test_user","password":'
            '"asd331dd&22","shard_number":0},{"dsn":"(DESCRIPTION='
            '(ADDRESS=(PROTOCOL=TCP)(HOST=tt2.oebs.yandex.net)))","user":'
            '"another_test_user","password":"asd331dd&22","shard_number":1}]',
        ),
        (
            'mssql',
            {
                'project': 'lavka',
                'provider_name': 'random_name',
                'shards': [
                    {
                        'database': 'LAVKA_DATASE',
                        'host': 'test_host_1',
                        'password': 'asd331dd&22',
                        'port': 'test_port_1',
                        'user': 'test_user',
                    },
                    {
                        'database': 'LAVKA_DATASE',
                        'host': 'test_host_2',
                        'password': 'asd331dd&22',
                        'port': 'test_port_2',
                        'user': 'test_user',
                    },
                ],
            },
            st.ParseResult(
                'MSSQL_LAVKA_RANDOM_NAME',
                [
                    vs.SecretValue('project', 'lavka'),
                    vs.SecretValue('provider_name', 'random_name'),
                    vs.SecretValue('shards.0.database', 'LAVKA_DATASE'),
                    vs.SecretValue('shards.0.host', 'test_host_1'),
                    vs.SecretValue('shards.0.password', 'asd331dd&22'),
                    vs.SecretValue('shards.0.port', 'test_port_1'),
                    vs.SecretValue('shards.0.user', 'test_user'),
                    vs.SecretValue('shards.1.database', 'LAVKA_DATASE'),
                    vs.SecretValue('shards.1.host', 'test_host_2'),
                    vs.SecretValue('shards.1.password', 'asd331dd&22'),
                    vs.SecretValue('shards.1.port', 'test_port_2'),
                    vs.SecretValue('shards.1.user', 'test_user'),
                ],
            ),
            '"random_name": [{"database":"LAVKA_DATASE","host":"test_host_1",'
            '"password":"asd331dd&22","port":"test_port_1","user":"test_user",'
            '"shard_number":0},{"database":"LAVKA_DATASE",'
            '"host":"test_host_2","password":"asd331dd&22",'
            '"port":"test_port_2","user":"test_user","shard_number":1}]',
        ),
        (
            'mysql',
            {
                'project': 'lavka',
                'provider_name': 'random_name',
                'shards': [
                    {
                        'database': 'LAVKA_DATASE',
                        'host': 'test_host_1',
                        'password': 'asd331dd&22',
                        'port': 'test_port_1',
                        'user': 'test_user',
                    },
                    {
                        'database': 'LAVKA_DATASE',
                        'host': 'test_host_2',
                        'password': 'asd331dd&22',
                        'port': 'test_port_2',
                        'user': 'test_user',
                    },
                ],
            },
            st.ParseResult(
                'MYSQL_LAVKA_RANDOM_NAME',
                [
                    vs.SecretValue('project', 'lavka'),
                    vs.SecretValue('provider_name', 'random_name'),
                    vs.SecretValue('shards.0.database', 'LAVKA_DATASE'),
                    vs.SecretValue('shards.0.host', 'test_host_1'),
                    vs.SecretValue('shards.0.password', 'asd331dd&22'),
                    vs.SecretValue('shards.0.port', 'test_port_1'),
                    vs.SecretValue('shards.0.user', 'test_user'),
                    vs.SecretValue('shards.1.database', 'LAVKA_DATASE'),
                    vs.SecretValue('shards.1.host', 'test_host_2'),
                    vs.SecretValue('shards.1.password', 'asd331dd&22'),
                    vs.SecretValue('shards.1.port', 'test_port_2'),
                    vs.SecretValue('shards.1.user', 'test_user'),
                ],
            ),
            '"random_name": [{"database":"LAVKA_DATASE","host":"test_host_1",'
            '"password":"asd331dd&22","port":"test_port_1","user":"test_user",'
            '"shard_number":0},{"database":"LAVKA_DATASE",'
            '"host":"test_host_2","password":"asd331dd&22",'
            '"port":"test_port_2","user":"test_user","shard_number":1}]',
        ),
        (
            'mongodb',
            {
                'project': 'taxi',
                'provider_name': 'strongbox',
                'user': 'test_user',
                'password': None,
                'host': 'test_host',
                'port': 'test_port',
                'db_name': 'test_db',
            },
            st.ParseResult(
                'MONGODB_TAXI_STRONGBOX',
                [
                    vs.SecretValue('project', 'taxi'),
                    vs.SecretValue('provider_name', 'strongbox'),
                    vs.SecretValue('user', 'test_user'),
                    vs.SecretValue('password', '***'),
                    vs.SecretValue('host', 'test_host'),
                    vs.SecretValue('port', 'test_port'),
                    vs.SecretValue('db_name', 'test_db'),
                ],
            ),
            '"strongbox": {"uri": "mongodb://test_user:***@test_host:'
            'test_port/test_db"}',
        ),
        (
            'mongos_proxy',
            {
                'project': 'taxi',
                'provider_name': 'strongbox',
                'user': 'test_user',
                'password': 'str0ngbox',
                'hostlist': 'host1:3310,host2:3320',
                'db_name': 'test_db',
                'options': 'opt1=5&opt2=500',
            },
            st.ParseResult(
                'MONGOS_PROXY_TAXI_STRONGBOX_TEST_USER',
                [
                    vs.SecretValue('project', 'taxi'),
                    vs.SecretValue('provider_name', 'strongbox'),
                    vs.SecretValue('user', 'test_user'),
                    vs.SecretValue('password', 'str0ngbox'),
                    vs.SecretValue('hostlist', 'host1:3310,host2:3320'),
                    vs.SecretValue('db_name', 'test_db'),
                    vs.SecretValue('options', 'opt1=5&opt2=500'),
                ],
            ),
            '"strongbox": {"uri": "mongodb://test_user:str0ngbox@'
            'host1:3310,host2:3320/test_db?opt1=5&opt2=500"}',
        ),
        (
            'postgresql',
            {
                'project': 'taxi',
                'provider_name': 'strongbox',
                'shards': [
                    {
                        'user': 'test_user_1',
                        'password': None,
                        'host': 'test_host_1',
                        'port': 'test_port_1',
                        'db_name': 'test_db_1',
                    },
                    {
                        'user': 'test_user_2',
                        'password': None,
                        'host': 'test_host_2',
                        'port': 'test_port_2',
                        'db_name': 'test_db_2',
                    },
                ],
            },
            st.ParseResult(
                'POSTGRES_TAXI_STRONGBOX',
                [
                    vs.SecretValue('project', 'taxi'),
                    vs.SecretValue('provider_name', 'strongbox'),
                    vs.SecretValue('shards.0.user', 'test_user_1'),
                    vs.SecretValue('shards.0.password', '***'),
                    vs.SecretValue('shards.0.host', 'test_host_1'),
                    vs.SecretValue('shards.0.port', 'test_port_1'),
                    vs.SecretValue('shards.0.db_name', 'test_db_1'),
                    vs.SecretValue('shards.1.user', 'test_user_2'),
                    vs.SecretValue('shards.1.password', '***'),
                    vs.SecretValue('shards.1.host', 'test_host_2'),
                    vs.SecretValue('shards.1.port', 'test_port_2'),
                    vs.SecretValue('shards.1.db_name', 'test_db_2'),
                ],
            ),
            '"strongbox":['
            '{"shard_number": 0,"hosts": ['
            '"host=test_host_1 port=test_port_1 dbname=test_db_1 '
            'user=test_user_1 password=*** sslmode=require"'
            ']},'
            '{"shard_number": 1,"hosts": ['
            '"host=test_host_2 port=test_port_2 dbname=test_db_2 '
            'user=test_user_2 password=*** sslmode=require"'
            ']}]',
        ),
        (
            'redis',
            {
                'project': 'taxi',
                'provider_name': 'strongbox',
                'shards': [
                    {'name': 'taxi_db_redis_strongbox'},
                    {'name': 'taxi_db_redis_strongbox_second'},
                ],
                'sentinels': [
                    {
                        'host': 'man-1ab2cdefgabcd3f4.db.yandex.net',
                        'port': '26379',
                    },
                    {
                        'host': 'sas-ighooquae3eeze9E.db.yandex.net',
                        'port': '26379',
                    },
                    {
                        'host': 'vla-Eisheingae9Eich7.db.yandex.net',
                        'port': '26379',
                    },
                ],
                'password': None,
            },
            st.ParseResult(
                'REDIS_TAXI_STRONGBOX',
                [
                    vs.SecretValue('project', 'taxi'),
                    vs.SecretValue('provider_name', 'strongbox'),
                    vs.SecretValue('shards.0.name', 'taxi_db_redis_strongbox'),
                    vs.SecretValue(
                        'shards.1.name', 'taxi_db_redis_strongbox_second',
                    ),
                    vs.SecretValue(
                        'sentinels.0.host',
                        'man-1ab2cdefgabcd3f4.db.yandex.net',
                    ),
                    vs.SecretValue('sentinels.0.port', '26379'),
                    vs.SecretValue(
                        'sentinels.1.host',
                        'sas-ighooquae3eeze9E.db.yandex.net',
                    ),
                    vs.SecretValue('sentinels.1.port', '26379'),
                    vs.SecretValue(
                        'sentinels.2.host',
                        'vla-Eisheingae9Eich7.db.yandex.net',
                    ),
                    vs.SecretValue('sentinels.2.port', '26379'),
                    vs.SecretValue('password', '***'),
                ],
            ),
            '"strongbox": { "shards" : ['
            '{ "name": "taxi_db_redis_strongbox" },'
            '{ "name": "taxi_db_redis_strongbox_second" }'
            '],'
            '"sentinels" : ['
            '{ "host": "man-1ab2cdefgabcd3f4.db.yandex.net",'
            '"port": 26379 },'
            '{ "host": "sas-ighooquae3eeze9E.db.yandex.net",'
            '"port": 26379 },'
            '{ "host": "vla-Eisheingae9Eich7.db.yandex.net",'
            '"port": 26379 }'
            '],'
            '"password" : "***"'
            '}',
        ),
        (
            'api_token',
            {'project': 'taxi', 'provider_name': 'strongbox', 'value': None},
            st.ParseResult(
                'API_TOKEN_TAXI_STRONGBOX',
                [
                    vs.SecretValue('project', 'taxi'),
                    vs.SecretValue('provider_name', 'strongbox'),
                    vs.SecretValue('value', '***'),
                ],
            ),
            '***',
        ),
        (
            'tvm',
            {
                'project': 'taxi',
                'provider_name': 'strongbox',
                'tvm_id': '100500',
                'secret': '***',
            },
            st.ParseResult(
                'TVM_TAXI_STRONGBOX',
                [
                    vs.SecretValue('project', 'taxi'),
                    vs.SecretValue('provider_name', 'strongbox'),
                    vs.SecretValue('tvm_id', '100500'),
                    vs.SecretValue('secret', '***'),
                ],
            ),
            '{"id": 100500, "secret": "***"}',
        ),
        (
            's3mds',
            {
                'project': 'taxi',
                'provider_name': 'strongbox',
                'host': 's3.mds.yandex.net',
                'bucket': 'strongbox',
                'access_key_id': 'strongbox-id',
                'access_secret_key': 'strongbox-key',
            },
            st.ParseResult(
                'S3MDS_TAXI_STRONGBOX',
                [
                    vs.SecretValue('project', 'taxi'),
                    vs.SecretValue('provider_name', 'strongbox'),
                    vs.SecretValue('host', 's3.mds.yandex.net'),
                    vs.SecretValue('bucket', 'strongbox'),
                    vs.SecretValue('access_key_id', 'strongbox-id'),
                    vs.SecretValue('access_secret_key', 'strongbox-key'),
                ],
            ),
            '{ "url": "s3.mds.yandex.net",'
            '"bucket": "strongbox",'
            '"access_key_id": "strongbox-id",'
            '"secret_key": "strongbox-key"'
            '}',
        ),
        (
            'clickhouse',
            {
                'project': 'taxi',
                'provider_name': 'strongbox',
                'hosts': [
                    {'fqdn': 'sas-abc098cds765qp21.db.yandex.net'},
                    {'fqdn': 'vla-abc098cds765qp22.db.yandex.net'},
                    {'fqdn': 'iva-abc098cds765qp23.db.yandex.net'},
                    {'fqdn': 'man-abc098cds765qp24.db.yandex.net'},
                ],
                'port_http': '8443',
                'port_client': '9440',
                'cluster_name': 'mdbns6srpk0rwmd9hlor',
                'service_name': 'cluster-prod',
                'user': 'taxi-test_1',
                'password': None,
            },
            st.ParseResult(
                'CLICKHOUSE_TAXI_CLUSTER_PROD_STRONGBOX',
                [
                    vs.SecretValue('project', 'taxi'),
                    vs.SecretValue('provider_name', 'strongbox'),
                    vs.SecretValue(
                        'hosts.0.fqdn', 'sas-abc098cds765qp21.db.yandex.net',
                    ),
                    vs.SecretValue(
                        'hosts.1.fqdn', 'vla-abc098cds765qp22.db.yandex.net',
                    ),
                    vs.SecretValue(
                        'hosts.2.fqdn', 'iva-abc098cds765qp23.db.yandex.net',
                    ),
                    vs.SecretValue(
                        'hosts.3.fqdn', 'man-abc098cds765qp24.db.yandex.net',
                    ),
                    vs.SecretValue('port_http', '8443'),
                    vs.SecretValue('port_client', '9440'),
                    vs.SecretValue('cluster_name', 'mdbns6srpk0rwmd9hlor'),
                    vs.SecretValue('service_name', 'cluster-prod'),
                    vs.SecretValue('user', 'taxi-test_1'),
                    vs.SecretValue('password', '***'),
                ],
            ),
            '"strongbox": {'
            '"hosts": ['
            '"sas-abc098cds765qp21.db.yandex.net",'
            '"vla-abc098cds765qp22.db.yandex.net",'
            '"iva-abc098cds765qp23.db.yandex.net",'
            '"man-abc098cds765qp24.db.yandex.net"'
            '],'
            '"port_http": 8443,'
            '"port_client": 9440,'
            '"cluster_name": "mdbns6srpk0rwmd9hlor",'
            '"user": "taxi-test_1",'
            '"password": "***"'
            '}',
        ),
        (
            'freeform',
            {'name': 'freeform-data', 'value': '{"a": "b"}'},
            st.ParseResult(
                'FREEFORM_FREEFORM_DATA',
                [
                    vs.SecretValue('name', 'freeform-data'),
                    vs.SecretValue('value', '{"a": "b"}'),
                ],
            ),
            '{"a": "b"}',
        ),
        (
            'elasticsearch',
            {
                'cluster_name': 'taxi',
                'auth_profiles': {
                    'profile_01': {'type': 'oauth', 'password': 'oauth_token'},
                    'profile_02': {
                        'type': 'basic',
                        'user': 'default_user',
                        'password': 'default_password',
                    },
                },
            },
            st.ParseResult(
                'ELASTICSEARCH_TAXI',
                [
                    vs.SecretValue('cluster_name', 'taxi'),
                    vs.SecretValue('auth_profiles.profile_01.type', 'oauth'),
                    vs.SecretValue(
                        'auth_profiles.profile_01.password', 'oauth_token',
                    ),
                    vs.SecretValue('auth_profiles.profile_02.type', 'basic'),
                    vs.SecretValue(
                        'auth_profiles.profile_02.user', 'default_user',
                    ),
                    vs.SecretValue(
                        'auth_profiles.profile_02.password',
                        'default_password',
                    ),
                ],
            ),
            '"taxi": {"auth_profiles": {'
            '"profile_01": {"type": "oauth", "password": "oauth_token"}, '
            '"profile_02": {"type": "basic", "user": "default_user", '
            '"password": "default_password"}}}',
        ),
    ],
)
async def test_secret_type(
        web_context,
        patch,
        type_name,
        data,
        expected_parsed,
        expected_rendered,
):
    @patch('uuid.uuid4')
    def uuid4():
        def _uuid4():
            pass

        _uuid4.hex = '***'
        return _uuid4

    strongbox_schemas = ssp.StongboxSchemas(web_context, None, [True])
    secret_type = strongbox_schemas.get_secret_type(type_name)
    parse_result = secret_type.parse(data)
    assert expected_parsed.secret_name == parse_result.secret_name
    assert set(expected_parsed.secret_values) == set(
        parse_result.secret_values,
    )
    render_result = secret_type.render(parse_result.secret_values)
    assert expected_rendered.replace('\n', '').replace(
        ' ', '',
    ) == render_result.replace('\n', '').replace(' ', '')


@pytest.mark.features_on('ensure_freeform_json')
@pytest.mark.parametrize(
    ['value', 'expect_fail'],
    [
        ('{}', False),
        ('null', False),
        ('true', False),
        ('false', False),
        ('5', False),
        ('[]', False),
        ('"privet"', False),
        ('privet', True),
        ('"p": {"r": "ivet"}', True),
        pytest.param(
            '"p": {"r": "ivet"}',
            False,
            marks=pytest.mark.features_off('ensure_freeform_json'),
        ),
    ],
)
@pytest.mark.parametrize(
    ['type_name', 'base_data', 'expected_fail_message'],
    [
        (
            'freeform',
            {'name': 'freeform-data'},
            (
                'Data has bad format: '
                'failed to validate value via validator \'format\' for scheme '
                '{\'type\': \'string\', \'format\': \'json\', '
                '\'description\': \'Произвольное секретное значение\'}'
            ),
        ),
        (
            'api_token',
            {'project': 'taxi', 'provider_name': 'strongbox'},
            (
                'Data has bad format: '
                'failed to validate value via validator \'oneOf\' for scheme '
                '{\'oneOf\': [{\'type\': \'string\', \'format\': \'json\'}, '
                '{\'type\': \'null\'}], \'description\': \'Секретный токен\'}'
            ),
        ),
    ],
)
async def test_format_json(
        web_context,
        type_name,
        base_data,
        value,
        expect_fail,
        expected_fail_message,
):
    data = copy.deepcopy(base_data)
    data['value'] = value

    strongbox_schemas = ssp.StongboxSchemas(web_context, None, [True])
    secret_type = strongbox_schemas.get_secret_type(type_name)

    manager = (
        pytest.raises(st.ValidationError)
        if expect_fail
        else contextlib.nullcontext()
    )
    with manager as excinfo:
        secret_type.parse(data)

    if expect_fail:
        assert str(excinfo.value) == expected_fail_message
        assert value not in str(excinfo.value)
