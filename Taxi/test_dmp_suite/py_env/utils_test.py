import logging
import os

from mock import patch, MagicMock

from dmp_suite.datetime_utils import timestamp
from dmp_suite.tskv import dict_to_tskv
from dmp_suite.py_env.log_setup import TskvFormatter
from dmp_suite.py_env.utils import extract_python_module, safe_init
from dmp_suite.string_utils import to_bytes


def test_extract_python_module():
    assert 'aaa' == extract_python_module('python -m aaa')
    assert 'a.b.c' == extract_python_module('python -m a.b.c')
    assert 'a_b.b.c' == extract_python_module('python -m a_b.b.c')
    assert 'a.b.c' == extract_python_module('python  -m\t  \t\t a.b.c')
    assert 'a.b.c' == extract_python_module('python -m a.b.c ')
    assert 'a.b.c' == extract_python_module('python -m a.b.c\t \t')
    assert 'a.b.c' == extract_python_module('python -m a.b.c -d asdf')
    assert 'a.b.c' == extract_python_module('ENV=VAL python -m a.b.c -d asdf')
    assert '' == extract_python_module('python /path/to/file')
    assert '' == extract_python_module('asdfasdf')
    assert '' == extract_python_module('')
    assert '' == extract_python_module('python -mmm a.b.c')
    assert '' == extract_python_module('python  -m  \t a,b.c')


def test_safe_init():
    def f():
        return 1

    test_func = safe_init(exclude_predicates=lambda: True)(f)
    assert test_func() is None

    test_func = safe_init(exclude_predicates=lambda: True,
                          default_return_value=2)(f)
    assert 2 == test_func()

    test_func = safe_init(exclude_predicates=lambda: False,
                          default_return_value=2)(f)
    assert 1 == test_func()

    test_func = safe_init(exclude_predicates=(lambda: False, lambda: True),
                          default_return_value=2)(f)
    assert 2 == test_func()


def test_tskv_encode():
    result = dict_to_tskv({'msg': 'Сообщение об ошибке'})
    assert result == 'msg=Сообщение об ошибке'
    assert type(result) is str

    result = dict_to_tskv({'msg': to_bytes('Сообщение об ошибке')})
    assert result == 'msg=Сообщение об ошибке'
    assert type(result) is str


@patch.dict(os.environ, {'TAXIDWH_RUN_ID': '22053fbf-532a-45f7-952e-66e4621ef4b0',
                         'TAXIDWH_TASK': 'unit-test',
                         '_SCRIPT_INFO_ID': 'e77e8bd43fc8429f826f4fa0029c2875'})
@patch('dmp_suite.py_env.log_setup.get_hostname', MagicMock(return_value='taxi-dwh.yandex.net'))
@patch('dmp_suite.py_env.utils.get_username', MagicMock(return_value='thebob'))
@patch('dmp_suite.py_env.utils.get_python_module', MagicMock(return_value=''))
@patch('dmp_suite.py_env.log_setup._taxidwh_task', 'unit-test')
@patch('version.__version__', '0.0')
def test_tskv_formatter():
    formatter = TskvFormatter(application='unittests')

    record = logging.LogRecord(
        name='foo',
        level=logging.ERROR,
        pathname='foo.py',
        lineno=100500,
        msg='Что-то случилось!',
        args=(),
        exc_info=None,
    )
    record.created = timestamp('2019-12-04 07:10:25')  # Current time in UTC
    record.process = 42

    result = formatter.format(record)
    assert type(result) is str
    expected_msg = '\t'.join([
        'python-taxidwh: tskv',
        'moscow_dttm=2019-12-04 10:10:25.000000',
        'timestamp=2019-12-04 10:10:25.000000',
        'logger=foo',
        'level=ERROR',
        'msg=Что-то случилось!',
        'taxidwh_run_id=22053fbf-532a-45f7-952e-66e4621ef4b0',
        'taxidwh_task=unit-test',
        'pid=42',
        'host=taxi-dwh.yandex.net',
        'utc_dttm=2019-12-04 07:10:25.000000',
        'status=',
        'user=thebob',
        'version=0.0',
        'taxidwh_python_module=',
        'application=unittests',
        'script_id=e77e8bd43fc8429f826f4fa0029c2875'
    ])
    assert result == expected_msg
