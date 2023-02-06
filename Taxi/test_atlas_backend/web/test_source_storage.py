# pylint: disable=W0621
import datetime
import typing as tp

from aiohttp import test_utils
import pytest

from test_atlas_backend.web import db_data


Patch = tp.Callable[[str], tp.Callable[[tp.Callable], tp.Callable]]

EXISTED_SOURCE = db_data.SOURCES


async def get_source(
        web_app_client: test_utils.TestClient, source_id: int,
) -> tp.Dict[str, tp.Any]:
    params = {'source_id': source_id}
    response = await web_app_client.get('/api/sources', params=params)
    assert response.status == 200, await response.text()
    return await response.json()


async def get_sources(
        web_app_client: test_utils.TestClient,
) -> tp.List[tp.Dict[str, tp.Any]]:
    response = await web_app_client.get('/api/sources/list')
    assert response.status == 200, await response.text()
    return await response.json()


async def delete_source(
        web_app_client: test_utils.TestClient, source_id: int,
) -> None:
    # in case passport error, make sure that you use atlas_blackbox_mock
    params = {'source_id': source_id}
    response = await web_app_client.delete('/api/sources', params=params)
    assert response.status == 204, await response.text()


class _NewSourcesGetter:
    def __init__(self, web_app_client: test_utils.TestClient) -> None:
        self._web_app_client = web_app_client
        self.existed_source_ids: tp.Set[int] = set()
        self.new_sources: tp.List[tp.Dict[str, tp.Any]] = []

    async def __aenter__(self):
        self.existed_source_ids = {
            source['source_id']
            for source in await get_sources(self._web_app_client)
        }
        return self

    async def __aexit__(self, *args, **kwargs):
        self.new_sources = [
            source
            for source in await get_sources(self._web_app_client)
            if source['source_id'] not in self.existed_source_ids
        ]


@pytest.fixture
def source_is_valid(patch: Patch) -> None:
    base_path = 'atlas_backend.internal.sources.models.'

    @patch(base_path + 'ch_source_model.CHSource.validate')
    async def ch_validate(  # pylint: disable=unused-variable
            *args, **kwargs,
    ) -> None:
        pass

    @patch(base_path + 'chyt_source_model.CHYTSource.validate')
    async def chyt_validate(  # pylint: disable=unused-variable
            *args, **kwargs,
    ) -> None:
        pass


class TestGetSources:
    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_source.sql'],
    )
    async def test_get_list(
            self, web_app_client: test_utils.TestClient,
    ) -> None:
        response = await web_app_client.get('/api/sources/list')
        assert response.status == 200, await response.text()
        sources = await response.json()
        assert len(sources) == len(EXISTED_SOURCE)
        sources.sort(key=lambda source: source['source_id'])
        assert sources == sorted(
            EXISTED_SOURCE, key=lambda source: source['source_id'],
        )


class TestGetSource:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            source_id: int,
            extra_info: tp.Optional[str] = None,
    ) -> test_utils.ClientResponse:
        path = '/api/sources'
        params: tp.Dict[str, tp.Union[str, int]] = {'source_id': source_id}
        if extra_info is not None:
            params['extra_info'] = extra_info
        return await web_app_client.get(path, params=params)

    async def test_get_not_existed_source(
            self, web_app_client: test_utils.TestClient,
    ) -> None:
        source_id = 1
        response = await self.request(web_app_client, source_id)
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::SourceNotExists'
        assert err['message'] == f'There is not source with id {source_id}'

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_source.sql'],
    )
    @pytest.mark.parametrize('source', [source for source in EXISTED_SOURCE])
    async def test_get(
            self,
            web_app_client: test_utils.TestClient,
            source: tp.Dict[str, tp.Any],
    ) -> None:
        response = await self.request(web_app_client, source['source_id'])
        assert response.status == 200, await response.text()
        source_data = await response.json()
        assert source_data == source

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_source.sql', 'pg_column.sql'],
    )
    @pytest.mark.parametrize('source', [source for source in EXISTED_SOURCE])
    async def test_get_with_columns(
            self,
            web_app_client: test_utils.TestClient,
            source: tp.Dict[str, tp.Any],
    ) -> None:
        source_id = source['source_id']
        response = await self.request(
            web_app_client, source_id, extra_info='with_columns',
        )
        assert response.status == 200, await response.text()
        source_data = await response.json()
        assert 'columns' in source_data
        columns_data = source_data.pop('columns')
        assert source_data == source
        columns = [
            column
            for column in db_data.COLUMNS
            if column['source_id'] == source_id
        ]
        for column in columns_data:
            assert column in columns
            columns.remove(column)
        assert not columns

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
        ],
    )
    @pytest.mark.parametrize('source', [source for source in EXISTED_SOURCE])
    async def test_get_with_col_and_dim(
            self,
            web_app_client: test_utils.TestClient,
            source: tp.Dict[str, tp.Any],
    ) -> None:
        source_id = source['source_id']
        response = await self.request(
            web_app_client,
            source_id,
            extra_info='with_columns_and_dimensions',
        )
        assert response.status == 200, await response.text()
        source_data = await response.json()
        assert 'columns' in source_data
        columns_data = source_data.pop('columns')
        assert source_data == source
        columns = [
            column
            for column in db_data.COLUMNS
            if column['source_id'] == source_id
        ]
        for column in columns_data:
            assert 'dimensions' in column
            dimensions_data = column.pop('dimensions')
            assert column in columns
            dimension_ids = {
                rel['dimension_id']
                for rel in db_data.COLUMNS_DIMENSIONS_REL
                if rel['source_id'] == source_id
                and rel['column_name'] == column['column_name']
            }
            dimensions = [
                dim
                for dim in db_data.DIMENSIONS
                if dim['dimension_id'] in dimension_ids
            ]
            for dimension in dimensions_data:
                assert dimension in dimensions
                dimensions.remove(dimension)
            assert not dimensions
            columns.remove(column)
        assert not columns


class TestDeleteSource:
    async def request(
            self, web_app_client: test_utils.TestClient, source_id: int,
    ) -> test_utils.ClientResponse:
        path = '/api/sources/'
        params = {'source_id': source_id}
        return await web_app_client.delete(path, params=params)

    @pytest.mark.parametrize('username', [None])
    async def test_delete_without_login(
            self,
            web_app_client: test_utils.TestClient,
            username: tp.Optional[str],
    ) -> None:
        source_id = 1
        path = '/api/sources/'
        params = {'source_id': source_id}
        response = await web_app_client.delete(
            path, params=params, allow_redirects=False,
        )
        assert response.status == 302, await response.text()

    async def test_delete_not_existed_source(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        source_id = 1  # not exists
        response = await self.request(web_app_client, source_id)
        assert response.status == 204, await response.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_source.sql'],
    )
    @pytest.mark.parametrize(
        'source_id', [source['source_id'] for source in EXISTED_SOURCE],
    )
    async def test_delete(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            source_id: int,
    ) -> None:
        response = await self.request(web_app_client, source_id)
        assert response.status == 204, await response.text()
        response = await web_app_client.get(
            '/api/sources/', params={'source_id': source_id},
        )
        assert response.status == 404, await response.text()


class TestCreateSource:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            source_data: tp.Dict[str, tp.Any],
    ) -> test_utils.ClientResponse:
        path = '/api/sources'
        return await web_app_client.post(path, json=source_data)

    @pytest.mark.parametrize('username', [None])
    async def test_create_without_login(
            self,
            web_app_client: test_utils.TestClient,
            username: tp.Optional[str],
    ) -> None:
        source_data = {
            'source_cluster': 'hahn',
            'source_path': '/path',
            'source_name': 'source_name',
        }
        path = '/api/sources'
        response = await web_app_client.post(
            path, json=source_data, allow_redirects=False,
        )
        assert response.status == 302, await response.text()

    @pytest.mark.parametrize(
        'source_name',
        [
            '_source_name',
            'source_name',
            'SourceName',
            'Source_Name',
            'SOURCE_NAME',
            'source_name_1',
        ],
    )
    async def test_create_source(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            source_is_valid: None,
            source_name: str,
    ) -> None:
        source_data = {
            'source_cluster': 'hahn',
            'source_path': '/path',
            'source_name': source_name,
        }
        async with _NewSourcesGetter(web_app_client) as helper:
            response = await self.request(web_app_client, source_data)
            assert response.status == 201, await response.text()
        (source,) = helper.new_sources
        for key, value in source_data.items():
            assert source[key] == value
        await delete_source(web_app_client, source['source_id'])

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_source.sql'],
    )
    @pytest.mark.parametrize(
        'source_name', [source['source_name'] for source in EXISTED_SOURCE],
    )
    async def test_name_conflict(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            source_is_valid: None,
            source_name: str,
    ) -> None:
        source_data = {
            'source_cluster': 'hahn',
            'source_path': '/path',
            'source_name': source_name,
        }
        response = await self.request(web_app_client, source_data)
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::SourceExists'
        assert err['message'] == f'Source named {source_name} already exists'

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_source.sql'],
    )
    @pytest.mark.parametrize(
        'source_type,source_cluster,source_path',
        [
            (
                source['source_type'],
                source['source_cluster'],
                source['source_path'],
            )
            for source in EXISTED_SOURCE
        ],
    )
    async def test_cluster_path_conflict(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            source_is_valid: None,
            source_type: str,
            source_cluster: str,
            source_path: str,
    ) -> None:
        source_data = {
            'source_type': source_type,
            'source_cluster': source_cluster,
            'source_path': source_path,
            'source_name': 'source_name',
        }
        response = await self.request(web_app_client, source_data)
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::SourceExists'
        assert err['message'] == (
            f'Source with cluster and path pair "{source_cluster}" and '
            f'"{source_path}" already exists'
        )

    async def test_create_partitioned_source(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            source_is_valid: None,
    ) -> None:
        source_data = {
            'source_cluster': 'hahn',
            'source_path': '/path',
            'source_name': 'source_name',
            'is_partitioned': True,
            'partition_key': 'datetime',
            'partition_template': '%Y-%m',
        }
        async with _NewSourcesGetter(web_app_client) as helper:
            response = await self.request(web_app_client, source_data)
            assert response.status == 201, await response.text()
        (source,) = helper.new_sources
        for key, value in source_data.items():
            assert source[key] == value
        await delete_source(web_app_client, source['source_id'])

    @pytest.mark.parametrize(
        'source_name',
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
            source_name: str,
    ) -> None:
        source_data = {
            'source_cluster': 'hahn',
            'source_path': '/path',
            'source_name': source_name,
        }
        response = await self.request(web_app_client, source_data)
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::NotAllowedSourceName'
        assert err['message'] == (
            'Source name must be a valid Python identifier, must not be a '
            'Python keyword, and not starts with two underscores'
        )

    async def test_empty_path(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        source_data = {
            'source_cluster': 'hahn',
            'source_path': '',
            'source_name': 'source_name',
        }
        response = await self.request(web_app_client, source_data)
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::InvalidSourcePath'
        assert (
            err['message']
            == 'It\'s not allowed to create source with empty path'
        )


class TestUpdateSource:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            source_id: int,
            source_data: tp.Dict[str, tp.Any],
    ) -> test_utils.ClientResponse:
        path = '/api/sources'
        params = {'source_id': source_id}
        return await web_app_client.patch(
            path, params=params, json=source_data,
        )

    @pytest.mark.parametrize('username', [None])
    async def test_update_without_login(
            self,
            web_app_client: test_utils.TestClient,
            username: tp.Optional[str],
    ) -> None:
        source_id = 1
        path = '/api/sources'
        params = {'source_id': source_id}
        response = await web_app_client.patch(
            path, params=params, json={}, allow_redirects=False,
        )
        assert response.status == 302, await response.text()

    async def test_update_not_existed_source(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        source_id = 1  # not exists
        response = await self.request(web_app_client, source_id, {})
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::SourceNotExists'
        assert err['message'] == f'There is not source with id {source_id}'

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_source.sql'],
    )
    @pytest.mark.parametrize(
        'existed_source', [source for source in EXISTED_SOURCE],
    )
    @pytest.mark.parametrize(
        'source_name',
        [
            '_source_name',
            'source_name',
            'SourceName',
            'Source_Name',
            'SOURCE_NAME',
            'source_name_1',
        ],
    )
    async def test_update_source(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            source_is_valid: None,
            existed_source: tp.Dict[str, tp.Any],
            source_name: str,
    ) -> None:

        cluster_map = {
            'arnold': 'hahn',
            'hahn': 'arnold',
            'atlas_mdb': 'atlastest_mdb',
            'atlastest_mdb': 'atlas_mdb',
        }
        another_paths = {'chyt': '//home', 'clickhouse': 'ho.me'}

        source_id = existed_source['source_id']
        another_is_partitioned = existed_source['source_type'] == 'chyt'

        source_data = {
            'source_cluster': cluster_map[existed_source['source_cluster']],
            'source_path': another_paths[existed_source['source_type']],
            'source_name': source_name,
            'description': 'description',
            'is_partitioned': another_is_partitioned,
            'partition_key': 'datetime' if another_is_partitioned else '',
            'partition_template': '%Y-%m' if another_is_partitioned else '',
        }

        response = await self.request(web_app_client, source_id, source_data)
        assert response.status == 204, await response.text()
        source = await get_source(web_app_client, source_id)
        for key, value in source.items():
            if key == 'changed_at':
                continue
            if key in source_data:
                assert source[key] == source_data[key]
            else:
                assert source[key] == value
        assert source['changed_at'] > existed_source['changed_at']

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_source.sql'],
    )
    async def test_name_conflict(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            source_is_valid: None,
    ) -> None:
        updated_source, *other_sources = EXISTED_SOURCE
        source_id = updated_source['source_id']
        for other_source in other_sources:
            source_name = other_source['source_name']
            source_data = {'source_name': source_name}
            response = await self.request(
                web_app_client, source_id, source_data,
            )
            assert response.status == 400, await response.text()
            err = await response.json()
            assert err['code'] == 'BadRequest::SourceExists'
            assert (
                err['message'] == f'Source named {source_name} already exists'
            )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_source.sql'],
    )
    @pytest.mark.parametrize('source_type', ['chyt', 'clickhouse'])
    async def test_cluster_path_conflict(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            source_is_valid: None,
            source_type: str,
    ) -> None:
        updated_source, *other_sources = [
            source
            for source in EXISTED_SOURCE
            if source['source_type'] == source_type
        ]
        source_id = updated_source['source_id']
        for other_source in other_sources:
            source_cluster = other_source['source_cluster']
            source_path = other_source['source_path']
            source_data = {
                'source_cluster': source_cluster,
                'source_path': source_path,
            }
            response = await self.request(
                web_app_client, source_id, source_data,
            )
            assert response.status == 400, await response.text()
            err = await response.json()
            assert err['code'] == 'BadRequest::SourceExists'
            assert err['message'] == (
                f'Source with cluster and path pair "{source_cluster}" and '
                f'"{source_path}" already exists'
            )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_source.sql'],
    )
    @pytest.mark.parametrize(
        'source_id', [source['source_id'] for source in EXISTED_SOURCE],
    )
    @pytest.mark.parametrize(
        'source_name',
        [
            '1_source_name',
            '__source_name',
            'source name',
            'source-name',
            'source%name',
            'class',
            'from',
            'import',
            '',
        ],
    )
    async def test_invalid_name(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            source_id: int,
            source_name: str,
    ) -> None:
        source_data = {'source_name': source_name}
        response = await self.request(web_app_client, source_id, source_data)
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::NotAllowedSourceName'
        assert err['message'] == (
            'Source name must be a valid Python identifier, must not be a '
            'Python keyword, and not starts with two underscores'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_source.sql'],
    )
    @pytest.mark.parametrize(
        'source_id', [source['source_id'] for source in EXISTED_SOURCE],
    )
    async def test_empty_path(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            source_id: int,
    ) -> None:
        source_data = {'source_path': ''}
        response = await self.request(web_app_client, source_id, source_data)
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::InvalidSourcePath'
        assert (
            err['message']
            == 'It\'s not allowed to create source with empty path'
        )


class TestSetDataUpdateTime:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            source_id: int,
            data_updated_at: tp.Optional[int] = None,
    ) -> test_utils.ClientResponse:
        path = '/api/sources/set_data_update_time'
        params = {'source_id': source_id}
        if data_updated_at is not None:
            params['data_updated_at'] = data_updated_at
        return await web_app_client.post(path, params=params)

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_source.sql'],
    )
    @pytest.mark.parametrize(
        'existed_source', [source for source in EXISTED_SOURCE],
    )
    async def test_set_data_update_time(
            self,
            web_app_client: test_utils.TestClient,
            existed_source: tp.Dict[str, tp.Any],
    ) -> None:
        source_id = existed_source['source_id']
        data_updated_at = 1640995200  # 2022-01-01 00:00:00+00:00
        assert data_updated_at > existed_source['data_updated_at']
        response = await self.request(
            web_app_client, source_id, data_updated_at,
        )
        assert response.status == 204, await response.text()
        source = await get_source(web_app_client, source_id)
        for key, value in source.items():
            if key == 'data_updated_at':
                continue
            assert value == existed_source[key]
        assert source['data_updated_at'] == data_updated_at

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_source.sql'],
    )
    @pytest.mark.parametrize(
        'existed_source', [source for source in EXISTED_SOURCE],
    )
    async def test_set_data_update_time_now(
            self,
            web_app_client: test_utils.TestClient,
            existed_source: tp.Dict[str, tp.Any],
    ) -> None:
        source_id = existed_source['source_id']
        response = await self.request(web_app_client, source_id)
        assert response.status == 204, await response.text()
        source = await get_source(web_app_client, source_id)
        for key, value in source.items():
            if key == 'data_updated_at':
                continue
            assert value == existed_source[key]
        now = datetime.datetime.now().timestamp()
        assert abs(source['data_updated_at'] - now) < 5

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_source.sql'],
    )
    @pytest.mark.parametrize(
        'existed_source', [source for source in EXISTED_SOURCE],
    )
    async def test_set_old_data_update_time(
            self,
            web_app_client: test_utils.TestClient,
            existed_source: tp.Dict[str, tp.Any],
    ) -> None:
        source_id = existed_source['source_id']
        data_updated_at = 315514800  # 1980-01-01 00:00:00+00:00
        assert data_updated_at < existed_source['data_updated_at']
        response = await self.request(
            web_app_client, source_id, data_updated_at,
        )
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::DataUpdatingTime'
        assert err['message'] == 'Setted updating time less than current'
