from __future__ import absolute_import, division, print_function

from sandbox.projects.yabs.sandbox_task_tracing.test.lib.mocks import (
    RESOURCE_DEFAULTS,
    mock_resource,
)

from sandbox.projects.yabs.sandbox_task_tracing.info import resource_info


def test_resource_info():
    resource = mock_resource()
    result = resource_info(resource)

    assert result['id'] == RESOURCE_DEFAULTS['resource_id']

    assert isinstance(result['path'], str)
    assert result['path'] == str(RESOURCE_DEFAULTS['path'])

    assert isinstance(result['size'], int)
    assert result['size'] == RESOURCE_DEFAULTS['size']

    assert isinstance(result['state'], str)
    assert result['state'] == RESOURCE_DEFAULTS['state']

    assert result['type']['name'] == type(resource).__name__
    assert result['type']['module'] == type(resource).__module__


def test_incomplete_resource_info():
    resource = mock_resource(fields=())
    result = resource_info(resource)

    assert result['id'] == RESOURCE_DEFAULTS['resource_id']

    assert result['path'] is None
    assert result['size'] is None
    assert result['state'] is None

    assert result['type']['name'] == type(resource).__name__
    assert result['type']['module'] == type(resource).__module__
