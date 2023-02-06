from __future__ import absolute_import, division, print_function

import pytest

import traceback

from sandbox.projects.yabs.sandbox_task_tracing.info import (
    set_tracing_files_prefix,
    stack_info,
)
from sandbox.projects.yabs.sandbox_task_tracing.util import frozendict


def get_stack():
    return traceback.extract_stack()


def generate_stack_info(stack_info_spec=(), set_tracing_files_prefix_here=False):
    stack_info_spec = frozendict(exclude_tracing_files=False, last_frame=True, traceback=True) + stack_info_spec
    set_tracing_files_prefix(__file__ + ('' if set_tracing_files_prefix_here else '/not/here'))
    return stack_info(get_stack(), stack_info_spec=stack_info_spec)


def simplified_frame_info(frame_info):
    assert set(frame_info) >= {'filename', 'line', 'lineno', 'name'}
    return {key: frame_info[key] for key in ('filename', 'name')}


@pytest.mark.parametrize('last_frame', (False, True))
@pytest.mark.parametrize('traceback', (False, True))
def test_stack_info_stack_info_parts_enabled(last_frame, traceback):
    result = generate_stack_info(stack_info_spec=dict(last_frame=last_frame, traceback=traceback))
    assert ('last_frame' in result) == last_frame
    assert ('traceback' in result) == traceback
    if last_frame:
        last_frame_info = result['last_frame']
        assert simplified_frame_info(last_frame_info) == dict(filename=__file__, name=get_stack.__name__)
    if traceback:
        traceback_info = result['traceback']
        for frame_info in traceback_info:
            assert simplified_frame_info(frame_info)
        assert simplified_frame_info(traceback_info[-1]) == dict(filename=__file__, name=get_stack.__name__)
        assert simplified_frame_info(traceback_info[-2]) == dict(filename=__file__, name=generate_stack_info.__name__)


@pytest.mark.parametrize('exclude_tracing_files', (False, True))
@pytest.mark.parametrize('set_tracing_files_prefix_here', (False, True))
def test_stack_info_exclude_tracing_files(exclude_tracing_files, set_tracing_files_prefix_here):
    result = generate_stack_info(
        stack_info_spec=dict(exclude_tracing_files=exclude_tracing_files),
        set_tracing_files_prefix_here=set_tracing_files_prefix_here,
    )
    assert (result['last_frame']['filename'] != __file__) == (exclude_tracing_files and set_tracing_files_prefix_here)
    assert (result['traceback'][-1]['filename'] != __file__) == (exclude_tracing_files and set_tracing_files_prefix_here)
