import collections
import contextlib

import pytest

USERVER_CONFIG_HOOKS = ['userver_config_stat_client_config']


@pytest.fixture(name='statistics', autouse=True)
def mock_statistics(mockserver):
    class Capture:
        def __init__(self, service_name=None):
            self._statistics = collections.defaultdict(
                lambda: collections.defaultdict(int),
            )
            self._accepting = True
            self._service_name = service_name

        def stop_accepting(self):
            self._accepting = False

        def update_statistics(self, metrics):
            assert self._accepting

            for metric in metrics:
                self._statistics[self._service_name][metric['name']] += metric[
                    'value'
                ]

        @property
        def statistics(self):
            assert not self._accepting, (
                'Do not check statistics while service accepting it. '
                'Result can flap'
            )
            return dict(self._statistics[self._service_name])

    class Context:
        def __init__(self):
            self.fallbacks = []
            self._capture = None
            self._service_name = None

        def update_statistics(self, service_name, metrics):
            if not self._capture:
                return
            if self._service_name and service_name != self._service_name:
                return
            self._capture.update_statistics(metrics)

        @contextlib.asynccontextmanager
        async def capture(self, service, service_name=None):
            try:
                await service.invalidate_caches()
                self._capture = Capture(service_name)
                self._service_name = service_name
                yield self._capture
                await service.invalidate_caches()
            finally:
                self._capture.stop_accepting()
                self._capture = False

    context = Context()

    @mockserver.json_handler('/statistics/v1/service/health')
    async def _mock_v1_service_health(request):
        assert request.args['service']
        return {'fallbacks': context.fallbacks}

    @mockserver.json_handler('/statistics/v1/metrics/store')
    async def _v1_metrics_store(request):
        request = request.json
        assert request['service']
        context.update_statistics(request['service'], request['metrics'])

        return {}

    @mockserver.json_handler('/statistics/v1/metrics/list')
    async def _v1_metrics_list(request):
        request = request.json
        assert request['service']
        if not context._capture:
            return {'metrics': []}
        return {
            'metrics': [
                {'name': name, 'value': value}
                for name, value in context._capture._statistics[
                    request['service']
                ].items()
            ],
        }

    return context


# This hook is used to enable statistics client. It is necessary for
# tests concerning service metrics and fallbacks
@pytest.fixture(scope='session', name='userver_config_stat_client_config')
def _userver_config_stat_client_config():
    def patch_config(config, config_vars):
        config_vars['use-dummy-statistics-client'] = False

    return patch_config
