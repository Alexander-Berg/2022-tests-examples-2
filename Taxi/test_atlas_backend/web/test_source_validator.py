import abc
import datetime
import typing

from aiohttp import test_utils
import pytest

from atlas_backend.internal.sources import exceptions
from atlas_backend.internal.sources.models import base_source_model
from atlas_backend.internal.sources.models import chyt_source_model
from test_atlas_backend.web import db_data

Patch = typing.Callable[
    [str], typing.Callable[[typing.Callable], typing.Callable],
]

Source = base_source_model.Source
YTObject = chyt_source_model.YTObject

EXISTED_SOURCE = db_data.SOURCES

VALIDATORS_PATH = 'atlas_backend.internal.sources.models.'
CHYT_VALIDATORS_PATH = VALIDATORS_PATH + 'chyt_source_model.CHYTSource.'
CH_VALIDATORS_PATH = VALIDATORS_PATH + 'ch_source_model.CHSource.'


class BaseTestValidatorClass(abc.ABC):

    status = 0
    code = ''
    message = ''

    source_type = ''
    source_data: typing.Dict[str, typing.Any] = {}

    async def test_create_source(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        response = await web_app_client.post(
            '/api/sources', json=self.source_data,
        )
        assert response.status == self.status, await response.text()
        source = await response.json()
        assert 'code' in source, 'There is no "code" field in response'
        assert source['code'] == self.code
        assert 'message' in source, 'There is no "message" field in response'
        assert source['message'] == self.message.format(**self.source_data)

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_source.sql'],
    )
    @pytest.mark.parametrize('source', [source for source in EXISTED_SOURCE])
    async def test_update_source(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            source: typing.Dict[str, typing.Any],
    ) -> None:
        source_type = source['source_type']
        if source_type != self.source_type:
            # TODO здесь бы скипать тесты, но пока что при этом валятся ошибки
            return
        params = {'source_id': source['source_id']}
        response = await web_app_client.patch(
            '/api/sources', params=params, json=self.source_data,
        )
        assert response.status == self.status, await response.text()
        source = await response.json()
        assert 'code' in source, 'There is no "code" field in response'
        assert source['code'] == self.code
        assert 'message' in source, 'There is no "message" field in response'
        assert source['message'] == self.message.format(**self.source_data)


class BaseCHYTValidatorClass(BaseTestValidatorClass):

    _yt_username = 'yt_username'
    source_type = 'chyt'
    source_data = {
        'source_cluster': 'hahn',
        'source_path': '/path',
        'source_name': 'source_name',
        'is_partitioned': True,
        'partition_key': 'datetime',
        'partition_template': '%Y-%m',
    }

    @pytest.fixture(scope='function', autouse=True)
    def yt_username(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_get_username')
        async def _get_username(*args, **kwargs) -> str:
            return self._yt_username


class TestCHYTUnsupportedCluster(BaseCHYTValidatorClass):

    status = 400
    code = 'BadRequest::UnavailableSourceCluster'
    message = 'Unknown source cluster "atlastest_mdb"'

    source_data = {
        'source_cluster': 'atlastest_mdb',
        'source_path': '/path',
        'source_name': 'source_name',
        'is_partitioned': True,
        'partition_key': '',
        'partition_template': '%Y-%m',
    }


class TestCHYTPartitionedSourceWithoutKey(BaseCHYTValidatorClass):

    status = 400
    code = 'BadRequest::EmptyPartitionKey'
    message = (
        'It not allowed to create partitioned source without partition key'
    )

    source_data = {
        'source_cluster': 'hahn',
        'source_path': '/path',
        'source_name': 'source_name',
        'is_partitioned': True,
        'partition_key': '',
        'partition_template': '%Y-%m',
    }


class TestCHYTPartitionedSourceWithoutTemplate(BaseCHYTValidatorClass):

    status = 400
    code = 'BadRequest::EmptyPartitionTemplate'
    message = (
        'It not allowed to create partitioned source without partition '
        'template'
    )

    source_data = {
        'source_cluster': 'hahn',
        'source_path': '/path',
        'source_name': 'source_name',
        'is_partitioned': True,
        'partition_key': 'datetime',
        'partition_template': '',
    }


class TestCHYTNotPartitionedSourceWithKey(BaseCHYTValidatorClass):

    status = 400
    code = 'BadRequest::NotEmptyPartitionKey'
    message = (
        'It not allowed to create not partitioned source with partition key'
    )

    source_data = {
        'source_cluster': 'hahn',
        'source_path': '/path',
        'source_name': 'source_name',
        'is_partitioned': False,
        'partition_key': 'datetime',
        'partition_template': '',
    }


class TestCHYTNotPartitionedSourceWithTemplate(BaseCHYTValidatorClass):

    status = 400
    code = 'BadRequest::NotEmptyPartitionTemplate'
    message = (
        'It not allowed to create not partitioned source with partition '
        'template'
    )

    source_data = {
        'source_cluster': 'hahn',
        'source_path': '/path',
        'source_name': 'source_name',
        'is_partitioned': False,
        'partition_key': '',
        'partition_template': '%Y-%m',
    }


class TestCHYTUnavailableCluster(BaseCHYTValidatorClass):

    status = 400
    code = 'BadRequest::UnavailableSourceCluster'
    message = 'Unavailable cluster "{source_cluster}"'

    @pytest.fixture(scope='function', autouse=True)
    def invalid_cluster(self, patch: Patch) -> None:
        cluster = self.source_data['source_cluster']

        @patch(CHYT_VALIDATORS_PATH + '_validate_cluster')
        def _validate_cluster(*args, **kwargs) -> None:
            raise exceptions.SourceException400(
                code='BadRequest::UnavailableSourceCluster',
                message=f'Unavailable cluster "{cluster}"',
            )


class TestCHYTNotExistedSource(BaseCHYTValidatorClass):

    status = 404
    code = 'NotFound::UnavailableSource'
    message = 'Source "{source_path} doesn\'t exists"'

    @pytest.fixture(scope='function', autouse=True)
    def valid_cluster(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_validate_cluster')
        def _validate_cluster(*args, **kwargs) -> None:
            pass

    @pytest.fixture(scope='function', autouse=True)
    def not_existed_source(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_is_object_exists')
        async def _is_object_exists(*args, **kwargs) -> bool:
            return False


class TestCHYTNotReadableSource(BaseCHYTValidatorClass):

    status = 400
    code = 'BadRequest::UnreadableSource'
    message = (
        f'It\'s not allowed for {BaseCHYTValidatorClass._yt_username} to read '
        'source by path "{source_path}"'
    )

    @pytest.fixture(scope='function', autouse=True)
    def valid_cluster(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_validate_cluster')
        def _validate_cluster(*args, **kwargs) -> None:
            pass

    @pytest.fixture(scope='function', autouse=True)
    def existed_source(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_is_object_exists')
        async def _is_object_exists(*args, **kwargs) -> bool:
            return True

    @pytest.fixture(scope='function', autouse=True)
    def not_readable_source(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_check_permission')
        async def _check_permission(*args, **kwargs) -> str:
            return 'deny'


class TestCHYTUnsupportedSourceType(BaseCHYTValidatorClass):

    status = 400
    code = 'BadRequest::UnsupportedSourceType'
    message = 'Unsupported source type "file"'

    @pytest.fixture(scope='function', autouse=True)
    def valid_cluster(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_validate_cluster')
        def _validate_cluster(*args, **kwargs) -> None:
            pass

    @pytest.fixture(scope='function', autouse=True)
    def valid_path(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_validate_path')
        async def _validate_path() -> None:
            pass

    @pytest.fixture(scope='function', autouse=True)
    def not_supported_source_type(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_get_object_type')
        async def _get_object_type(*args, **kwargs) -> str:
            return 'file'


class TestCHYTPartitionedTable(BaseCHYTValidatorClass):

    status = 400
    code = 'BadRequest::PartitionedSource'
    message = 'Source is YT table, it mustn\'t be partitioned'

    @pytest.fixture(scope='function', autouse=True)
    def valid_cluster(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_validate_cluster')
        def _validate_cluster(*args, **kwargs) -> None:
            pass

    @pytest.fixture(scope='function', autouse=True)
    def valid_path(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_validate_path')
        async def _validate_path() -> None:
            pass

    @pytest.fixture(scope='function', autouse=True)
    def source_is_table(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_get_object_type')
        async def _get_object_type(*args, **kwargs) -> str:
            return 'table'


class TestCHYTNotPartitionedMapNode(BaseCHYTValidatorClass):

    status = 400
    code = 'BadRequest::NotPartitionedSource'
    message = 'Source is YT map node, it must be partitioned'

    source_data = {
        'source_cluster': 'hahn',
        'source_path': '/path',
        'source_name': 'source_name',
        'is_partitioned': False,
        'partition_key': '',
        'partition_template': '',
    }

    @pytest.fixture(scope='function', autouse=True)
    def valid_cluster(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_validate_cluster')
        def _validate_cluster(*args, **kwargs) -> None:
            pass

    @pytest.fixture(scope='function', autouse=True)
    def valid_path(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_validate_path')
        async def _validate_path() -> None:
            pass

    @pytest.fixture(scope='function', autouse=True)
    def source_is_map_node(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_get_object_type')
        async def _get_object_type(*args, **kwargs) -> str:
            return 'map_node'


class TestCHYTEmptyMapNode(BaseCHYTValidatorClass):

    status = 404
    code = 'BadRequest::NotPartitionedSource'
    message = 'Source has not got partitions'

    @pytest.fixture(scope='function', autouse=True)
    def valid_cluster(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_validate_cluster')
        def _validate_cluster(*args, **kwargs) -> None:
            pass

    @pytest.fixture(scope='function', autouse=True)
    def valid_path(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_validate_path')
        async def _validate_path() -> None:
            pass

    @pytest.fixture(scope='function', autouse=True)
    def source_is_map_node(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_get_object_type')
        async def _get_object_type(*args, **kwargs) -> str:
            return 'map_node'

    @pytest.fixture(scope='function', autouse=True)
    def source_is_empty(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_get_map_objects')
        async def _get_map_objects(*args, **kwargs) -> typing.List[YTObject]:
            return []


class TestCHYTMapNodeWithoutTables(BaseCHYTValidatorClass):

    status = 404
    code = 'BadRequest::NotPartitionedSource'
    message = 'Source has not got partitions'

    @pytest.fixture(scope='function', autouse=True)
    def valid_cluster(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_validate_cluster')
        def _validate_cluster(*args, **kwargs) -> None:
            pass

    @pytest.fixture(scope='function', autouse=True)
    def valid_path(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_validate_path')
        async def _validate_path() -> None:
            pass

    @pytest.fixture(scope='function', autouse=True)
    def source_is_map_node(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_get_object_type')
        async def _get_object_type(*args, **kwargs) -> str:
            return 'map_node'

    @pytest.fixture(scope='function', autouse=True)
    def source_is_empty(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_get_map_objects')
        async def _get_map_objects(*args, **kwargs) -> typing.List[YTObject]:
            return [
                YTObject(name='name', type_='map_node', columns={}),
                YTObject(name='other_name', type_='file', columns={}),
            ]


class TestCHYTInvalidPartitionName(BaseCHYTValidatorClass):

    status = 400
    code = 'BadRequest::InvalidPartitionName'
    message = (
        f'Partition name "2000-01-01T00:00:00" is not matched by '
        'template "{partition_template}"'
    )

    @pytest.fixture(scope='function', autouse=True)
    def valid_cluster(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_validate_cluster')
        def _validate_cluster(*args, **kwargs) -> None:
            pass

    @pytest.fixture(scope='function', autouse=True)
    def valid_path(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_validate_path')
        async def _validate_path() -> None:
            pass

    @pytest.fixture(scope='function', autouse=True)
    def source_is_map_node(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_get_object_type')
        async def _get_object_type(*args, **kwargs) -> str:
            return 'map_node'

    @pytest.fixture(scope='function', autouse=True)
    def tables_without_needed_key(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_get_map_objects')
        async def _get_map_objects(*args, **kwargs) -> typing.List[YTObject]:
            return [
                YTObject(
                    name='2000-01-01T00:00:00', type_='table', columns={},
                ),
            ]


class TestCHYTNoRequiredPartitionColumnNames(BaseCHYTValidatorClass):

    partition_template = typing.cast(
        str, BaseCHYTValidatorClass.source_data['partition_template'],
    )
    partition_name = datetime.datetime.now().strftime(partition_template)

    status = 404
    code = 'BadRequest::InvalidPartitionSchema'
    message = (
        f'Partition "{partition_name}" has not got column "{{partition_key}}"'
    )

    @pytest.fixture(scope='function', autouse=True)
    def valid_cluster(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_validate_cluster')
        def _validate_cluster(*args, **kwargs) -> None:
            pass

    @pytest.fixture(scope='function', autouse=True)
    def valid_path(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_validate_path')
        async def _validate_path() -> None:
            pass

    @pytest.fixture(scope='function', autouse=True)
    def source_is_map_node(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_get_object_type')
        async def _get_object_type(*args, **kwargs) -> str:
            return 'map_node'

    @pytest.fixture(scope='function', autouse=True)
    def tables_without_needed_key(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_get_map_objects')
        async def _get_map_objects(*args, **kwargs) -> typing.List[YTObject]:
            return [
                YTObject(
                    name=self.partition_name,
                    type_='table',
                    columns={'column': 'type'},
                ),
            ]


class TestCHYTUnsupportedKeyColumnType(BaseCHYTValidatorClass):

    partition_template = typing.cast(
        str, BaseCHYTValidatorClass.source_data['partition_template'],
    )
    partition_name = datetime.datetime.now().strftime(partition_template)

    status = 400
    code = 'BadRequest::InvalidPartitionSchema'
    message = (
        f'Key column "{{partition_key}}" of partition "{partition_name}" has '
        'not supported type: "type"'
    )

    @pytest.fixture(scope='function', autouse=True)
    def valid_cluster(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_validate_cluster')
        def _validate_cluster(*args, **kwargs) -> None:
            pass

    @pytest.fixture(scope='function', autouse=True)
    def valid_path(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_validate_path')
        async def _validate_path() -> None:
            pass

    @pytest.fixture(scope='function', autouse=True)
    def source_is_map_node(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_get_object_type')
        async def _get_object_type(*args, **kwargs) -> str:
            return 'map_node'

    @pytest.fixture(scope='function', autouse=True)
    def tables_without_needed_key(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_get_map_objects')
        async def _get_map_objects(*args, **kwargs) -> typing.List[YTObject]:
            partition_key = typing.cast(str, self.source_data['partition_key'])
            return [
                YTObject(
                    name=self.partition_name,
                    type_='table',
                    columns={partition_key: 'type'},
                ),
            ]


class TestCHYTUnreadablePartition(BaseCHYTValidatorClass):

    partition_template = typing.cast(
        str, BaseCHYTValidatorClass.source_data['partition_template'],
    )
    partition_name = datetime.datetime.now().strftime(partition_template)

    status = 400
    code = 'BadRequest::UnreadablePartition'
    message = (
        f'It\'s not allowed for {BaseCHYTValidatorClass._yt_username} to read '
        f'source partition "{partition_name}"'
    )

    @pytest.fixture(scope='function', autouse=True)
    def valid_cluster(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_validate_cluster')
        def _validate_cluster(*args, **kwargs) -> None:
            pass

    @pytest.fixture(scope='function', autouse=True)
    def valid_path(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_validate_path')
        async def _validate_path() -> None:
            pass

    @pytest.fixture(scope='function', autouse=True)
    def source_is_map_node(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_get_object_type')
        async def _get_object_type(*args, **kwargs) -> str:
            return 'map_node'

    @pytest.fixture(scope='function', autouse=True)
    def tables_without_needed_key(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_get_map_objects')
        async def _get_map_objects(*args, **kwargs) -> typing.List[YTObject]:
            partition_key = typing.cast(str, self.source_data['partition_key'])
            return [
                YTObject(
                    name=self.partition_name,
                    type_='table',
                    columns={partition_key: 'int64'},
                ),
            ]

    @pytest.fixture(scope='function', autouse=True)
    def not_readable_source(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_check_permission')
        async def _check_permission(*args, **kwargs) -> str:
            return 'deny'


class TestCHYTInvalidValueFormat(BaseCHYTValidatorClass):

    partition_template = typing.cast(
        str, BaseCHYTValidatorClass.source_data['partition_template'],
    )
    partition_name = datetime.datetime.now().strftime(partition_template)

    status = 400
    code = 'BadRequest::InvalidPartitionSchema'
    message = (
        f'Invalid value format "invalid_value" of type string of key column '
        f'"{{partition_key}}" in partition "{partition_name}"'
    )

    @pytest.fixture(scope='function', autouse=True)
    def valid_cluster(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_validate_cluster')
        def _validate_cluster(*args, **kwargs) -> None:
            pass

    @pytest.fixture(scope='function', autouse=True)
    def valid_path(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_validate_path')
        async def _validate_path() -> None:
            pass

    @pytest.fixture(scope='function', autouse=True)
    def source_is_map_node(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_get_object_type')
        async def _get_object_type(*args, **kwargs) -> str:
            return 'map_node'

    @pytest.fixture(scope='function', autouse=True)
    def tables_without_needed_key(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_get_map_objects')
        async def _get_map_objects(*args, **kwargs) -> typing.List[YTObject]:
            partition_key = typing.cast(str, self.source_data['partition_key'])
            return [
                YTObject(
                    name=self.partition_name,
                    type_='table',
                    columns={partition_key: 'string'},
                ),
            ]

    @pytest.fixture(scope='function', autouse=True)
    def not_readable_source(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_check_permission')
        async def _check_permission(*args, **kwargs) -> str:
            return 'allow'

    @pytest.fixture(scope='function', autouse=True)
    def invalid_value(self, patch: Patch) -> None:
        @patch(CHYT_VALIDATORS_PATH + '_get_key_column_value')
        async def _get_key_column_value(*args, **kwargs) -> str:
            return 'invalid_value'


CH_SETTINGS = {
    'settings_override': {
        'clickhouse': {
            'atlas_mdb': {
                'host': 'clickhouse-atlas-mdb.taxi.yandex.net',
                'port_client': 9000,
                'port_http': 8123,
                'user': 'atlas_mdb_user',
                'password': 'atlas_mdb_pass',
                'cluster_name': 'atlas_mdb',
            },
            'atlastest_mdb': {
                'host': 'clickhouse-atlastest-mdb.taxi.yandex.net',
                'port_client': 9000,
                'port_http': 8123,
                'user': 'atlastest_mdb_user',
                'password': 'atlastest_mdb_pass',
                'cluster_name': 'atlastest_mdb',
            },
        },
    },
}


@pytest.mark.config(CH_SETTINGS)
class BaseCHValidatorClass(BaseTestValidatorClass):

    source_type = 'clickhouse'
    source_data = {
        'source_type': 'clickhouse',
        'source_cluster': 'atlastest_mdb',
        'source_path': 'test_database.test_table',
        'source_name': 'source_name',
    }


class TestCHUnsupportedCluster(BaseCHValidatorClass):

    status = 400
    code = 'BadRequest::UnavailableSourceCluster'
    message = 'Unknown source cluster "{source_cluster}"'

    source_data = {
        'source_type': 'clickhouse',
        'source_cluster': 'hahn',
        'source_path': 'test_database.test_table',
        'source_name': 'source_name',
    }


class TestCHUnavailablePath(BaseCHValidatorClass):

    status = 400
    code = 'BadRequest::InvalidPath'
    message = 'Invalid Clickhouse source path format'

    source_data = {
        'source_type': 'clickhouse',
        'source_cluster': 'atlastest_mdb',
        'source_path': 'test_database.test_table.',
        'source_name': 'source_name',
        'partition_template': '%Y-%m',
    }


class TestCHUnavailableCluster(BaseCHValidatorClass):

    status = 400
    code = 'BadRequest::UnavailableSourceCluster'
    message = 'Unavailable cluster "{source_cluster}"'

    @pytest.fixture(scope='function', autouse=True)
    def invalid_cluster(self, patch: Patch) -> None:
        cluster = self.source_data['source_cluster']

        @patch(CH_VALIDATORS_PATH + '_validate_cluster')
        def _validate_cluster(*args, **kwargs) -> None:
            raise exceptions.SourceException400(
                code='BadRequest::UnavailableSourceCluster',
                message=f'Unavailable cluster "{cluster}"',
            )


class TestCHUnavailableDatabase(BaseCHValidatorClass):

    status = 400
    code = 'BadRequest::UnavailableSourcePath'
    message = (
        'Unavailable database "test_database" on cluster "{source_cluster}"'
    )

    @pytest.fixture(scope='function', autouse=True)
    def valid_cluster(self, patch: Patch) -> None:
        @patch(CH_VALIDATORS_PATH + '_validate_cluster')
        def _validate_cluster(*args, **kwargs) -> None:
            pass

    @pytest.fixture(scope='function', autouse=True)
    def not_existed_database(
            self, patch: Patch, clickhouse_client_mock: None,
    ) -> None:
        database, _, _ = self.source_data['source_path'].partition('.')
        cluster = self.source_data['source_cluster']

        @patch(CH_VALIDATORS_PATH + '_check_database_exists')
        async def _check_database_exists() -> None:
            raise exceptions.SourceException400(
                code='BadRequest::UnavailableSourcePath',
                message=(
                    f'Unavailable database "{database}" on cluster '
                    f'"{cluster}"'
                ),
            )


class TestCHUnavailableTable(BaseCHValidatorClass):

    status = 400
    code = 'BadRequest::UnavailableSourcePath'
    message = 'Unavailable table "test_table" in database "test_database"'

    @pytest.fixture(scope='function', autouse=True)
    def valid_cluster(self, patch: Patch) -> None:
        @patch(CH_VALIDATORS_PATH + '_validate_cluster')
        def _validate_cluster(*args, **kwargs) -> None:
            pass

    @pytest.fixture(scope='function', autouse=True)
    def existed_database(
            self, patch: Patch, clickhouse_client_mock: None,
    ) -> None:
        @patch(CH_VALIDATORS_PATH + '_check_database_exists')
        async def _check_database_exists() -> None:
            pass

    @pytest.fixture(scope='function', autouse=True)
    def not_existed_table(self, patch: Patch) -> None:
        database, _, table = self.source_data['source_path'].partition('.')

        @patch(CH_VALIDATORS_PATH + '_validate_path')
        async def _validate_path() -> None:
            raise exceptions.SourceException400(
                code='BadRequest::UnavailableSourcePath',
                message=(
                    f'Unavailable table "{table}" in database "{database}"'
                ),
            )
