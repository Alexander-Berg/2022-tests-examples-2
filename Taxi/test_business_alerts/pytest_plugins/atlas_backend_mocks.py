import copy
import functools
import typing as tp

import attr
import pytest


V3_METRICS_BY_ID = {
    1: dict(
        metric_id=1,
        ru_name='ru_name',
        en_name='en_name',
        ru_description='',
        en_description='',
        group_id=1,
    ),
}

V3_INSTANCES_BY_ID = {
    1: dict(
        metric_id=1,
        source_id=1,
        expression='',
        filters=[],
        use_final=True,
        default_time_dimension_id=1,
    ),
}

DIMENSIONS_BY_ID = {
    1: dict(
        dimension_id=1,
        dimension_name='count',
        description='',
        dimension_type='INT',
    ),
}

DELIVERIES_BY_ID = {
    1: dict(
        settings=dict(
            delivery_id=1,
            metric_id=1,
            sensor='orders',
            duration='5m',
            grid='1m',
        ),
        dimensions=[DIMENSIONS_BY_ID[1]],
    ),
}


@pytest.fixture(name='atlas_backend')
def mock_atlas_backend(mockserver):
    v3_metrics_by_id = copy.deepcopy(V3_METRICS_BY_ID)
    v3_instances_by_id = copy.deepcopy(V3_INSTANCES_BY_ID)
    dimensions_by_id = copy.deepcopy(DIMENSIONS_BY_ID)
    deliveries_by_id = copy.deepcopy(DELIVERIES_BY_ID)

    @attr.dataclass
    class Context:
        # mock-name -> requests
        requests: tp.Dict[str, tp.List[tp.Dict]] = {}

        def add_request_data(self, name: str, request):
            reqs = self.requests.setdefault(name, [])
            reqs.append(request)

        def mock_handler(
                self,
                path: str,
                prefix: bool = False,
                raw_request: bool = False,
                regex: bool = False,
        ):
            def decorator(func):
                @functools.wraps(func)
                def wrapper(request):
                    self.add_request_data(path, request)
                    return func(request)

                full_path = '/atlas-backend' + path
                return mockserver.json_handler(
                    full_path,
                    prefix=prefix,
                    raw_request=raw_request,
                    regex=regex,
                )(wrapper)

            return decorator

    ctx = Context()
    atlas_404 = mockserver.make_response(
        json=dict(code='err', message='', detials={}), status=404,
    )

    @ctx.mock_handler('/api/v3/metrics/list')
    def _v3_metrics_list(request):
        return list(v3_metrics_by_id.values())

    @ctx.mock_handler('/api/v3/solomon/deliveries/list')
    def _v3_solomon_deliveries_list(request):
        offset = int(request.query.get('offset', 0))
        count = int(request.query.get('count', len(deliveries_by_id)))
        response_deliveries = [
            delivery
            for delivery in list(deliveries_by_id.values())[
                offset : offset + count
            ]
        ]
        return dict(
            total=len(response_deliveries), deliveries=response_deliveries,
        )

    @ctx.mock_handler('/api/v3/metric_with_instance/')
    def _v3_metric_instance(request):
        metric_id = int(request.query['metric_id'])
        try:
            return dict(
                metric=v3_metrics_by_id[metric_id],
                instance=v3_instances_by_id[metric_id],
            )
        except KeyError:
            return atlas_404

    @ctx.mock_handler('/api/v1/sources/dimensions/list')
    def _v1_source_dimensions(request):
        return list(dimensions_by_id.values())

    @ctx.mock_handler('/api/v3/solomon/deliveries')
    def _v3_solomon_delivery(request):
        delivery_id = max(deliveries_by_id) + 1
        req_settings = request.json['settings']
        metric_name = v3_metrics_by_id[req_settings['metric_id']]['en_name']
        try:
            delivery = deliveries_by_id[delivery_id] = dict(
                settings=dict(
                    **req_settings,
                    delivery_id=delivery_id,
                    sensor=f'{delivery_id}_{metric_name}',
                ),
                dimensions=[
                    dimensions_by_id[dim_id]
                    for dim_id in request.json['dimension_ids']
                ],
            )
            return mockserver.make_response(json=delivery, status=201)
        except KeyError:
            return atlas_404

    return ctx
