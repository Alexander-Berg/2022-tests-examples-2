import pytest
import contextlib

from functools import partial

from dmp_suite.yt.task.processing import TaskProcessing


@contextlib.contextmanager
def dummy_context(lst: list, x):
    lst.append(x)
    yield
    lst.remove(x)


def test_processing_1():
    _lst = []
    cont_1 = partial(dummy_context, _lst)
    cont_2 = partial(dummy_context, _lst)
    cont_3 = partial(dummy_context, _lst)

    _proc = TaskProcessing(cont_1, cont_2, cont_3)

    with _proc.context(123):
        assert _lst == [123, 123, 123]
    assert _lst == []


def test_processing_2():
    _lst = []
    cont_1 = TaskProcessing.no_args_context(dummy_context)(_lst, 1)
    cont_2 = TaskProcessing.no_args_context(dummy_context)(_lst, 2)
    cont_3 = TaskProcessing.no_args_context(dummy_context)(_lst, 3)

    _proc = TaskProcessing(cont_1, cont_2, cont_3)

    with _proc.context(123):
        assert _lst == [1, 2, 3]
    assert _lst == []


def test_processing_plus():
    _lst = []
    cont_1 = TaskProcessing.no_args_context(dummy_context)(_lst, 1)
    cont_2 = partial(dummy_context, _lst)
    cont_3 = TaskProcessing.no_args_context(dummy_context)(_lst, 3)

    _proc_1 = TaskProcessing(cont_1)
    _proc_2 = TaskProcessing(cont_3, cont_2)

    with (_proc_1 + _proc_2).context(123):
        assert _lst == [1, 3, 123]
    assert _lst == []


def test_processing_plus_not_processing():
    _lst = []
    cont_1 = TaskProcessing.no_args_context(dummy_context)(_lst, 1)

    def cont_2(_):
        _lst.append(2)
        yield
        _lst.remove(2)

    def cont_3(_):
        _lst.append(3)
        yield
        _lst.remove(3)

    _proc_1 = TaskProcessing(cont_1)

    with (_proc_1 + cont_2 + cont_3).context(123):
        assert _lst == [1, 2, 3]
    assert _lst == []
    with (cont_2 + _proc_1).context(123):
        assert _lst == [2, 1]
    assert _lst == []
    with (cont_3 + _proc_1).context(123):
        assert _lst == [3, 1]
    assert _lst == []
