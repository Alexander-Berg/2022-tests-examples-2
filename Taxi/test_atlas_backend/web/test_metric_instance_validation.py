import typing as tp

from aiohttp import test_utils
import pytest

from test_atlas_backend.web import db_data


CHYT_SOURCES = [
    source for source in db_data.SOURCES if source['source_type'] == 'chyt'
]
CLICKHOUSE_SOURCES = [
    source
    for source in db_data.SOURCES
    if source['source_type'] == 'clickhouse'
]
CHYT_SOURCE = CHYT_SOURCES[0]
CLICKHOUSE_SOURCE = CLICKHOUSE_SOURCES[0]
INSTANCE_WITH_CHYT_SOURCE = next(
    instance
    for instance in db_data.INSTANCES
    if instance['source_id']
    in {source['source_id'] for source in CHYT_SOURCES}
)
INSTANCE_WITH_CLICKHOUSE_SOURCE = next(
    instance
    for instance in db_data.INSTANCES
    if instance['source_id']
    in {source['source_id'] for source in CLICKHOUSE_SOURCES}
)


async def get_instance(
        web_app_client: test_utils.TestClient, metric_id: int, source_id: int,
) -> tp.Dict[str, tp.Any]:
    path = '/api/v3/metrics/instances'
    params = {'metric_id': metric_id, 'source_id': source_id}
    response = await web_app_client.get(path, params=params)
    assert response.status == 200, await response.text()
    return await response.json()


@pytest.mark.skip(
    reason='delete for /api/v3/metrics/instances temporarily deleted',
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

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_metric_group.sql', 'pg_metric.sql', 'pg_source.sql'],
    )
    async def test_invalid_use_final(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = 1
        source_id = CHYT_SOURCE['source_id']
        use_final = True
        instance_data = {
            'expression': '1',
            'filters': [],
            'use_final': use_final,
        }
        response = await self.request(
            web_app_client, metric_id, source_id, instance_data,
        )
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::SourceDoesNotSupportFinalClause'
        assert err['message'] == (
            f'Source {CHYT_SOURCE["source_name"]} of type '
            f'{CHYT_SOURCE["source_type"]} does not support final clause'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_metric_group.sql', 'pg_metric.sql', 'pg_source.sql'],
    )
    @pytest.mark.parametrize(
        'source_id, use_final',
        [
            (CHYT_SOURCE['source_id'], False),
            (CLICKHOUSE_SOURCE['source_id'], True),
            (CLICKHOUSE_SOURCE['source_id'], False),
        ],
    )
    async def test_valid_use_final(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            source_id: int,
            use_final: bool,
    ) -> None:
        metric_id = 1
        instance_data = {
            'expression': '1',
            'filters': [],
            'use_final': use_final,
        }
        response = await self.request(
            web_app_client, metric_id, source_id, instance_data,
        )
        assert response.status == 201, await response.text()
        instance = await get_instance(web_app_client, metric_id, source_id)
        for key, value in instance_data.items():
            assert instance[key] == value, key


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

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_source.sql',
            'pg_metric_instance.sql',
        ],
    )
    async def test_invalid_use_final(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = INSTANCE_WITH_CHYT_SOURCE['metric_id']
        source_id = INSTANCE_WITH_CHYT_SOURCE['source_id']
        use_final = True
        instance_data = {'use_final': use_final}
        response = await self.request(
            web_app_client, metric_id, source_id, instance_data,
        )
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::SourceDoesNotSupportFinalClause'
        assert err['message'] == (
            f'Source {CHYT_SOURCE["source_name"]} of type '
            f'{CHYT_SOURCE["source_type"]} does not support final clause'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_source.sql',
            'pg_metric_instance.sql',
        ],
    )
    @pytest.mark.parametrize(
        'existed_instance, use_final',
        [
            (INSTANCE_WITH_CHYT_SOURCE, False),
            (INSTANCE_WITH_CLICKHOUSE_SOURCE, True),
            (INSTANCE_WITH_CLICKHOUSE_SOURCE, False),
        ],
    )
    async def test_valid_use_final(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            existed_instance: tp.Dict[str, tp.Any],
            use_final: bool,
    ) -> None:
        metric_id = existed_instance['metric_id']
        source_id = existed_instance['source_id']
        instance_data = {'use_final': use_final}
        response = await self.request(
            web_app_client, metric_id, source_id, instance_data,
        )
        assert response.status == 204, await response.text()
        instance = await get_instance(web_app_client, metric_id, source_id)
        instance_data = {**existed_instance, **instance_data}
        for key, value in instance_data.items():
            assert instance[key] == value, key
