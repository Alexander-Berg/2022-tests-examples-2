import pytest
import os.path
import yatest.common

from metrika.pylib.file import write_data_to_file
from metrika.pylib.file import atomic_write
from metrika.pylib.file import md5sum


@pytest.fixture(scope='session')
def dirs(tmpdir_factory):
    class Dirs:
        tmp_dir = str(tmpdir_factory.mktemp("src", numbered=False))
        dst_dir = str(tmpdir_factory.mktemp("dst", numbered=False))

    yield Dirs


class TestFileData:
    text = 'test is good'
    file_name = 'test.txt'
    tmp_file_name = 'test.txt.tmp'


def test_write_wo_tmp(dirs):
    write_data_to_file(TestFileData.text, TestFileData.file_name, dirs.dst_dir)
    file_path = os.path.join(dirs.dst_dir, TestFileData.file_name)
    assert os.path.isfile(file_path)

    with open(file_path) as f:
        data = f.read()

    assert data == TestFileData.text


def test_write_with_tmp(dirs):
    write_data_to_file(TestFileData.text, TestFileData.file_name, dirs.dst_dir, dirs.tmp_dir)
    file_path = os.path.join(dirs.dst_dir, TestFileData.file_name)
    assert os.path.isfile(file_path)
    assert not os.path.isfile(os.path.join(dirs.tmp_dir, TestFileData.file_name))

    with open(file_path) as f:
        data = f.read()

    assert data == TestFileData.text


def test_write_with_fsync(dirs):
    write_data_to_file(TestFileData.text, TestFileData.file_name, dirs.dst_dir, dirs.tmp_dir, fsync=True)

    file_path = os.path.join(dirs.dst_dir, TestFileData.file_name)
    assert os.path.isfile(file_path)
    assert not os.path.isfile(os.path.join(dirs.tmp_dir, TestFileData.file_name))

    with open(file_path) as f:
        data = f.read()

    assert data == TestFileData.text


def test_atomic_write():
    atomic_write(TestFileData.file_name, TestFileData.text)

    assert os.path.isfile(TestFileData.file_name)
    assert not os.path.isfile(TestFileData.tmp_file_name)

    with open(TestFileData.file_name) as fd:
        data = fd.read()

    assert data == TestFileData.text


def test_atomic_write_with_fsync():
    atomic_write(TestFileData.file_name, TestFileData.text, fsync=True)

    assert os.path.isfile(TestFileData.file_name)
    assert not os.path.isfile(TestFileData.tmp_file_name)

    with open(TestFileData.file_name) as fd:
        data = fd.read()

    assert data == TestFileData.text


def test_md5sum():
    file_path = yatest.common.source_path('metrika/pylib/file/tests/datafile')
    assert md5sum(file_path) == '602206d913fefa61c256947cd72fcf92'
    assert md5sum(file_path, chunk_size=1) == '602206d913fefa61c256947cd72fcf92'

    with pytest.raises(IOError):
        md5sum('does_not_exist')
