# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from eventus_orchestrator_mock import (
    fbs_pipelines_config,
)  # make_pipelines_config_response
from eventus_orchestrator_mock import (
    fbs_polygon_values,
)  # make_polygon_values_response


class PolygonValuesContext:
    def _set_polygon_values(self, response_data):
        polygons_dict = {
            'cursor': 'some-cursor-' + str(self._cursor),
            'polygons': (
                response_data
                if isinstance(response_data, list)
                else [response_data]
            ),
        }
        data_bytes = fbs_polygon_values.make_polygon_values_response(
            polygons_dict,
        )
        self._polygon_values = data_bytes

    def __init__(self):
        self._cursor = 1
        self._polygon_values = bytes()

    @property
    def polygon_values(self):
        return self._polygon_values

    async def set_polygon_values(self, response_data):
        self._cursor += 1
        self._set_polygon_values(response_data)


class PipelinesConfigContext:
    def __init__(self):
        self._cursor = 1
        self._pipelines_config = bytes()

    # Current value of pipelines_config
    @property
    def pipelines_config(self):
        return self._pipelines_config

    def _set_pipelines_config(self, response_data):
        pipelines_dict = {
            'cursor': f'some-cursor-{str(self._cursor)}',
            'pipelines': response_data,
        }
        data_bytes = fbs_pipelines_config.make_pipelines_config_response(
            pipelines_dict,
        )

        self._pipelines_config = data_bytes

    async def set_pipelines_config(self, response_data):
        self._cursor += 1
        self._set_pipelines_config(response_data)


class EventusOrchestratorContext:
    def __init__(self, handle_mocks):
        self.put_pipeline_schema_calls = []
        self._polygon_values_ctx = PolygonValuesContext()
        self._pipelines_config_ctx = PipelinesConfigContext()
        self._handle_mocks = handle_mocks

    # Current values of polygons
    @property
    def polygon_values(self):
        return self._polygon_values_ctx.polygon_values

    # Current values of polygons
    @property
    def pipelines_config(self):
        return self._pipelines_config_ctx.pipelines_config

    async def get_service_schema(self, service):
        self._handle_mocks.put_schema_handler.flush()
        await service.run_task('schema-send-task')
        return (await self._handle_mocks.put_schema_handler.wait_call())[
            'request'
        ].json['schema']

    async def _has_registered_operation(
            self, service, kind: str, op_names: list,
    ):
        service_schema = await self.get_service_schema(service)
        op_registered = [
            schema['name']
            for schema in service_schema[kind + 's']
            if schema['name'] in op_names
        ]
        op_unregistered = [
            name for name in op_names if name not in op_registered
        ]
        error_message = (
            f'Please, register {kind}(s) {op_unregistered} in your'
            + 'implemention of SchemasSender::OperationSchemaLists'
            + '::{kind}_list (e.g. in src/components.cpp)'
        )
        return not op_unregistered, error_message

    # FIXME: move this check into set_pipelines_config
    async def has_registered_sinks(self, service, sink_names: list):
        """
        Check sink is registered in schemas for eventus-orchestrator
        Example usage:
        .. code-block:: python
        is_registered, error_message = (
            await taxi_eventus_orchestrator_mock.has_registered_sinks(
                taxi_service_name, ['source-name-from-config'],
            )
        )
        assert is_registered, error_message
        """
        return await self._has_registered_operation(
            service, 'sink', sink_names,
        )

    # FIXME: move this check into set_pipelines_config
    async def has_registered_sources(self, service, source_names: list):
        """
        Check source is registered in schemas for eventus-orchestrator
        Example usage:
        .. code-block:: python
        is_registered, error_message = (
            await taxi_eventus_orchestrator_mock.has_registered_sources(
                taxi_service_name, ['source-name-from-config'],
            )
        )
        assert is_registered, error_message
        """
        return await self._has_registered_operation(
            service, 'source', source_names,
        )

    # "eventus-orch-cfg-update"
    async def set_polygon_values(self, taxi_service, response_data):
        """
        Set pipeline config format as in eventus orchestrator admin
        Example usage:
        .. code-block:: python
        poligon_values = {
            'coordinates': [
                {
                    'points': [
                        {'lon': 37.56593397, 'lat': 55.89496673},
                        {'lon': 37.56593397, 'lat': 55.69496673},
                        {'lon': 37.76593397, 'lat': 55.69496673},
                        {'lon': 37.76593397, 'lat': 55.89496673},
                    ],
                },
            ],
            'enabled': True,
            'groups': ['lavka'],
            'metadata': {},
            'polygon_id': 'polygon-id',
        }
        set_pipelines_config(testpoint, taxi_service_name, poligon_values)
        """
        await self._polygon_values_ctx.set_polygon_values(response_data)

    async def set_pipelines_config(
            self,
            testpoint,
            taxi_service,
            orch_pipelines,
            testpoint_timeout=10.0,
            wait_for_apply: bool = True,
            force_pipeline_update: bool = False,
    ):
        """
        Set pipeline config format as in eventus orchestrator admin
        Example usage:
        .. code-block:: python
        pipeline_conf = (
            {
                'description': '',
                'st_ticket': '',
                'source': {'name': 'your_source_name'},
                'root': {
                    'output': {'sink_name': 'log_sink'},
                    'operations': [
                        {
                            'name': 'operation',
                            'operation_variant': {
                                'arguments': {},
                                'operation_name': (
                                    'some_operation_variant_name'
                                ),
                                'type': 'mapper',
                            },
                        },
                    ],
                },
                'name': 'communal-events',
            },
        )
        set_pipelines_config(testpoint, taxi_service_name, pipeline_conf)
        """

        @testpoint('pipeline_manager::updated')
        def pipelines_manager_updated(data):
            pass

        @testpoint('pipeline_config_manager::updated')
        def pipelines_config_updated(data):
            pass

        pipelines_manager_updated.flush()
        pipelines_config_updated.flush()

        await self._pipelines_config_ctx.set_pipelines_config(orch_pipelines)

        if force_pipeline_update:
            await taxi_service.run_task('pipeline-cfg-force-next-update')

        if wait_for_apply:
            await taxi_service.invalidate_caches()

            update_config_call = await pipelines_config_updated.wait_call(
                testpoint_timeout,
            )

            if not update_config_call['data']['is_update_skiped']:
                await pipelines_manager_updated.wait_call(testpoint_timeout)

    async def set_empty_config_without_sync(self):
        await self._polygon_values_ctx.set_polygon_values([])
        await self._pipelines_config_ctx.set_pipelines_config([])


@pytest.fixture(name='taxi_eventus_orchestrator_mock', autouse=True)
async def _taxi_eventus_orchestrator_mock(mockserver):
    class Mocks:
        _expect_times_called = 0

        @staticmethod
        @mockserver.handler(
            '/eventus-orchestrator-uservices/v1/polygon/values',
        )
        def _v1_polygons_values(request):
            return mockserver.make_response(
                response=taxi_eventus_orchestrator_ctx.polygon_values,
            )

        @staticmethod
        @mockserver.handler(
            '/eventus-orchestrator-uservices/v1/instance'
            '/pipelines/config/values',
        )
        def _v1_instance_pipelines_config_values(request):
            return mockserver.make_response(
                response=taxi_eventus_orchestrator_ctx.pipelines_config,
            )

        @staticmethod
        @mockserver.handler(
            '/eventus-orchestrator-uservices/v1/eventus'
            '/instance/status/update',
        )
        def handler(request):
            return mockserver.make_response('{}', 200)

        @staticmethod
        @mockserver.handler(
            '/eventus-orchestrator-uservices/v1/eventus/pipeline/schema',
        )
        def put_schema_handler(request):
            taxi_eventus_orchestrator_ctx.put_pipeline_schema_calls.append(
                request,
            )
            return mockserver.make_response('{}', 200)

        @staticmethod
        def expect_times_called(times):
            Mocks._expect_times_called = times

        @staticmethod
        def verify():
            return Mocks._expect_times_called == 0

    taxi_eventus_orchestrator_ctx = EventusOrchestratorContext(Mocks())

    await taxi_eventus_orchestrator_ctx.set_empty_config_without_sync()

    return taxi_eventus_orchestrator_ctx
