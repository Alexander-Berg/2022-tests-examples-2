import contextlib

import pytest

from scripts.stuff.async_check import handlers


@pytest.fixture(name='init_arc')
def _init_arc(tmp_path, arc_mock):
    arc_mock_ = arc_mock(tmp_path)

    path = arc_mock_.mk_dir(
        'taxi/backend-py3/services/taxi_api_admin/postgresql/api_admin',
    )
    path = arc_mock_.mk_dir(path / 'migrations')

    def _file_writer(file_name: str, file_content: str):
        arc_mock_.write_file(path / file_name, file_content)

    return _file_writer, arc_mock_


@pytest.fixture(name='set_pgmigrate_root_dir')
def _set_pgmigrate_root_dir():
    @contextlib.contextmanager
    def _wrapper(root_dir):
        # pylint: disable=protected-access
        token = handlers._PGMIGRATE_ROOT_DIR.set(root_dir)
        try:
            yield
        finally:
            # pylint: disable=protected-access
            handlers._PGMIGRATE_ROOT_DIR.reset(token)

    return _wrapper
