import typing as tp
import uuid

from aiohttp import test_utils
import pytest

from test_atlas_backend.web import db_data

EXISTED_METRICS = db_data.METRICS


async def delete_metric(
        web_app_client: test_utils.TestClient, metric_id: int,
) -> None:
    # in case passport error, make sure that you use atlas_blackbox_mock
    params = {'metric_id': metric_id}
    response = await web_app_client.delete('/api/v3/metrics', params=params)
    assert response.status == 204, await response.text()


async def get_metric(
        web_app_client: test_utils.TestClient, metric_id: int,
) -> tp.Dict[str, tp.Any]:
    params = {'metric_id': metric_id}
    response = await web_app_client.get('/api/v3/metrics', params=params)
    assert response.status == 200, await response.text()
    return await response.json()


async def get_metrics(
        web_app_client: test_utils.TestClient,
) -> tp.List[tp.Dict[str, tp.Any]]:
    response = await web_app_client.get('/api/v3/metrics/list')
    assert response.status == 200, await response.text()
    return await response.json()


class _NewMetricsGetter:
    def __init__(self, web_app_client: test_utils.TestClient) -> None:
        self._web_app_client = web_app_client
        self.existed_metric_ids: tp.Set[int] = set()
        self.new_metrics: tp.List[tp.Dict[str, tp.Any]] = []

    async def __aenter__(self):
        self.existed_metric_ids = {
            metric['metric_id']
            for metric in await get_metrics(self._web_app_client)
        }
        return self

    async def __aexit__(self, *args, **kwargs):
        self.new_metrics = [
            metric
            for metric in await get_metrics(self._web_app_client)
            if metric['metric_id'] not in self.existed_metric_ids
        ]


class TestGetMetric:
    async def request(
            self, web_app_client: test_utils.TestClient, metric_id: int,
    ) -> test_utils.ClientResponse:
        path = '/api/v3/metrics'
        params = {'metric_id': metric_id}
        return await web_app_client.get(path, params=params)

    async def test_get_not_existed_metric(
            self, web_app_client: test_utils.TestClient,
    ) -> None:
        metric_id = 1  # not exists
        response = await self.request(web_app_client, metric_id)
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::MetricNotExists'
        assert err['message'] == f'There is not metric with id {metric_id}'

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_metric_group.sql', 'pg_metric.sql'],
    )
    @pytest.mark.parametrize('metric', [metric for metric in EXISTED_METRICS])
    async def test_get(
            self,
            web_app_client: test_utils.TestClient,
            metric: tp.Dict[str, tp.Any],
    ) -> None:
        response = await self.request(web_app_client, metric['metric_id'])
        assert response.status == 200, await response.text()
        group_data = await response.json()
        assert group_data == metric


class TestGetMetrics:
    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_metric_group.sql', 'pg_metric.sql'],
    )
    async def test_get_list(
            self, web_app_client: test_utils.TestClient,
    ) -> None:
        response = await web_app_client.get('/api/v3/metrics/list')
        assert response.status == 200, await response.text()
        metrics = await response.json()
        assert len(metrics) == len(EXISTED_METRICS)
        metrics.sort(key=lambda metric: metric['metric_id'])
        assert metrics == sorted(
            EXISTED_METRICS, key=lambda metric: metric['metric_id'],
        )


@pytest.mark.skip(reason='post for /api/v3/metrics temporarily deleted')
class TestCreateMetric:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            metric_data: tp.Dict[str, tp.Any],
    ) -> test_utils.ClientResponse:
        path = '/api/v3/metrics'
        return await web_app_client.post(path, json=metric_data)

    @pytest.mark.parametrize('username', [None])
    async def test_create_without_login(
            self,
            web_app_client: test_utils.TestClient,
            username: tp.Optional[str],
    ) -> None:
        metric_data = {
            'ru_name': 'Метрика3',
            'en_name': 'Metric3',
            'ru_description': 'Метрика',
            'en_description': 'Metric',
            'group_id': 1,
        }
        path = '/api/v3/metrics'
        response = await web_app_client.post(
            path, json=metric_data, allow_redirects=False,
        )
        assert response.status == 302, await response.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_metric_group.sql'],
    )
    @pytest.mark.parametrize('ru_description', [None, 'Описание 1'])
    @pytest.mark.parametrize('en_description', [None, 'Описание 2'])
    async def test_create_metric(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            ru_description: tp.Optional[str],
            en_description: tp.Optional[str],
    ) -> None:
        metric_data = {
            'ru_name': f'Метрика {uuid.uuid4()}',
            'en_name': f'Metric {uuid.uuid4()}',
            'group_id': 1,
        }
        if ru_description is not None:
            metric_data['ru_description'] = ru_description
        if en_description is not None:
            metric_data['en_description'] = en_description
        async with _NewMetricsGetter(web_app_client) as helper:
            response = await self.request(web_app_client, metric_data)
            assert response.status == 201, await response.text()
        (metric,) = helper.new_metrics
        for key, value in metric_data.items():
            assert metric[key] == value
        await delete_metric(web_app_client, metric['metric_id'])

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_metric_group.sql', 'pg_metric.sql'],
    )
    @pytest.mark.parametrize(
        'ru_name', [EXISTED_METRICS[0]['ru_name'], 'МетрикаN'],
    )
    @pytest.mark.parametrize(
        'en_name', [EXISTED_METRICS[1]['en_name'], 'MetricN'],
    )
    async def test_name_conflict(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            ru_name: str,
            en_name: str,
    ) -> None:
        if ru_name == 'МетрикаN' and en_name == 'MetricN':
            # TODO здесь бы скипать тесты, но пока что при этом валятся ошибки
            return
        metric_data = {'ru_name': ru_name, 'en_name': en_name, 'group_id': 1}
        response = await self.request(web_app_client, metric_data)
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::MetricExists'
        ru_err = f'Metric with ru name {ru_name} already exists'
        en_err = f'Metric with en name {en_name} already exists'
        if ru_name == 'МетрикиN':
            assert err['message'] == en_err
        elif en_name == 'MetricsN':
            assert err['message'] == ru_err
        else:
            assert err['message'] in (en_err, ru_err)

    async def test_not_existed_group(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        group_id = 1
        metric_data = {
            'ru_name': 'МетрикаN',
            'en_name': 'MetricN',
            'group_id': group_id,
        }
        response = await self.request(web_app_client, metric_data)
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::UnknownMetricGroup'
        assert (
            err['message'] == f'There is not metric group with id {group_id}'
        )


class TestUpdateMetric:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            metric_id: int,
            metric_data: tp.Dict[str, tp.Any],
    ) -> test_utils.ClientResponse:
        path = '/api/v3/metrics'
        params = {'metric_id': metric_id}
        return await web_app_client.patch(
            path, params=params, json=metric_data,
        )

    @pytest.mark.parametrize('username', [None])
    async def test_update_without_login(
            self,
            web_app_client: test_utils.TestClient,
            username: tp.Optional[str],
    ) -> None:
        metric_id = 1
        path = '/api/v3/metrics'
        params = {'metric_id': metric_id}
        response = await web_app_client.patch(
            path, params=params, json={}, allow_redirects=False,
        )
        assert response.status == 302, await response.text()

    async def test_update_not_existed_metric(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = 1  # not exists
        response = await self.request(web_app_client, metric_id, {})
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::MetricNotExists'
        assert err['message'] == f'There is not metric with id {metric_id}'

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_metric_group.sql', 'pg_metric.sql'],
    )
    @pytest.mark.parametrize('existed_metric', [EXISTED_METRICS[0]])
    @pytest.mark.parametrize('ru_name', [None, 'Метрика3'])
    @pytest.mark.parametrize('en_name', [None, 'Metric'])
    @pytest.mark.parametrize('ru_description', [None, 'Обновленная метрика'])
    @pytest.mark.parametrize('en_description', [None, 'Updated metric'])
    @pytest.mark.parametrize('group_id', [None, 2])
    async def test_update_metric(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            existed_metric: tp.Dict[str, tp.Any],
            ru_name: tp.Optional[str],
            en_name: tp.Optional[str],
            ru_description: tp.Optional[str],
            en_description: tp.Optional[str],
            group_id: tp.Optional[int],
    ) -> None:
        metric_data: tp.Dict[str, tp.Any] = {}
        if ru_name is not None:
            metric_data['ru_name'] = ru_name
        if en_name is not None:
            metric_data['en_name'] = en_name
        if ru_description is not None:
            metric_data['ru_description'] = ru_description
        if en_description is not None:
            metric_data['en_description'] = en_description
        if group_id is not None:
            metric_data['group_id'] = group_id
        response = await self.request(
            web_app_client, existed_metric['metric_id'], metric_data,
        )
        assert response.status == 204, await response.text()
        metric = await get_metric(web_app_client, existed_metric['metric_id'])
        for key, value in metric.items():
            if key in metric_data:
                assert metric_data[key] == value
            else:
                assert existed_metric[key] == value

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_metric_group.sql', 'pg_metric.sql'],
    )
    @pytest.mark.parametrize('existed_metric', [EXISTED_METRICS[0]])
    @pytest.mark.parametrize('ru_name', [None, EXISTED_METRICS[1]['ru_name']])
    @pytest.mark.parametrize('en_name', [None, EXISTED_METRICS[1]['en_name']])
    @pytest.mark.parametrize(
        'ru_description', [None, 'Обновленная группа с метриками'],
    )
    @pytest.mark.parametrize('en_description', [None, 'Updated metric'])
    @pytest.mark.parametrize('group_id', [None, 2])
    async def test_name_conflict(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            existed_metric: tp.Dict[str, tp.Any],
            ru_name: tp.Optional[str],
            en_name: tp.Optional[str],
            ru_description: tp.Optional[str],
            en_description: tp.Optional[str],
            group_id: tp.Optional[int],
    ) -> None:
        if ru_name is None and en_name is None:
            # TODO здесь бы скипать тесты, но пока что при этом валятся ошибки
            return
        metric_data: tp.Dict[str, tp.Any] = {}
        if ru_name is not None:
            metric_data['ru_name'] = ru_name
        if en_name is not None:
            metric_data['en_name'] = en_name
        if ru_description is not None:
            metric_data['ru_description'] = ru_description
        if en_description is not None:
            metric_data['en_description'] = en_description
        if group_id is not None:
            metric_data['group_id'] = group_id
        response = await self.request(
            web_app_client, existed_metric['group_id'], metric_data,
        )
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::MetricExists'
        ru_err = f'Metric with ru name {ru_name} already exists'
        en_err = f'Metric with en name {en_name} already exists'
        if ru_name is None:
            assert err['message'] == en_err
        elif en_name is None:
            assert err['message'] == ru_err
        else:
            assert err['message'] in (en_err, ru_err)

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_metric_group.sql', 'pg_metric.sql'],
    )
    async def test_move_to_not_existed_group(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        group_id = 3
        metric_id = 1
        metric_data = {
            'ru_name': 'МетрикаN',
            'en_name': 'MetricN',
            'group_id': group_id,
        }
        response = await self.request(web_app_client, metric_id, metric_data)
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::UnknownMetricGroup'
        assert (
            err['message'] == f'There is not metric group with id {group_id}'
        )


class TestDeleteMetric:
    async def request(
            self, web_app_client: test_utils.TestClient, metric_id: int,
    ) -> test_utils.ClientResponse:
        path = '/api/v3/metrics'
        params = {'metric_id': metric_id}
        return await web_app_client.delete(path, params=params)

    @pytest.mark.parametrize('username', [None])
    async def test_delete_without_login(
            self,
            web_app_client: test_utils.TestClient,
            username: tp.Optional[str],
    ) -> None:
        metric_id = 1
        path = '/api/v3/metrics'
        params = {'metric_id': metric_id}
        response = await web_app_client.delete(
            path, params=params, allow_redirects=False,
        )
        assert response.status == 302, await response.text()

    async def test_delete_not_existed_metric(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = 1  # not exists
        response = await self.request(web_app_client, metric_id)
        assert response.status == 204, await response.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_metric_group.sql', 'pg_metric.sql'],
    )
    @pytest.mark.parametrize(
        'metric_id', [metric['metric_id'] for metric in EXISTED_METRICS],
    )
    async def test_delete(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            metric_id: int,
    ) -> None:
        response = await self.request(web_app_client, metric_id)
        assert response.status == 204, await response.text()
        response = await web_app_client.get(
            '/api/v3/metrics', params={'metric_id': metric_id},
        )
        assert response.status == 404, await response.text()
