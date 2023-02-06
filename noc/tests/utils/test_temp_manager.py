import os

import pytest

from checkist.utils.temp_manager import TempManager


def test_temp_manager_dir_create():
    with TempManager() as tmgr:
        d1 = tmgr.temp_dir("test_temp_manager_dir_create")
        d2 = tmgr.temp_dir("test_temp_manager_dir_create")
        assert os.path.isdir(d1)
        assert os.path.isdir(d2)
    assert not os.path.exists(d1)
    assert not os.path.exists(d2)


def test_temp_manager_not_entered():
    tmgr = TempManager()
    with pytest.raises(RuntimeError):
        tmgr.temp_dir("test_temp_manager_not_entered")


def test_temp_manager_dir_clear_file():
    with TempManager() as tmgr:
        directory = tmgr.temp_dir("test_temp_manager_dir_clear_file")
        file = os.path.join(directory, "file")
        with open(file, "w") as fh:
            fh.write("filedata")
        assert os.path.exists(file)
    assert not os.path.exists(file)


def test_temp_manager_reenter():
    with TempManager() as tmgr:
        with tmgr:
            d1 = tmgr.temp_dir("test_temp_manager_reenter")
            assert os.path.isdir(d1)
        assert os.path.isdir(d1)
    assert not os.path.exists(d1)
