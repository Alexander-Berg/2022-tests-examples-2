# pylint: disable=C0103
import typing as tp

from aiohttp import test_utils
import pytest

from test_atlas_backend.web import db_data

METRIC_ID = db_data.DEFAULT_TIME_DIMENSIONS[0]['metric_id']
SOURCE_ID = db_data.DEFAULT_TIME_DIMENSIONS[0]['source_id']
DIMENSION_ID = db_data.DEFAULT_TIME_DIMENSIONS[0]['dimension_id']
OTHER_DIMENSION_ID = tp.cast(int, db_data.DIMENSIONS[4]['dimension_id'])


async def get_instance(
        web_app_client: test_utils.TestClient,
) -> tp.Dict[str, tp.Any]:
    path = '/api/v3/metrics/instances'
    params = {'metric_id': METRIC_ID, 'source_id': SOURCE_ID}
    response = await web_app_client.get(path, params=params)
    assert response.status == 200, await response.text()
    return await response.json()


class TestSetDefaultTimeDimension:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            metric_id: int,
            source_id: int,
            dimension_id: int,
    ) -> test_utils.ClientResponse:
        path = '/api/v3/metric/instances/default_time_dimension'
        params = {
            'metric_id': metric_id,
            'source_id': source_id,
            'dimension_id': dimension_id,
        }
        return await web_app_client.post(path, params=params)

    @pytest.mark.parametrize('username', [None])
    async def test_set_without_login(
            self,
            web_app_client: test_utils.TestClient,
            username: tp.Optional[str],
    ) -> None:
        metric_id = METRIC_ID
        source_id = SOURCE_ID
        dimension_id = DIMENSION_ID
        path = '/api/v3/metric/instances/default_time_dimension'
        params = {
            'metric_id': metric_id,
            'source_id': source_id,
            'dimension_id': dimension_id,
        }
        response = await web_app_client.post(
            path, params=params, allow_redirects=False,
        )
        assert response.status == 302, await response.text()

    async def test_unknown_metric_source_and_dimension(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = METRIC_ID  # not exists
        source_id = SOURCE_ID  # not exists
        dimension_id = DIMENSION_ID  # not exists
        responce = await self.request(
            web_app_client, metric_id, source_id, dimension_id,
        )
        assert responce.status == 404, await responce.text()
        err = await responce.json()
        assert err['code'] == 'NotFound::UnknownMetricInstance'
        assert err['message'] == (
            f'Unknown metric instance with metric id {metric_id} and source '
            f'id {source_id}'
        )

    async def test_unknown_metric_and_source(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = METRIC_ID  # not exists
        source_id = SOURCE_ID  # not exists
        dimension_id = DIMENSION_ID
        responce = await self.request(
            web_app_client, metric_id, source_id, dimension_id,
        )
        assert responce.status == 404, await responce.text()
        err = await responce.json()
        assert err['code'] == 'NotFound::UnknownMetricInstance'
        assert err['message'] == (
            f'Unknown metric instance with metric id {metric_id} and source '
            f'id {source_id}'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_source.sql'],
    )
    async def test_unknown_metric_and_dimension(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = METRIC_ID  # not exists
        source_id = SOURCE_ID
        dimension_id = DIMENSION_ID  # not exists
        responce = await self.request(
            web_app_client, metric_id, source_id, dimension_id,
        )
        assert responce.status == 404, await responce.text()
        err = await responce.json()
        assert err['code'] == 'NotFound::UnknownMetricInstance'
        assert err['message'] == (
            f'Unknown metric instance with metric id {metric_id} and source '
            f'id {source_id}'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_metric_group.sql', 'pg_metric.sql'],
    )
    async def test_unknown_source_and_dimension(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = METRIC_ID
        source_id = SOURCE_ID  # not exists
        dimension_id = DIMENSION_ID  # not exists
        responce = await self.request(
            web_app_client, metric_id, source_id, dimension_id,
        )
        assert responce.status == 404, await responce.text()
        err = await responce.json()
        assert err['code'] == 'NotFound::UnknownMetricInstance'
        assert err['message'] == (
            f'Unknown metric instance with metric id {metric_id} and source '
            f'id {source_id}'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_dimension.sql',
            'pg_column.sql',
            'pg_col_dim_relation.sql',
        ],
    )
    async def test_unknown_metric(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = METRIC_ID  # not exists
        source_id = SOURCE_ID
        dimension_id = DIMENSION_ID
        responce = await self.request(
            web_app_client, metric_id, source_id, dimension_id,
        )
        assert responce.status == 404, await responce.text()
        err = await responce.json()
        assert err['code'] == 'NotFound::UnknownMetricInstance'
        assert err['message'] == (
            f'Unknown metric instance with metric id {metric_id} and source '
            f'id {source_id}'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_dimension.sql', 'pg_metric_group.sql', 'pg_metric.sql'],
    )
    async def test_unknown_source(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = METRIC_ID
        source_id = SOURCE_ID  # not exists
        dimension_id = DIMENSION_ID
        responce = await self.request(
            web_app_client, metric_id, source_id, dimension_id,
        )
        assert responce.status == 404, await responce.text()
        err = await responce.json()
        assert err['code'] == 'NotFound::UnknownMetricInstance'
        assert err['message'] == (
            f'Unknown metric instance with metric id {metric_id} and source '
            f'id {source_id}'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_column.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
        ],
    )
    async def test_unknown_dimension(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = METRIC_ID
        source_id = SOURCE_ID
        dimension_id = DIMENSION_ID  # not exists
        responce = await self.request(
            web_app_client, metric_id, source_id, dimension_id,
        )
        assert responce.status == 404, await responce.text()
        err = await responce.json()
        assert err['code'] == 'NonFound::UnknownSourceDimensinRelation'
        assert err['message'] == (
            f'Unknown source with id {source_id} or dimension with id '
            f'{dimension_id} or their relation'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_dimension.sql',
            'pg_column.sql',
            'pg_col_dim_relation.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
        ],
    )
    async def test_unknown_metric_instance(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = METRIC_ID
        source_id = SOURCE_ID
        dimension_id = DIMENSION_ID
        responce = await self.request(
            web_app_client, metric_id, source_id, dimension_id,
        )
        assert responce.status == 404, await responce.text()
        err = await responce.json()
        assert err['code'] == 'NotFound::UnknownMetricInstance'
        assert err['message'] == (
            f'Unknown metric instance with metric id {metric_id} and source '
            f'id {source_id}'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_dimension.sql',
            'pg_column.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
        ],
    )
    async def test_unknown_source_dimension_relation(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = METRIC_ID
        source_id = SOURCE_ID
        dimension_id = DIMENSION_ID
        responce = await self.request(
            web_app_client, metric_id, source_id, dimension_id,
        )
        assert responce.status == 404, await responce.text()
        err = await responce.json()
        assert err['code'] == 'NonFound::UnknownSourceDimensinRelation'
        assert err['message'] == (
            f'Unknown source with id {source_id} or dimension with id '
            f'{dimension_id} or their relation'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_dimension.sql',
            'pg_column.sql',
            'pg_col_dim_relation.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
        ],
    )
    async def test_create(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = METRIC_ID
        source_id = SOURCE_ID
        dimension_id = DIMENSION_ID
        responce = await self.request(
            web_app_client, metric_id, source_id, dimension_id,
        )
        assert responce.status == 201, await responce.text()
        instance = await get_instance(web_app_client)
        assert instance['default_time_dimension_id'] == dimension_id

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_dimension.sql',
            'pg_column.sql',
            'pg_col_dim_relation.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
            'pg_default_time_dimension.sql',
        ],
    )
    async def test_replace(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = METRIC_ID
        source_id = SOURCE_ID
        dimension_id = OTHER_DIMENSION_ID
        responce = await self.request(
            web_app_client, metric_id, source_id, dimension_id,
        )
        assert responce.status == 201, await responce.text()
        instance = await get_instance(web_app_client)
        assert instance['default_time_dimension_id'] == dimension_id


class TestDeleteDefaultTimeDimension:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            metric_id: int,
            source_id: int,
    ) -> test_utils.ClientResponse:
        path = '/api/v3/metric/instances/default_time_dimension'
        params = {'metric_id': metric_id, 'source_id': source_id}
        return await web_app_client.delete(path, params=params)

    @pytest.mark.parametrize('username', [None])
    async def test_delete_without_login(
            self,
            web_app_client: test_utils.TestClient,
            username: tp.Optional[str],
    ) -> None:
        metric_id = METRIC_ID
        source_id = SOURCE_ID
        path = '/api/v3/metric/instances/default_time_dimension'
        params = {'metric_id': metric_id, 'source_id': source_id}
        response = await web_app_client.delete(
            path, params=params, allow_redirects=False,
        )
        assert response.status == 302, await response.text()

    async def test_unknown_metric_source_and_dimension(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = METRIC_ID  # not exists
        source_id = SOURCE_ID  # not exists
        responce = await self.request(web_app_client, metric_id, source_id)
        assert responce.status == 204, await responce.text()

    async def test_unknown_metric_and_source(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = METRIC_ID  # not exists
        source_id = SOURCE_ID  # not exists
        responce = await self.request(web_app_client, metric_id, source_id)
        assert responce.status == 204, await responce.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_source.sql'],
    )
    async def test_unknown_metric_and_dimension(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = METRIC_ID  # not exists
        source_id = SOURCE_ID
        responce = await self.request(web_app_client, metric_id, source_id)
        assert responce.status == 204, await responce.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_metric_group.sql', 'pg_metric.sql'],
    )
    async def test_unknown_source_and_dimension(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = METRIC_ID
        source_id = SOURCE_ID  # not exists
        responce = await self.request(web_app_client, metric_id, source_id)
        assert responce.status == 204, await responce.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_dimension.sql',
            'pg_column.sql',
            'pg_col_dim_relation.sql',
        ],
    )
    async def test_unknown_metric(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = METRIC_ID  # not exists
        source_id = SOURCE_ID
        responce = await self.request(web_app_client, metric_id, source_id)
        assert responce.status == 204, await responce.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_dimension.sql', 'pg_metric_group.sql', 'pg_metric.sql'],
    )
    async def test_unknown_source(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = METRIC_ID
        source_id = SOURCE_ID  # not exists
        responce = await self.request(web_app_client, metric_id, source_id)
        assert responce.status == 204, await responce.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_column.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
        ],
    )
    async def test_unknown_dimension(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = METRIC_ID
        source_id = SOURCE_ID
        responce = await self.request(web_app_client, metric_id, source_id)
        assert responce.status == 204, await responce.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_dimension.sql',
            'pg_column.sql',
            'pg_col_dim_relation.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
        ],
    )
    async def test_unknown_metric_instance(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = METRIC_ID
        source_id = SOURCE_ID
        responce = await self.request(web_app_client, metric_id, source_id)
        assert responce.status == 204, await responce.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_dimension.sql',
            'pg_column.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
        ],
    )
    async def test_unknown_source_dimension_relation(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = METRIC_ID
        source_id = SOURCE_ID
        responce = await self.request(web_app_client, metric_id, source_id)
        assert responce.status == 204, await responce.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_dimension.sql',
            'pg_column.sql',
            'pg_col_dim_relation.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
        ],
    )
    async def test_unknown_default_time_dimension(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = METRIC_ID
        source_id = SOURCE_ID
        responce = await self.request(web_app_client, metric_id, source_id)
        assert responce.status == 204, await responce.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_dimension.sql',
            'pg_column.sql',
            'pg_col_dim_relation.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
            'pg_default_time_dimension.sql',
        ],
    )
    async def test_delete(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = METRIC_ID
        source_id = SOURCE_ID
        responce = await self.request(web_app_client, metric_id, source_id)
        assert responce.status == 204, await responce.text()
        instance = await get_instance(web_app_client)
        assert instance['default_time_dimension_id'] == 0
