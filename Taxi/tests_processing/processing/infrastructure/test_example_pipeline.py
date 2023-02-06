import dataclasses
import datetime
import typing

import bson
import pytest

from tests_processing import util  # noqa


@pytest.mark.processing_pipeline_config(
    'simple-example.yaml',
    scope='testsuite_single_pipelines',
    single_pipeline='simple_example',
    example_resource=util.UrlMock('/resource'),
)
async def test_example_single_pipeline_simple(mockserver, processing):
    @mockserver.json_handler('/resource')
    async def mock_resource(request):
        assert request.content_type == 'application/json'
        assert request.method == 'GET'
        return {'foo': 'bar'}

    await processing.testsuite_single_pipelines.simple_example.run_pipeline(
        '123456789', payload={'foo': 'bar'},
    )

    assert mock_resource.times_called == 1


@pytest.mark.processing_pipeline_config(
    'simple-example.yaml',
    scope='testsuite_single_pipelines',
    single_pipeline='simple_example',
    example_resource=util.UrlMock('/resource'),
)
async def test_example_single_pipeline_exactly_once(mockserver, processing):
    @mockserver.json_handler('/resource')
    async def mock_resource(request):
        assert request.content_type == 'application/json'
        assert request.method == 'GET'
        return {'foo': 'bar'}

    await processing.testsuite_single_pipelines.simple_example.run_pipeline(
        '123456789', payload={'name': 'foo'}, idempotency_token='heh',
    )
    await processing.testsuite_single_pipelines.simple_example.run_pipeline(
        '123456789', payload={'name': 'bar'}, idempotency_token='heh',
    )
    assert mock_resource.times_called == 1


@pytest.mark.processing_pipeline_config(
    'simple-example.yaml',
    scope='testsuite_single_pipelines',
    single_pipeline='simple_example',
    example_resource=util.UrlMock('/resource'),
)
async def test_example_single_pipeline_race(mockserver, processing):
    @mockserver.json_handler('/resource')
    async def mock_resource(request):
        assert request.content_type == 'application/json'
        assert request.method == 'GET'
        return {'foo': 'bar'}

    await processing.testsuite_single_pipelines.simple_example.run_pipeline(
        '123456789', payload={'name': 'foo'}, idempotency_token='heh',
    )

    await processing.testsuite_single_pipelines.simple_example.run_pipeline(
        '123456789', payload={'name': 'bar'}, idempotency_token='heh',
    )

    with pytest.raises(ValueError):
        tsp = processing.testsuite_single_pipelines
        await tsp.simple_example.run_pipeline(
            '123456789', payload={'name': 'fizz'}, idempotency_token='hah',
        )

    assert mock_resource.times_called == 1


@pytest.mark.processing_pipeline_config(
    'calculate-example.yaml',
    scope='testsuite_single_pipelines',
    single_pipeline='calculate_example',
    login_resource=util.UrlMock('/login_resource'),
    password_resource=util.UrlMock('/password_resource'),
    credentials_resource=util.UrlMock('/credentials_resource'),
)
async def test_example_single_pipeline_login(mockserver, processing):
    @mockserver.json_handler('/login_resource')
    async def mock_login_resource(request):
        assert request.content_type == 'application/json'
        assert request.method == 'POST'
        assert request.json == {'name': 'Alex'}
        return {'login': 'alex'}

    @mockserver.json_handler('/password_resource')
    async def mock_password_resource(request):
        assert request.content_type == 'application/json'
        assert request.method == 'POST'
        assert request.json == {'login': 'alex'}
        return {'password': '1234'}

    @mockserver.json_handler('/credentials_resource')
    async def mock_credentials_resource(request):
        assert request.content_type == 'application/json'
        assert request.method == 'POST'
        assert request.json == {'credentials': 'alex:1234'}
        return {'status': 'welcome'}

    await processing.testsuite_single_pipelines.calculate_example.run_pipeline(
        '123456789', payload={'foo': 'bar'},
    )
    assert mock_login_resource.times_called == 1
    assert mock_password_resource.times_called == 1
    assert mock_credentials_resource.times_called == 1


@pytest.mark.pgsql('processing_db')
@pytest.mark.processing_pipeline_config(
    'args-example.yaml',
    scope='testsuite_single_pipelines',
    single_pipeline='args_example',
    example_resource=util.UrlMock('/resource'),
)
async def test_example_single_pipeline_args(mockserver, processing, pgsql):
    @mockserver.json_handler('/resource')
    async def mock_resource(request):
        cursor = pgsql['processing_db'].cursor()
        cursor.execute('SELECT created FROM processing.tasks')
        rows = list(cursor)
        created = rows[0][0].astimezone(tz=datetime.timezone.utc)
        assert request.content_type == 'application/json'
        assert request.method == 'POST'
        assert request.json['foo'] == 'bar'
        assert (
            datetime.datetime.strptime(
                request.json['created'], '%Y-%m-%dT%H:%M:%S.%f%z',
            )
            == created
        )
        assert request.json['item_id'] == '123456789'

    await processing.testsuite_single_pipelines.args_example.run_pipeline(
        '123456789', payload={'foo': 'bar'},
    )

    assert mock_resource.times_called == 1


@pytest.mark.processing_pipeline_config(
    'reschedule-example.yaml',
    scope='testsuite_single_pipelines',
    single_pipeline='reschedule_example',
    example_resource=util.UrlMock('/resource'),
)
async def test_example_single_pipeline_reschedule(mockserver, processing):
    @mockserver.json_handler('/resource')
    async def mock_resource(request):
        assert request.content_type == 'application/json'
        assert request.method == 'GET'
        response = {}
        if mock_resource.times_called == 0:
            response = {'reschedule-eta': 1}
        else:
            response = {'foo': 'bar'}
        return response

    tsp = processing.testsuite_single_pipelines
    await tsp.reschedule_example.run_pipeline(
        '123456789', payload={'foo': 'bar'}, already_flushing_stq=True,
    )
    await tsp.reschedule_example.check_reschedule('123456789')


@pytest.mark.processing_pipeline_config(
    'checkpoints-example.yaml',
    scope='testsuite_single_pipelines',
    single_pipeline='simple_example',
)
@pytest.mark.config(PROCESSING_MAINTAIN_IS_ARCHIVABLE=False)
@pytest.mark.parametrize(
    'enable_checkpoints',
    [
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    PROCESSING_ENABLE_SINGLE_PIPELINES_CHECKPOINTS={
                        'default': True,
                        'overrides': [],
                    },
                ),
            ],
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    PROCESSING_ENABLE_SINGLE_PIPELINES_CHECKPOINTS={
                        'default': False,
                        'overrides': [],
                    },
                ),
            ],
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    PROCESSING_ENABLE_SINGLE_PIPELINES_CHECKPOINTS={
                        'default': True,
                        'overrides': [
                            {
                                'scope': 'testsuite_single_pipelines',
                                'single_pipeline': 'simple_example',
                                'enabled': False,
                            },
                        ],
                    },
                ),
            ],
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    PROCESSING_ENABLE_SINGLE_PIPELINES_CHECKPOINTS={
                        'default': False,
                        'overrides': [
                            {
                                'scope': 'testsuite_single_pipelines',
                                'single_pipeline': 'simple_example',
                                'enabled': False,
                            },
                        ],
                    },
                ),
            ],
        ),
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    PROCESSING_ENABLE_SINGLE_PIPELINES_CHECKPOINTS={
                        'default': True,
                        'overrides': [
                            {
                                'scope': 'testsuite_single_pipelines',
                                'single_pipeline': 'simple_example',
                                'enabled': True,
                            },
                        ],
                    },
                ),
            ],
        ),
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    PROCESSING_ENABLE_SINGLE_PIPELINES_CHECKPOINTS={
                        'default': False,
                        'overrides': [
                            {
                                'scope': 'testsuite_single_pipelines',
                                'single_pipeline': 'simple_example',
                                'enabled': True,
                            },
                        ],
                    },
                ),
            ],
        ),
    ],
)
async def test_example_single_pipeline_checkpoints_usage(
        processing, mockserver, testpoint, enable_checkpoints,
):
    @testpoint('GetTask::IsCheckpointsEnabled')
    async def tp_checkpoints_enabled(data):
        assert data['checkpoint_enabled'] == enable_checkpoints

    await processing.testsuite_single_pipelines.simple_example.run_pipeline(
        '123456789', payload={'foo': 'bar'},
    )
    assert tp_checkpoints_enabled.times_called == 1


@pytest.mark.processing_pipeline_config(
    'fallback-example.yaml',
    scope='testsuite_single_pipelines',
    single_pipeline='fallback_example',
    deadline_fallback_resource_url=util.UrlMock('/fallback'),
    example_resource_a=util.UrlMock('/resource-a'),
    example_resource_b=util.UrlMock('/resource-b'),
)
@pytest.mark.parametrize(
    'enable_checkpoints',
    [
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    PROCESSING_ENABLE_CHECKPOINTS={
                        'default': True,
                        'overrides': [],
                    },
                ),
            ],
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    PROCESSING_ENABLE_CHECKPOINTS={
                        'default': False,
                        'overrides': [],
                    },
                ),
            ],
        ),
    ],
)
async def test_example_single_pipeline_fallback_usage(
        processing, mockserver, pgsql, testpoint, enable_checkpoints,
):
    item_id = '1234567890'

    @testpoint('handle-default')
    async def _tp_handle_default(data):
        pass

    @mockserver.json_handler('/resource-a')
    async def _mock_resource_a(request):
        assert request.content_type == 'application/json'
        assert request.method == 'GET'
        return {}  # this answer will cause fail in handler 'bar'

    @mockserver.json_handler('/fallback')
    def _mock_fallback(request):
        return {'result': 'ok'}

    # for state-1
    await processing.testsuite_single_pipelines.fallback_example.run_pipeline(
        item_id, {'foo': 'bar'}, expect_fail=True,
    )

    @dataclasses.dataclass
    class ProcessingTasksStateRow:
        scope: str
        single_pipeline: str
        item_id: str
        shared_state_bson: bytes
        stage: typing.Optional[str]
        finished_handlers: list
        handlers_result_bson: bytes

    cursor = pgsql['processing_noncritical_db'].cursor()
    cursor.execute(
        'SELECT scope, single_pipeline, item_id, shared_state_bson, stage, '
        'finished_handlers, handlers_result_bson '
        'FROM processing_noncritical.processing_tasks_state_v1',
    )
    row = ProcessingTasksStateRow(*list(cursor)[0])
    assert row.scope == 'testsuite_single_pipelines'
    assert row.single_pipeline == 'fallback_example'
    assert row.item_id == item_id
    assert bson.BSON.decode(row.shared_state_bson.tobytes()) == {
        'example-key': 'example-value',
    }
    assert row.stage == 'stage-2'
    assert row.finished_handlers == ['deadline-fallback']
    assert bson.BSON.decode(row.handlers_result_bson.tobytes()) == {
        'deadline-handler-result': {'result': 'ok'},
    }


@pytest.mark.processing_pipeline_config(
    'experiments-example.yaml',
    scope='testsuite_single_pipelines',
    single_pipeline='experiments_example',
    example_resource_a=util.UrlMock('/resource-a'),
    example_resource_b=util.UrlMock('/resource-b'),
)
@pytest.mark.experiments3(filename='exp-pipeline-level.json')
@pytest.mark.experiments3(filename='exp-stage-level.json')
@pytest.mark.experiments3(filename='exp-handler-level.json')
@pytest.mark.experiments3(filename='exp-single-pipeline-level.json')
async def test_example_single_pipelines_experiments(mockserver, processing):
    item_id = '123456789'

    @mockserver.json_handler('/resource-a')
    async def mock_resource_a(request):
        assert request.content_type == 'application/json'
        assert request.method == 'GET'
        return {'foo': 'bar'}

    @mockserver.json_handler('/resource-b')
    async def mock_resource_b(request):
        assert request.content_type == 'application/json'
        assert request.method == 'POST'
        assert request.json == {
            'shared-state': {
                'foo': 'bar',
                'example-key': 'example-value',
                'pipeline-exp': True,
                'stage-exp': True,
                'handler-exp': True,
                'single-pipeline-exp': True,
            },
        }
        return {}

    tsp = processing.testsuite_single_pipelines
    await tsp.experiments_example.run_pipeline(
        item_id, payload={'fizz': 'buzz'},
    )

    assert mock_resource_a.times_called == 1
    assert mock_resource_b.times_called == 1
