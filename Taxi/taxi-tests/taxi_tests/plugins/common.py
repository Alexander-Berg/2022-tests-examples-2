# pylint: disable=redefined-outer-name
import json
import os.path

import pytest


@pytest.fixture
def search_path(request):
    """
    Returns static path options relative to the current test.
    """
    fullname = str(request.fspath)
    test_module_dir = os.path.dirname(fullname)
    test_module_name = os.path.splitext(os.path.basename(fullname))[0]
    static_dir = os.path.join(test_module_dir, 'static')
    search_directories = [
        os.path.join(static_dir, subdir)
        for subdir in [test_module_name, 'default']
    ]

    def _search_path(filename):
        for directory in search_directories:
            abs_filename = os.path.join(directory, filename)
            if os.path.isfile(abs_filename):
                yield abs_filename
    return _search_path


@pytest.fixture
def open_file(search_path):
    """
    Open static file corresponding to the current test.
    """
    def _open_file(filename, *args, **kwargs):
        for path in search_path(filename):
            return open(path, *args, **kwargs)
        raise FileNotFoundError('File %s wasn\'t found' % filename)

    return _open_file


@pytest.fixture
def load(open_file):
    """Load binary data from `static` directory.
    Usage:
        def test_something(load):
            data = load('filename')
    If file doesn't exist `FileNotFoundError` exception is raised.
    :param request: `request` fixture.
    :return: Loader (function).
    """
    def _load(filename, *args, **kwargs):
        with open_file(filename, *args, **kwargs) as fp:
            return fp.read()

    return _load


@pytest.fixture
def load_json(load):
    """Load json doc from `static directory
    Usage:
        def test_something(load_json):
            json_obj = load_json('filename')
    """
    def _load_json(filename, *args, **kwargs):
        return json.loads(load(filename), *args, **kwargs)

    return _load_json
