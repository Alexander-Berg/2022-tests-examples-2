import contextlib
import itertools
import os.path
import socket

import pytest
import yaml

from taxi_tests.utils import json_util

BASE_PORT = 30000
MAX_PORTS_NUMBER = 100


class NoEnabledPorts(Exception):
    """Raised if there are not free ports for worker"""


@pytest.fixture
def static_dir(request):
    fullname = str(request.fspath)
    test_module_dir = os.path.dirname(fullname)
    return os.path.join(test_module_dir, 'static')


@pytest.fixture
def get_search_pathes(request, static_dir, initial_data_path):
    fullname = str(request.fspath)
    test_module_name = os.path.splitext(os.path.basename(fullname))[0]
    node_name = request.node.name
    local_path = [os.path.join(test_module_name, node_name)]
    if '[' in node_name:
        node_short_name = node_name[: node_name.index('[')]
        local_path.append(os.path.join(test_module_name, node_short_name))
    local_path.append(test_module_name)
    local_path.append('default')
    search_directories = [
        os.path.join(static_dir, subdir) for subdir in local_path
    ]
    search_directories.extend(initial_data_path)

    def _get_search_pathes(filename):
        for directory in search_directories:
            yield os.path.join(directory, filename)

    return _get_search_pathes


@pytest.fixture
def initial_data_path():
    return ()


@pytest.fixture(scope='session')
def _file_paths_cache():
    return {}


@pytest.fixture
def get_all_static_file_paths(static_dir, _file_paths_cache):
    def _get_file_paths():
        if static_dir not in _file_paths_cache:
            all_files = []
            for dir_path, _, file_names in os.walk(static_dir):
                all_files.extend(
                    os.path.join(dir_path, file_name)
                    for file_name in file_names
                )
            _file_paths_cache[static_dir] = all_files
        return _file_paths_cache[static_dir]

    return _get_file_paths


@pytest.fixture
def search_path(get_search_pathes):
    def _search_path(filename, directory=False):
        if directory:
            path_check = os.path.isdir
        else:
            path_check = os.path.isfile
        for abs_filename in get_search_pathes(filename):
            if path_check(abs_filename):
                yield abs_filename

    return _search_path


@pytest.fixture
def _file_not_found_error(get_search_pathes):
    def _file_not_found_error(message, filename):
        message = message % filename
        pathes = '\n'.join(
            ' - %s' % path for path in get_search_pathes(filename)
        )
        return FileNotFoundError(
            '%s\n\nThe following pathes were examined:\n%s'
            % (message, pathes),
        )

    return _file_not_found_error


@pytest.fixture
def get_file_path(search_path, _file_not_found_error):
    def _get_file_path(filename):
        for path in search_path(filename):
            return path
        raise _file_not_found_error('File %s was not found', filename)

    return _get_file_path


@pytest.fixture
def get_directory_path(search_path, _file_not_found_error):
    def _get_directory_path(filename):
        for path in search_path(filename, directory=True):
            return path
        raise _file_not_found_error('Directory %s was not found', filename)

    return _get_directory_path


@pytest.fixture
def open_file(get_file_path):
    # pylint: disable=keyword-arg-before-vararg
    def _open_file(filename, mode='r', encoding='utf-8', *args, **kwargs):
        filename = get_file_path(filename)
        return open(filename, mode=mode, encoding=encoding, *args, **kwargs)

    return _open_file


@pytest.fixture
def load(open_file):
    """Load data from `tests-pytest/static` directory.

    Usage:

        def test_something(load):
            data = load('filename')

    File search order is:

    1. `tests-pytest/static/test_something/filename`.
    2. `tests-pytest/static/default/filename`.

    If file doesn't exist `ValueError` exception is raised.

    :return: Loader (function).
    """

    def _load(filename, *args, **kwargs):
        with open_file(filename, *args, **kwargs) as file:
            return file.read()

    return _load


@pytest.fixture
def load_binary(load):
    """Load binary data from `tests-pytest/static` directory

    Usage:

        def test_something(load_binary):
            raw_data = load_binary('filename')
    """

    def _load_binary(filename):
        return load(filename, 'rb', encoding=None)

    return _load_binary


@pytest.fixture
def load_json(load, mockserver_info, mockserver_ssl_info):
    """Load json doc from `tests-pytest/static directory

    Usage:

        def test_something(load_json):
            json_obj = load_json('filename')
    """

    def _load_json(filename, *args, **kwargs):
        return json_util.loads(
            load(filename),
            mockserver=mockserver_info,
            mockserver_https=mockserver_ssl_info,
            *args,
            **kwargs,
        )

    return _load_json


@pytest.fixture
def load_yaml(load):
    """Load yaml doc from `tests-pytest/static directory

    Usage:

        def test_something(load_yaml):
            yaml_obj = load_yaml('filename')
    """

    def _load_yaml(filename, *args, **kwargs):
        return yaml.load(
            load(filename),
            Loader=getattr(yaml, 'CLoader', yaml.Loader),
            *args,
            **kwargs,
        )

    return _load_yaml


@pytest.fixture(scope='session')
def worker_id(request):
    if hasattr(request.config, 'workerinput'):
        return request.config.workerinput['workerid']
    return 'master'


@pytest.fixture(scope='session')
def get_free_port(worker_id):
    counter = itertools.islice(itertools.count(), MAX_PORTS_NUMBER)
    worker_num = 0 if worker_id == 'master' else int(worker_id[2:]) + 1

    def _get_free_port():
        for value in counter:
            port = BASE_PORT + worker_num * MAX_PORTS_NUMBER + value
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            with contextlib.closing(sock):
                result_code = sock.connect_ex(('localhost', port))
            if result_code != 0:
                return port
        raise NoEnabledPorts()

    return _get_free_port


def pytest_addoption(parser):
    parser.addoption(
        '--build-dir',
        default=os.path.join(os.getcwd(), '.build'),
        help='Path to build directory.',
    )
