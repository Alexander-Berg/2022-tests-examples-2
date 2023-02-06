from __future__ import absolute_import, division, print_function

import pytest

from sandbox.projects.yabs.sandbox_task_tracing.test.lib.mocks import (
    TASK_DEFAULTS,
    mock_task,
    patch_current_task_property,
)

from sandbox.projects.yabs.sandbox_task_tracing.info import task_info


@pytest.mark.parametrize('format_', (None, 'brief', 'full'))
def test_task_info(format_):
    with patch_current_task_property(dict(current_task=False)):
        task = mock_task()
        result = task_info(task, **({} if format_ is None else dict(format_=format_)))
        assert result['id'] == TASK_DEFAULTS['task_id']
        assert result['task_type'] == TASK_DEFAULTS['type']
        assert result['type']['name'] == type(task).__name__
        assert result['type']['module'] == type(task).__module__
        if format_ == 'full':
            assert result['_raw']['id'] == TASK_DEFAULTS['task_id']
            assert result['audit'][-1]['status'] == 'EXECUTING'
            assert result['gsid']['_raw'] == TASK_DEFAULTS['gsid']
