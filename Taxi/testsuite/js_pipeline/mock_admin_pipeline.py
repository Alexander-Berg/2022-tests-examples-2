import dataclasses
import typing
import uuid

import pytest


class AdminPipelineContext:
    @dataclasses.dataclass
    class Service:
        tvm_name: str
        balancer_hostname: str = 'mockserver'

    @dataclasses.dataclass
    class Config:
        prefix: str
        consumers: typing.List[str]
        service: typing.Any = None

    def __init__(self, mockserver):
        self.mockserver = mockserver

    def set_pipelines_by_consumer(
            self,
            pipelines_by_consumer,
            service: typing.Optional[Service] = None,
    ):
        for consumer in pipelines_by_consumer.keys():

            @self.mockserver.json_handler(
                f'/admin-pipeline/{consumer}/register/',
            )
            def _register_consumer(request):
                if service:
                    assert (
                        request.json['service_balancer_hostname']
                        == service.balancer_hostname
                    )
                    assert request.json['service_tvm_name'] == service.tvm_name

            @self.mockserver.json_handler(
                f'/admin-pipeline/cache/{consumer}/pipeline/enumerate/',
            )
            def _enumerate_pipelines(request, consumer_=consumer):
                pipelines_by_id = pipelines_by_consumer.get(consumer_, {})
                return [
                    {'id': pipeline['id']}
                    for pipeline in pipelines_by_id.values()
                ]

            @self.mockserver.json_handler(
                f'/admin-pipeline/cache/{consumer}/pipeline/',
            )
            def _get_pipeline(request, consumer_=consumer):
                pipelines_by_id = pipelines_by_consumer.get(consumer_, {})
                return pipelines_by_id[request.args['id']]

    def mock_single_pipeline(self, request, load_json, config: Config):
        marker = request.node.get_closest_marker('pipeline')

        prefix = config.prefix

        if marker:
            prefix += '_{}'.format(marker.args[0])

        pipeline = {
            'comment': 'comment 1',
            'created': '2019-12-16T23:38:47+03:00',
            'updated': '2019-12-16T23:38:47+03:00',
            'state': 'active',
            'version': 0,
        }

        pipelines = {}

        try:
            pipeline.update(load_json(f'{prefix}.json'))
            pipeline['id'] = str(uuid.uuid4())
            pipelines[pipeline['id']] = pipeline
        except FileNotFoundError:
            # Filename not found
            if marker:
                # Custom name given, this is an error then
                raise

        pipelines_by_consumer: dict = {
            consumer: pipelines for consumer in config.consumers
        }

        self.set_pipelines_by_consumer(pipelines_by_consumer, config.service)

    def mock_many_pipelines(self, request, load_json, config: Config):
        marker = request.node.get_closest_marker('pipeline')

        prefix = config.prefix

        if marker:
            prefix += '_{}'.format(marker.args[0])

        pipelines = {}

        try:
            for doc in load_json(f'{prefix}.json'):
                pipeline = {
                    'comment': 'comment 1',
                    'created': '2019-12-16T23:38:47+03:00',
                    'updated': '2019-12-16T23:38:47+03:00',
                    'state': 'active',
                    'version': 0,
                }
                pipeline.update(doc)
                pipeline['id'] = str(uuid.uuid4())
                pipelines[pipeline['id']] = pipeline
        except FileNotFoundError:
            # Filename not found
            if marker:
                # Custom name given, this is an error then
                raise

        pipelines_by_consumer: dict = {
            consumer: pipelines for consumer in config.consumers
        }

        self.set_pipelines_by_consumer(pipelines_by_consumer, config.service)


@pytest.fixture(autouse=True)
def admin_pipeline(mockserver, request):
    return AdminPipelineContext(mockserver)


def pytest_configure(config):
    config.addinivalue_line('markers', 'pipeline: pipeline name custom suffix')
