# root conftest for service processing
import dataclasses
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
import uuid

# pylint: disable=import-error
from processing_plugins import stq_worker_conftest_plugin
import pytest
import pytz
import yaml

from tests_processing import util  # noqa

pytest_plugins = ['processing_plugins.pytest_plugins']


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'processing_queue_config: processing queue config on the fly',
    )
    config.addinivalue_line(
        'markers',
        'processing_pipeline_config: processing queue config on the fly',
    )


def pytest_collection_modifyitems(items):
    for item in items:
        item.add_marker(pytest.mark.disable_config_check())
        item.add_marker(pytest.mark.experiments3())


@dataclasses.dataclass
class ProcessingEntityConfig:
    module: str
    scope: str
    queue: Optional[str] = None
    single_pipeline: Optional[str] = None
    main_operator: str = 'main'
    config_vars: Dict[str, Any] = dataclasses.field(default_factory=dict)


@pytest.fixture(name='processing')
def processing_fixture(
        taxi_processing, stq, taxi_config, get_file_path, load, mockserver,
):
    class ProcessingWrapper:
        class Scope:
            def __init__(self, wrapper, scope, queue=None):
                self._wrapper = wrapper
                self._scope = scope
                self._queue = queue

            def __getattr__(self, queue):
                return ProcessingWrapper.Scope(
                    self._wrapper, self._scope, queue,
                )

            def send_event(
                    self,
                    item_id,
                    payload,
                    expect_fail=False,
                    stq_queue=None,
                    eta=None,
                    already_flushing_stq=False,
                    idempotency_token=None,
                    extra_action=None,
                    tag=None,
            ):
                fun = (
                    self._wrapper.send_event
                    if already_flushing_stq
                    else self._wrapper.send_event_with_flushing
                )
                return fun(
                    self._scope,
                    self._queue,
                    item_id,
                    payload,
                    expect_fail=expect_fail,
                    stq_queue=stq_queue,
                    eta=eta,
                    idempotency_token=idempotency_token,
                    extra_action=extra_action,
                    tag=tag,
                )

            def run_pipeline(
                    self,
                    item_id,
                    payload,
                    expect_fail=False,
                    stq_queue=None,
                    eta=None,
                    already_flushing_stq=False,
                    idempotency_token=None,
                    extra_action=None,
            ):
                fun = (
                    self._wrapper.run_pipeline
                    if already_flushing_stq
                    else self._wrapper.run_pipeline_with_flushing
                )
                return fun(
                    self._scope,
                    self._queue,
                    item_id,
                    payload,
                    expect_fail=expect_fail,
                    stq_queue=stq_queue,
                    idempotency_token=idempotency_token,
                    eta=eta,
                    extra_action=extra_action,
                )

            def check_reschedule(self, item_id):
                return self._wrapper.check_reschedule(
                    self._scope, self._queue, item_id,
                )

            def call(
                    self, item_id, expect_fail=False, stq_queue=None, tag=None,
            ):
                return self._wrapper.call(
                    self._scope,
                    self._queue,
                    item_id,
                    expect_fail,
                    stq_queue,
                    tag,
                )

            def handle_single_event(
                    self,
                    item_id,
                    payload=None,
                    prev_state=None,
                    curr_state=None,
                    pipeline=None,
                    initial_state=None,
                    stage_id=None,
            ):
                return self._wrapper.handle_single_event(
                    self._scope,
                    self._queue,
                    item_id,
                    payload,
                    prev_state,
                    curr_state,
                    pipeline,
                    initial_state,
                    stage_id,
                )

            def events(self, item_id):
                return self._wrapper.events(self._scope, self._queue, item_id)

            def checkpoint(self, item_id):
                return self._wrapper.checkpoint(
                    self._scope, self._queue, item_id,
                )

        def __init__(
                self,
                taxi_processing,
                stq,
                taxi_config,
                get_file_path,
                load,
                mockserver,
        ):
            self._taxi_processing = taxi_processing
            self._stq = stq
            self._taxi_config = taxi_config
            self._get_file_path = get_file_path
            self._load = load
            self._mockserver = mockserver

        def __getattr__(self, scope):
            return self.Scope(self, scope)

        async def load_fs_configs(self, configs: List[ProcessingEntityConfig]):
            manifest: Dict = {}
            substitutions = []
            modules = []
            for cfg in configs:
                manifest_key, entity_key, entity = None, None, None
                if cfg.queue:
                    assert not entity
                    manifest_key, entity_key, entity = (
                        'queues',
                        'queue',
                        cfg.queue,
                    )
                if cfg.single_pipeline:
                    assert not entity
                    manifest_key, entity_key, entity = (
                        'pipelines',
                        'single_pipeline',
                        cfg.single_pipeline,
                    )
                assert entity is not None

                module_abs_path = self._get_file_path(cfg.module)
                module_code = yaml.load(
                    self._load(cfg.module), Loader=yaml.Loader,
                )
                module_name = module_code['module']
                config_vars = {}
                for key, var in cfg.config_vars.items():
                    if isinstance(var, util.UrlMock):
                        var = self._mockserver.url(var)
                    config_vars[key] = var
                substitutions.append(
                    {
                        'scope': cfg.scope,
                        entity_key: entity,
                        'vars': yaml.safe_dump(config_vars),
                    },
                )
                manifest.setdefault(manifest_key, []).append(
                    {
                        'scope': cfg.scope,
                        entity_key: entity,
                        'contents#xget': (
                            f'/external/{module_name}/{cfg.main_operator}'
                        ),
                    },
                )
                modules.append(
                    {
                        'modname': 'agl',
                        'isolation-key': {
                            'scope': cfg.scope,
                            entity_key: entity,
                        },
                        'path': str(module_abs_path),
                    },
                )

            if modules:
                overrides = {
                    'modules': modules,
                    'manifest': yaml.safe_dump(manifest),
                    'path-prefix': '',
                    'substutitions': substitutions,
                }
                response = await self._taxi_processing.post(
                    '/internal/deploy/v1/reload-from-fs',
                    json={'overrides': overrides},
                )
                assert response.status_code == 200, response.text
            else:
                response = await self._taxi_processing.post(
                    '/internal/deploy/v1/reload-from-fs', json={},
                )
                assert response.status_code == 200, response.text

        async def load_fs_queue_config(
                self,
                module,
                scope,
                queue,
                main_operator='main',
                **config_vars,
        ):
            config = ProcessingEntityConfig(
                module=module,
                scope=scope,
                queue=queue,
                main_operator=main_operator,
                config_vars=config_vars,
            )
            return await self.load_fs_configs([config])

        async def load_fs_pipeline_config(
                self,
                module,
                scope,
                pipeline,
                main_operator='main',
                **config_vars,
        ):
            config = ProcessingEntityConfig(
                module=module,
                scope=scope,
                single_pipeline=pipeline,
                main_operator=main_operator,
                config_vars=config_vars,
            )
            return await self.load_fs_configs([config])

        async def send_event_with_flushing(
                self,
                scope,
                queue,
                item_id,
                payload,
                expect_fail=False,
                stq_queue=None,
                eta=None,
                idempotency_token=None,
                extra_action=None,
                tag=None,
        ):
            with self._stq.flushing():
                event_id = await self.send_event(
                    scope=scope,
                    queue=queue,
                    item_id=item_id,
                    payload=payload,
                    expect_fail=expect_fail,
                    stq_queue=stq_queue,
                    eta=eta,
                    idempotency_token=idempotency_token,
                    extra_action=extra_action,
                    tag=tag,
                )
                return event_id

        async def run_pipeline_with_flushing(
                self,
                scope,
                single_pipeline,
                item_id,
                payload,
                expect_fail=False,
                stq_queue=None,
                eta=None,
                idempotency_token=None,
                extra_action=None,
        ):
            with self._stq.flushing():
                item_id = await self.run_pipeline(
                    scope=scope,
                    single_pipeline=single_pipeline,
                    item_id=item_id,
                    payload=payload,
                    expect_fail=expect_fail,
                    stq_queue=stq_queue,
                    eta=eta,
                    idempotency_token=idempotency_token,
                    extra_action=extra_action,
                )
                return item_id

        async def checkpoint(self, scope, queue, item_id):
            result = await self._taxi_processing.get(
                f'/v1/{scope}/{queue}/checkpoint', params={'item_id': item_id},
            )
            assert result.status in (200, 404)
            return result.json() if result.status == 200 else None

        async def send_event(
                self,
                scope,
                queue,
                item_id,
                payload,
                expect_fail=False,
                stq_queue=None,
                eta=None,
                idempotency_token=None,
                extra_action=None,
                tag=None,
        ):
            # create event's draft
            params = {'item_id': item_id}
            if eta is not None:
                params['due'] = eta.replace(tzinfo=pytz.UTC).isoformat()
            post_kwargs = {
                'data' if isinstance(payload, str) else 'json': payload,
            }
            if idempotency_token is None:
                idempotency_token = uuid.uuid4().hex
            result = await self._taxi_processing.post(
                f'/v1/{scope}/{queue}/create-event',
                params=params,
                headers={'X-Idempotency-Token': idempotency_token},
                **post_kwargs,
            )
            assert result.status_code == 200
            event_id = result.json()['event_id']

            # ensure event was put into STQ
            if stq_queue is None:
                stq_queue = f'{scope}_{queue}'
            # 1: only call to process event (flushing)
            # 2: first call to process event, second to dispose (not flushing)
            times_called = self._stq[stq_queue].times_called
            assert times_called in (1, 2)

            if times_called == 2:
                # reschedule call (for dispose)
                call = self._stq[stq_queue].next_call()
                assert not call['args']
                assert not call['kwargs']
                assert call['id'] == f'{scope}_{queue}_{item_id}'

            # event handling call
            call = self._stq[stq_queue].next_call()
            assert call['args'] == [scope, queue, item_id]
            assert call['kwargs'].pop('log_extra', None) is not None
            assert call['kwargs'] == {}
            assert call['id'] == f'{scope}_{queue}_{item_id}'

            if extra_action is not None:
                await extra_action(event_id)

            await self.call(scope, queue, item_id, expect_fail, stq_queue, tag)
            return event_id

        async def run_pipeline(
                self,
                scope,
                single_pipeline,
                item_id,
                payload,
                expect_fail=False,
                stq_queue=None,
                eta=None,
                idempotency_token=None,
                extra_action=None,
        ):
            # create task's draft
            params = {'item_id': item_id}
            if eta is not None:
                params['due'] = eta.replace(tzinfo=pytz.UTC).isoformat()
            post_kwargs = {'json': payload}
            if idempotency_token is None:
                idempotency_token = uuid.uuid4().hex
            result = await self._taxi_processing.post(
                f'/v1/{scope}/{single_pipeline}/run-pipeline',
                headers={'X-Idempotency-Token': idempotency_token},
                params=params,
                **post_kwargs,
            )

            if result.status_code == 409:
                raise ValueError('Race condition during task creation')

            assert result.status_code == 200
            item_id = result.json()['item_id']

            # ensure task was put into STQ
            if stq_queue is None:
                stq_queue = f'{scope}_{single_pipeline}'
            # call to process task (flushing)
            times_called = self._stq[stq_queue].times_called
            assert times_called == 1

            # task handling call
            call = self._stq[stq_queue].next_call()
            assert call['args'] == [scope, single_pipeline, item_id]
            assert call['kwargs'].pop('log_extra', None) is not None
            assert call['kwargs'] == {}
            assert call['id'] == f'{scope}_{single_pipeline}_{item_id}'

            if extra_action is not None:
                await extra_action(item_id)

            await self.call(
                scope, single_pipeline, item_id, expect_fail, stq_queue,
            )
            return item_id

        async def check_reschedule(
                self, scope, single_pipeline, item_id, stq_queue=None,
        ):
            if stq_queue is None:
                stq_queue = f'{scope}_{single_pipeline}'
            call = self._stq[stq_queue].next_call()
            assert not call['args']
            assert not call['kwargs']
            assert call['id'] == f'{scope}_{single_pipeline}_{item_id}'

        async def events(self, scope, queue, item_id):
            result = await self._taxi_processing.get(
                f'/v1/{scope}/{queue}/events', params={'item_id': item_id},
            )
            assert result.status_code == 200
            return result.json()

        async def call(
                self,
                scope,
                queue,
                item_id,
                expect_fail=False,
                stq_queue=None,
                tag=None,
        ):
            if stq_queue is None:
                stq_queue = f'{scope}_{queue}'

            # call STQ worker to do processing iteration
            stq_runnable = stq_worker_conftest_plugin.StqQueueCaller(
                stq_queue, taxi_processing,
            )
            return await stq_runnable.call(
                task_id=f'{scope}_{queue}_{item_id}',
                args=[scope, queue, item_id],
                expect_fail=expect_fail,
                tag=tag,
            )

        async def handle_single_event(
                self,
                scope,
                queue,
                item_id,
                payload=None,
                prev_state=None,
                curr_state=None,
                pipeline=None,
                initial_state=None,
                stage_id=None,
        ):
            if not payload:
                payload = {}
            request = {
                'event': payload,
                'prev_state': prev_state,
                'current_state': curr_state,
            }
            if pipeline is not None:
                request['pipeline'] = pipeline
                if stage_id is not None:
                    request['stage'] = {
                        'id': stage_id,
                        'shared_state': initial_state or {},
                    }
            response = await taxi_processing.post(
                f'/tests/v1/handle-event/{scope}/{queue}',
                params={'item_id': item_id},
                json=request,
            )
            assert response.status_code == 200
            return response.json()

    return ProcessingWrapper(
        taxi_processing, stq, taxi_config, get_file_path, load, mockserver,
    )


@pytest.fixture(autouse=True)
async def processing_queue_config(request, processing):
    configs: List[ProcessingEntityConfig] = []
    for marker in request.node.iter_markers('processing_queue_config'):
        config = ProcessingEntityConfig(
            module=marker.args[0],
            scope=marker.kwargs['scope'],
            queue=marker.kwargs['queue'],
            main_operator=marker.kwargs.get('main_operator', 'main'),
            config_vars={
                key: var
                for key, var in marker.kwargs.items()
                if key not in ('scope', 'queue', 'main_operator')
            },
        )
        configs.append(config)

    if configs:
        await processing.load_fs_configs(configs)
        yield
        await processing.load_fs_configs([])
    else:
        yield


@pytest.fixture(autouse=True)
async def processing_pipeline_config(request, processing):
    configs: List[ProcessingEntityConfig] = []
    for marker in request.node.iter_markers('processing_pipeline_config'):
        config = ProcessingEntityConfig(
            module=marker.args[0],
            scope=marker.kwargs['scope'],
            single_pipeline=marker.kwargs['single_pipeline'],
            main_operator=marker.kwargs.get('main_operator', 'main'),
            config_vars={
                key: var
                for key, var in marker.kwargs.items()
                if key not in ('scope', 'single_pipeline', 'main_operator')
            },
        )
        configs.append(config)

    if configs:
        await processing.load_fs_configs(configs)
        yield
        await processing.load_fs_configs([])
    else:
        yield
