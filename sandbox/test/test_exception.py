from __future__ import absolute_import, division, print_function

import pytest

import sys

from sandbox.projects.yabs.sandbox_task_tracing.info import (
    exception_info,
    set_tracing_files_prefix,
)
from sandbox.projects.yabs.sandbox_task_tracing.util import frozendict


class SomeError(Exception):
    pass


def raise_some_error():
    raise SomeError()


def generate_exception_info(stack_info_enabled=False, stack_info_spec=frozendict(), set_tracing_files_prefix_here=False):
    stack_info_spec = frozendict(exclude_tracing_files=False, last_frame=True, traceback=True) + stack_info_spec
    set_tracing_files_prefix(__file__ + ('' if set_tracing_files_prefix_here else '/not/here'))
    try:
        raise_some_error()
    except SomeError:
        exception_type, exception_value, exception_traceback = sys.exc_info()
        result = exception_info(
            exception_type=exception_type,
            exception_value=exception_value,
            exception_traceback=exception_traceback,
            stack_info_enabled=stack_info_enabled,
            stack_info_spec=stack_info_spec,
        )
    assert result['type']['name'] == 'SomeError'
    assert result['type']['module'] == SomeError.__module__
    return result


def test_exception_info():
    generate_exception_info()


@pytest.mark.parametrize('stack_info_enabled', (False, True))
def test_exception_info_stack_info_enabled(stack_info_enabled):
    result = generate_exception_info(stack_info_enabled=stack_info_enabled, stack_info_spec={})
    assert ('stack' in result) == stack_info_enabled


def simplified_frame_info(frame_info):
    assert set(frame_info) >= {'filename', 'line', 'lineno', 'name'}
    return {key: frame_info[key] for key in ('filename', 'name')}


@pytest.mark.parametrize('last_frame', (False, True))
@pytest.mark.parametrize('traceback', (False, True))
def test_exception_info_stack_info_parts_enabled(last_frame, traceback):
    result = generate_exception_info(stack_info_enabled=True, stack_info_spec=dict(last_frame=last_frame, traceback=traceback))
    assert ('last_frame' in result['stack']) == last_frame
    assert ('traceback' in result['stack']) == traceback
    if last_frame:
        last_frame_info = result['stack']['last_frame']
        assert simplified_frame_info(last_frame_info) == dict(filename=__file__, name=raise_some_error.__name__)
    if traceback:
        traceback_info = result['stack']['traceback']
        for frame_info in traceback_info:
            assert simplified_frame_info(frame_info)['filename'] == __file__
        assert simplified_frame_info(traceback_info[-1]) == dict(filename=__file__, name=raise_some_error.__name__)
        assert simplified_frame_info(traceback_info[-2]) == dict(filename=__file__, name=generate_exception_info.__name__)


@pytest.mark.parametrize('exclude_tracing_files', (False, True))
@pytest.mark.parametrize('set_tracing_files_prefix_here', (False, True))
def test_exception_info_exclude_tracing_files(exclude_tracing_files, set_tracing_files_prefix_here):
    result = generate_exception_info(
        stack_info_enabled=True,
        stack_info_spec=dict(exclude_tracing_files=exclude_tracing_files),
        set_tracing_files_prefix_here=set_tracing_files_prefix_here,
    )
    assert (result['stack']['last_frame'] is None) == (exclude_tracing_files and set_tracing_files_prefix_here)
    assert (len(result['stack']['traceback']) == 0) == (exclude_tracing_files and set_tracing_files_prefix_here)
