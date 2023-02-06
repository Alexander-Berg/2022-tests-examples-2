# pylint: disable=C0103, C0302, R1710, W0612, W0621
import copy
import json
import typing as tp

from aiohttp import test_utils
from clickhouse_driver import errors
import pytest

from test_atlas_backend.web import db_data

Patch = tp.Callable[[str], tp.Callable[[tp.Callable], tp.Callable]]
CHResult = tp.List[tp.Tuple[str, ...]]

EXISTED_SOURCE = db_data.SOURCES
EXISTED_COLUMNS = db_data.COLUMNS

CREATE_TABLE_STATEMENTS: tp.Dict[str, tp.List[tp.Tuple[str, ...]]] = {
    'some_database.some_table': [
        ('record_id', 'UInt32', '', '', '', '', ''),
        ('city', 'String', '', '', '', '', ''),
        ('dttm', 'DateTime', '', '', '', 'CODEC(ZSTD(1))', ''),
        ('quadkey', 'String', '', '', '', 'CODEC(ZSTD(1))', ''),
    ],
    'other_database.other_table': [
        ('key', 'String', '', '', '', 'CODEC(ZSTD(1))', ''),
        ('value', 'String', '', '', '', '', ''),
    ],
}

UPDATED_COLUMNS = [
    {
        'source_id': 3,
        'column_name': 'record_id',
        'description': 'Идентификатор записи',
        'db_type': 'UInt32',
        'native_type': 'INT',
        'expression': '',
        'metadata': [
            {
                'key': 'Комментарий',
                'value': '"Здесь будет шутка"',
                'set_by': 'someuser',
            },
        ],
        'is_valid': True,
    },
    {
        'source_id': 3,
        'column_name': 'city',
        'description': 'Город',
        'db_type': 'String',
        'native_type': 'STR',
        'expression': '',
        'metadata': [],
        'is_valid': True,
    },
    {  # столбец удален
        'source_id': 3,
        'column_name': 'dttm',
        'description': 'Время',
        'db_type': 'Nullable(Nothing)',
        'native_type': 'UNSUPPORTED_TYPE',
        'expression': 'NULL',
        'metadata': [
            {'key': 'used_columns', 'value': '[]', 'set_by': ''},
            {'key': 'utc_offset', 'value': '3', 'set_by': 'otheruser'},
        ],
        'is_valid': True,
    },
    {  # виртуальный столбец инвалидирован
        'source_id': 3,
        'column_name': 'dttm_utc',
        'description': 'Время UTC',
        'db_type': 'DateTime',
        'native_type': 'DATETIME',
        'expression': '{dttm} - 60 * 60 * 3',
        'metadata': [
            {'key': 'used_columns', 'value': '["dttm"]', 'set_by': ''},
            {'key': 'utc_offset', 'value': '0', 'set_by': 'otheruser'},
        ],
        'is_valid': False,
    },
    {
        'source_id': 3,
        'column_name': 'quadkey',
        'description': 'Идентификатор тайтла',
        'db_type': 'String',
        'native_type': 'STR',
        'expression': '',
        'metadata': [{'key': 'length', 'value': '15', 'set_by': 'thirduser'}],
        'is_valid': True,
    },
    {  # виртуальный столбец стал валидным, т. к. есть все используемые столбцы
        'source_id': 3,
        'column_name': 'datetime_utc',
        'description': 'Старое время',
        'db_type': 'DateTime',
        'native_type': 'DATETIME',
        'expression': '{datetime} + 3600',
        'metadata': [
            {'key': 'used_columns', 'value': '["datetime"]', 'set_by': ''},
            {'key': 'utc_offset', 'value': '0', 'set_by': 'thirduser'},
        ],
        'is_valid': True,
    },
    {  # новый столбец
        'source_id': 3,
        'column_name': 'datetime',
        'description': '',
        'db_type': 'LowCardinality(DateTime)',
        'native_type': 'DATETIME',
        'expression': '',
        'metadata': [
            {'key': 'low_cardinality', 'value': 'true', 'set_by': ''},
        ],
        'is_valid': True,
    },
    {
        'source_id': 3,
        'column_name': 'one_more_datetime',
        'description': 'Еще одно время',
        'db_type': 'DateTime',
        'native_type': 'DATETIME',
        'expression': '',
        'metadata': [
            {'key': 'o_key', 'value': '"o_value"', 'set_by': 'o_user'},
        ],
        'is_valid': True,
    },
]

UPDATED_TABLE_STATEMENTS: tp.Dict[str, tp.List[tp.Tuple[str, ...]]] = {
    'some_database.some_table': [
        ('record_id', 'UInt32', '', '', '', '', ''),
        ('city', 'String', '', '', '', '', ''),
        (
            'datetime',
            'LowCardinality(DateTime)',
            '',
            '',
            '',
            'CODEC(ZSTD(1))',
            '',
        ),
        ('quadkey', 'String', '', '', '', 'CODEC(ZSTD(1))', ''),
        ('one_more_datetime', 'DateTime', '', '', '', '', ''),
    ],
}


async def get_columns(
        web_app_client: test_utils.TestClient, source_id: int, **filters,
) -> tp.List[tp.Dict[str, tp.Any]]:
    path = '/api/sources/columns/list'
    params = {'source_id': source_id}
    response = await web_app_client.get(path, params=params)
    assert response.status == 200, await response.text()
    columns = await response.json()
    for key, value in filters.items():
        columns = [column for column in columns if column[key] == value]
    return columns


def get_existed_columns(**filters) -> tp.List[tp.Dict[str, tp.Any]]:
    columns = EXISTED_COLUMNS
    for key, value in filters.items():
        columns = [column for column in columns if column[key] == value]
    return copy.deepcopy(columns)


class FakeClickhouseClient:

    _func: tp.Optional[tp.Callable[[str], CHResult]] = None

    def __call__(self, func: tp.Callable[[str], CHResult]) -> None:
        self._func = func

    async def execute(self, query: str) -> CHResult:
        assert self._func is not None
        return self._func(query)


class TestGetColumns:
    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_source.sql', 'pg_column.sql'],
    )
    @pytest.mark.parametrize('source_id', [3, 4, 404])
    async def test_get_list(
            self, web_app_client: test_utils.TestClient, source_id: int,
    ) -> None:
        path = '/api/sources/columns/list'
        params = {'source_id': source_id}
        response = await web_app_client.get(path, params=params)
        assert response.status == 200, await response.text()
        columns = await response.json()
        existed_columns = get_existed_columns(source_id=source_id)
        for column in columns:
            assert column in existed_columns
            existed_columns.remove(column)
        assert not existed_columns


class TestGetColumn:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            source_id: int,
            column_name: str,
    ) -> test_utils.ClientResponse:
        path = '/api/sources/columns'
        params = {'source_id': source_id, 'column_name': column_name}
        return await web_app_client.get(path, params=params)

    async def test_unknown_source(
            self, web_app_client: test_utils.TestClient,
    ) -> None:
        source_id = 1  # not exists
        column_name = 'some_name'  # not exists too
        response = await self.request(web_app_client, source_id, column_name)
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::ColumnNotExists'
        assert err['message'] == (
            f'There is not column name {column_name} of source with id '
            f'{source_id}'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_source.sql', 'pg_column.sql'],
    )
    async def test_unknown_column(
            self, web_app_client: test_utils.TestClient,
    ) -> None:
        source_id = 1
        column_name = 'some_name'  # not exists
        assert not [
            *filter(
                lambda column: (
                    column['source_id'] == source_id
                    and column['column_name'] == column_name
                ),
                EXISTED_COLUMNS,
            ),
        ]
        response = await self.request(web_app_client, source_id, column_name)
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::ColumnNotExists'
        assert err['message'] == (
            f'There is not column name {column_name} of source with id '
            f'{source_id}'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_source.sql', 'pg_column.sql'],
    )
    async def test_get(self, web_app_client: test_utils.TestClient) -> None:
        source_id = 3
        existed_column = next(
            filter(
                lambda column: column['source_id'] == source_id,
                EXISTED_COLUMNS,
            ),
        )
        column_name = existed_column['column_name']
        response = await self.request(web_app_client, source_id, column_name)
        assert response.status == 200, await response.text()
        column = await response.json()
        assert column == existed_column


class TestDeleteColumn:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            source_id: int,
            column_name: str,
    ) -> test_utils.ClientResponse:
        path = '/api/sources/columns'
        params = {'source_id': source_id, 'column_name': column_name}
        return await web_app_client.delete(path, params=params)

    @pytest.mark.parametrize('username', [None])
    async def test_delete_without_login(
            self,
            web_app_client: test_utils.TestClient,
            username: tp.Optional[str],
    ) -> None:
        source_id = 3
        column_name = 'dttm_utc'
        path = '/api/sources/columns'
        params = {'source_id': source_id, 'column_name': column_name}
        response = await web_app_client.delete(
            path, params=params, allow_redirects=False,
        )
        assert response.status == 302, await response.text()

    async def test_delete_not_existed_source_column(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        source_id = 404  # not exists
        column_name = 'dttm_utc'  # not exists
        response = await self.request(web_app_client, source_id, column_name)
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::ColumnNotExists'
        assert err['message'] == (
            f'There is not column name {column_name} of source '
            f'with id {source_id}'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_source.sql'],
    )
    async def test_delete_not_existed_column(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        source_id = 3
        column_name = 'not_existed_dttm_utc'  # not exists
        response = await self.request(web_app_client, source_id, column_name)
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::ColumnNotExists'
        assert err['message'] == (
            f'There is not column name {column_name} of source with id '
            f'{source_id}'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_source.sql', 'pg_column.sql'],
    )
    async def test_delete(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        source_id = 3
        column_name = 'dttm_utc'
        response = await self.request(web_app_client, source_id, column_name)
        assert response.status == 204, await response.text()
        columns = await get_columns(
            web_app_client, source_id, column_name=column_name,
        )
        assert not columns

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_source.sql', 'pg_column.sql'],
    )
    async def test_delete_real_column(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        source_id = 3
        column_name = 'dttm'
        response = await self.request(web_app_client, source_id, column_name)
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::NoExpression'
        assert (
            err['message'] == 'It\'s not allowed to delete non-virtual column'
        )


class TestCreateVirtualColumn:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            source_id: int,
            column_data: tp.Dict[str, tp.Any],
    ) -> test_utils.ClientResponse:
        path = '/api/sources/columns'
        params = {'source_id': source_id}
        return await web_app_client.post(path, params=params, json=column_data)

    @pytest.mark.parametrize('username', [None])
    async def test_create_without_login(
            self,
            web_app_client: test_utils.TestClient,
            username: tp.Optional[str],
    ) -> None:
        source_id = 3
        column_data = {
            'column_name': 'some_name',
            'description': 'some description',
            'expression': '1',
        }
        path = '/api/sources/columns'
        params = {'source_id': source_id}
        response = await web_app_client.post(
            path, params=params, json=column_data, allow_redirects=False,
        )
        assert response.status == 302, await response.text()

    async def test_create_not_existed_source_column(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        source_id = 404  # not exists
        column_data = {
            'column_name': 'some_name',
            'description': 'some description',
            'expression': '1',
        }
        response = await self.request(web_app_client, source_id, column_data)
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::SourceNotExists'
        assert err['message'] == f'There is not source with id {source_id}'

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_source.sql'],
    )
    async def test_create_column(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            patch: Patch,
    ) -> None:
        @patch('atlas_clickhouse.components.ClickHouseClient.__getitem__')
        def getitem(item: str) -> FakeClickhouseClient:
            client = FakeClickhouseClient()

            @client
            def execute(query: str) -> CHResult:
                if query.startswith('DESCRIBE TABLE '):
                    table = query[len('DESCRIBE TABLE ') :]
                    return CREATE_TABLE_STATEMENTS[table]
                if query.startswith('SELECT'):
                    db_type = 'UInt32'
                    return [(db_type,)]
                assert False

            return client

        source_id = 3
        column_name = 'some_name'
        column_data = {
            'column_name': column_name,
            'description': 'some description',
            'expression': '1',
        }
        response = await self.request(web_app_client, source_id, column_data)
        assert response.status == 201, await response.text()

        columns = await get_columns(
            web_app_client, source_id, column_name=column_name,
        )
        assert len(columns) == 1
        (column,) = columns
        assert column == {
            **column_data,
            'source_id': source_id,
            'db_type': 'UInt32',
            'native_type': 'INT',
            'metadata': [{'key': 'used_columns', 'value': '[]', 'set_by': ''}],
            'is_valid': True,
        }

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_source.sql'],
    )
    async def test_create_real_columns(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        source_id = 3
        column_data = {
            'column_name': 'some_name',
            'description': 'some description',
            'expression': '',
        }
        response = await self.request(web_app_client, source_id, column_data)
        assert response.status == 400, await response.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_source.sql'],
    )
    async def test_create_invalid_expression(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            patch: Patch,
    ) -> None:
        @patch('atlas_clickhouse.components.ClickHouseClient.__getitem__')
        def getitem(item: str) -> FakeClickhouseClient:
            client = FakeClickhouseClient()

            @client
            def execute(query: str) -> CHResult:
                if query.startswith('DESCRIBE TABLE '):
                    table = query[len('DESCRIBE TABLE ') :]
                    return CREATE_TABLE_STATEMENTS[table]
                if query.startswith('SELECT'):
                    raise errors.ServerException(
                        'DB::Exception: Expression error:',
                    )
                assert False

            return client

        source_id = 3
        column_data = {
            'column_name': 'some_name',
            'description': 'some description',
            'expression': 'invalid expression',
        }
        response = await self.request(web_app_client, source_id, column_data)
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::InvalidExpression'
        assert err['message'] == 'Expression error'

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_source.sql', 'pg_column.sql'],
    )
    async def test_create_expression_with_unknown_columns(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            patch: Patch,
    ) -> None:
        @patch('atlas_clickhouse.components.ClickHouseClient.__getitem__')
        def getitem(item: str) -> FakeClickhouseClient:
            client = FakeClickhouseClient()

            @client
            def execute(query: str) -> CHResult:
                if query.startswith('DESCRIBE TABLE '):
                    table = query[len('DESCRIBE TABLE ') :]
                    return CREATE_TABLE_STATEMENTS[table]
                assert False

            return client

        source_id = 3
        column_data = {
            'column_name': 'some_name',
            'description': 'some description',
            'expression': '{unknown_column} OR {dttm} OR {kek}',
        }
        response = await self.request(web_app_client, source_id, column_data)
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::ColumnsNotExist'
        assert err['message'] in (
            (
                'Some columns used in expression (unknown_column, kek) not '
                'exist in source third_test_source'
            ),
            (
                'Some columns used in expression (kek, unknown_column) not '
                'exist in source third_test_source'
            ),
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_source.sql'],
    )
    async def test_create_with_expression_without_accolades(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            patch: Patch,
    ) -> None:
        @patch('atlas_clickhouse.components.ClickHouseClient.__getitem__')
        def getitem(item: str) -> FakeClickhouseClient:
            client = FakeClickhouseClient()

            @client
            def execute(query: str) -> CHResult:
                if query.startswith('DESCRIBE TABLE '):
                    table = query[len('DESCRIBE TABLE ') :]
                    return CREATE_TABLE_STATEMENTS[table]
                if query.startswith('SELECT'):
                    raise errors.ServerException(
                        'DB::Exception: Missing columns: \'city\' '
                        '\'unknown\' while processing query:...',
                    )
                assert False

            return client

        source_id = 3
        column_data = {
            'column_name': 'some_name',
            'description': 'some description',
            'expression': 'unknown OR city OR {record_id}',
        }
        response = await self.request(web_app_client, source_id, column_data)
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::InvalidExpression'
        assert err['message'] == 'Missing columns: \'city\' \'unknown\''

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_source.sql', 'pg_column.sql'],
    )
    async def test_create_with_name_conflict(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            patch: Patch,
    ) -> None:
        @patch('atlas_clickhouse.components.ClickHouseClient.__getitem__')
        def getitem(item: str) -> FakeClickhouseClient:
            client = FakeClickhouseClient()

            @client
            def execute(query: str) -> CHResult:
                if query.startswith('DESCRIBE TABLE '):
                    table = query[len('DESCRIBE TABLE ') :]
                    return CREATE_TABLE_STATEMENTS[table]
                if query.startswith('SELECT'):
                    db_type = 'UInt32'
                    return [(db_type,)]
                assert False

            return client

        source_id = 3
        column_data = {
            'column_name': 'city',
            'description': 'some description',
            'expression': '\'Moscow\'',
        }
        response = await self.request(web_app_client, source_id, column_data)
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::ColumnExists'
        assert (
            err['message']
            == 'Column "city" already exists in the source with id 3'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_source.sql', 'pg_column.sql'],
    )
    @pytest.mark.parametrize(
        'name',
        [
            '1_source_name',  # не должно начинаться с числа
            '__source_name',  # не должно начинаться с двух подчеркиваний
            # не может иметь не альфаньюмерик символов, кроме андерскора
            'source name',
            'source-name',
            'source%name',
            'class',  # не должно быть ключевым словом
            'from',
            'import',
            '',
        ],
    )
    async def test_invalid_name(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            name: str,
    ) -> None:
        source_id = 3
        column_data = {
            'column_name': name,
            'description': 'some description',
            'expression': '\'Moscow\'',
        }
        response = await self.request(web_app_client, source_id, column_data)
        assert response.status == 400, await response.json()
        err = await response.json()
        assert err['code'] == 'BadRequest::NotAllowedColumnName'
        assert err['message'] == (
            'Column name must be a valid Python identifier, must not '
            'be a Python keyword, and not starts with two underscores'
        )


class TestExtractColumns:
    async def request(
            self, web_app_client: test_utils.TestClient, source_id: int,
    ) -> test_utils.ClientResponse:
        path = '/api/sources/columns/extract'
        params = {'source_id': source_id}
        return await web_app_client.post(path, params=params)

    @pytest.mark.parametrize('username', [None])
    async def test_extract_without_login(
            self,
            web_app_client: test_utils.TestClient,
            username: tp.Optional[str],
    ) -> None:
        source_id = 3
        path = '/api/sources/columns/extract'
        params = {'source_id': source_id}
        response = await web_app_client.post(
            path, params=params, allow_redirects=False,
        )
        assert response.status == 302, await response.text()

    async def test_extract_columns_from_not_existed_source(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        source_id = 404  # not exists
        response = await self.request(web_app_client, source_id)
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::SourceNotExists'
        assert err['message'] == f'There is not source with id {source_id}'

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_source.sql'],
    )
    @pytest.mark.parametrize('source_id', [3, 4])
    async def test_first_extraction(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            patch: Patch,
            source_id: int,
    ) -> None:
        @patch('atlas_clickhouse.components.ClickHouseClient.__getitem__')
        def getitem(item: str) -> FakeClickhouseClient:
            client = FakeClickhouseClient()

            @client
            def execute(query: str) -> CHResult:
                if query.startswith('DESCRIBE TABLE '):
                    table = query[len('DESCRIBE TABLE ') :]
                    return CREATE_TABLE_STATEMENTS[table]
                assert False

            return client

        response = await self.request(web_app_client, source_id)
        assert response.status == 201, await response.text()

        existed_columns = [
            {
                'source_id': source_id,
                'column_name': column['column_name'],
                'description': '',
                'db_type': column['db_type'],
                'native_type': column['native_type'],
                'expression': '',
                'metadata': [],
                'is_valid': True,
            }
            for column in get_existed_columns(
                source_id=source_id, expression='',
            )
        ]

        columns = await get_columns(web_app_client, source_id)
        for column in columns:
            assert column in existed_columns
            existed_columns.remove(column)
        assert not existed_columns

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_source.sql', 'pg_column.sql'],
    )
    @pytest.mark.parametrize('source_id', [3, 4])
    async def test_not_first_extraction_without_changing(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            patch: Patch,
            source_id: int,
    ) -> None:
        @patch('atlas_clickhouse.components.ClickHouseClient.__getitem__')
        def getitem(item: str) -> FakeClickhouseClient:
            client = FakeClickhouseClient()

            @client
            def execute(query: str) -> CHResult:
                if query.startswith('DESCRIBE TABLE '):
                    table = query[len('DESCRIBE TABLE ') :]
                    return CREATE_TABLE_STATEMENTS[table]
                if query.startswith('SELECT toTypeName(NULL)'):
                    db_type = 'Nullable(Nothing)'
                    return [(db_type,)]
                if query.startswith('SELECT '):
                    db_type = 'DateTime'
                    return [(db_type,)]
                assert False

            return client

        response = await self.request(web_app_client, source_id)
        assert response.status == 201, await response.text()

        existed_columns = get_existed_columns(source_id=source_id)

        columns = await get_columns(web_app_client, source_id)
        for column in columns:
            assert column in existed_columns
            existed_columns.remove(column)
        assert not existed_columns

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_source.sql', 'pg_column.sql'],
    )
    async def test_not_first_extraction_with_changing(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            patch: Patch,
    ) -> None:
        @patch('atlas_clickhouse.components.ClickHouseClient.__getitem__')
        def getitem(item: str) -> FakeClickhouseClient:
            client = FakeClickhouseClient()

            @client
            def execute(query: str) -> CHResult:
                if query.startswith('DESCRIBE TABLE '):
                    table = query[len('DESCRIBE TABLE ') :]
                    return UPDATED_TABLE_STATEMENTS[table]
                if query.startswith('SELECT '):
                    db_type = 'DateTime'
                    return [(db_type,)]
                assert False

            return client

        source_id = 3
        response = await self.request(web_app_client, source_id)
        assert response.status == 201, await response.text()

        existed_columns = copy.deepcopy(UPDATED_COLUMNS)

        columns = await get_columns(web_app_client, source_id)
        for column in columns:
            assert column in existed_columns
            existed_columns.remove(column)
        assert not existed_columns


class TestUpdateColumn:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            source_id: int,
            column_name: str,
            column_data: tp.Dict[str, tp.Any],
    ) -> test_utils.ClientResponse:
        path = '/api/sources/columns'
        params = {'source_id': source_id, 'column_name': column_name}
        return await web_app_client.patch(
            path, params=params, json=column_data,
        )

    @pytest.mark.parametrize('username', [None])
    async def test_update_without_login(
            self,
            web_app_client: test_utils.TestClient,
            username: tp.Optional[str],
    ) -> None:
        source_id = 3
        column_name = 'dttm_utc'
        path = '/api/sources/columns'
        params = {'source_id': source_id, 'column_name': column_name}
        response = await web_app_client.patch(
            path, params=params, json={}, allow_redirects=False,
        )
        assert response.status == 302, await response.text()

    async def test_update_not_existed_source_column(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        source_id = 404  # not exists
        column_name = 'not_existed_column_name'  # not exists
        response = await self.request(
            web_app_client, source_id, column_name, {},
        )
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::SourceNotExists'
        assert err['message'] == f'There is not source with id {source_id}'

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_source.sql'],
    )
    async def test_update_not_existed_column(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        source_id = 3
        column_name = 'not_existed_column_name'  # not exists
        response = await self.request(
            web_app_client, source_id, column_name, {},
        )
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::ColumnNotExists'
        assert err['message'] == (
            f'There is not column name {column_name} of source '
            f'with id {source_id}'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_source.sql', 'pg_column.sql'],
    )
    @pytest.mark.parametrize(
        'column_name, description, expression',
        [
            ('record_id', None, None),
            ('record_id', 'Другое описание', None),
            ('dttm_utc', None, None),
            ('dttm_utc', 'Третье описание', None),
            ('dttm_utc', None, '{dttm} - 60 * 60 * 2'),
            ('dttm_utc', 'Четвертое описание', None),
            ('dttm_utc', 'Еще описание', '{dttm} - 60 * 60 * 1'),
        ],
    )
    async def test_update(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            patch: Patch,
            column_name: str,
            description: tp.Optional[str],
            expression: tp.Optional[str],
    ) -> None:
        @patch('atlas_clickhouse.components.ClickHouseClient.__getitem__')
        def getitem(item: str) -> FakeClickhouseClient:
            client = FakeClickhouseClient()

            @client
            def execute(query: str) -> CHResult:
                if query.startswith('DESCRIBE TABLE '):
                    table = query[len('DESCRIBE TABLE ') :]
                    return CREATE_TABLE_STATEMENTS[table]
                if query.startswith('SELECT'):
                    db_type = 'DateTime'
                    return [(db_type,)]
                assert False

            return client

        source_id = 3
        column_data = {}
        if description is not None:
            column_data['description'] = description
        if expression is not None:
            column_data['expression'] = expression
        response = await self.request(
            web_app_client, source_id, column_name, column_data,
        )
        assert response.status == 204, await response.text()

        columns = await get_columns(
            web_app_client, source_id, column_name=column_name,
        )
        assert len(columns) == 1
        (column,) = columns
        (old_column,) = get_existed_columns(
            source_id=source_id, column_name=column_name,
        )
        assert column == {**old_column, **column_data}

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_source.sql', 'pg_column.sql'],
    )
    async def test_virtual_to_real(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        source_id = 3
        column_name = 'dttm_utc'
        column_data = {'expression': ''}
        response = await self.request(
            web_app_client, source_id, column_name, column_data,
        )
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::ChangingVirtualColumn'
        assert (
            err['message']
            == 'It\'s not allowed to set empty expression of virtual column'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_source.sql', 'pg_column.sql'],
    )
    async def test_real_to_virtual(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        source_id = 3
        column_name = 'record_id'
        column_data = {'expression': '{dttm} - 60 * 60 * 3'}
        response = await self.request(
            web_app_client, source_id, column_name, column_data,
        )
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::ChangingNonVirtualColumn'
        assert (
            err['message']
            == 'It\'s not allowed to set expression to non-virtual column'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_source.sql', 'pg_column.sql'],
    )
    async def test_update_with_invalid_expression(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            patch: Patch,
    ) -> None:
        @patch('atlas_clickhouse.components.ClickHouseClient.__getitem__')
        def getitem(item: str) -> FakeClickhouseClient:
            client = FakeClickhouseClient()

            @client
            def execute(query: str) -> CHResult:
                if query.startswith('DESCRIBE TABLE '):
                    table = query[len('DESCRIBE TABLE ') :]
                    return CREATE_TABLE_STATEMENTS[table]
                if query.startswith('SELECT'):
                    raise errors.ServerException(
                        'DB::Exception: Expression error:',
                    )
                assert False

            return client

        source_id = 3
        column_name = 'dttm_utc'
        column_data = {'expression': 'invalid expression'}
        response = await self.request(
            web_app_client, source_id, column_name, column_data,
        )
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::InvalidExpression'
        assert err['message'] == 'Expression error'

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_source.sql', 'pg_column.sql'],
    )
    async def test_update_with_expression_with_unknown_columns(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            patch: Patch,
    ) -> None:
        @patch('atlas_clickhouse.components.ClickHouseClient.__getitem__')
        def getitem(item: str) -> FakeClickhouseClient:
            client = FakeClickhouseClient()

            @client
            def execute(query: str) -> CHResult:
                if query.startswith('DESCRIBE TABLE '):
                    table = query[len('DESCRIBE TABLE ') :]
                    return CREATE_TABLE_STATEMENTS[table]
                assert False

            return client

        source_id = 3
        column_name = 'dttm_utc'
        column_data = {'expression': '{invalid} + {expression}'}
        response = await self.request(
            web_app_client, source_id, column_name, column_data,
        )
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::ColumnsNotExist'
        assert err['message'] in (
            (
                'Some columns used in expression (invalid, expression) not '
                'exist in source third_test_source'
            ),
            (
                'Some columns used in expression (expression, invalid) not '
                'exist in source third_test_source'
            ),
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_source.sql', 'pg_column.sql'],
    )
    async def test_expression_without_accolades(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            patch: Patch,
    ) -> None:
        @patch('atlas_clickhouse.components.ClickHouseClient.__getitem__')
        def getitem(item: str) -> FakeClickhouseClient:
            client = FakeClickhouseClient()

            @client
            def execute(query: str) -> CHResult:
                if query.startswith('DESCRIBE TABLE '):
                    table = query[len('DESCRIBE TABLE ') :]
                    return CREATE_TABLE_STATEMENTS[table]
                if query.startswith('SELECT'):
                    raise errors.ServerException(
                        'DB::Exception: Missing columns: \'dttm\' '
                        'while processing query:...',
                    )
                assert False

            return client

        source_id = 3
        column_name = 'dttm_utc'
        column_data = {'expression': 'dttm - 60 * 60 * 3'}
        response = await self.request(
            web_app_client, source_id, column_name, column_data,
        )
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::InvalidExpression'
        assert err['message'] == 'Missing columns: \'dttm\''


class TestDeleteColumnMetadata:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            source_id: int,
            column_name: str,
            metadata_key: str,
    ) -> test_utils.ClientResponse:
        path = '/api/sources/columns/metadata/'
        params = {
            'source_id': source_id,
            'column_name': column_name,
            'metadata_key': metadata_key,
        }
        return await web_app_client.delete(path, params=params)

    @pytest.mark.parametrize('username', [None])
    async def test_create_without_login(
            self,
            web_app_client: test_utils.TestClient,
            username: tp.Optional[str],
    ) -> None:
        source_id = 3
        column_name = 'dttm_utc'
        metadata_key = 'utc_offset'
        path = '/api/sources/columns/metadata/'
        params = {
            'source_id': source_id,
            'column_name': column_name,
            'metadata_key': metadata_key,
        }
        response = await web_app_client.delete(
            path, params=params, allow_redirects=False,
        )
        assert response.status == 302, await response.text()

    async def test_delete_not_existed_source(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        source_id = 404  # not exists
        column_name = 'column'  # not exists
        metadata_key = 'key'  # not exists
        response = await self.request(
            web_app_client, source_id, column_name, metadata_key,
        )
        assert response.status == 204, await response.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_source.sql'],
    )
    async def test_delete_not_existed_column(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        source_id = 3
        column_name = 'column'  # not exists
        metadata_key = 'key'  # not exists
        response = await self.request(
            web_app_client, source_id, column_name, metadata_key,
        )
        assert response.status == 204, await response.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_source.sql', 'pg_column.sql'],
    )
    async def test_delete_not_existed_key(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        source_id = 3
        column_name = 'dttm_utc'
        metadata_key = 'key'  # not exists
        response = await self.request(
            web_app_client, source_id, column_name, metadata_key,
        )
        assert response.status == 204, await response.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_source.sql', 'pg_column.sql'],
    )
    async def test_delete(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        source_id = 3
        column_name = 'dttm_utc'
        metadata_key = 'utc_offset'
        response = await self.request(
            web_app_client, source_id, column_name, metadata_key,
        )
        assert response.status == 204, await response.text()
        columns = await get_columns(
            web_app_client, source_id, column_name=column_name,
        )
        assert len(columns) == 1
        (column,) = columns
        metadata_item = {
            'key': 'used_columns',
            'value': '["dttm"]',
            'set_by': '',
        }
        assert column['metadata'] == [metadata_item]

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_source.sql', 'pg_column.sql'],
    )
    async def test_delete_not_user_set_by(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        source_id = 3
        column_name = 'dttm_utc'
        metadata_key = 'used_columns'
        response = await self.request(
            web_app_client, source_id, column_name, metadata_key,
        )
        assert response.status == 204, await response.text()
        columns = await get_columns(
            web_app_client, source_id, column_name=column_name,
        )
        assert len(columns) == 1
        (column,) = columns
        (old_column,) = get_existed_columns(
            source_id=source_id, column_name=column_name,
        )
        assert column['metadata'] == old_column['metadata']


class TestSetColumnMetadata:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            source_id: int,
            column_name: str,
            metadata_key: str,
            value: str,
    ) -> test_utils.ClientResponse:
        path = '/api/sources/columns/metadata/'
        params = {
            'source_id': source_id,
            'column_name': column_name,
            'metadata_key': metadata_key,
            'value': value,
        }
        return await web_app_client.post(path, params=params)

    @pytest.mark.parametrize('username', [None])
    async def test_set_without_login(
            self,
            web_app_client: test_utils.TestClient,
            username: tp.Optional[str],
    ) -> None:
        source_id = 3
        column_name = 'dttm_utc'
        metadata_key = 'utc_offset'
        value = '10'
        path = '/api/sources/columns/metadata/'
        params = {
            'source_id': source_id,
            'column_name': column_name,
            'metadata_key': metadata_key,
            'value': value,
        }
        response = await web_app_client.post(
            path, params=params, allow_redirects=False,
        )
        assert response.status == 302, await response.text()

    async def test_set_not_existed_source(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        source_id = 404  # not exists
        column_name = 'column'  # not exists
        metadata_key = 'key'
        value = 'value'
        response = await self.request(
            web_app_client, source_id, column_name, metadata_key, value,
        )
        assert response.status == 204, await response.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_source.sql'],
    )
    async def test_set_not_existed_column(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        source_id = 3
        column_name = 'column'  # not exists
        metadata_key = 'key'
        value = 'value'
        response = await self.request(
            web_app_client, source_id, column_name, metadata_key, value,
        )
        assert response.status == 204, await response.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_source.sql', 'pg_column.sql'],
    )
    @pytest.mark.parametrize(
        'metadata_key, value',
        [
            ('used_columns', '["not_existed_column"]'),
            ('used_columns', '["dttm"]'),
            ('utc_offset', '5'),
            ('utc_offset', '0'),
            ('new_key', 'new_value'),
        ],
    )
    async def test_set(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            username: str,
            metadata_key: str,
            value: str,
    ) -> None:
        source_id = 3
        column_name = 'dttm_utc'
        response = await self.request(
            web_app_client, source_id, column_name, metadata_key, value,
        )
        assert response.status == 204, await response.text()

        columns = await get_columns(
            web_app_client, source_id, column_name=column_name,
        )
        assert len(columns) == 1
        (column,) = columns
        (old_column,) = get_existed_columns(
            source_id=source_id, column_name=column_name,
        )
        old_metadata = old_column['metadata']
        try:
            old_value_ = json.loads(value)
        except ValueError:
            old_value_ = value
        old_value = json.dumps(old_value_)

        for metadata_item in old_metadata:
            if metadata_item['key'] == metadata_key:
                metadata_item['value'] = old_value
                metadata_item['set_by'] = username
                break
        else:
            old_metadata.append(
                {'key': metadata_key, 'value': old_value, 'set_by': username},
            )

        for metadata_item in column['metadata']:
            assert metadata_item in old_metadata
            old_metadata.remove(metadata_item)
        assert not old_metadata
