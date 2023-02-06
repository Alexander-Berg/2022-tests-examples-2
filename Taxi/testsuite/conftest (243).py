import copy

from psycopg2 import extras
import pytest

# root conftest for service eats-nomenclature-viewer
pytest_plugins = ['eats_nomenclature_viewer_plugins.pytest_plugins']


def pytest_configure(config):
    config.addinivalue_line('markers', 's3: store s3 files in mock')


@pytest.fixture(autouse=True)
def s3_apply(request, mds_s3_storage, load):
    def _put_files(files):
        for s3_path, file_path in files.items():
            mds_s3_storage.put_object(
                key=s3_path, body=load(file_path).encode('utf-8'),
            )

    for mark in request.node.iter_markers('s3'):
        _put_files(*mark.args, **mark.kwargs)


@pytest.fixture
def pg_cursor(pgsql):
    return pgsql['eats_nomenclature_viewer'].cursor(
        cursor_factory=extras.RealDictCursor,
    )


@pytest.fixture
def update_taxi_config(taxi_config):
    """
    Updates only specified keys in the config, without touching other keys.
    E.g. if original config is `{ a: 1, b: 2}`, then value `{ b: 3, c: 4}`
    will set the config to `{ a: 1, b: 3, c: 4}`.
    """

    def impl(config_name, config_value):
        updated_config = copy.deepcopy(taxi_config.get(config_name))
        updated_config.update(config_value)
        taxi_config.set(**{config_name: updated_config})

    return impl
