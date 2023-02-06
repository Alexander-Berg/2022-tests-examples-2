import uuid

from dmp_suite.py_env.utils import is_inside_yt_job

try:
    import pytest
except ImportError:
    if is_inside_yt_job():
        pytest = None
    else:
        raise

from dmp_suite.yt import join_path_parts, NotLayeredYtLayout, NotLayeredYtLocation
from dmp_suite.yt.paths import TAXI_DWH_TEST_PREFIX


def random_yt_table(table_cls):
    """Decorator add fields __layout__ with random folder and name."""

    random_name = uuid.uuid4().hex

    new_layout = NotLayeredYtLayout(
        folder=join_path_parts(TAXI_DWH_TEST_PREFIX, random_name),
        name=random_name
    )
    new_location = NotLayeredYtLocation
    random_table_cls = type(
        'Random' + table_cls.__name__,
        (table_cls,),
        {
            '__layout__': new_layout,
            '__location_cls__': new_location,
        }
    )

    return random_table_cls


def fixture_random_yt_table(scope='function'):
    """Decorator transform YTTable class to pytest fixture. Fixture generate
    subclass __layout__ with random folder and table.
    """

    def decorator(table_cls):
        @pytest.fixture(scope=scope)
        def randomized_table_fixture():
            yield random_yt_table(table_cls)

        return randomized_table_fixture

    if isinstance(scope, str):
        return decorator
    else:
        table_cls = scope
        scope = 'function'
        return decorator(table_cls)
