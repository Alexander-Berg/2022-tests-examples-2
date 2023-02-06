"""
Mock for experiments3 proxy.
"""

import pytest

NEWER_THAN = 'newer_than'


@pytest.fixture(autouse=True)
def mock_experiments3_proxy(experiments3, mockserver):
    @mockserver.json_handler('/v1/experiments/updates')
    def _handler_experiments3(request):
        version = -1
        if NEWER_THAN in request.args:
            version = int(request.args[NEWER_THAN])
        if 'consumer' in request.args:
            consumer = request.args['consumer']
            return {
                'experiments': experiments3.get_experiments(consumer, version),
            }
        return {'experiments': []}

    @mockserver.json_handler('/v1/configs/updates')
    def _handler_config(request):
        version = -1
        if NEWER_THAN in request.args:
            version = int(request.args[NEWER_THAN])
        if 'consumer' in request.args:
            consumer = request.args['consumer']
            return {'configs': experiments3.get_configs(consumer, version)}
        return {'configs': []}

    @mockserver.json_handler('/v1/consumers')
    def _handler_consumers(request):
        assert 'prefix' in request.args
        result = []
        for consumer in experiments3.get_consumers():
            if consumer.startswith(request.args['prefix']):
                result.append(consumer)
        return {'consumers': result}
