from __future__ import absolute_import, division, print_function

import pytest

from sandbox.projects.yabs.sandbox_task_tracing.info import command_info


@pytest.mark.parametrize('type_', (iter, list, str, tuple), ids=(lambda type_: type_.__name__))
def test_command_info_iter(type_):
    command = 'ls -l "1 2" 3' if type_ is str else type_(('ls', '-l', '1 2', 3))
    assert command_info(command) == ['ls', '-l', '1 2', '3']
