# pylint: disable=too-many-lines
import copy
import datetime
import itertools
import random
import typing as tp

from aiohttp import test_utils
import pytest

from test_atlas_backend.web import db_data

CURRENT_DELIVERY_SETTINGS = db_data.DELIVERY_SETTINGS[0]
CURRENT_DELIVERY_DIMENSION_IDS = [
    rel['dimension_id']
    for rel in db_data.SOLOMON_METRIC_DIMENSION
    if rel['delivery_id'] == CURRENT_DELIVERY_SETTINGS['delivery_id']
]
CURRENT_DELIVERY_DIMENSIONS = [
    dim
    for dim in db_data.DIMENSIONS
    if dim['dimension_id'] in CURRENT_DELIVERY_DIMENSION_IDS
]


def get_current_delivery_by_id(delivery_id: int) -> dict:
    settings = next(
        settings
        for settings in db_data.DELIVERY_SETTINGS
        if settings['delivery_id'] == delivery_id
    )
    dimension_ids = [
        dim['dimension_id']
        for dim in db_data.SOLOMON_METRIC_DIMENSION
        if dim['delivery_id'] == delivery_id
    ]
    dimensions = [
        dim
        for dim in db_data.DIMENSIONS
        if dim['dimension_id'] in dimension_ids
    ]
    dimensions.sort(key=lambda dim: dim['dimension_id'])
    return {'settings': settings, 'dimensions': dimensions}


def get_current_deliveries(
        count: tp.Optional[int] = None, offset: tp.Optional[int] = None,
) -> dict:
    if count is None:
        count = 10  # default value in api
    if offset is None:
        offset = 0  # default value in api
    delivery_ids = [
        delivery['delivery_id'] for delivery in db_data.DELIVERY_SETTINGS
    ]
    delivery_ids.sort()
    deliveries: tp.List[dict] = []
    for delivery_id in delivery_ids[offset : offset + count]:
        deliveries.append(get_current_delivery_by_id(delivery_id))
    return {'deliveries': deliveries, 'total': len(db_data.DELIVERY_SETTINGS)}


Patch = tp.Callable[[str], tp.Callable[[tp.Callable], tp.Callable]]


async def get_deliveries(web_app_client: test_utils.TestClient) -> dict:
    params = {'count': 1000}
    response = await web_app_client.get(
        '/api/v3/solomon/deliveries/list', params=params,
    )
    assert response.status == 200, await response.text()
    return await response.json()


async def get_delivery(
        web_app_client: test_utils.TestClient, delivery_id: int,
) -> dict:
    params = {'delivery_id': delivery_id}
    response = await web_app_client.get(
        '/api/v3/solomon/deliveries', params=params,
    )
    assert response.status == 200, await response.text()
    return await response.json()


class _NewDeliveriesGetter:
    def __init__(self, web_app_client: test_utils.TestClient) -> None:
        self._web_app_client = web_app_client
        self.existed_deliveries_ids: tp.Set[int] = set()
        self.new_deliveries: tp.List[dict] = []

    async def __aenter__(self):
        deliveries = (await get_deliveries(self._web_app_client))['deliveries']
        self.existed_deliveries_ids = {
            delivery['settings']['delivery_id'] for delivery in deliveries
        }
        return self

    async def __aexit__(self, *args, **kwargs):
        deliveries = (await get_deliveries(self._web_app_client))['deliveries']
        self.new_deliveries = [
            delivery
            for delivery in deliveries
            if delivery['settings']['delivery_id']
            not in self.existed_deliveries_ids
        ]


def compare_deliveries(delivery1: dict, delivery2: dict) -> None:
    delivery1 = copy.deepcopy(delivery1)
    settings1 = delivery1['settings']
    settings1.pop('delivery_id', None)
    settings1.pop('sensor', None)
    settings1.pop('source_id', None)

    delivery2 = copy.deepcopy(delivery2)
    settings2 = delivery2['settings']
    settings2.pop('delivery_id', None)
    settings2.pop('sensor', None)
    settings2.pop('source_id', None)

    assert settings1 == settings2
    if 'dimension_ids' in delivery1:
        dimension_ids1 = sorted(delivery1['dimension_ids'])
    else:
        dimension_ids1 = sorted(
            [dim['dimension_id'] for dim in delivery1['dimensions']],
        )
    if 'dimension_ids' in delivery2:
        dimension_ids2 = sorted(delivery2['dimension_ids'])
    else:
        dimension_ids2 = sorted(
            [dim['dimension_id'] for dim in delivery2['dimensions']],
        )
    assert dimension_ids1 == dimension_ids2


def compare_delivery_lists(deliveries1: dict, deliveries2: dict) -> None:
    assert deliveries1['total'] == deliveries2['total']
    assert len(deliveries1['deliveries']) == len(deliveries2['deliveries'])
    if not deliveries1['deliveries']:
        return
    delivery_list1 = copy.deepcopy(deliveries1['deliveries'])
    delivery_list2 = copy.deepcopy(deliveries2['deliveries'])
    delivery_list1.sort(
        key=lambda delivery: delivery['settings']['delivery_id'],
    )
    delivery_list2.sort(
        key=lambda delivery: delivery['settings']['delivery_id'],
    )
    for delivery1, delivery2 in zip(delivery_list1, delivery_list2):
        compare_deliveries(delivery1, delivery2)


class TestGetDelivery:
    async def request(
            self, web_app_client: test_utils.TestClient, delivery_id: int,
    ) -> test_utils.ClientResponse:
        path = '/api/v3/solomon/deliveries'
        params = {'delivery_id': delivery_id}
        return await web_app_client.get(path, params=params)

    async def test_unknown_delivery(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        delivery_id = 1  # unknown
        response = await self.request(web_app_client, delivery_id)
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::SolomonMetricDeliveryNotExists'
        message = f'There is no solomon metric delivery with id {delivery_id}'
        assert err['message'] == message

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
            'pg_solomon_metric_delivery.sql',
        ],
    )
    async def test_get(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        delivery_id = CURRENT_DELIVERY_SETTINGS['delivery_id']
        response = await self.request(web_app_client, delivery_id)
        assert response.status == 200, await response.text()
        delivery = await response.json()
        delivery['dimensions'].sort(key=lambda dim: dim['dimension_id'])
        compare_deliveries(delivery, get_current_delivery_by_id(delivery_id))


class TestGetDeliveries:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            count: tp.Optional[int] = None,
            offset: tp.Optional[int] = None,
    ) -> test_utils.ClientResponse:
        path = '/api/v3/solomon/deliveries/list'
        params: tp.Dict[str, int] = {}
        if count is not None:
            params['count'] = count
        if offset is not None:
            params['offset'] = offset
        return await web_app_client.get(path, params=params)

    @pytest.mark.parametrize('count', [None, 1, 1000])
    @pytest.mark.parametrize('offset', [None, 0, 1, 1000])
    async def test_get_empty_list(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            count: tp.Optional[int],
            offset: tp.Optional[int],
    ) -> None:
        response = await self.request(web_app_client, count, offset)
        assert response.status == 200, await response.text()
        deliveries = await response.json()
        assert deliveries['total'] == 0
        assert not deliveries['deliveries']

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
            'pg_solomon_metric_delivery.sql',
        ],
    )
    @pytest.mark.parametrize(
        'count', [None, 1, len(db_data.DELIVERY_SETTINGS)],
    )
    @pytest.mark.parametrize(
        'offset', [None, 0, 1, len(db_data.DELIVERY_SETTINGS)],
    )
    async def test_get(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            count: tp.Optional[int],
            offset: tp.Optional[int],
    ) -> None:
        response = await self.request(web_app_client, count, offset)
        assert response.status == 200, await response.text()
        deliveries = await response.json()
        for delivery in deliveries['deliveries']:
            delivery['dimensions'].sort(key=lambda dim: dim['dimension_id'])
        compare_delivery_lists(
            deliveries, get_current_deliveries(count, offset),
        )

    @pytest.mark.parametrize('count', [None, 0, -1])
    @pytest.mark.parametrize('offset', [None, -1])
    async def test_invalid_params(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            count: tp.Optional[int],
            offset: tp.Optional[int],
    ) -> None:
        if count is None and offset is None:
            # TODO здесь бы скипать тесты, но пока что при этом валятся ошибки
            return
        response = await self.request(web_app_client, count, offset)
        assert response.status == 400, await response.text()


class TestCreateDelivery:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            settings: tp.Dict[str, tp.Any],
            dimension_ids: tp.List[int],
    ) -> test_utils.ClientResponse:
        path = '/api/v3/solomon/deliveries'
        delivery_data = {'settings': settings, 'dimension_ids': dimension_ids}
        return await web_app_client.post(path, json=delivery_data)

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
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
        metric_id = 1000  # unknown
        delivery_settings = {'metric_id': metric_id}
        dimension_ids = CURRENT_DELIVERY_DIMENSION_IDS
        response = await self.request(
            web_app_client, delivery_settings, dimension_ids,
        )
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::UnknownMetric'
        assert err['message'] == f'Unknown metric with id {metric_id}'

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
        ],
    )
    async def test_unknown_source_dim_rel(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = CURRENT_DELIVERY_SETTINGS['metric_id']
        source_id = CURRENT_DELIVERY_SETTINGS['source_id']
        delivery_settings = {'metric_id': metric_id}
        dimension_ids = CURRENT_DELIVERY_DIMENSION_IDS.copy()
        connected_dimension_ids = [
            rel['dimension_id']
            for rel in db_data.COLUMNS_DIMENSIONS_REL
            if rel['source_id'] == source_id
        ]
        not_connected_dimension_id = next(
            dim['dimension_id']
            for dim in db_data.DIMENSIONS
            if dim['dimension_id'] not in connected_dimension_ids
        )
        dimension_ids.append(not_connected_dimension_id)
        response = await self.request(
            web_app_client, delivery_settings, dimension_ids,
        )
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::UnknownSourceDimensionRelation'
        assert (
            err['message']
            == 'Unknown dimension or its relation with solomon metric source'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
        ],
    )
    async def test_unknown_dimension(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = CURRENT_DELIVERY_SETTINGS['metric_id']
        delivery_settings = {'metric_id': metric_id}
        dimension_ids = CURRENT_DELIVERY_DIMENSION_IDS.copy()
        unknown_dimension_id = 1000  # unknown
        dimension_ids.append(unknown_dimension_id)
        response = await self.request(
            web_app_client, delivery_settings, dimension_ids,
        )
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::UnknownSourceDimensionRelation'
        assert (
            err['message']
            == 'Unknown dimension or its relation with solomon metric source'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
        ],
    )
    @pytest.mark.parametrize('duration', ['1 день', '1 day', '1.24'])
    async def test_invalid_duration(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            duration: str,
    ) -> None:
        metric_id = CURRENT_DELIVERY_SETTINGS['metric_id']
        delivery_settings = {'metric_id': metric_id, 'duration': duration}
        dimension_ids = CURRENT_DELIVERY_DIMENSION_IDS
        response = await self.request(
            web_app_client, delivery_settings, dimension_ids,
        )
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::InvalidPeriodFormat'
        assert err['message'] == f'Unknown period format: "{duration}"'

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
        ],
    )
    async def test_empty_duration(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = CURRENT_DELIVERY_SETTINGS['metric_id']
        duration = ''
        delivery_settings = {'metric_id': metric_id, 'duration': duration}
        dimension_ids = CURRENT_DELIVERY_DIMENSION_IDS
        response = await self.request(
            web_app_client, delivery_settings, dimension_ids,
        )
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::InvalidPeriodFormat'
        assert err['message'] == 'Empty period'

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
        ],
    )
    @pytest.mark.parametrize('grid', ['1 день', '1 day', '1.24'])
    async def test_invalid_grid(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            grid: str,
    ) -> None:
        metric_id = CURRENT_DELIVERY_SETTINGS['metric_id']
        delivery_settings = {'metric_id': metric_id, 'grid': grid}
        dimension_ids = CURRENT_DELIVERY_DIMENSION_IDS
        response = await self.request(
            web_app_client, delivery_settings, dimension_ids,
        )
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::InvalidPeriodFormat'
        assert err['message'] == f'Unknown period format: "{grid}"'

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
        ],
    )
    @pytest.mark.parametrize('grid', ['1d5s', '2d8h50m57s', '4d16h3m10s'])
    async def test_wrong_grid_period(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            grid: str,
    ) -> None:
        metric_id = CURRENT_DELIVERY_SETTINGS['metric_id']
        delivery_settings = {'metric_id': metric_id, 'grid': grid}
        dimension_ids = CURRENT_DELIVERY_DIMENSION_IDS
        response = await self.request(
            web_app_client, delivery_settings, dimension_ids,
        )
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::InvalidPeriodFormat'
        divisible = 60 * 60 * 24 * 7  # week
        assert err['message'] == (
            f'Wrong period: "{grid}", it must be divided into '
            f'{divisible} or {divisible} must be divided into it'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
        ],
    )
    async def test_empty_grid(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = CURRENT_DELIVERY_SETTINGS['metric_id']
        grid = ''
        delivery_settings = {'metric_id': metric_id, 'grid': grid}
        dimension_ids = CURRENT_DELIVERY_DIMENSION_IDS
        response = await self.request(
            web_app_client, delivery_settings, dimension_ids,
        )
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::InvalidPeriodFormat'
        assert err['message'] == 'Empty period'

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
        ],
    )
    @pytest.mark.parametrize('grid', [None, '10m', '6h'])
    @pytest.mark.parametrize('duration', [None, '20m', '7w'])
    async def test_create(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            grid: tp.Optional[str],
            duration: tp.Optional[str],
    ) -> None:
        metric_id = CURRENT_DELIVERY_SETTINGS['metric_id']
        delivery_settings = {'metric_id': metric_id}
        if grid is not None:
            delivery_settings['grid'] = grid
        if duration is not None:
            delivery_settings['duration'] = duration
        dimension_ids = CURRENT_DELIVERY_DIMENSION_IDS
        async with _NewDeliveriesGetter(web_app_client) as getter:
            response = await self.request(
                web_app_client, delivery_settings, dimension_ids,
            )
            assert response.status == 201, await response.text()
            delivery_from_response = await response.json()
        assert len(getter.new_deliveries) == 1
        (new_delivery,) = getter.new_deliveries
        delivery_settings.setdefault('grid', '1m')
        delivery_settings.setdefault('duration', '5m')
        reference_delivery = {
            'settings': delivery_settings,
            'dimension_ids': CURRENT_DELIVERY_DIMENSION_IDS.copy(),
        }
        compare_deliveries(new_delivery, reference_delivery)
        compare_deliveries(delivery_from_response, reference_delivery)

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
            'pg_solomon_metric_delivery.sql',
        ],
    )
    async def test_create_the_same(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        metric_id = CURRENT_DELIVERY_SETTINGS['metric_id']
        grid = CURRENT_DELIVERY_SETTINGS['grid']
        duration = CURRENT_DELIVERY_SETTINGS['duration']
        delivery_settings = {
            'metric_id': metric_id,
            'grid': grid,
            'duration': duration,
        }
        dimension_ids = CURRENT_DELIVERY_DIMENSION_IDS
        async with _NewDeliveriesGetter(web_app_client) as getter:
            response = await self.request(
                web_app_client, delivery_settings, dimension_ids,
            )
            assert response.status == 201, await response.text()
            delivery_from_response = await response.json()
        assert len(getter.new_deliveries) == 1
        assert len(getter.new_deliveries) == 1
        (new_delivery,) = getter.new_deliveries
        reference_delivery = {
            'settings': delivery_settings,
            'dimension_ids': CURRENT_DELIVERY_DIMENSION_IDS.copy(),
        }
        compare_deliveries(new_delivery, reference_delivery)
        compare_deliveries(delivery_from_response, reference_delivery)


class TestUpdateDelivery:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            delivery_id: int,
            settings: tp.Optional[tp.Dict[str, tp.Any]] = None,
            dimension_ids: tp.Optional[tp.List[int]] = None,
    ) -> test_utils.ClientResponse:
        path = '/api/v3/solomon/deliveries'
        params = {'delivery_id': delivery_id}
        delivery_data: dict = {}
        if settings is not None:
            delivery_data['settings'] = settings
        if dimension_ids is not None:
            delivery_data['dimension_ids'] = dimension_ids
        return await web_app_client.patch(
            path, params=params, json=delivery_data,
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
            'pg_solomon_metric_delivery.sql',
        ],
    )
    async def test_unknown_delivery(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        delivery_id = 1000  # unknown
        grid = CURRENT_DELIVERY_SETTINGS['grid']
        duration = CURRENT_DELIVERY_SETTINGS['duration']
        delivery_settings = {'grid': grid, 'duration': duration}
        response = await self.request(
            web_app_client, delivery_id, settings=delivery_settings,
        )
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::SolomonMetricDeliveryNotExists'
        assert (
            err['message']
            == f'There is no solomon metric delivery with id {delivery_id}'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
            'pg_solomon_metric_delivery.sql',
        ],
    )
    async def test_unknown_source_dim_rel(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        delivery_id = CURRENT_DELIVERY_SETTINGS['delivery_id']
        source_id = CURRENT_DELIVERY_SETTINGS['source_id']
        dimension_ids = CURRENT_DELIVERY_DIMENSION_IDS.copy()
        connected_dimension_ids = [
            rel['dimension_id']
            for rel in db_data.COLUMNS_DIMENSIONS_REL
            if rel['source_id'] == source_id
        ]
        not_connected_dimension_id = next(
            dim['dimension_id']
            for dim in db_data.DIMENSIONS
            if dim['dimension_id'] not in connected_dimension_ids
        )
        dimension_ids.append(not_connected_dimension_id)
        response = await self.request(
            web_app_client, delivery_id, dimension_ids=dimension_ids,
        )
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::UnknownSourceDimensionRelation'
        assert (
            err['message']
            == 'Unknown dimension or its relation with solomon metric source'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
            'pg_solomon_metric_delivery.sql',
        ],
    )
    async def test_unknown_dimension(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        delivery_id = CURRENT_DELIVERY_SETTINGS['delivery_id']
        dimension_ids = CURRENT_DELIVERY_DIMENSION_IDS.copy()
        unknown_dimension_id = 1000  # unknown
        dimension_ids.append(unknown_dimension_id)
        response = await self.request(
            web_app_client, delivery_id, dimension_ids=dimension_ids,
        )
        assert response.status == 404, await response.text()
        err = await response.json()
        assert err['code'] == 'NotFound::UnknownSourceDimensionRelation'
        assert (
            err['message']
            == 'Unknown dimension or its relation with solomon metric source'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
            'pg_solomon_metric_delivery.sql',
        ],
    )
    @pytest.mark.parametrize('duration', ['1 день', '1 day', '1.24'])
    async def test_invalid_duration(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            duration: str,
    ) -> None:
        delivery_id = CURRENT_DELIVERY_SETTINGS['delivery_id']
        delivery_settings = {'duration': duration}
        response = await self.request(
            web_app_client, delivery_id, settings=delivery_settings,
        )
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::InvalidPeriodFormat'
        assert err['message'] == f'Unknown period format: "{duration}"'

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
            'pg_solomon_metric_delivery.sql',
        ],
    )
    async def test_empty_duration(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        delivery_id = CURRENT_DELIVERY_SETTINGS['delivery_id']
        duration = ''
        delivery_settings = {'duration': duration}
        response = await self.request(
            web_app_client, delivery_id, settings=delivery_settings,
        )
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::InvalidPeriodFormat'
        assert err['message'] == 'Empty period'

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
            'pg_solomon_metric_delivery.sql',
        ],
    )
    @pytest.mark.parametrize('grid', ['1 день', '1 day', '1.24'])
    async def test_invalid_grid(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            grid: str,
    ) -> None:
        delivery_id = CURRENT_DELIVERY_SETTINGS['delivery_id']
        delivery_settings = {'grid': grid}
        response = await self.request(
            web_app_client, delivery_id, settings=delivery_settings,
        )
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::InvalidPeriodFormat'
        assert err['message'] == f'Unknown period format: "{grid}"'

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
            'pg_solomon_metric_delivery.sql',
        ],
    )
    async def test_empty_grid(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        delivery_id = CURRENT_DELIVERY_SETTINGS['delivery_id']
        grid = ''
        delivery_settings = {'grid': grid}
        response = await self.request(
            web_app_client, delivery_id, settings=delivery_settings,
        )
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::InvalidPeriodFormat'
        assert err['message'] == 'Empty period'

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
            'pg_solomon_metric_delivery.sql',
        ],
    )
    @pytest.mark.parametrize('grid', ['1d5s', '2d8h50m57s', '4d16h3m10s'])
    async def test_wrong_grid_period(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            grid: str,
    ) -> None:
        delivery_id = CURRENT_DELIVERY_SETTINGS['delivery_id']
        delivery_settings = {'grid': grid}
        response = await self.request(
            web_app_client, delivery_id, settings=delivery_settings,
        )
        assert response.status == 400, await response.text()
        err = await response.json()
        assert err['code'] == 'BadRequest::InvalidPeriodFormat'
        divisible = 60 * 60 * 24 * 7  # week
        assert err['message'] == (
            f'Wrong period: "{grid}", it must be divided into '
            f'{divisible} or {divisible} must be divided into it'
        )

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
            'pg_solomon_metric_delivery.sql',
        ],
    )
    @pytest.mark.parametrize('grid', [None, '2s', '2w'])
    @pytest.mark.parametrize('duration', [None, '2s', '2w'])
    @pytest.mark.parametrize('number_of_remote_dimensions', [0, 1])
    @pytest.mark.parametrize('number_of_new_dimensions', [0, 1])
    async def test_update(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
            grid: tp.Optional[str],
            duration: tp.Optional[str],
            number_of_remote_dimensions: int,
            number_of_new_dimensions: int,
    ) -> None:
        delivery_id = CURRENT_DELIVERY_SETTINGS['delivery_id']
        source_id = CURRENT_DELIVERY_SETTINGS['source_id']
        dimension_ids = CURRENT_DELIVERY_DIMENSION_IDS
        delivery_settings: tp.Dict[str, str] = {}
        if grid is not None:
            delivery_settings['grid'] = grid
        if duration is not None:
            delivery_settings['duration'] = duration
        if number_of_new_dimensions:
            connected_dimension_ids = [
                rel['dimension_id']
                for rel in db_data.COLUMNS_DIMENSIONS_REL
                if rel['source_id'] == source_id
                and rel['dimension_id'] not in dimension_ids
            ]
            dimension_ids.extend(
                connected_dimension_ids[:number_of_new_dimensions],
            )
        if number_of_remote_dimensions:
            dimension_ids = dimension_ids[number_of_remote_dimensions:]
        response = await self.request(
            web_app_client,
            delivery_id,
            settings=delivery_settings,
            dimension_ids=dimension_ids,
        )
        assert response.status == 200, await response.text()
        delivery_from_response = await response.json()
        updated_delivery = next(
            delivery
            for delivery in (await get_deliveries(web_app_client))[
                'deliveries'
            ]
            if delivery['settings']['delivery_id'] == delivery_id
        )
        reference_settings = CURRENT_DELIVERY_SETTINGS.copy()
        reference_settings.update(delivery_settings)
        reference_delivery = {
            'settings': reference_settings,
            'dimension_ids': dimension_ids,
        }
        compare_deliveries(updated_delivery, reference_delivery)
        compare_deliveries(delivery_from_response, reference_delivery)


class TestDeleteDelivery:
    async def request(
            self, web_app_client: test_utils.TestClient, delivery_id: int,
    ) -> test_utils.ClientResponse:
        path = '/api/v3/solomon/deliveries'
        params = {'delivery_id': delivery_id}
        return await web_app_client.delete(path, params=params)

    async def test_unknown_delivery(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        delivery_id = 1000  # unknown
        response = await self.request(web_app_client, delivery_id)
        assert response.status == 204, await response.text()

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=[
            'pg_source.sql',
            'pg_metric_group.sql',
            'pg_metric.sql',
            'pg_metric_instance.sql',
            'pg_column.sql',
            'pg_dimension.sql',
            'pg_col_dim_relation.sql',
            'pg_solomon_metric_delivery.sql',
        ],
    )
    async def test_delete(
            self,
            web_app_client: test_utils.TestClient,
            atlas_blackbox_mock: None,
    ) -> None:
        delivery_id = CURRENT_DELIVERY_SETTINGS['delivery_id']
        response = await self.request(web_app_client, delivery_id)
        assert response.status == 204, await response.text()
        deliveries = await get_deliveries(web_app_client)
        assert all(
            delivery['settings']['delivery_id'] != delivery_id
            for delivery in deliveries['deliveries']
        )


class TestGetSolmonMetricValues:
    async def request(
            self,
            web_app_client: test_utils.TestClient,
            period: str,
            now: datetime.datetime,
    ) -> test_utils.ClientResponse:
        path = '/api/v3/solomon/values'
        params = {'period': period, 'now': now.isoformat()}
        return await web_app_client.get(path, params=params)

    @pytest.mark.pgsql(
        'taxi_db_postgres_atlas_backend',
        files=['pg_solomon_metric_values.sql'],
    )
    async def test_get(
            self, web_app_client: test_utils.TestClient, patch: Patch,
    ) -> None:
        async def execute(  # pylint: disable=unused-variable
                context: tp.Any, query: str,
        ) -> tp.Any:
            if query.startswith('SELECT\ntoTypeName('):
                return [('UInt32',)]
            if query.startswith('SELECT\ntoUInt32(max('):
                value = int(datetime.datetime.now().timestamp())
                return [(value,)]
            if query.startswith('SELECT\n'):
                times = [*range(3)]
                cities = ['Екатеринбург', 'Москва', 'Санкт-Петербург']
                tariffs = ['Эконом', 'Промо', 'Что-то еще']
                corp_types = ['eda', 'corp_type', 'no_corp']
                res = [
                    (time, time, *labels)
                    for time, *labels in itertools.product(
                        times, cities, tariffs, corp_types,
                    )
                ]
                random.shuffle(res)
                return res
            assert False

        base_path = 'atlas_backend.internal.sources.models.'
        patch(base_path + 'Source' + '._prevalidate')(
            lambda *args, **kwargs: None,
        )
        for model in ('CHSource', 'Source', 'CHYTSource'):
            patch(base_path + model + '.execute')(execute)

        response = await self.request(
            web_app_client, '5m', datetime.datetime.now(),
        )
        assert response.status == 200, await response.text()
