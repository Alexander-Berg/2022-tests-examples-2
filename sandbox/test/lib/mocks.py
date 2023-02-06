from __future__ import absolute_import, division, print_function

import datetime
import mock
import six

from sandbox.projects.yabs.sandbox_task_tracing.util import coalesce, frozendict


DEFAULT_ITERATION_STARTED_UTC = datetime.datetime(year=2022, month=2, day=28, hour=12, minute=35, second=12, microsecond=123456)
DEFAULT_ITERATION_STARTED_UTC_ISO = DEFAULT_ITERATION_STARTED_UTC.isoformat() + 'Z'
DEFAULT_ITERATION_STARTED_MICROSECONDS = int((DEFAULT_ITERATION_STARTED_UTC - datetime.datetime(1970, 1, 1)).total_seconds() * 1E6)

TASK_DEFAULTS = frozendict(
    audit=(
        frozendict(status='EXECUTING', time=DEFAULT_ITERATION_STARTED_UTC_ISO),
    ),
    current_task=True,
    gsid='ARCANUM:123',
    input_parameters=frozendict(dict_id='input_parameters'),
    iteration_id=102,
    other_tasks_spec=frozendict(),
    requirements=frozendict(semaphores='semaphores_value'),
    sandbox_exception=None,
    task_id=101,
    type='SANDBOX_TASK_TYPE',
)


def mock_server_task_info(spec=frozendict()):
    return dict(
        dict_id='server_task_info',
        id=spec.get('task_id', TASK_DEFAULTS['task_id']),
        input_parameters=spec.get('input_parameters', TASK_DEFAULTS['input_parameters']),
        requirements=spec.get('requirements', TASK_DEFAULTS['requirements']),
        type=spec.get('type', TASK_DEFAULTS['type']),
    )


def mock_server_task_context(spec=frozendict()):
    return {'__GSID': spec.get('gsid', TASK_DEFAULTS['gsid'])}


def mock_server_task(spec=frozendict()):
    result = mock.Mock(name='server_task')

    result.read = mock.Mock(return_value=mock_server_task_info(spec))

    result.audit = mock.Mock(name='server_task.audit')
    result.audit.read = mock.Mock(return_value=spec.get('audit', TASK_DEFAULTS['audit']))

    result.context = mock.Mock(name='server_task.context')
    result.context.read = mock.Mock(return_value=mock_server_task_context(spec))

    return result


def mock_server(spec=frozendict()):
    result = mock.Mock(name='server')
    spec = frozendict(spec)
    ids_task = {spec.get('task_id', TASK_DEFAULTS['task_id']): mock_server_task(spec)}
    for other_task_id, other_task_spec in six.iteritems(spec.get('other_tasks_spec', TASK_DEFAULTS['other_tasks_spec'])):
        other_task_spec = spec + frozendict(task_id=other_task_id) + other_task_spec
        assert other_task_spec['task_id'] == other_task_id
        if other_task_id in ids_task:
            raise ValueError('Task {} is already mocked'.format(other_task_id))
        ids_task[other_task_id] = mock_server_task(other_task_spec)
    result.task = ids_task
    return result


def mock_current_task(spec=frozendict()):
    result = mock.Mock(name='current_task')
    if spec.get('current_task', TASK_DEFAULTS['current_task']):
        result.id = spec.get('task_id', TASK_DEFAULTS['task_id'])
        result.agentr = mock.Mock(name='current_task.agentr')
        result.agentr.iteration = spec.get('iteration_id', TASK_DEFAULTS['iteration_id'])
    result.server = mock_server(spec)
    return result


def mock_current_task_property(spec=frozendict()):
    sandbox_exception = spec.get('sandbox_exception', TASK_DEFAULTS['sandbox_exception'])
    result = mock.PropertyMock(name='current_task_property')
    if sandbox_exception is None:
        result.return_value = mock_current_task(spec)
    else:
        result.side_effect = sandbox_exception
    return result


def patch_current_task_property(spec=frozendict()):
    return mock.patch('sandbox.sdk2.internal.task.TaskMeta.current', new=mock_current_task_property(spec))


def mock_task(task_id=None):
    result = mock.Mock(name='task_object')
    result.id = coalesce(task_id, TASK_DEFAULTS['task_id'])
    return result


RESOURCE_DEFAULTS = frozendict(
    resource_id=201,
    path=999,  # will test conversion to string
    size=301,
    state='READY',
)


def mock_resource(resource_id=None, fields=('path', 'size', 'state', 'type'), **kwargs):
    result = mock.Mock(name='resource', spec=('id',) + fields)
    result.id = coalesce(resource_id, RESOURCE_DEFAULTS['resource_id'])
    for field in fields:
        default = RESOURCE_DEFAULTS[field] if field != 'type' else type(result)
        setattr(result, field, kwargs.get(field, default))
    return result
