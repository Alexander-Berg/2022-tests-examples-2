import shutil

import pytest


@pytest.fixture(scope='session', name='userver_dumps_root')
def _userver_dumps_root(tmp_path_factory):
    path = tmp_path_factory.mktemp('userver-cache-dumps', numbered=True)
    return path.resolve()


@pytest.fixture
def read_latest_dump(userver_dumps_root):
    def read(dumper_name):
        specific_dir = userver_dumps_root.joinpath(dumper_name)
        if not specific_dir.is_dir():
            return None
        latest_dump_filename = max(
            (
                f
                for f in specific_dir.iterdir()
                if specific_dir.joinpath(f).is_file()
            ),
            default=None,
        )
        if not latest_dump_filename:
            return None
        with open(specific_dir.joinpath(latest_dump_filename), 'rb') as dump:
            return dump.read()

    return read


@pytest.fixture
def setup_userver_dumps(get_directory_path, userver_dumps_root):
    def hook(config, config_vars):
        initial_dumps = get_directory_path('dumps')
        shutil.rmtree(userver_dumps_root, ignore_errors=True)
        shutil.copytree(initial_dumps, userver_dumps_root)

    return hook


@pytest.fixture
def cleanup_userver_dumps(userver_dumps_root, request):
    """
    To avoid leaking dumps between tests, cache_dump_dir must be cleaned after
    each test. To observe the dumps, add a final `time.sleep(1000000)` to your
    test locally. The returned function may also be used to clean dumps
    manually as appropriate.
    """

    def cleanup():
        shutil.rmtree(userver_dumps_root, ignore_errors=True)
        userver_dumps_root.mkdir()

    request.addfinalizer(cleanup)
    return cleanup
