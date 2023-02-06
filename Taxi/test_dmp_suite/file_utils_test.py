# coding: utf-8
import os
import pytest

from dmp_suite import file_utils as fu


def test_tempdir():
    with pytest.raises(ValueError):
        with fu.tempdir() as tmp:
            assert os.path.exists(tmp)
            raise ValueError
    assert not os.path.exists(tmp)

    with fu.tempdir() as tmp:
        assert os.path.exists(tmp)
    assert not os.path.exists(tmp)


def test_from_same_directory():
    assert (
        fu.from_same_directory("some_dir/some_file.txt", "another_file.py")
        == "some_dir/another_file.py"
    )
