import typing as tp

from aiohttp import test_utils
import pytest

from test_atlas_backend.web import db_data

EXISTED_METRICS = db_data.METRICS
EXISTED_INSTANCES = db_data.INSTANCES


async def get_instance(
        web_app_client: test_utils.TestClient, metric_id: int, source_id: int,
) -> tp.Dict[str, tp.Any]:
    path = '/api/v3/metrics/instances'
    params = {'metric_id': metric_id, 'source_id': source_id}
    response = await web_app_client.get(path, params=params)
    assert response.status == 200, await response.text()
    return await response.json()


class TestGetMetricInstance:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            metric_id: int,
            source_id: int,
    ) -> test_utils.ClientResponse:
        path = '/api/v3/metrics/instances'
        params = {'metric_id': metric_id, 'source_id': source_id}
        return await web_app_client.get(path, params=params)

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_source.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
            'pg_metric_instance.sql',
        ],
    )
    @pytest.mark.parametrize(
        'metric_id,source_id',
        [
            (EXISTED_METRICS[0]['metric_id'], 2),  # нет инстанса
            (1000000, 2),  # нет метрики
            (EXISTED_METRICS[0]['metric_id'], 1000000),  # нет источника
            (1000000, 1000000),  # нет метрики и источника
        ],
    )
    async def test_get_unknown_instance(
            self,
            web_app_client: test_utils.TestClient,
            metric_id: int,
            source_id: int,
    ) -> None:
        response = await self.request(web_app_client, metric_id, source_id)
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::MetricInstanceNotExists'
        assert err['message'] == (
            f'There is not metric instance with metric id '
            f'{metric_id} and source id {source_id}'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_source.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
            'pg_metric_instance.sql',
        ],
    )
    @pytest.mark.parametrize('instance', [EXISTED_INSTANCES[0]])
    async def test_get(
            self,
            web_app_client: test_utils.TestClient,
            instance: tp.Dict[str, tp.Any],
    ) -> None:
        metric_id = instance['metric_id']
        source_id = instance['source_id']
        response = await self.request(web_app_client, metric_id, source_id)
        assert response.status == 200, await response.text()
        metric_instance = await response.json()
        assert metric_instance == instance


class TestGetMetricInstances:
    async def request(
            self, web_app_client: test_utils.TestClient, metric_id: int,
    ) -> test_utils.ClientResponse:
        path = '/api/v3/metrics/instances/list'
        params = {'metric_id': metric_id}
        return await web_app_client.get(path, params=params)

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_metric_group.sql', 'pg_metric.sql'],
    )
    @pytest.mark.parametrize(
        'metric_id', [EXISTED_METRICS[0]['metric_id'], 1000000],
    )
    async def test_get_unknown_instance(
            self, web_app_client: test_utils.TestClient, metric_id: int,
    ) -> None:
        response = await self.request(web_app_client, metric_id)
        assert response.status == 200, await response.text()
        metric_instances = await response.json()
        assert not metric_instances

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_source.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
            'pg_metric_instance.sql',
        ],
    )
    @pytest.mark.parametrize('instance', [EXISTED_INSTANCES[0]])
    async def test_get(
            self,
            web_app_client: test_utils.TestClient,
            instance: tp.Dict[str, tp.Any],
    ) -> None:
        metric_id = instance['metric_id']
        response = await self.request(web_app_client, metric_id)
        assert response.status == 200, await response.text()
        metric_instances = await response.json()
        assert metric_instances == [instance]


@pytest.mark.skip(
    reason='post for /api/v3/metrics/instances temporarily deleted',
)
class TestCreateMetricInstance:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            metric_id: int,
            source_id: int,
            instance_data: tp.Dict[str, tp.Any],
    ) -> test_utils.ClientResponse:
        path = '/api/v3/metrics/instances'
        params = {'metric_id': metric_id, 'source_id': source_id}
        return await web_app_client.post(
            path, params=params, json=instance_data,
        )

    @pytest.mark.parametrize('username', [None])
    async def test_create_without_login(
            self,
            web_app_client: test_utils.TestClient,
            username: tp.Optional[str],
    ) -> None:
        metric_id = 1
        source_id = 1
        instance_data = {'expression': '1', 'filters': []}
        path = '/api/v3/metrics/instances'
        params = {'metric_id': metric_id, 'source_id': source_id}
        response = await web_app_client.post(
            path, params=params, json=instance_data, allow_redirects=False,
        )
        assert response.status == 302, await response.text()

    async def test_unknown_metric_and_source(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = 1  # not exists
        source_id = 1  # not exists
        instance_data = {'expression': '1', 'filters': []}
        response = await self.request(
            web_app_client, metric_id, source_id, instance_data,
        )
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] in (
            'NotFound::UnknownMetric',
            'NotFound::UnknownSource',
        )
        assert err['message'] in (
            f'Metric with id {metric_id} doesn\t exists',
            f'Source with id {source_id} doesn\t exists',
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
        ],
    )
    async def test_unknown_metric(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = 1  # not exists
        source_id = 1
        instance_data = {'expression': '1', 'filters': []}
        response = await self.request(
            web_app_client, metric_id, source_id, instance_data,
        )
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::UnknownMetric'
        assert err['message'] == f'Metric with id {metric_id} doesn\t exists'

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_metric_group.sql', 'pg_metric.sql'],
    )
    async def test_unknown_source(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = 1
        source_id = 1  # not exists
        instance_data = {'expression': '1', 'filters': []}
        response = await self.request(
            web_app_client, metric_id, source_id, instance_data,
        )
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::UnknownSource'
        assert err['message'] == f'Source with id {source_id} doesn\t exists'

    # TODO создавать не тривиальный инстанс
    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_source.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
        ],
    )
    async def test_create(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = 1
        source_id = 1
        instance_data = {'expression': '1', 'filters': []}
        response = await self.request(
            web_app_client, metric_id, source_id, instance_data,
        )
        assert response.status == 201, await response.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_source.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
            'pg_metric_instance.sql',
        ],
    )
    @pytest.mark.parametrize('instance', [EXISTED_INSTANCES[0]])
    async def test_metric_source_conflict(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            instance: tp.Dict[str, tp.Any],
    ) -> None:
        metric_id = instance['metric_id']
        source_id = instance['source_id']
        instance_data = {'expression': '1', 'filters': []}
        response = await self.request(
            web_app_client, metric_id, source_id, instance_data,
        )
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::MetricInstanceExists'
        assert err['message'] == (
            f'Metric instance for metric with id {metric_id} and source with '
            f'id {source_id} already exists'
        )

    # временный тест, пока в базе есть ограничение на один инстанс на метрику
    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_source.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
            'pg_metric_instance.sql',
        ],
    )
    @pytest.mark.parametrize('instance', [EXISTED_INSTANCES[0]])
    async def test_metric_conflict(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            instance: tp.Dict[str, tp.Any],
    ) -> None:
        metric_id = instance['metric_id']
        source_id = 1 if instance['source_id'] != 1 else 2
        instance_data = {'expression': '1', 'filters': []}
        response = await self.request(
            web_app_client, metric_id, source_id, instance_data,
        )
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::MetricInstanceExists'
        assert (
            err['message']
            == f'Metric with id {metric_id} has already instance'
        )


class TestUpdateMetricInstance:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            metric_id: int,
            source_id: int,
            instance_data: tp.Dict[str, tp.Any],
    ) -> test_utils.ClientResponse:
        path = '/api/v3/metrics/instances'
        params = {'metric_id': metric_id, 'source_id': source_id}
        return await web_app_client.patch(
            path, params=params, json=instance_data,
        )

    @pytest.mark.parametrize('username', [None])
    async def test_create_without_login(
            self,
            web_app_client: test_utils.TestClient,
            username: tp.Optional[str],
    ) -> None:
        metric_id = 1
        source_id = 1
        instance_data = {'expression': '1'}
        path = '/api/v3/metrics/instances'
        params = {'metric_id': metric_id, 'source_id': source_id}
        response = await web_app_client.patch(
            path, params=params, json=instance_data, allow_redirects=False,
        )
        assert response.status == 302, await response.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_source.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
        ],
    )
    @pytest.mark.parametrize('metric_id', [1, 1000000])
    @pytest.mark.parametrize('source_id', [1, 1000000])
    async def test_update_unknown_instance(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            metric_id: int,
            source_id: int,
    ) -> None:
        response = await self.request(web_app_client, metric_id, source_id, {})
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::MetricInstanceNotExists'
        assert err['message'] == (
            'There is not metric instance with metric id '
            f'{metric_id} and source id {source_id}'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_source.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
            'pg_metric_instance.sql',
        ],
    )
    @pytest.mark.parametrize('existed_instance', [EXISTED_INSTANCES[0]])
    @pytest.mark.parametrize(
        'expression', [None, 'MAX({record_id})', 'MIN({record_id})'],
    )
    @pytest.mark.parametrize(
        'filters',
        [
            None,
            ['{record_id} > 100'],
            ['intDiv({record_id}, 2) == 1', '{record_id} > 100'],
        ],
    )
    async def test_update(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            existed_instance: tp.Dict[str, tp.Any],
            expression: tp.Any,
            filters: tp.Any,
    ) -> None:
        metric_id = existed_instance['metric_id']
        source_id = existed_instance['source_id']
        instance_data = {}
        if expression is not None:
            instance_data['expression'] = expression
        if filters is not None:
            instance_data['filters'] = filters
        responce = await self.request(
            web_app_client, metric_id, source_id, instance_data,
        )
        assert responce.status == 204, await responce.text()
        instance = await get_instance(web_app_client, metric_id, source_id)
        for key, value in instance_data.items():
            if key == 'filters':
                assert sorted(instance[key]) == sorted(value)
            else:
                assert instance[key] == value


@pytest.mark.skip(
    reason='delete for /api/v3/metrics/instances temporarily deleted',
)
class TestDeleteMetricInstance:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            metric_id: int,
            source_id: int,
    ) -> test_utils.ClientResponse:
        path = '/api/v3/metrics/instances'
        params = {'metric_id': metric_id, 'source_id': source_id}
        return await web_app_client.delete(path, params=params)

    @pytest.mark.parametrize('username', [None])
    async def test_delete_without_login(
            self,
            web_app_client: test_utils.TestClient,
            username: tp.Optional[str],
    ) -> None:
        metric_id = 1
        source_id = 1
        path = '/api/v3/metrics/instances'
        params = {'metric_id': metric_id, 'source_id': source_id}
        response = await web_app_client.delete(
            path, params=params, allow_redirects=False,
        )
        assert response.status == 302, await response.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_source.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
            'pg_metric_instance.sql',
        ],
    )
    @pytest.mark.parametrize(
        'metric_id,source_id',
        [
            (EXISTED_METRICS[0]['metric_id'], 2),  # нет инстанса
            (1000000, 2),  # нет метрики
            (EXISTED_METRICS[0]['metric_id'], 1000000),  # нет источника
            (1000000, 1000000),  # нет метрики и источника
        ],
    )
    async def test_delete_unknown_instance(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            metric_id: int,
            source_id: int,
    ) -> None:
        response = await self.request(web_app_client, metric_id, source_id)
        assert response.status == 204, await response.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_source.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
            'pg_metric_instance.sql',
        ],
    )
    @pytest.mark.parametrize('instance', [EXISTED_INSTANCES[0]])
    async def test_delete(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            instance: tp.Dict[str, tp.Any],
    ) -> None:
        metric_id = instance['metric_id']
        source_id = instance['source_id']
        response = await self.request(web_app_client, metric_id, source_id)
        assert response.status == 204, await response.text()
