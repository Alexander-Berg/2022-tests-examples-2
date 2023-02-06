# pylint: disable=no-name-in-module
# pylint: disable=import-error
import distutils.dir_util as dir_util
import os
import subprocess
import tempfile

import pytest


@pytest.fixture(name='tempdir')
def _tempdir():
    with tempfile.TemporaryDirectory() as temp_dir:

        class TempDir:
            def write(self, fname: str, contents: str) -> None:
                oname = os.path.join(temp_dir, fname)
                dirname = os.path.dirname(oname)
                os.makedirs(dirname, exist_ok=True)

                with open(oname, 'w') as ofile:
                    ofile.write(contents)

            def read(self, fname: str) -> str:
                iname = os.path.join(temp_dir, fname)
                with open(iname) as ifile:
                    return ifile.read()

            def name(self) -> str:
                return temp_dir

        yield TempDir()


@pytest.fixture(name='client_yaml_contents')
def _client_yaml():
    def gen():
        return {
            'host': {
                'testing': 'http://testing.com',
                'production': 'http://prod.com',
            },
        }

    yield gen


@pytest.fixture(name='gen_operation')
def _gen_operation():
    def gen(name='foo'):
        return {
            'description': name,
            'responses': {'200': {'description': 'OK'}},
        }

    yield gen


STATIC_FILETREE = os.path.join(
    os.path.dirname(__file__), 'static', 'filetrees',
)


@pytest.fixture(name='load_fstree')
def _load_fstree(tempdir):
    def load(name: str) -> None:
        src = os.path.join(STATIC_FILETREE, name)
        dst = tempdir.name()
        dir_util.copy_tree(src, dst)

    yield load


@pytest.fixture(name='validate_filetree')
def _validate_filetree(tempdir):
    def cmp(name: str) -> None:
        src = os.path.join(STATIC_FILETREE, name, 'schemas', 'external-api')
        dst = os.path.join(tempdir.name(), 'schemas', 'external-api')
        subprocess.check_call(['/usr/bin/diff', '-uNrp', src, dst])

    yield cmp
