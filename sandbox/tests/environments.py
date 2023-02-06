import os
import time
import shutil
import tempfile
import datetime as dt
import multiprocessing as mp

import pytest

from sandbox.sdk2 import environments


@pytest.fixture()
def temp_dir(request):
    tdir = tempfile.mkdtemp()

    def fin():
        shutil.rmtree(tdir)

    request.addfinalizer(fin)
    return tdir


@pytest.fixture()
def test_files(temp_dir):
    files = {"test1", "test2", "test3"}

    for f in files:
        with open(os.path.join(temp_dir, f), "w"):
            pass

    return files


@pytest.fixture()
def meta(temp_dir, sandbox_tasks_dir):
    return environments.FileSizeMetadata(temp_dir)


class TestMeta(object):

    def test__metadata(self, meta):
        meta.store()
        for r in meta.check_files():
            assert len(r) == 0

    def test__extra_absent(self, meta, test_files, temp_dir):
        meta.store()

        deleted = test_files.pop()
        os.unlink(os.path.join(temp_dir, deleted))

        added = "_unnecessary_"
        open(os.path.join(temp_dir, added), "w").close()

        absent, extra, different = meta.check_files()

        assert absent == {deleted}
        assert extra == {added}
        assert different == set()

    def test__change_file(self, meta, test_files, temp_dir):
        meta.store()

        fname = next(iter(test_files))
        with open(os.path.join(temp_dir, fname), "w") as f:
            f.write("Hello tests")

        absent, extra, different = meta.check_files()

        assert absent == set()
        assert extra == set()
        assert len(different) == 1
        assert next(iter(different))[0] == fname

    def test__existense(self, meta):
        meta.store()
        assert meta.exists

        os.unlink(meta.full_path)
        assert not meta.exists

    def test__obsolescense(self, meta):
        meta.store()

        atime = mtime = time.time() - 14 * 3600
        os.utime(meta.full_path, (atime, mtime))

        assert not meta.outdated(dt.timedelta(hours=16))
        assert meta.outdated(dt.timedelta(hours=3))

        meta.touch()
        assert not meta.outdated(dt.timedelta(minutes=10))

    def test__touch_without_meta(self, meta):
        assert not meta.exists
        meta.touch()
        assert meta.exists

        with open(meta.full_path) as f:
            assert f.read() == ""


class TestSandboxEnvironment(object):

    @pytest.mark.usefixtures("initialize")
    def test__exclusive_build_dir(self):
        seq = "xyz"
        lock = mp.Lock()
        lock.acquire()
        rpipe, wpipe = os.pipe()
        pid = os.fork()
        if not pid:
            os.close(rpipe)
            with lock:
                d = environments.SandboxEnvironment.exclusive_build_cache_dir("exclusive", seq)
                os.write(wpipe, d)
                os._exit(0)
        else:
            os.close(wpipe)
            d = environments.SandboxEnvironment.exclusive_build_cache_dir("exclusive", seq)
            assert d.endswith("x")
            lock.release()
            assert os.waitpid(pid, 0)[1] == 0
            dchild = os.read(rpipe, 100500)
            assert d != dchild

        # Check numerical, default and empty sequence providers
        assert environments.SandboxEnvironment.exclusive_build_cache_dir("exclusive", (9,)).endswith("9")
        assert environments.SandboxEnvironment.exclusive_build_cache_dir("exclusive").endswith("0")
        with pytest.raises(IndexError):
            environments.SandboxEnvironment.exclusive_build_cache_dir("exclusive", iter([]))
