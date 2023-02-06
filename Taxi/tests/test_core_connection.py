import pytest
import psycopg2
from core.connection import replace_exception, BasicError, RetryableError


@pytest.mark.parametrize(
    'original_exception, new_exception', (
            (None, None),
            (psycopg2.DataError, BasicError),
            (psycopg2.OperationalError, RetryableError),
            (psycopg2.InterfaceError, RetryableError),
    )
)
def test_replace_exception(original_exception, new_exception):
    """проверяем что replace_exception подменяет исключение"""
    @replace_exception
    def decorate_func():
        if original_exception:
            raise original_exception
        return True

    if original_exception:
        with pytest.raises(new_exception):
            decorate_func()
    else:
        assert decorate_func()
