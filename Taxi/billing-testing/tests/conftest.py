import glob
import os
import os.path

import pytest

from sibilla import storage


WORKDIR = '/tmp/test_reporter'


def prepare_workdir():
    os.makedirs(WORKDIR, mode=0o755, exist_ok=True)


def cleanup_workdir():
    for name in glob.glob(WORKDIR + '/*'):
        if os.path.isfile(name):
            os.unlink(name)
        else:
            assert False, f'STRANGE THING: "{name}"'


@pytest.fixture
def workdir():
    prepare_workdir()
    yield WORKDIR
    cleanup_workdir()


@pytest.fixture
def stg():
    return storage.Storage(':memory:')
