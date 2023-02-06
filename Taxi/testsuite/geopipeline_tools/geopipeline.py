# pylint: disable=import-error,invalid-name,useless-object-inheritance
# pylint: disable=undefined-variable,unused-variable,too-many-lines
# pylint: disable=no-name-in-module
# pylint: disable=redefined-outer-name
# flake8: noqa F501 F401 F841 F821
import pytest
import asyncio


@pytest.fixture
def control_plane_context():
    class ControlPlaneContext:
        def __init__(self):
            self.data = {}

        def set_value(self, data):
            self.data = data

    return ControlPlaneContext()


@pytest.fixture
def mock_geo_pipeline_control_plane(mockserver, control_plane_context):
    class GeoPipelineControlPlaneMock:
        def set_value(self, value):
            control_plane_context.set_value(value)

        @mockserver.json_handler(
            '/geo-pipeline-control-plane/internal/config/get-all/',
        )
        @staticmethod
        def get_config_mock_internal(request):
            return control_plane_context.data

        @mockserver.json_handler('/geo-pipeline-control-plane/get_config/v3/')
        @staticmethod
        def get_config_mock_v3(request):
            return control_plane_context.data

        @mockserver.json_handler('/geo-pipeline-control-plane/get_config/v2/')
        @staticmethod
        def get_config_mock_v2(request):
            return control_plane_context.data

    return GeoPipelineControlPlaneMock()


@pytest.fixture
def geopipeline_config(load_json, control_plane_context):
    class GeoPipelineConfig(object):
        def __init__(self, service):
            self.service = service
            self.control_plane_context = control_plane_context
            self.config = {}

        async def update_service_config(self, config_path):
            await self.update_service_config_by_value(load_json(config_path))

        async def update_service_config_by_value(self, value):
            self.control_plane_context.set_value(value)
            await self.service.run_periodic_task('geo-pipeline config update')

        def __getattr__(self, attr):
            if attr in self.__dict__:
                return getattr(self, attr)
            return getattr(self.service, attr)

    async def create_geopipeline_config(service_fixture):
        obj = GeoPipelineConfig(service_fixture)
        await obj.update_service_config_by_value({})
        return obj

    return create_geopipeline_config
