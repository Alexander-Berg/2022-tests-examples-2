import os
import py
import codecs
import pytest

from sandbox import projects

HISTKEY = "source_encoding/mtimes"


@pytest.fixture(scope="session")
def cached_files(request):
    cache = request.session.config.cache.get(HISTKEY, {})

    def fin():
        request.session.config.cache.set(HISTKEY, cache)
    request.addfinalizer(fin)
    return cache


def pytest_generate_tests(metafunc):
    source_files = []
    for root, dirs, files in os.walk(py.path.local(projects.__file__).dirpath().join("..").strpath):
        for fname in files:
            if not fname.endswith(".py"):
                continue
            fpath = os.path.join(root, fname)
            source_files.append(fpath)

    metafunc.parametrize("src_fname", source_files)


def test__resource_types_encoding(cached_files, sandbox_tasks_dir, src_fname):
    val = cached_files.get(src_fname)
    mtime = os.path.getmtime(src_fname)

    if val and val == mtime:
        pytest.skip()

    try:
        with codecs.open(src_fname, "rb", encoding="utf8") as f:
            chunk = None
            while chunk != "":
                chunk = f.read(500 * 1024)
    except UnicodeDecodeError as ex:
        pytest.fail("Source file '{}' MUST be in UTF8 encoding: {}".format(
            os.path.relpath(src_fname, sandbox_tasks_dir), ex)
        )

    cached_files[src_fname] = mtime
