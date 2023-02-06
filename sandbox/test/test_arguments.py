from __future__ import absolute_import, division, print_function

import pytest

import six

from sandbox.projects.yabs.sandbox_task_tracing.info import (
    arguments_info,
    make_arguments_info_spec,
)


@pytest.mark.parametrize(
    'save_arguments',
    [
        'all',
        'positional',
        'keyword',
        [],
        [0, 1],
        ['argument1', 'argument2'],
        [0, 'argument1'],
        [1, 'argument2'],
        [0, 1, 'argument1', 'argument2'],
    ],
    ids=repr,
)
@pytest.mark.parametrize(
    ('args', 'kwargs'),
    [
        ([], dict()),
        ([1], dict()),
        ([1, 2], dict()),
        ([1], dict(argument2=2)),
        ([], dict(argument1=1)),
        ([], dict(argument2=2)),
        ([], dict(argument1=1, argument2=2)),
    ],
    ids=repr,
)
def test_arguments_info(args, kwargs, save_arguments):
    arguments_info_spec = make_arguments_info_spec(save_arguments)
    result = arguments_info(args, kwargs, arguments_info_spec)
    save_arguments_set = set() if isinstance(save_arguments, str) else set(save_arguments)
    if save_arguments in ('all', 'positional') or (save_arguments_set & {0, 1}):
        saved_args = result['args']
        assert len(saved_args) == len(args)
        for index, value in enumerate(args):
            if save_arguments in ('all', 'positional') or index in save_arguments_set:
                assert saved_args[index] == value
            else:
                assert saved_args[index] is None
    if save_arguments in ('all', 'keyword') or (save_arguments_set & {'argument1', 'argument2'}):
        saved_kwargs = result['kwargs']
        for key, value in six.iteritems(kwargs):
            if save_arguments in ('all', 'keyword') or key in save_arguments_set:
                assert saved_kwargs[key] == value
            else:
                assert key not in saved_kwargs
