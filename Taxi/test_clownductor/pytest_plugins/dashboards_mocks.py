import itertools
from typing import Dict
from typing import Iterator
from typing import NamedTuple
from typing import Tuple

from aiohttp import web
import pytest

from generated.clients_libs.dashboards import dashboard_config
from testsuite.mockserver import classes as mock_types


class AlreadyExists(Exception):
    pass


@pytest.fixture
def patch_configs_upload_handler(mock_dashboards):
    def _wrapper(response: Dict, status: int):
        @mock_dashboards('/v1/configs/upload')
        def _configs_upload_handler(request: mock_types.MockserverRequest):
            return web.json_response(response, status=status)

        return _configs_upload_handler

    return _wrapper


@pytest.fixture
def patch_get_old_config_handler(mock_dashboards):
    def _wrapper(response: Dict, status: int):
        @mock_dashboards('/v1/configs/get_config')
        def _configs_upload_handler(request: mock_types.MockserverRequest):
            return web.json_response(response, status=status)

        return _configs_upload_handler

    return _wrapper


class DashboardKey(NamedTuple):
    project_name: str
    service_name: str
    branch_name: str
    service_type: str


class MockContext:
    def __init__(self):
        map_type = Dict[DashboardKey, dashboard_config.DashboardConfig]
        self._dashboards: map_type = {}
        self._id_generator = itertools.count(1)

    @property
    def configs(
            self,
    ) -> Iterator[Tuple[DashboardKey, dashboard_config.DashboardConfig]]:
        yield from self._dashboards.items()

    def create(
            self, key: DashboardKey, config: dashboard_config.DashboardConfig,
    ) -> dashboard_config.DashboardConfig:
        if key in self._dashboards:
            raise AlreadyExists
        self._dashboards[key] = config
        return config


@pytest.fixture(name='mock_dashboards_context')
def _mock_dashboards_context() -> MockContext:
    return MockContext()


@pytest.fixture(name='dashboards_mockserver')
def _dashboards_mockserver(mockserver, mock_dashboards_context):
    class Mocks:
        @staticmethod
        @mockserver.json_handler('/dashboards/v1/configs/upload')
        async def _configs_upload(request):
            body = request.json
            query = request.query
            key = DashboardKey(
                query['project_name'],
                query['service_name'],
                query['branch_name'],
                query['service_type'],
            )
            config = dashboard_config.DashboardConfig.deserialize(body)
            try:
                is_created = True
                config = mock_dashboards_context.create(key, config)
            except AlreadyExists:
                is_created = False

            return mockserver.make_response(
                json={'is_created': is_created, 'config': config.serialize()},
                status=200,
            )

    return Mocks()
