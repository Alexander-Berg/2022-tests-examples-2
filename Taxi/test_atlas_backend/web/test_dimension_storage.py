# TODO: Split the file?
# pylint: disable=C0103, C0302, W0621
import copy
import typing as tp

from aiohttp import test_utils
import pytest

from test_atlas_backend.web import db_data

Patch = tp.Callable[[str], tp.Callable[[tp.Callable], tp.Callable]]

dimensions = pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_dimension.sql'],
)
dimensions_and_columns = pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend',
    files=['pg_source.sql', 'pg_column.sql', 'pg_dimension.sql'],
)
dimensions_with_relations = pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend',
    files=[
        'pg_source.sql',
        'pg_column.sql',
        'pg_dimension.sql',
        'pg_col_dim_relation.sql',
    ],
)

EXISTED_DIMENSIONS = db_data.DIMENSIONS
EXISTED_RELATIONS = db_data.COLUMNS_DIMENSIONS_REL


async def get_dimensions(
        web_app_client: test_utils.TestClient, **filters,
) -> tp.List[tp.Dict[str, tp.Any]]:
    response = await web_app_client.get('/api/v1/dimensions/list')
    assert response.status == 200, await response.text()
    dims = await response.json()
    for key, value in filters.items():
        dims = [dim for dim in dims if dim[key] == value]
    return dims


def get_existed_dimensions(**filters) -> tp.List[tp.Dict[str, tp.Any]]:
    dims = EXISTED_DIMENSIONS
    if 'source_id' in filters or 'column_name' in filters:
        relations = EXISTED_RELATIONS
        for key in ['source_id', 'column_name']:
            value = filters.pop(key, None)
            if value is None:
                continue
            relations = [rel for rel in relations if rel[key] == value]
        ids = {rel['dimension_id'] for rel in relations}
        dims = [dim for dim in dims if dim['dimension_id'] in ids]
    for key, value in filters.items():
        dims = [dim for dim in dims if dim[key] == value]
    return copy.deepcopy(dims)


class TestGetDimensions:
    @dimensions
    async def test_get_dimensions(
            self, web_app_client: test_utils.TestClient,
    ) -> None:
        response = await web_app_client.get('/api/v1/dimensions/list')
        assert response.status == 200, await response.text()
        dims = await response.json()
        assert len(dims) == len(EXISTED_DIMENSIONS)
        dims.sort(key=lambda dim: dim['dimension_id'])
        assert dims == sorted(
            EXISTED_DIMENSIONS, key=lambda dim: dim['dimension_id'],
        )

    @dimensions_with_relations
    @pytest.mark.parametrize('source_id', [1, 2, 3, 4])
    async def test_get_source_dimensions(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            source_id: int,
    ) -> None:
        params = {'source_id': source_id}
        path = '/api/v1/sources/dimensions/list'
        response = await web_app_client.get(path, params=params)
        assert response.status == 200, await response.text()
        dims = await response.json()
        existed_dims = get_existed_dimensions(source_id=source_id)
        for dim in dims:
            assert dim in existed_dims
            existed_dims.remove(dim)
        assert not existed_dims

    @dimensions_with_relations
    @pytest.mark.parametrize(
        'source_id, column_name',
        [
            (1, 'some_column'),
            (2, 'other_column'),
            (3, 'city'),
            (3, 'dttm'),
            (4, 'key'),
        ],
    )
    async def test_get_column_dimensions(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            source_id: int,
            column_name: str,
    ) -> None:
        params = {'source_id': source_id, 'column_name': column_name}
        path = '/api/v1/sources/columns/dimensions/list'
        response = await web_app_client.get(path, params=params)
        assert response.status == 200, await response.text()
        dims = await response.json()
        existed_dims = get_existed_dimensions(
            source_id=source_id, column_name=column_name,
        )
        for dim in dims:
            assert dim in existed_dims
            existed_dims.remove(dim)
        assert not existed_dims

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
        ],
    )
    @dimensions_with_relations
    @pytest.mark.parametrize(
        'metric_id', [metric['metric_id'] for metric in db_data.METRICS],
    )
    async def test_get_metric_dimensions(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            metric_id: int,
    ) -> None:
        params = {'metric_id': metric_id}
        path = '/api/v3/metric/dimension/list'
        response = await web_app_client.get(path, params=params)
        assert response.status == 200, await response.text()
        dims = await response.json()
        metric_dimension_ids = {
            rel['dimension_id']
            for rel in db_data.INSTANCES_DIMENSIONS_REL
            if rel['metric_id'] == metric_id
        }
        existed_dims = [
            dim
            for dim in EXISTED_DIMENSIONS
            if dim['dimension_id'] in metric_dimension_ids
        ]
        for dim in dims:
            assert dim in existed_dims
            existed_dims.remove(dim)
        assert not existed_dims


class TestDeleteDimension:
    async def request(
            self, web_app_client: test_utils.TestClient, dimension_id: int,
    ) -> test_utils.ClientResponse:
        path = '/api/v1/dimensions'
        params = {'dimension_id': dimension_id}
        return await web_app_client.delete(path, params=params)

    @pytest.mark.parametrize('username', [None])
    async def test_delete_without_login(
            self, web_app_client: test_utils.TestClient, username: None,
    ):
        dimension_id = 1
        path = '/api/v1/dimensions'
        params = {'dimension_id': dimension_id}
        response = await web_app_client.delete(
            path, params=params, allow_redirects=False,
        )
        assert response.status == 302, await response.text()

    async def test_delete_not_existed_dimension(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ):
        dimension_id = 1
        response = await self.request(web_app_client, dimension_id)
        assert response.status == 204, await response.text()

    @dimensions_with_relations
    @pytest.mark.parametrize('dimension_id', [3, 4])
    async def test_delete(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            dimension_id: int,
    ):
        dims = await get_dimensions(web_app_client, dimension_id=dimension_id)
        assert len(dims) == 1
        response = await self.request(web_app_client, dimension_id)
        assert response.status == 204, await response.text()
        dims = await get_dimensions(web_app_client, dimension_id=dimension_id)
        assert not dims

    @dimensions_with_relations
    @pytest.mark.parametrize('dimension_id', [1, 2, 5])
    async def test_delete_dimension_with_relation(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            dimension_id: int,
    ):
        dims = await get_dimensions(web_app_client, dimension_id=dimension_id)
        assert len(dims) == 1
        response = await self.request(web_app_client, dimension_id)
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::Can\'tDeleteDimension'
        assert err['message'] == (
            f'Can\'t delete dimension with id {dimension_id}, it has '
            'relations with columns'
        )
        dims = await get_dimensions(web_app_client, dimension_id=dimension_id)
        assert len(dims) == 1


class TestCreateDimension:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            dimension_data: tp.Dict[str, str],
    ) -> test_utils.ClientResponse:
        path = '/api/v1/dimensions'
        return await web_app_client.post(path, json=dimension_data)

    @pytest.mark.parametrize('username', [None])
    async def test_create_without_login(
            self, web_app_client: test_utils.TestClient, username: None,
    ):
        dimension_data = {
            'dimension_name': 'name',
            'description': 'description',
            'dimension_type': 'STR',
        }
        path = '/api/v1/dimensions'
        response = await web_app_client.post(
            path, json=dimension_data, allow_redirects=False,
        )
        assert response.status == 302, await response.text()

    async def test_create(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ):
        dimension_name = 'name'
        dimension_data = {
            'dimension_name': dimension_name,
            'description': 'description',
            'dimension_type': 'STR',
        }
        response = await self.request(
            web_app_client, dimension_data=dimension_data,
        )
        assert response.status == 201, await response.text()
        (dim,) = await get_dimensions(
            web_app_client, dimension_name=dimension_name,
        )
        dim.pop('dimension_id')
        assert dim == dimension_data

    @dimensions
    @pytest.mark.parametrize(
        'dimension_name', ['city', 'time', 'tariff', 'tags', 'one_more_time'],
    )
    async def test_name_conflict(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            dimension_name: str,
    ):
        dimension_data = {
            'dimension_name': dimension_name,
            'description': 'description',
            'dimension_type': 'STR',
        }
        response = await self.request(
            web_app_client, dimension_data=dimension_data,
        )
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::DimensionExists'
        assert (
            err['message']
            == f'Dimension with name {dimension_name} already exists'
        )

    @pytest.mark.parametrize(
        'dimension_name',
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
            dimension_name: str,
    ) -> None:
        dimension_data = {
            'dimension_name': dimension_name,
            'description': 'description',
            'dimension_type': 'STR',
        }
        response = await self.request(
            web_app_client, dimension_data=dimension_data,
        )
        assert response.status == 400, await response.json()
        err = await response.json()
        assert err['code'] == 'BadRequest::NotAllowedDimensionName'
        assert err['message'] == (
            'Dimension name must be a valid Python identifier, must '
            'not be a Python keyword, and not starts with two '
            'underscores'
        )


class TestUpdateDimension:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            dimension_id: int,
            dimension_data: tp.Dict[str, str],
    ) -> test_utils.ClientResponse:
        path = '/api/v1/dimensions'
        params = {'dimension_id': dimension_id}
        return await web_app_client.patch(
            path, params=params, json=dimension_data,
        )

    @pytest.mark.parametrize('username', [None])
    async def test_update_without_login(
            self, web_app_client: test_utils.TestClient, username: None,
    ):
        dimension_id = 1
        path = '/api/v1/dimensions'
        params = {'dimension_id': dimension_id}
        response = await web_app_client.patch(
            path, params=params, json={}, allow_redirects=False,
        )
        assert response.status == 302, await response.text()

    @dimensions
    @pytest.mark.parametrize(
        'description, dimension_type',
        [
            (None, None),
            ('other_description', None),
            (None, 'INT'),
            ('third_description', 'ARRAY_OF_INT'),
            (
                EXISTED_DIMENSIONS[0]['description'],
                EXISTED_DIMENSIONS[0]['dimension_type'],
            ),
        ],
    )
    async def test_update(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            description: tp.Optional[str],
            dimension_type: tp.Optional[str],
    ):
        dimension_id = tp.cast(int, EXISTED_DIMENSIONS[0]['dimension_id'])
        dimension_data = {}
        if description is not None:
            dimension_data['description'] = description
        if dimension_type is not None:
            dimension_data['dimension_type'] = dimension_type
        response = await self.request(
            web_app_client, dimension_id, dimension_data,
        )
        assert response.status == 204, await response.text()
        (dim,) = await get_dimensions(
            web_app_client, dimension_id=dimension_id,
        )
        (existed_dim,) = get_existed_dimensions(dimension_id=dimension_id)
        existed_dim.update(dimension_data)
        assert dim == existed_dim


class TestCreateColDimRelation:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            source_id: int,
            column_name: str,
            dimension_id: int,
    ) -> test_utils.ClientResponse:
        path = '/api/v1/sources/columns/dimensions'
        params = {
            'dimension_id': dimension_id,
            'column_name': column_name,
            'source_id': source_id,
        }
        return await web_app_client.post(path, params=params)

    @pytest.mark.parametrize('username', [None])
    async def test_create_without_login(
            self, web_app_client: test_utils.TestClient, username: None,
    ):
        path = '/api/v1/sources/columns/dimensions'
        params = {'dimension_id': 1, 'column_name': 'name', 'source_id': 1}
        response = await web_app_client.post(
            path, params=params, allow_redirects=False,
        )
        assert response.status == 302, await response.text()

    @dimensions_and_columns
    @pytest.mark.parametrize(
        'source_id, column_name, dimension_id',
        [
            (1000000, 'unknown_column', 1000000),
            (3, 'unknown_column', 1000000),
            (1000000, 'city', 1000000),
            (1000000, 'unknown_column', 1),
            (3, 'unknown_column', 1),
            (1000000, 'city', 1),
        ],
    )
    async def test_create_relation_with_not_existed_column(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            source_id: int,
            column_name: str,
            dimension_id: int,
    ):
        response = await self.request(
            web_app_client, source_id, column_name, dimension_id,
        )
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::ColumnOrDimensionNotFound'
        assert err['message'] == (
            f'Source with id {source_id} or column with name '
            f'{column_name} of source doesn\'t exists'
        )

    @dimensions_and_columns
    @pytest.mark.parametrize(
        'source_id, column_name, dimension_id', [(3, 'city', 1000000)],
    )
    async def test_create_relation_with_not_existed_dimension(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            source_id: int,
            column_name: str,
            dimension_id: int,
    ):
        response = await self.request(
            web_app_client, source_id, column_name, dimension_id,
        )
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::ColumnOrDimensionNotFound'
        assert (
            err['message']
            == f'Dimension with id {dimension_id} doesn\'t exists'
        )

    @dimensions_and_columns
    async def test_create(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ):
        source_id = 3
        column_name = 'city'
        dimension_id = 1
        response = await self.request(
            web_app_client, source_id, column_name, dimension_id,
        )
        assert response.status == 204, await response.text()
        params: tp.Dict[str, tp.Any] = {'source_id': source_id}
        response = await web_app_client.get(
            '/api/v1/sources/dimensions/list', params=params,
        )
        assert response.status == 200, await response.text()
        (dim,) = await response.json()
        assert dim['dimension_id'] == dimension_id
        params['column_name'] = column_name
        response = await web_app_client.get(
            '/api/v1/sources/columns/dimensions/list', params=params,
        )
        assert response.status == 200, await response.text()
        (dim,) = await response.json()
        assert dim['dimension_id'] == dimension_id

    @dimensions_with_relations
    @pytest.mark.parametrize(
        'source_id, column_name, dimension_id',
        [(3, 'dttm', 2), (3, 'dttm_utc', 2)],
    )
    async def test_conflict(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            source_id: int,
            column_name: str,
            dimension_id: int,
    ):
        response = await self.request(
            web_app_client, source_id, column_name, dimension_id,
        )
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::SourceDimensionRelationExists'
        assert err['message'] == (
            f'Relation between dimension with id {dimension_id} and source '
            f'with id {source_id} already exists'
        )


class TestDeleteColDimRelation:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            source_id: int,
            column_name: str,
            dimension_id: int,
    ) -> test_utils.ClientResponse:
        path = '/api/v1/sources/columns/dimensions'
        params = {
            'dimension_id': dimension_id,
            'column_name': column_name,
            'source_id': source_id,
        }
        return await web_app_client.delete(path, params=params)

    @pytest.mark.parametrize('username', [None])
    async def test_delete_without_login(
            self, web_app_client: test_utils.TestClient, username: None,
    ):
        path = '/api/v1/sources/columns/dimensions'
        params = {'dimension_id': 1, 'column_name': 'name', 'source_id': 1}
        response = await web_app_client.delete(
            path, params=params, allow_redirects=False,
        )
        assert response.status == 302, await response.text()

    @dimensions_with_relations
    @pytest.mark.parametrize(
        'source_id, column_name, dimension_id',
        [
            (1000000, 'city', 1000000),
            (3, 'city', 1000000),
            (1000000, 'unknown_column', 1000000),
            (3, 'unknown_column', 1000000),
            (1000000, 'city', 1),
            (3, 'city', 1),
            (1000000, 'unknown_column', 1),
            (3, 'city', 1),
            (3, 'city', 2),
        ],
    )
    async def test_delete(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            source_id: int,
            column_name: str,
            dimension_id: int,
    ):
        response = await self.request(
            web_app_client, source_id, column_name, dimension_id,
        )
        assert response.status == 204, await response.text()
