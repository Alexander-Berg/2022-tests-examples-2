import asyncio
import typing as tp
import uuid

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

EXISTED_METRICS = db_data.METRICS
EXISTED_INSTANCES = db_data.INSTANCES
METRICS_AND_INSTANCES_FILES = [
    'pg_metric_group.sql',
    'pg_metric.sql',
    'pg_source.sql',
    'pg_column.sql',
    'pg_dimension.sql',
    'pg_col_dim_relation.sql',
    'pg_metric_instance.sql',
]
BUNCH_OF_ERRORS = [
    #   (metric_id, metric_data, instance_data, new_source_id, error),
    (500, None, None, None, 'NotFound::MetricNotExists'),
    (1, EXISTED_METRICS[2], None, None, 'BadRequest::MetricExists'),
    (1, {'group_id': 100500}, None, None, 'BadRequest::UnknownMetricGroup'),
    (1, None, None, 42, 'NotFound::UnknownSource'),
]


def compare_instances(instance1: dict, instance2: dict) -> None:
    assert {*instance1['filters']} == {*instance2['filters']}
    instance1 = instance1.copy()
    instance1.pop('filters')
    instance2 = instance2.copy()
    instance2.pop('filters')
    assert instance1 == instance2


async def get_metric(
        web_app_client: test_utils.TestClient, metric_id,
) -> tp.Dict[str, tp.Any]:
    response = await web_app_client.get(
        '/api/v3/metrics', params={'metric_id': metric_id},
    )
    assert response.status == 200, await response.text()
    return await response.json()


async def get_metrics(
        web_app_client: test_utils.TestClient,
) -> tp.List[tp.Dict[str, tp.Any]]:
    response = await web_app_client.get('/api/v3/metrics/list')
    assert response.status == 200, await response.text()
    return await response.json()


async def get_instances(
        web_app_client: test_utils.TestClient, metric_id: int,
) -> tp.List[tp.Dict[str, tp.Any]]:
    response = await web_app_client.get(
        '/api/v3/metrics/instances/list', params={'metric_id': metric_id},
    )
    assert response.status == 200, await response.text()
    return await response.json()


@pytest.fixture(scope='function')
async def check_nothing_added(web_app_client):
    metrics_before = await get_metrics(web_app_client)
    instances_before = await asyncio.gather(
        *[
            get_instances(web_app_client, m['metric_id'])
            for m in metrics_before
        ],
    )
    yield
    metrics_after = await get_metrics(web_app_client)
    instances_after = await asyncio.gather(
        *[
            get_instances(web_app_client, m['metric_id'])
            for m in metrics_after
        ],
    )
    assert metrics_after == metrics_before
    assert instances_after == instances_before


class TestCreateMetricWithInstance:
    url = '/api/v3/metric_with_instance/'
    default_metric_data = {
        'ru_name': 'Метрика3',
        'en_name': 'Metric3',
        'ru_description': 'Метрика',
        'en_description': 'Metric',
        'group_id': 1,
    }
    default_instance_data = {'expression': '1', 'filters': []}
    source_id = 3

    async def request(
            self,
            web_app_client: test_utils.TestClient,
            metric_data=None,
            instance_data=None,
            source_id=None,
            **kwargs,
    ):
        data = {
            'metric': metric_data or self.default_metric_data,
            'instance': instance_data or self.default_instance_data,
        }

        params = {'source_id': source_id or self.source_id}

        response = await web_app_client.post(
            self.url, json=data, params=params, **kwargs,
        )
        return response

    @pytest.mark.parametrize('username', [None])
    async def test_create_without_login(
            self,
            web_app_client: test_utils.TestClient,
            username: tp.Optional[str],
    ) -> None:
        response = await self.request(web_app_client, allow_redirects=False)
        assert response.status == 302, await response.text()

    # TODO создавать не тривиальный инстанс
    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_metric_group.sql',
            'pg_source.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
        ],
    )
    @pytest.mark.parametrize('ru_description', [None, 'Описание 1'])
    @pytest.mark.parametrize('en_description', [None, 'Описание 2'])
    @pytest.mark.parametrize('time_dimension_id', [0, 2])
    async def test_create(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            ru_description: tp.Optional[str],
            en_description: tp.Optional[str],
            time_dimension_id: int,
    ) -> None:
        metric_data = {
            'ru_name': f'Метрика {uuid.uuid4()}',
            'en_name': f'Metric {uuid.uuid4()}',
            'group_id': 1,
            **({'ru_description': ru_description} if ru_description else {}),
            **({'en_description': en_description} if en_description else {}),
        }
        inst_data: tp.Dict[str, tp.Any] = {**self.default_instance_data}
        if time_dimension_id:
            inst_data['default_time_dimension_id'] = time_dimension_id
        response = await self.request(web_app_client, metric_data, inst_data)

        assert response.status == 201, await response.text()

        [saved_metric] = await get_metrics(web_app_client)
        for key, value in metric_data.items():
            assert saved_metric[key] == value

        [inst] = await get_instances(web_app_client, saved_metric['metric_id'])
        assert inst['source_id'] == self.source_id
        for key, value in self.default_instance_data.items():
            assert inst[key] == value
        assert inst['default_time_dimension_id'] == time_dimension_id

    @pytest.mark.usefixtures('check_nothing_added')
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
    @pytest.mark.usefixtures('check_nothing_added')
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

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=['pg_metric_group.sql'],
    )
    @pytest.mark.usefixtures('atlas_blackbox_mock')
    @pytest.mark.usefixtures('check_nothing_added')
    async def test_unknown_source(
            self, web_app_client: test_utils.TestClient,
    ) -> None:
        source_id = 1  # not exists
        response = await self.request(web_app_client, source_id=source_id)
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::UnknownSource'
        assert err['message'] == f'Source with id {source_id} doesn\t exists'

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_metric_group.sql', 'pg_metric.sql', 'pg_source.sql'],
    )
    @pytest.mark.usefixtures('check_nothing_added')
    async def test_invalid_use_final(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        source_id = CHYT_SOURCE['source_id']
        use_final = True
        instance_data = {
            'expression': '1',
            'filters': [],
            'use_final': use_final,
        }
        response = await self.request(
            web_app_client, source_id=source_id, instance_data=instance_data,
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
        files=['pg_metric_group.sql', 'pg_source.sql'],
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
            web_app_client, source_id=source_id, instance_data=instance_data,
        )
        assert response.status == 201, await response.text()
        [instance] = await get_instances(web_app_client, metric_id)
        for key, value in instance_data.items():
            assert instance[key] == value, key


class TestUpdateMetricWithInstance:
    url = '/api/v3/metric_with_instance/'
    default_metric_data = {
        'ru_name': 'Новая_метрика',
        'en_name': 'New_metric',
        'ru_description': 'Метрика новая',
        'en_description': 'Metric_new',
        'group_id': 1,
    }
    default_instance_data = {
        'expression': 'some_expression',
        'filters': ['filter1', 'filter2'],
        'use_final': False,
    }
    source_id = 3

    async def request(
            self,
            web_app_client: test_utils.TestClient,
            metric_id,
            metric_data=None,
            instance_data=None,
            new_source_id=None,
            empty_body=False,
            **kwargs,
    ):
        data = (
            {
                'metric': metric_data or self.default_metric_data,
                'instance': instance_data or self.default_instance_data,
            }
            if not empty_body
            else {}
        )

        params = {
            **({'new_source_id': new_source_id} if new_source_id else {}),
            'metric_id': metric_id,
        }

        response = await web_app_client.patch(
            self.url, json=data, params=params, **kwargs,
        )
        return response

    @pytest.mark.parametrize('username', [None])
    async def test_update_without_login(
            self,
            web_app_client: test_utils.TestClient,
            username: tp.Optional[str],
    ) -> None:
        response = await self.request(web_app_client, 1, allow_redirects=False)
        assert response.status == 302, await response.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=METRICS_AND_INSTANCES_FILES,
    )
    @pytest.mark.usefixtures('atlas_blackbox_mock')
    @pytest.mark.parametrize('time_dimension_id', [0, 2])
    async def test_update(
            self,
            web_app_client: test_utils.TestClient,
            time_dimension_id: int,
    ):
        metric_id = 1
        old_metric = await get_metric(web_app_client, metric_id)
        [old_instance] = await get_instances(web_app_client, metric_id)

        inst_data = {**self.default_instance_data}
        if time_dimension_id:
            inst_data['default_time_dimension_id'] = time_dimension_id
        response = await self.request(
            web_app_client, metric_id=metric_id, instance_data=inst_data,
        )
        assert response.status == 204, await response.text()

        metric = await get_metric(web_app_client, metric_id)
        [instance] = await get_instances(web_app_client, metric_id)

        assert metric != old_metric
        assert instance != old_instance
        assert metric == {
            **self.default_metric_data,  # type: ignore
            'metric_id': metric_id,
        }
        assert instance == {
            'default_time_dimension_id': 0,
            **inst_data,  # type: ignore
            'metric_id': metric_id,
            'source_id': old_instance['source_id'],
        }

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=METRICS_AND_INSTANCES_FILES,
    )
    @pytest.mark.usefixtures('atlas_blackbox_mock')
    @pytest.mark.usefixtures('check_nothing_added')
    async def test_empty_query(self, web_app_client: test_utils.TestClient):
        metric_id = 1

        response = await self.request(
            web_app_client, metric_id, empty_body=True,
        )
        assert response.status == 204, await response.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=METRICS_AND_INSTANCES_FILES,
    )
    @pytest.mark.usefixtures('atlas_blackbox_mock')
    async def test_change_source_id(self, web_app_client):
        metric_id = 1
        new_source_id = 2
        [old_instance] = await get_instances(web_app_client, metric_id)
        assert old_instance['source_id'] != new_source_id

        response = await self.request(
            web_app_client,
            metric_id=metric_id,
            new_source_id=new_source_id,
            empty_body=True,
        )
        assert response.status == 204, await response.text()

        [instance] = await get_instances(web_app_client, metric_id)

        assert instance['source_id'] == new_source_id
        assert instance != old_instance
        del instance['source_id'], old_instance['source_id']
        assert instance == old_instance

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=METRICS_AND_INSTANCES_FILES,
    )
    @pytest.mark.usefixtures('check_nothing_added')
    @pytest.mark.usefixtures('atlas_blackbox_mock')
    async def test_change_to_unknown_source(self, web_app_client):
        metric_id = 1
        new_source_id = 10

        response = await self.request(
            web_app_client,
            metric_id=metric_id,
            new_source_id=new_source_id,
            empty_body=True,
        )

        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::UnknownSource'
        assert (
            err['message'] == f'Source with id {new_source_id} doesn\t exists'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=METRICS_AND_INSTANCES_FILES,
    )
    @pytest.mark.parametrize(
        'metric_id, metric_data, instance_data, new_source_id, err',
        BUNCH_OF_ERRORS,
    )
    @pytest.mark.usefixtures('atlas_blackbox_mock')
    @pytest.mark.usefixtures('check_nothing_added')
    async def test_nothing_changed_on_error(
            self,
            web_app_client,
            metric_id,
            metric_data,
            instance_data,
            new_source_id,
            err,
    ):
        response = await self.request(
            web_app_client,
            metric_id=metric_id,
            metric_data=metric_data,
            instance_data=instance_data,
            new_source_id=new_source_id,
        )

        assert response.status != 204
        error = await response.json()
        assert error['code'] == err


class TestGetMetricWithInstance:
    url = '/api/v3/metric_with_instance/'

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend', files=METRICS_AND_INSTANCES_FILES,
    )
    @pytest.mark.parametrize('metric', [metric for metric in EXISTED_METRICS])
    async def test_get(self, web_app_client, metric):
        response = await web_app_client.get(
            self.url, params={'metric_id': metric['metric_id']},
        )

        assert response.status == 200, await response.text()
        metric_instance_data = await response.json()

        assert metric_instance_data['metric'] == metric
        expected_inst = next(
            i
            for i in EXISTED_INSTANCES
            if i['metric_id'] == metric['metric_id']
        )
        compare_instances(metric_instance_data['instance'], expected_inst)

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_metric_group.sql', 'pg_metric.sql'],
    )
    @pytest.mark.parametrize(
        'metric_id', [metric['metric_id'] for metric in EXISTED_METRICS],
    )
    async def test_get_no_instance(
            self, web_app_client: test_utils.TestClient, metric_id,
    ):
        response = await web_app_client.get(
            self.url, params={'metric_id': metric_id},
        )

        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::NoMetricInstance'

    async def test_get_not_existed(
            self, web_app_client: test_utils.TestClient,
    ):
        metric_id = 1
        response = await web_app_client.get(
            self.url, params={'metric_id': metric_id},
        )

        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::MetricNotExists'
        assert err['message'] == f'There is not metric with id {metric_id}'
