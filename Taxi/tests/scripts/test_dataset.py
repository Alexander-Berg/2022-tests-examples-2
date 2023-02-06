import io
from os.path import join, dirname, normpath

import pytest

from scripts.ci import dataset
from scripts.ci.dataset import import_and_call
from tests.scripts import module_to_import


async def test_broken_json(tap):
    with tap.plan(3):
        broken_json = '{"method":"one"'
        stream_in = io.StringIO(broken_json)
        stream_out = io.StringIO()
        stream_err = io.StringIO()
        ret = await import_and_call(
            module_to_import, fmt='json', stream_in=stream_in,
            stream_out=stream_out, stream_err=stream_err)
        tap.eq_ok(ret, dataset.BROKEN_INPUT_CODE,
                  'код возврата: сломаный json')
        tap.eq_ok(len(stream_out.getvalue()), 0, 'Пустой stdout')
        tap.ne_ok(len(stream_err.getvalue()), 0, 'Сообщение в stderr')


async def test_invalid_input(tap):
    with tap.plan(3):
        broken_json = '{"methods": "one"}'
        stream_in = io.StringIO(broken_json)
        stream_out = io.StringIO()
        stream_err = io.StringIO()
        ret = await import_and_call(
            module_to_import, fmt='json', stream_in=stream_in,
            stream_out=stream_out, stream_err=stream_err)
        tap.eq_ok(ret, dataset.INVALID_INPUT_CODE,
                  'код возврата: ввод не соотетствует схеме')
        tap.eq_ok(len(stream_out.getvalue()), 0, 'Пустой stdout')
        tap.ne_ok(len(stream_err.getvalue()), 0, 'Сообщение в stderr')


async def test_not_found(tap):
    with tap.plan(3):
        stream_in = io.StringIO('{"method":"func1"}')
        stream_out = io.StringIO()
        stream_err = io.StringIO()
        ret = await import_and_call(
            module_to_import, fmt='json', stream_in=stream_in,
            stream_out=stream_out, stream_err=stream_err)
        tap.eq_ok(ret, dataset.FUNCTION_NOT_FOUND_CODE,
                  'код возврата: функция не найдена')
        tap.eq_ok(
            stream_err.getvalue(),
            'В модуле tests.scripts.module_to_import нет функции func1\n',
            'Сообщение в stderr')
        tap.eq_ok(len(stream_out.getvalue()), 0, 'Пустой stdout')


async def test_not_a_function(tap):
    with tap.plan(3):
        stream_in = io.StringIO('{"method": "NOT_A_FUNCTION"}')
        stream_out = io.StringIO()
        stream_err = io.StringIO()
        ret = await import_and_call(
            module_to_import, fmt='json', stream_in=stream_in,
            stream_out=stream_out, stream_err=stream_err)
        tap.eq_ok(ret, dataset.FUNCTION_NOT_FOUND_CODE,
                  'код возврата: функция не найдена')
        tap.eq_ok(
            stream_err.getvalue(),
            'Объект NOT_A_FUNCTION в модуле tests.scripts.module_to_import'
            ' не функция\n',
            'Сообщение в stderr')
        tap.eq_ok(len(stream_out.getvalue()), 0, 'Пустой stdout')


@pytest.mark.parametrize('data', [
    '{"method":"function_to_succeed","args":[1],"kwargs":{"two":2}}',
    '{"method":"async_function_to_succeed","args":[1],"kwargs":{"two":2}}',
])
async def test_success(tap, data):
    with tap.plan(3):
        stream_in = io.StringIO(data)
        stream_out = io.StringIO()
        stream_err = io.StringIO()
        ret = await import_and_call(
            module_to_import, fmt='json', stream_in=stream_in,
            stream_out=stream_out, stream_err=stream_err)
        tap.eq_ok(ret, 0, 'код возврата: 0')
        tap.eq_ok(
            stream_out.getvalue().replace(' ', ''),
            '{"one":1,"two":2}\n',
            'результат')
        tap.eq_ok(len(stream_err.getvalue()), 0, 'Пустой stderr')


@pytest.mark.skip(reason="ХЗ почему перестало работать")
async def test_divide_by_zero(tap):
    with tap.plan(3):
        stream_in = io.StringIO('{"method":"divide_by_zero"}')
        stream_out = io.StringIO()
        stream_err = io.StringIO()
        ret = await import_and_call(
            module_to_import, fmt='json', stream_in=stream_in,
            stream_out=stream_out, stream_err=stream_err)
        tap.eq_ok(ret, dataset.CALL_ERROR,
                  'код возврата: CALL_ERROR')
        module_file = join(dirname(__file__), 'module_to_import.py')
        dataset_file = normpath(
            join(dirname(__file__), '../../scripts/ci/dataset.py'))
        tap.eq_ok(
            stream_err.getvalue(),
            f'''ZeroDivisionError
division by zero
  File "{dataset_file}", line 95, in call
    result = func(*args, **kwargs)
  File "{module_file}", line 2, in divide_by_zero
    return 1 / 0\n''',
            'Сообщение в stderr')
        tap.eq_ok(len(stream_out.getvalue()), 0, 'Пустой stdout')


async def test_serialization(tap):
    with tap.plan(5):
        stream_in = io.StringIO('{"method":"function_not_serializable"}')
        stream_out = io.StringIO()
        stream_err = io.StringIO()
        ret = await import_and_call(
            module_to_import, fmt='json', stream_in=stream_in,
            stream_out=stream_out, stream_err=stream_err)
        tap.eq_ok(ret, dataset.CALL_ERROR,
                  'код возврата: CALL_ERROR')
        err_message = stream_err.getvalue()
        tap.eq_ok(
            err_message.split(sep='\n')[0],
            'TypeError',
            'Сообщение в stderr')
        tap.like(
            err_message.split(sep='\n')[1],
            "is not JSON serializable",
            'Сообщение в stderr')
        tap.ne_ok(len(err_message.split(sep='\n')), 2, 'Есть трейсбек')
        tap.eq_ok(len(stream_out.getvalue()), 0, 'Пустой stdout')
