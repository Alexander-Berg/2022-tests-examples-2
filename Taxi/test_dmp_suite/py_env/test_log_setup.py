import pytest

from dmp_suite.py_env.log_setup import TskvFormatter


truncate_formatter = TskvFormatter()
truncate_formatter.MAX_PAYLOAD_SIZE = 6
truncate_formatter._MAX_NON_TRUNCATED_SIZE = 2


@pytest.mark.parametrize('term, expected', [
    ('ё', 'ё'),
    ('z', 'z'),
    ('ёё', 'ёё'),
    ('ёёё', 'ёёё'),
    ('ё'*10, 'ёёё... truncated'),
    # исходная строка состоит из 7 байт, после отсечения байтов
    # шестой байт - невалидны символ utf8, decode должен проигнорировать ошибку
    ('zzzzzё', 'z'*5 + '... truncated'),
])
def test_truncate_term(term, expected):
    assert truncate_formatter._truncate_term(term) == expected
