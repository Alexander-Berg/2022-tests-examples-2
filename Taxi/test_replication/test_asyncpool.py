import itertools
import random
import traceback

import pytest

from replication import asyncpool


class PoolError(Exception):
    def __init__(self, name):
        super().__init__()
        self.pool_error_key = name


ARGS = ('testarg1', 'testarg2')
KWARGS = {'kwarg_1': 'testkwargs1', 'kwarg_2': 'testkwargs1'}


async def _coro(*args, **kwargs):
    _assertion(*args, **kwargs)
    return 'coro'


async def _failed_coro(*args, **kwargs):
    _assertion(*args, **kwargs)
    raise PoolError('failed_coro')


def _not_coro(*args, **kwargs):
    _assertion(*args, **kwargs)
    return 'not_coro'


def _failed_not_coro(*args, **kwargs):
    _assertion(*args, **kwargs)
    raise PoolError('failed_not_coro')


FUNCS = {
    'coro': _coro,
    'failed_coro': _failed_coro,
    'failed_not_coro': _failed_not_coro,
    'not_coro': _not_coro,
}
ALL_TYPES = sorted(FUNCS.keys())


@pytest.mark.parametrize('concurrency', [1, 4])
@pytest.mark.parametrize(
    'funcs_info',
    [
        {tp: value for tp, value in zip(ALL_TYPES, state)}
        for state in sorted(itertools.product([0, 2], [0, 4], [0, 6], [0, 3]))
        if state != (0, 0, 0, 0)
    ],
)
@pytest.mark.nofilldb()
async def test_pool(concurrency, funcs_info):
    with asyncpool.AsyncPool(concurrency, set_default_executor=True) as pool:
        for run_num in range(2):
            funcs = _get_test_funcs(funcs_info)
            counter = {key: 0 for key in FUNCS}

            for num, func in funcs:
                pool.put(num, func, *ARGS, **KWARGS)

            task_ids = []
            for task_id, is_success, result in await pool.get_results():
                task_ids.append(task_id)
                if is_success:
                    counter[result] += 1
                else:
                    counter[result.pool_error_key] += 1

            assert sorted(task_ids) == list(range(len(funcs)))
            assert funcs_info == counter, 'attempt %d failed' % run_num


@pytest.mark.parametrize('concurrency', [1, 2])
@pytest.mark.nofilldb()
async def test_pool_single_exception(concurrency):
    async def func_with_exception():
        raise Exception('inner error')

    with asyncpool.AsyncPool(concurrency) as pool:
        for num in range(4):
            pool.put(num, func_with_exception)
        try:
            await pool.wait_and_raise_if_errors('pool_with_single_raise')
        except asyncpool.ExecutionError as error:
            traceback_list = traceback.format_exception(
                type(error), error, error.__traceback__,
            )
            assert traceback_list
            assert (
                '\nThe above exception was the direct cause of '
                'the following exception:\n\n' not in traceback_list
            )
            assert (
                '\nDuring handling of the above exception, '
                'another exception occurred:\n\n' not in traceback_list
            )


@pytest.mark.parametrize('concurrency', [1, 2])
@pytest.mark.nofilldb()
async def test_pool_chained_exception(concurrency):
    async def inner_func_with_exception():
        raise Exception()

    async def outer_func_with_exception():
        try:
            await inner_func_with_exception()
        except Exception as exc:
            raise Exception() from exc

    with asyncpool.AsyncPool(concurrency) as pool:
        for num in range(4):
            pool.put(num, outer_func_with_exception)
        try:
            await pool.wait_and_raise_if_errors('pool_with_chained_raise')
        except asyncpool.ExecutionError as error:
            traceback_list = traceback.format_exception(
                type(error), error, error.__traceback__,
            )
            assert traceback_list
            assert (
                '\nThe above exception was the direct cause of '
                'the following exception:\n\n' in traceback_list
            )


def _assertion(*args, **kwargs):
    assert args == ARGS
    assert kwargs == KWARGS


def _get_test_funcs(funcs_info):
    funcs = []
    func_num = 0

    for func_name, value in funcs_info.items():
        func = FUNCS[func_name]
        for _ in range(value):
            funcs.append((func_num, func))
            func_num += 1

    random.shuffle(funcs)
    return funcs
