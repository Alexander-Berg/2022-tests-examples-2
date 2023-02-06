# pylint: disable=redefined-outer-name
import os.path
import shutil
import tarfile

import pytest

import clowny_alert_manager.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['clowny_alert_manager.generated.service.pytest_plugins']


def pytest_register_matching_hooks():
    class _AnyNumber:
        def __eq__(self, other):
            return isinstance(other, (int, float))

        def __repr__(self):
            return self.__class__.__name__

    return {'any-number': _AnyNumber()}


@pytest.fixture
def load_yaml(load_yaml, object_hook):
    def _wrapper(filename, *args, **kwargs):
        return load_yaml(filename, *args, object_hook=object_hook, **kwargs)

    return _wrapper


@pytest.fixture(name='pack_repo')
def pack_repo_fixture(tmp_path, search_path):
    def _impl(static_repo_dir):
        for static_repo_path in search_path(static_repo_dir, directory=True):
            tarball_path = tmp_path / f'{static_repo_dir}.tar.gz'

            with tarfile.open(tarball_path, 'w:gz') as out_tar:
                for fname in os.listdir(static_repo_path):
                    out_tar.add(
                        os.path.join(static_repo_path, fname), arcname=fname,
                    )

            return tarball_path

        assert False, 'failed to find static_repo_dir'

    return _impl


@pytest.fixture(name='copy_repo')
def copy_repo_fixture(tmp_path, search_path):
    def _impl(static_repo_dir, dest_dir):
        for static_repo_path in search_path(static_repo_dir, directory=True):
            for item in os.listdir(static_repo_path):
                src = os.path.join(static_repo_path, item)
                dst = os.path.join(dest_dir, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)

            return

        assert False, 'failed to find static_repo_dir'

    return _impl
