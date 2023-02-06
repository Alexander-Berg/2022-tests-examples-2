import pytest
import six

import os
import time
import shutil
import textwrap
import datetime
import urlparse
import threading

from sandbox.common import config as common_config
from sandbox.common import errors as common_errors

from sandbox.sdk2.vcs import svn as sdk_svn


@pytest.fixture()
def patch_log_dir(monkeypatch):
    from sandbox.common import config
    from sandbox.sdk2 import paths
    log_dir = os.path.join(config.Registry().client.log.root, 'svn')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    monkeypatch.setattr(paths, 'get_logs_folder', lambda: log_dir)


@pytest.fixture()
def svn(initialize, patch_log_dir):
    return sdk_svn.Svn


@pytest.fixture()
def arcadia(initialize, patch_log_dir):
    return sdk_svn.Arcadia


@pytest.fixture()
def arcadia_testdata(initialize, patch_log_dir):
    return sdk_svn.ArcadiaTestData


@pytest.fixture()
def svn_user(arcadia, monkeypatch):
    monkeypatch.setenv('SVN_SSH', 'ssh -l {}'.format(arcadia.RO_USER))


@pytest.fixture()
def threading_ident(monkeypatch):
    monkeypatch.setattr(threading.Thread, "ident", 42)


_pytest_ini_path = "sandbox/projects/pytest.ini"
_pytest_ini_r3343622 = (
    "[pytest]\n"
    "addopts = --flakes\n"
    "\n"
    "norecursedirs = .svn\n"
    "python_files = projects/tests/*.py\n"
    "    projects/sandbox_ci/tests/*.py\n"
    "    projects/pulse/tests/*.py\n"
)


def validate_log(log, revision):
    revisions = {
        999998: {
            "revision": 999998,
            "author": "dmitryno",
            "date": datetime.datetime(2013, 4, 16, 13, 0, 37, 973319),
            "msg": "delete subphrase header",
            "paths": [("M", "/trunk/arcadia/search/wizard/rules/adult_rule.h")],
        },
        1000000: {
            "revision": 1000000,
            "author": "zosimov",
            "date": datetime.datetime(2013, 4, 16, 13, 0, 39, 174092),
            "msg": "Small quota for MP3Urls policy",
            "paths": [("M", "/trunk/arcadia/yweb/common/roboconf/conf-production/policy.cfg")],
        },
        1388646: {
            "revision": 1388646,
            "author": "korum",
            "date": datetime.datetime(2014, 05, 26, 17, 57, 47, 627945),
            "msg": "Added Sandbox test data for build-time tests.\n",
            "paths": [
                ("A", "/trunk/arcadia_tests_data/sandbox"),
                ("A", "/trunk/arcadia_tests_data/sandbox/file"),
                ("A", "/trunk/arcadia_tests_data/sandbox/subdir"),
                ("A", "/trunk/arcadia_tests_data/sandbox/subdir/file")
            ],
        },
    }

    for param_name, param_value in six.iteritems(revisions[revision]):
        if isinstance(param_value, list):
            assert set(log[param_name]) == set(param_value)
        else:
            assert log[param_name] == param_value


def validate_svn_info(info, url, path):
    assert info["url"] == url
    assert info["entry_path"] == path
    for field in ("author", "date", "entry_revision", "commit_revision"):
        assert field in info


@pytest.mark.sdk_svn
class TestSvn(object):

    def test__info(self, svn, tmpdir, svn_user):
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia'
        info = svn.info(url)
        validate_svn_info(info, url, "arcadia")

        tmpdir = str(tmpdir)
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/sandbox/bin'
        svn.checkout(url, tmpdir)
        info = svn.info(tmpdir)
        validate_svn_info(info, url, tmpdir)

    def _run_parallel_info(self, svn):
        """
        Run many `svn info` using threads. Return True if they all have succeded, False otherwise.
        """
        url = "svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/"

        s = threading.Event()
        f = threading.Event()

        def info():
            s.wait()
            try:
                svn.info(url)
            except:
                f.set()

        threads = [threading.Thread(target=info) for _ in range(16)]

        for t in threads:
            t.start()

        # wait for all threads to reach a barrier
        time.sleep(1)

        s.set()

        for t in threads:
            t.join()

        return not f.is_set()

    def test__parallel_info_succeded(self, svn, svn_user):
        ok = self._run_parallel_info(svn)
        assert ok, "All svn.info should have succeded"

    def test__parallel_info_failed(self, svn, svn_user, threading_ident):
        """
        Mock Thread.ident to return a constant value. This will result in all threads
        using the same logger instance during the `Svn._svn` call which should lead to failures.
        """
        ok = self._run_parallel_info(svn)
        assert not ok, "Some of the svn.info should have failed"

    def test__info_timeout(self, svn, svn_user):
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/'
        pytest.raises(sdk_svn.SvnTimeout, svn.info, url, timeout=0)

    def test__list(self, svn, tmpdir, svn_user):
        # remote directory
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/sandbox/bin'
        assert 'client.py' in svn.list(url, as_list=True)

        # remote file
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/sandbox/bin/client.py'
        assert svn.list(url, as_list=True) == ['client.py']

        # local directory
        tmpdir = str(tmpdir)
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/sandbox/bin'
        svn.checkout(url, tmpdir)
        assert 'client.py' in svn.list(tmpdir, as_list=True)

    def test__checkout(self, svn, tmpdir, svn_user):
        tmpdir = str(tmpdir)
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/sandbox/bin'
        svn.checkout(url, tmpdir)
        assert os.path.exists(os.path.join(tmpdir, 'client.py'))

    def test__checkout__invalid_path(self, svn, tmpdir, svn_user):
        tmpdir = str(tmpdir)
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/sandbox/bin_bin'
        with pytest.raises(sdk_svn.SvnError) as exc_info:
            svn.checkout(url, tmpdir)
        assert exc_info.value.error_code == 'E170000'

    def test__checkout__url_with_revision(self, svn, tmpdir, svn_user):
        tmpdir = str(tmpdir)
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/sandbox/bin@3333333'
        svn.checkout(url, tmpdir)
        assert os.path.exists(os.path.join(tmpdir, 'client.py'))

    def test__checkout__url_with_invalid_revision(self, svn, tmpdir, svn_user):
        tmpdir = str(tmpdir)
        # raise because url@invalid_revision
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/sandbox/bin@1000000'
        with pytest.raises(sdk_svn.SvnError) as exc_info:
            svn.checkout(url, tmpdir)
        assert exc_info.value.error_code == 'E170000'

    def test__checkout__revision(self, svn, tmpdir, svn_user):
        tmpdir = str(tmpdir)
        # co url with specific revision
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/sandbox/bin'
        svn.checkout(url, tmpdir, revision=3333333)
        assert os.path.exists(os.path.join(tmpdir, 'client.py'))

    def test__checkout__invalid_revision(self, svn, tmpdir, svn_user):
        tmpdir = str(tmpdir)
        # raise because invalid_revision
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/sandbox/bin'
        with pytest.raises(sdk_svn.SvnError) as exc_info:
            svn.checkout(url, tmpdir, revision=1000000)
        assert exc_info.value.error_code == 'E195012'

    def test__checkout__file(self, svn, tmpdir, svn_user):
        tmpdir = str(tmpdir)
        # can't co file - raise
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/sandbox/bin/client.py'
        with pytest.raises(sdk_svn.SvnError) as exc_info:
            svn.checkout(url, tmpdir)
        assert exc_info.value.error_code == 'E200007'

    def test__update(self, svn, tmpdir, svn_user):
        tmpdir = str(tmpdir)

        # not in selected revision - raise
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/search/garden/sandbox/bin'
        svn.checkout(url + "@1339498", tmpdir)
        assert not os.path.exists(os.path.join(tmpdir, 'shell.py'))
        # update to rev with shell.py
        svn.update(tmpdir, revision=1340112)
        assert os.path.exists(os.path.join(tmpdir, 'shell.py'))

    def test__update__not_root_dir(self, svn, tmpdir, svn_user):
        tmpdir = str(tmpdir)
        svn.checkout('svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/search/garden/sandbox/', tmpdir, revision=1339498)
        assert not os.path.exists(os.path.join(tmpdir, 'bin', 'shell.py'))

        svn.update(os.path.join(tmpdir, 'bin'), revision=1340112)
        assert os.path.exists(os.path.join(tmpdir, 'bin', 'shell.py'))

    def test__update__empty(self, svn, tmpdir, svn_user):
        tmpdir = str(tmpdir)
        svn.checkout('svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/sandbox/', tmpdir, depth='empty')
        assert not os.path.exists(os.path.join(tmpdir, 'bin'))

        svn.update(os.path.join(tmpdir, 'bin'))
        assert os.path.exists(os.path.join(tmpdir, 'bin'))
        assert not os.path.exists(os.path.join(tmpdir, 'yasandbox'))

    def test__update__parents(self, svn, tmpdir, svn_user):
        tmpdir = str(tmpdir)
        svn.checkout('svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia', tmpdir, revision=3533646, depth='empty')
        assert not os.path.exists(os.path.join(tmpdir, 'sandbox'))

        svn.update(os.path.join(tmpdir, 'sandbox', 'agentr', 'bin', '__init__.py'), parents=True, revision=3533646)
        assert os.path.exists(os.path.join(tmpdir, 'sandbox', 'agentr', 'bin', '__init__.py'))

        svn.update(os.path.join(tmpdir, 'sandbox', 'bin', 'i_am_not_here.py'), parents=True, revision=3533646)
        assert os.path.exists(os.path.join(tmpdir, 'sandbox', 'bin'))
        assert not os.path.exists(os.path.join(tmpdir, 'i_am_not_here.py'))

    def test__export(self, svn, tmpdir, svn_user):
        tmpdir = str(tmpdir)
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/sandbox/bin'
        svn.export(url, tmpdir)
        assert os.path.exists(os.path.join(tmpdir, 'client.py'))

    def test__export__invalid_path(self, svn, tmpdir, svn_user):
        tmpdir = str(tmpdir)
        # raise because invalid path
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/sandbox/bin_dir'
        with pytest.raises(sdk_svn.SvnError) as exc_info:
            svn.export(url, tmpdir)
        assert exc_info.value.error_code == 'E170000'

    def test__export__url_with_revision(self, svn, tmpdir, svn_user):
        tmpdir = str(tmpdir)
        # export url@revision
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/sandbox/bin@3333333'
        svn.export(url, tmpdir)
        assert os.path.exists(os.path.join(tmpdir, 'client.py'))

    def test__export__url_with_invalid_revision(self, svn, tmpdir, svn_user):
        tmpdir = str(tmpdir)
        # raise because @invalid_revision
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/sandbox/bin@1000000'
        pytest.raises(sdk_svn.SvnError, svn.export, url, tmpdir)

    def test__export__file_url_with_revision(self, svn, tmpdir, svn_user):
        tmpdir = str(tmpdir)
        # export url@revision
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/sandbox/bin/client.py@3333333'
        svn.export(url, tmpdir)
        assert os.path.exists(os.path.join(tmpdir, 'client.py'))

    def test__export__file_url_with_invalid_revision(self, svn, tmpdir, svn_user):
        tmpdir = str(tmpdir)
        # raise because @invalid_revision
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/sandbox/bin/client.py@1000000'
        with pytest.raises(sdk_svn.SvnError) as exc_info:
            svn.export(url, tmpdir)
        assert exc_info.value.error_code == 'E170000'

    def test__export__file_revision_at(self, svn, tmpdir, svn_user):
        tmpdir = str(tmpdir)
        # export file with specific revision
        url = ('svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/'
               'extsearch/images/base/imgsearch/configs/ImgTier0-msk-resharded.cfg@1347762')
        svn.export(url, tmpdir)
        assert os.path.exists(os.path.join(tmpdir, 'ImgTier0-msk-resharded.cfg'))

    def test__log(self, svn, svn_user):
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/'
        log = svn.log(url, 1000000)
        validate_log(log[0], 1000000)

        log = svn.log(url, 999998, 1000000)
        validate_log(log[0], 999998)
        validate_log(log[1], 1000000)

    def test__log_timeout(self, svn, svn_user):
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/'
        pytest.raises(sdk_svn.SvnTimeout, svn.log, url, 999998, 1000000, timeout=0)

    def test__find_first_commit_for_path(self, svn, svn_user):
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia_tests_data/sandbox'
        log = svn.log(url, 'r0', 'HEAD', limit=1, stop_on_copy=True)
        validate_log(log[0], 1388646)

    def test__cat(self, svn, svn_user):
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/'
        assert svn.cat(url + _pytest_ini_path + "@3343622") == _pytest_ini_r3343622
        assert svn.cat(url + _pytest_ini_path, revision=3343622) == _pytest_ini_r3343622

    def test__info_on_non_existent_path(self, svn, tmpdir):
        garden_path = str(tmpdir)
        sandbox_path = os.path.join(garden_path, 'sandbox')
        bin_path = os.path.join(sandbox_path, 'bin')
        garden_url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/search/garden'
        sandbox_url = '/'.join((garden_url, 'sandbox'))
        bin_url = '/'.join((sandbox_url, 'bin'))
        svn.checkout(garden_url, garden_path, depth='empty')
        assert not os.path.exists(sandbox_path)

        info = svn.info(sandbox_path)
        assert info['entry_path'] == sandbox_path
        assert info['url'] == sandbox_url

        info = svn.info(bin_path)
        assert info['entry_path'] == bin_path
        assert info['url'] == bin_url

    def test__diff(self, svn):
        diff = textwrap.dedent("""\
            Index: search/garden/sandbox-tasks/projects/RunScript/__init__.py
            ===================================================================
            --- search/garden/sandbox-tasks/projects/RunScript/__init__.py\t(revision 3013219)
            +++ search/garden/sandbox-tasks/projects/RunScript/__init__.py\t(revision 3013220)
            @@ -68,7 +68,7 @@
                     If true path to the cache of Arcadia trunk will be in ARCADIA_CACHE_PATH env var
                     '''
                     name = 'use_arcadia_cache'
            -        description = 'Should use cache of Arcaia trunk on Sandbox client'
            +        description = 'Should use cache of Arcadia trunk on Sandbox client'
                     required = False

                 input_parameters = [ScriptUrl,
        """)

        url = "svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia"
        assert diff == svn.diff(url, change=3013220)
        assert diff == svn.diff(url + "@3013220", change=3013220)

    def test__propget(self, svn):
        url = "svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/sandbox/sandbox@3333333"
        assert ["*"] == svn.propget("svn:executable", url)


@pytest.mark.sdk_svn
class TestArcadia:
    def test__normalize_url(self, arcadia):
        url = 'svn+ssh://sandbox@arcadia.yandex.ru/arc/trunk/arcadia/sandbox@12345'
        assert arcadia.normalize_url(url) == 'arcadia:/arc/trunk/arcadia/sandbox@12345'
        url = "svn+ssh://arcadia-ro.yandex.ru//arc/trunk/data/antispam/fastban/totalban.txt"
        assert arcadia.normalize_url(url) == 'arcadia:/arc/trunk/data/antispam/fastban/totalban.txt'
        url = "svn+ssh://arcadia-ro.yandex.ru///arc/trunk/data/antispam/fastban/totalban.txt"
        assert arcadia.normalize_url(url) == 'arcadia:/arc/trunk/data/antispam/fastban/totalban.txt'
        url = 'arcadia:/arc/trunk/arcadia/sandbox@12345'
        assert arcadia.normalize_url(url) == 'arcadia:/arc/trunk/arcadia/sandbox@12345'
        url = 'arcadia:///arc/trunk/arcadia/sandbox@12345'
        assert arcadia.normalize_url(url) == 'arcadia:/arc/trunk/arcadia/sandbox@12345'
        url = 'arcadia://arc/trunk/arcadia/sandbox@12345'
        pytest.raises(common_errors.TaskFailure, arcadia.normalize_url, url)
        url = 'arcadia-hg:/'
        assert arcadia.normalize_url(url) == 'arcadia-hg:/'

    def test__parse_url(self, arcadia):
        url = 'arcadia:/arc/trunk/arcadia/sandbox@12345'
        p = arcadia.parse_url(url)
        assert p.path == 'arc/trunk/arcadia/sandbox'
        assert p[0] == 'arc/trunk/arcadia/sandbox'
        assert p.revision == '12345'
        assert p[1] == '12345'
        assert p.branch is None
        assert p[2] is None
        assert p.tag is None
        assert p[3] is None
        assert p.trunk
        assert p[4]
        assert p.subpath == 'sandbox'
        assert p[5] == 'sandbox'

        url = 'arcadia:/arc/trunk/arcadia/@12345'
        p = arcadia.parse_url(url)
        assert p.subpath == ''

        url = 'arcadia:/arc/branches/some/branch/arcadia@12345'
        p = arcadia.parse_url(url)
        assert p.path == 'arc/branches/some/branch/arcadia'
        assert p.revision == '12345'
        assert p.branch == 'some/branch'
        assert p.tag is None
        assert not p.trunk
        assert p.subpath == ''

        url = 'arcadia:/arc/tags/some/tag/arcadia/some/path'
        p = arcadia.parse_url(url)
        assert p.path == 'arc/tags/some/tag/arcadia/some/path'
        assert p.revision is None
        assert p.branch is None
        assert p.tag == 'some/tag'
        assert not p.trunk
        assert p.subpath == 'some/path'

        url = 'svn+ssh://sandbox@arcadia.yandex.ru/arc/trunk@12345'
        p = arcadia.parse_url(url)
        assert p.path == 'arc/trunk'
        assert p.revision == '12345'
        assert p.branch is None
        assert p.tag is None
        assert not p.trunk
        assert p.subpath is None

        url = 'svn://localhost/arc/trunk/arcadia/some/path/@12345'
        p = arcadia.parse_url(url)
        assert p.path == 'arc/trunk/arcadia/some/path/'
        assert p.revision == '12345'
        assert p.branch is None
        assert p.tag is None
        assert p.trunk
        assert p.subpath == 'some/path/'

        url = 'https://arcadia.yandex.ru/arc/branches/some/branch/arcadia/some/path'
        p = arcadia.parse_url(url)
        assert p.path == 'arc/branches/some/branch/arcadia/some/path'
        assert p.revision is None
        assert p.branch == 'some/branch'
        assert p.tag is None
        assert not p.trunk
        assert p.subpath == 'some/path'

        url = 'svn+ssh://arcadia-ro.yandex.ru/arc/tags/some/tag/arcadia/some/path@12345'
        p = arcadia.parse_url(url)
        assert p.path == 'arc/tags/some/tag/arcadia/some/path'
        assert p.revision == '12345'
        assert p.branch is None
        assert p.tag == 'some/tag'
        assert not p.trunk
        assert p.subpath == 'some/path'

    def test__parse_url_hg(self, arcadia):
        url = 'arcadia-hg:/'
        p = arcadia.parse_url(url)
        assert p.subpath == ''
        assert p.path == ''
        assert p.revision is None

        url = 'arcadia-hg:/#revision'
        p = arcadia.parse_url(url)
        assert p.subpath == ''
        assert p.path == ''
        assert p.revision == 'revision'

        url = 'arcadia-hg:/some/path/#revision'
        p = arcadia.parse_url(url)
        assert p.subpath == 'some/path/'
        assert p.path == ''
        assert p.revision == 'revision'

    def test__replace(self, arcadia):
        url = 'arcadia:/arc/trunk/arcadia/some/path@12345'

        new_url = arcadia.replace(url)
        assert new_url == url

        new_url = arcadia.replace(url, path='/arc/branches/some/branch/arcadia/some/path')
        assert new_url == 'arcadia:/arc/branches/some/branch/arcadia/some/path@12345'
        new_url = arcadia.replace(url, path='arc/branches/some/branch/arcadia/some/path@54321')
        assert new_url == 'arcadia:/arc/branches/some/branch/arcadia/some/path@54321'

        new_url = arcadia.replace(url, revision=54321)
        assert new_url == 'arcadia:/arc/trunk/arcadia/some/path@54321'
        new_url = arcadia.replace(url, revision='')
        assert new_url == 'arcadia:/arc/trunk/arcadia/some/path'
        new_url = arcadia.replace('arcadia:/arc/trunk/arcadia/some/path', revision='12345')
        assert new_url == 'arcadia:/arc/trunk/arcadia/some/path@12345'

        new_url = arcadia.replace(url, path='/arc/branches/some/branch/arcadia/some/path', revision=54321)
        assert new_url == 'arcadia:/arc/branches/some/branch/arcadia/some/path@54321'
        new_url = arcadia.replace(url, path='/arc/branches/some/branch/arcadia/some/path@67890', revision=54321)
        assert new_url == 'arcadia:/arc/branches/some/branch/arcadia/some/path@54321'
        new_url = arcadia.replace(url, path='/arc/branches/some/branch/arcadia/some/path@67890', revision='')
        assert new_url == 'arcadia:/arc/branches/some/branch/arcadia/some/path'

        url = 'svn+ssh://sandbox@arcadia.yandex.ru/arc/trunk/arcadia/some/path@12345'

        new_url = arcadia.replace(url)
        assert new_url == 'arcadia:/arc/trunk/arcadia/some/path@12345'

        new_url = arcadia.replace(url, path='/arc/branches/some/branch/arcadia/some/path')
        assert new_url == 'arcadia:/arc/branches/some/branch/arcadia/some/path@12345'

        new_url = arcadia.replace(url, revision=54321)
        assert new_url == 'arcadia:/arc/trunk/arcadia/some/path@54321'

        new_url = arcadia.replace(url, path='/arc/branches/some/branch/arcadia/some/path', revision=54321)
        assert new_url == 'arcadia:/arc/branches/some/branch/arcadia/some/path@54321'

    def test__replace_hg(self, arcadia):
        url = 'arcadia-hg:/path/#revision'

        new_url = arcadia.replace(url, path='/path2/')
        assert new_url == 'arcadia-hg:/path2/#revision'

        new_url = arcadia.replace(url, revision='revision2')
        assert new_url == 'arcadia-hg:/path/#revision2'

        new_url = arcadia.replace(url, path='/path2/', revision='revision2')
        assert new_url == 'arcadia-hg:/path2/#revision2'

    def test__get_ro_url(self, arcadia, settings):
        original = settings.client.sdk.svn.arcadia.force_use_rw

        settings.client.sdk.svn.arcadia.force_use_rw = False
        url = 'arcadia:/arc/trunk/arcadia.yandex.ru@1000000'
        ro_url = arcadia._get_ro_url(url)
        assert ro_url == '{}://{}@{}/arc/trunk/arcadia.yandex.ru@1000000'.format(
            arcadia.DEFAULT_SCHEME, arcadia.RO_USER, arcadia.ARCADIA_RO
        )

        url = 'svn+ssh://sandbox@arcadia.yandex.ru/arc/trunk@1000000'
        ro_url = arcadia._get_ro_url(url)
        assert ro_url == '{}://{}@{}/arc/trunk@1000000'.format(
            arcadia.DEFAULT_SCHEME, arcadia.RO_USER, arcadia.ARCADIA_RO
        )

        url = 'svn://sandbox@localhost:1234/arc/trunk@1000000'
        ro_url = arcadia._get_ro_url(url)
        assert ro_url == '{}://{}@{}/arc/trunk@1000000'.format(
            arcadia.DEFAULT_SCHEME, arcadia.RO_USER, arcadia.ARCADIA_RO
        )

        url = '/some/local/path'
        assert arcadia._get_ro_url(url) == url

        settings.client.sdk.svn.arcadia.force_use_rw = True
        url = 'arcadia:/arc/trunk/arcadia.yandex.ru@1000000'
        ro_url = arcadia._get_ro_url(url)
        assert ro_url == arcadia._get_rw_url(url)

        url = 'svn+ssh://sandbox@arcadia.yandex.ru/arc/trunk@1000000'
        ro_url = arcadia._get_ro_url(url)
        assert ro_url == arcadia._get_rw_url(url)

        url = 'svn://sandbox@localhost:1234/arc/trunk@1000000'
        ro_url = arcadia._get_ro_url(url)
        assert ro_url == arcadia._get_rw_url(url)

        url = '/some/local/path'
        assert arcadia._get_ro_url(url) == url

        settings.client.sdk.svn.arcadia.force_use_rw = original

    def test__get_rw_url(self, arcadia):
        url = 'arcadia:/arc/trunk/arcadia.yandex.ru@1000000'
        rw_url = arcadia._get_rw_url(url)
        assert rw_url == '{}://{}@{}/arc/trunk/arcadia.yandex.ru@1000000'.format(
            arcadia.DEFAULT_SCHEME, arcadia.RO_USER, arcadia.ARCADIA_RW
        )

        url = 'svn+ssh://sandbox@arcadia-ro.yandex.ru/arc/trunk/arcadia.yandex.ru@1000000'
        rw_url = arcadia._get_rw_url(url)
        assert rw_url == '{}://{}@{}/arc/trunk/arcadia.yandex.ru@1000000'.format(
            arcadia.DEFAULT_SCHEME, arcadia.RO_USER, arcadia.ARCADIA_RW
        )

        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk@1000000'
        rw_url = arcadia._get_rw_url(url)
        assert rw_url == '{}://{}@{}/arc/trunk@1000000'.format(
            arcadia.DEFAULT_SCHEME, arcadia.RO_USER, arcadia.ARCADIA_RW
        )

        url = 'svn://sandbox@localhost:1234/arc/trunk@1000000'
        rw_url = arcadia._get_rw_url(url)
        assert rw_url == '{}://{}@{}/arc/trunk@1000000'.format(
            arcadia.DEFAULT_SCHEME, arcadia.RO_USER, arcadia.ARCADIA_RW
        )

        url = 'svn://sandbox@localhost:1234/arc/trunk@1000000'
        rw_url = arcadia._get_rw_url(url, user='another_user')
        assert rw_url == '{}://another_user@{}/arc/trunk@1000000'.format(
            arcadia.DEFAULT_SCHEME, arcadia.ARCADIA_RW
        )

        url = '/some/local/path'
        assert arcadia._get_rw_url(url) == url

    def test__is_ro(self, arcadia):
        url = '{}://{}@{}/arc/trunk@12345'.format(arcadia.DEFAULT_SCHEME, arcadia.RO_USER, arcadia.ARCADIA_RO)
        assert arcadia._is_ro(url)

        url = 'svn://{}@{}/arc/trunk@12345'.format(arcadia.RO_USER, arcadia.ARCADIA_RO)
        assert not arcadia._is_ro(url)

        url = 'svn+ssh://{}:1234/arc/trunk'.format(arcadia.ARCADIA_RW)
        assert not arcadia._is_ro(url)

        url = 'svn+ssh://sandbox@{}/arc/trunk@12345'.format(arcadia.ARCADIA_RW)
        assert not arcadia._is_ro(url)

    def test__is_rw(self, arcadia):
        url = '{}://{}/arc/trunk@12345'.format(arcadia.DEFAULT_SCHEME, arcadia.ARCADIA_RW)
        assert arcadia._is_rw(url)

        url = 'svn://{}/arc/trunk@12345'.format(arcadia.ARCADIA_RW)
        assert not arcadia._is_rw(url)

        url = 'svn://{}/arc/trunk@12345'.format(arcadia.ARCADIA_RO)
        assert not arcadia._is_rw(url)

        url = 'svn+ssh://{}:1234/arc/trunk'.format(arcadia.ARCADIA_RW)
        assert not arcadia._is_rw(url)

        url = 'svn+ssh://sandbox@{}/arc/trunk@12345'.format(arcadia.ARCADIA_RW)
        assert arcadia._is_rw(url)

    def test__get_hg_url(self, arcadia):
        url = 'arcadia:/arc/trunk/arcadia.yandex.ru@1000000'
        assert arcadia._get_hg_url(url) is None

        url = 'arcadia-hg:/'
        assert arcadia._get_hg_url(url) == arcadia.ARCADIA_HG

        url = 'arcadia-hg:/path/#branch'
        assert arcadia._get_hg_url(url) == arcadia.ARCADIA_HG + '#branch'

    def test__info(self, arcadia, tmpdir):
        url = 'arcadia:/arc/trunk/arcadia'
        info = arcadia.info(url)
        validate_svn_info(info, url, "arcadia")

        tmpdir = str(tmpdir)
        url = 'arcadia:/arc/trunk/arcadia/sandbox/bin'
        arcadia.checkout(url, tmpdir)
        info = arcadia.info(tmpdir)
        validate_svn_info(info, url, tmpdir)

    def test__info_timeout(self, arcadia):
        url = 'arcadia:/arc/trunk/arcadia/'
        pytest.raises(sdk_svn.SvnTimeout, arcadia.info, url, timeout=0)

    def test__check(self, arcadia):
        # url exists
        assert arcadia.check('arcadia:/arc/trunk/arcadia/')
        assert arcadia.check('svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/')
        assert arcadia.check('svn+ssh://nobody@arcadia.yandex.ru/arc/trunk/arcadia/')
        # url not exists
        assert not arcadia.check('arcadia:/arc/trunk/arcadia__new/')
        assert not arcadia.check('svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia__new/')

    def test__list(self, arcadia, tmpdir):
        # remote directory
        url = 'arcadia:/arc/trunk/arcadia/sandbox/bin'
        assert 'client.py' in arcadia.list(url, as_list=True)
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/sandbox/bin'
        assert 'client.py' in arcadia.list(url, as_list=True)

        # remote file
        url = 'arcadia:/arc/trunk/arcadia/sandbox/bin/client.py'
        assert arcadia.list(url, as_list=True) == ['client.py']
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/sandbox/bin/client.py'
        assert arcadia.list(url, as_list=True) == ['client.py']

        # local directory
        tmpdir = str(tmpdir)
        url = 'arcadia:/arc/trunk/arcadia/sandbox/bin'
        arcadia.checkout(url, tmpdir)
        assert 'client.py' in arcadia.list(tmpdir, as_list=True)

    def test__checkout(self, arcadia, tmpdir):
        tmpdir = str(tmpdir)
        dir1 = os.path.join(tmpdir, 'dir1')
        os.mkdir(dir1)
        dir2 = os.path.join(tmpdir, 'dir2')
        os.mkdir(dir2)
        url = 'arcadia:/arc/trunk/arcadia/sandbox/bin'
        arcadia.checkout(url, dir1)
        assert os.path.exists(os.path.join(dir1, 'client.py'))
        url = 'svn+ssh://nobody@arcadia.yandex.ru/arc/trunk/arcadia/sandbox/bin'
        arcadia.checkout(url, dir2)
        assert os.path.exists(os.path.join(dir2, 'client.py'))

    def test__checkout__invalid_path(self, arcadia, tmpdir):
        tmpdir = str(tmpdir)
        url = 'arcadia:/arc/trunk/arcadia/sandbox/bin_bin'
        pytest.raises(sdk_svn.SvnPathNotExists, arcadia.checkout, url, tmpdir)

    def test__checkout__url_with_revision(self, arcadia, tmpdir):
        tmpdir = str(tmpdir)
        url = 'arcadia:/arc/trunk/arcadia/sandbox/bin@3333333'
        arcadia.checkout(url, tmpdir)
        assert os.path.exists(os.path.join(tmpdir, 'client.py'))

    def test__checkout__url_with_invalid_revision(self, arcadia, tmpdir):
        tmpdir = str(tmpdir)
        # raise because url@invalid_revision
        url = 'arcadia:/arc/trunk/arcadia/sandbox/bin@1000000'
        pytest.raises(sdk_svn.SvnPathNotExists, arcadia.checkout, url, tmpdir)

    def test__checkout__revision(self, arcadia, tmpdir):
        tmpdir = str(tmpdir)
        # co url with specific revision
        url = 'arcadia:/arc/trunk/arcadia/sandbox/bin'
        arcadia.checkout(url, tmpdir, revision=3333333)
        assert os.path.exists(os.path.join(tmpdir, 'client.py'))
        assert arcadia.get_revision(tmpdir) == '3333333'

    def test__checkout__invalid_revision(self, arcadia, tmpdir):
        tmpdir = str(tmpdir)
        # raise because invalid_revision
        url = 'arcadia:/arc/trunk/arcadia/sandbox/bin'
        pytest.raises(sdk_svn.SvnPathNotExists, arcadia.checkout, url, tmpdir, revision=1000000)

    def test__checkout__file(self, arcadia, tmpdir):
        tmpdir = str(tmpdir)
        # can't co file - raise
        url = 'arcadia:/arc/trunk/arcadia/sandbox/bin/client.py'
        pytest.raises(sdk_svn.SvnError, arcadia.checkout, url, tmpdir)

    def test__update(self, arcadia, tmpdir):
        tmpdir = str(tmpdir)
        dir1 = os.path.join(tmpdir, 'dir1')
        os.mkdir(dir1)
        dir2 = os.path.join(tmpdir, 'dir2')
        os.mkdir(dir2)

        # not in selected revision - raise
        url = 'arcadia:/arc/trunk/arcadia/search/garden/sandbox/bin'
        arcadia.checkout(url, dir1, revision=1339498)
        assert not os.path.exists(os.path.join(dir1, 'shell.py'))
        # update to rev with shell.py
        arcadia.update(dir1, revision=1340112)
        assert os.path.exists(os.path.join(dir1, 'shell.py'))
        assert arcadia.get_revision(dir1) == '1340112'

        # not in selected revision - raise
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/search/garden/sandbox/bin'
        arcadia.checkout(url, dir2, revision=1339498)
        assert not os.path.exists(os.path.join(dir2, 'shell.py'))
        # update to rev with shell.py
        arcadia.update(dir2, revision=1340113)
        assert os.path.exists(os.path.join(dir2, 'shell.py'))
        assert arcadia.get_revision(dir2) == '1340113'
        arcadia.update(dir2, revision=1340112)
        assert arcadia.get_revision(dir2) == '1340112'

    def test__update__not_root_dir(self, arcadia, tmpdir):
        tmpdir = str(tmpdir)
        arcadia.checkout('arcadia:/arc/trunk/arcadia/search/garden/sandbox/', tmpdir, revision=1339498)
        assert not os.path.exists(os.path.join(tmpdir, 'bin', 'shell.py'))

        arcadia.update(os.path.join(tmpdir, 'bin'), revision=1340112)
        assert os.path.exists(os.path.join(tmpdir, 'bin', 'shell.py'))

    def test__update__empty(self, arcadia, tmpdir):
        tmpdir = str(tmpdir)
        arcadia.checkout('arcadia:/arc/trunk/arcadia/sandbox', tmpdir, depth='empty')
        assert not os.path.exists(os.path.join(tmpdir, 'bin'))

        arcadia.update(os.path.join(tmpdir, 'bin'))
        assert os.path.exists(os.path.join(tmpdir, 'bin'))
        assert not os.path.exists(os.path.join(tmpdir, 'yasandbox'))

    def test__update__depth(self, arcadia, tmpdir, monkeypatch):

        svn_info_orig = sdk_svn.Svn.info
        target_revision = 4261754

        def late_ro_arcadia_info(cls, url, timeout=None):
            res = svn_info_orig(url, timeout)
            parsed_url = urlparse.urlparse(url)
            res["entry_revision"] = str(target_revision - int(sdk_svn.Arcadia.ARCADIA_RO in parsed_url.netloc))
            return res

        # emulate case when RO arcadia returns not the last revision
        monkeypatch.setattr(sdk_svn.Svn, "info", classmethod(late_ro_arcadia_info))
        # activate usage of ro-arcadia in test
        monkeypatch.setattr(common_config.Registry().client.sdk.svn.arcadia, "force_use_rw", False)

        tmpdir = str(tmpdir)
        etc_path = os.path.join(tmpdir, "etc")
        ya_make_path = os.path.join(etc_path, "ya.make")

        arcadia.checkout("arcadia:/arc/trunk/arcadia/sandbox", tmpdir, depth="immediates", revision=target_revision)
        assert os.path.exists(etc_path)
        assert not os.path.exists(ya_make_path)

        arcadia.update(etc_path, set_depth="files", revision=target_revision)
        assert os.path.exists(ya_make_path)

    def test__update__parents(self, arcadia, tmpdir):
        tmpdir = str(tmpdir)
        arcadia.checkout('svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia', tmpdir, revision=3533646, depth='empty')
        assert not os.path.exists(os.path.join(tmpdir, 'sandbox'))

        arcadia.update(os.path.join(tmpdir, 'sandbox', 'agentr', 'bin', '__init__.py'), parents=True, revision=3533646)
        assert os.path.exists(os.path.join(tmpdir, 'sandbox', 'agentr', 'bin', '__init__.py'))

        arcadia.update(os.path.join(tmpdir, 'sandbox', 'bin', 'i_am_not_here.py'), parents=True, revision=3533646)
        assert os.path.exists(os.path.join(tmpdir, 'sandbox', 'bin'))
        assert not os.path.exists(os.path.join(tmpdir, 'i_am_not_here.py'))

    def test__export(self, arcadia, tmpdir):
        tmpdir = str(tmpdir)
        dir1 = os.path.join(tmpdir, 'dir1')
        os.mkdir(dir1)
        dir2 = os.path.join(tmpdir, 'dir2')
        os.mkdir(dir2)
        url = 'arcadia:/arc/trunk/arcadia/sandbox/bin'
        arcadia.export(url, dir1)
        assert os.path.exists(os.path.join(dir1, 'client.py'))
        assert not os.path.exists(os.path.join(dir1, '.svn'))
        url = 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/sandbox/bin'
        arcadia.export(url, dir2)
        assert os.path.exists(os.path.join(dir2, 'client.py'))
        assert not os.path.exists(os.path.join(dir2, '.svn'))

    def test__export__invalid_path(self, arcadia, tmpdir):
        tmpdir = str(tmpdir)
        # raise because invalid path
        url = 'arcadia:/arc/trunk/arcadia/sandbox/bin_dir'
        pytest.raises(sdk_svn.SvnPathNotExists, arcadia.export, url, tmpdir)

    def test__export__url_with_revision(self, arcadia, tmpdir):
        tmpdir = str(tmpdir)
        # export url@revision
        url = 'arcadia:/arc/trunk/arcadia/sandbox/bin@3333333'
        arcadia.export(url, tmpdir)
        assert os.path.exists(os.path.join(tmpdir, 'client.py'))

    def test__export__url_with_invalid_revision(self, arcadia, tmpdir):
        tmpdir = str(tmpdir)
        # raise because @invalid_revision
        url = 'arcadia:/arc/trunk/arcadia/sandbox/bin@1000000'
        pytest.raises(sdk_svn.SvnPathNotExists, arcadia.export, url, tmpdir)

    def test__export__revision(self, arcadia, tmpdir):
        tmpdir = str(tmpdir)
        # export url with specific revision
        svn_url = 'arcadia:/arc/trunk/arcadia/sandbox/bin'
        arcadia.export(svn_url, tmpdir, revision=3333333)
        assert os.path.exists(os.path.join(tmpdir, 'client.py'))

    def test__export__invalid_revision(self, arcadia, tmpdir):
        tmpdir = str(tmpdir)
        # raise because invalid_revision
        url = 'arcadia:/arc/trunk/arcadia/sandbox/bin'
        pytest.raises(sdk_svn.SvnPathNotExists, arcadia.export, url, tmpdir, revision=1000000)

    def test__export__file(self, arcadia, tmpdir):
        tmpdir = str(tmpdir)
        # export file
        url = 'arcadia:/arc/trunk/arcadia/sandbox/bin/client.py'
        arcadia.export(url, tmpdir)
        assert os.path.exists(os.path.join(tmpdir, 'client.py'))

    def test__export__file_url_with_revision(self, arcadia, tmpdir):
        tmpdir = str(tmpdir)
        # export url@revision
        url = 'arcadia:/arc/trunk/arcadia/sandbox/bin/client.py@3333333'
        arcadia.export(url, tmpdir)
        assert os.path.exists(os.path.join(tmpdir, 'client.py'))

    def test__export__file_url_with_invalid_revision(self, arcadia, tmpdir):
        tmpdir = str(tmpdir)
        # raise because @invalid_revision
        url = 'arcadia:/arc/trunk/arcadia/sandbox/bin/client.py@1000000'
        pytest.raises(sdk_svn.SvnPathNotExists, arcadia.export, url, tmpdir)

    def test__export__file_revision(self, arcadia, tmpdir):
        tmpdir = str(tmpdir)
        # export file with specific revision
        url = 'arcadia:/arc/trunk/arcadia/sandbox/bin/client.py'
        arcadia.export(url, tmpdir, revision=3333333)
        assert os.path.exists(os.path.join(tmpdir, 'client.py'))

    def test__export__file_revision_at(self, arcadia, tmpdir):
        tmpdir = str(tmpdir)
        # export file with specific revision
        url = 'arcadia:/arc/trunk/arcadia/extsearch/images/base/imgsearch/configs/ImgTier0-msk-resharded.cfg@1347762'
        arcadia.export(url, tmpdir)
        assert os.path.exists(os.path.join(tmpdir, 'ImgTier0-msk-resharded.cfg'))

    def test__export__file_invalid_revision(self, arcadia, tmpdir):
        tmpdir = str(tmpdir)
        # raise because invalid_revision
        url = 'arcadia:/arc/trunk/arcadia/sandbox/bin/client.py'
        pytest.raises(sdk_svn.SvnPathNotExists, arcadia.export, url, tmpdir, revision=1000000)

    def test__parent_dir(self, arcadia):
        url = 'arcadia:/arc/trunk/'
        assert arcadia.parent_dir(url, count=0) == 'arcadia:/arc/trunk'
        assert arcadia.parent_dir(url, count=1) == 'arcadia:/arc'
        assert arcadia.parent_dir(url, count=2) == 'arcadia:/'
        assert arcadia.parent_dir(url, count=3) == 'arcadia:/'
        assert arcadia.parent_dir('svn+ssh://somebody@arcadia.yandex.ru/arc/trunk/', count=1) == 'arcadia:/arc'

    def test__append(self, arcadia):
        url = 'arcadia:/arc/trunk'
        assert arcadia.append(url, 'arcadia/search') == 'arcadia:/arc/trunk/arcadia/search'
        url = 'arcadia:/arc/trunk/'
        assert arcadia.append(url, 'arcadia/search') == 'arcadia:/arc/trunk/arcadia/search'
        url = 'arcadia:/arc/trunk@1000000'
        assert arcadia.append(url, 'arcadia/search') == 'arcadia:/arc/trunk/arcadia/search@1000000'
        url = 'arcadia:/arc/trunk/@1000000'
        assert arcadia.append(url, 'arcadia/search') == 'arcadia:/arc/trunk/arcadia/search@1000000'
        url = 'svn+ssh://sandbox@arcadia.yandex.ru/arc/trunk@1000000'
        assert arcadia.append(url, 'arcadia/search') == 'arcadia:/arc/trunk/arcadia/search@1000000'

    def test__log(self, arcadia):
        for url in ("arcadia:/arc/trunk/arcadia/", "svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/"):
            log = arcadia.log(url, 1000000)
            validate_log(log[0], 1000000)

            log = arcadia.log(url, 999998, 1000000)
            validate_log(log[0], 999998)
            validate_log(log[1], 1000000)

        # Absent `msg` in commit.
        log = arcadia.log(url, 1958897)
        assert log[0]["msg"] == ""

        # empty commit message
        log = arcadia.log(url, 3421125)
        assert log[0]["msg"] == ""

        def get_revisions(logs):
            return [_["revision"] for _ in logs]

        assert get_revisions(arcadia.log(url, 999998)) == [999998]
        assert get_revisions(arcadia.log(url, 999998, 1000000)) == [999998, 1000000]
        assert get_revisions(arcadia.log(url, 1000000, 999998)) == [1000000, 999998]
        with pytest.raises(ValueError):
            get_revisions(arcadia.log(url, revision_to="HEAD"))
        revisions = get_revisions(arcadia.log(url, limit=2))
        assert len(revisions) == 2
        assert revisions[0] > revisions[1]

    def test__log_timeout(self, arcadia):
        for url in ('arcadia:/arc/trunk/arcadia/', 'svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/'):
            pytest.raises(sdk_svn.SvnTimeout, arcadia.log, url, 999998, 1000000, timeout=0)

    def test__find_first_commit_for_path(self, arcadia):
        url = 'arcadia:/arc/trunk/arcadia_tests_data/sandbox'
        log = arcadia.log(url, 'r0', 'HEAD', limit=1, stop_on_copy=True)
        validate_log(log[0], 1388646)

    def test__trunk_url(self, arcadia):
        assert arcadia.trunk_url() == 'arcadia:/arc/trunk/arcadia'
        assert arcadia.trunk_url('some/path') == 'arcadia:/arc/trunk/arcadia/some/path'
        assert arcadia.trunk_url('some/path/') == 'arcadia:/arc/trunk/arcadia/some/path'
        assert arcadia.trunk_url('/some/path') == 'arcadia:/arc/trunk/arcadia/some/path'
        assert arcadia.trunk_url('/some/path', '') == 'arcadia:/arc/trunk/arcadia/some/path'
        assert arcadia.trunk_url('/some/path', 0) == 'arcadia:/arc/trunk/arcadia/some/path'
        assert arcadia.trunk_url('/some/path', 12345) == 'arcadia:/arc/trunk/arcadia/some/path@12345'
        assert arcadia.trunk_url('/some/path', '12345') == 'arcadia:/arc/trunk/arcadia/some/path@12345'
        assert arcadia.trunk_url('/some/path@12345') == 'arcadia:/arc/trunk/arcadia/some/path@12345'
        assert arcadia.trunk_url('/some/path@12345', 54321) == 'arcadia:/arc/trunk/arcadia/some/path@54321'

    def test__branch_url(self, arcadia):
        assert arcadia.branch_url('my/branch') == 'arcadia:/arc/branches/my/branch/arcadia'
        assert arcadia.branch_url('my/branch/') == 'arcadia:/arc/branches/my/branch/arcadia'
        assert arcadia.branch_url('/my/branch') == 'arcadia:/arc/branches/my/branch/arcadia'

        b = 'my/branch'
        assert arcadia.branch_url(b, 'some/path') == 'arcadia:/arc/branches/my/branch/arcadia/some/path'
        assert arcadia.branch_url(b, 'some/path/') == 'arcadia:/arc/branches/my/branch/arcadia/some/path'
        assert arcadia.branch_url(b, '/some/path') == 'arcadia:/arc/branches/my/branch/arcadia/some/path'
        assert arcadia.branch_url(b, '/some/path', '') == 'arcadia:/arc/branches/my/branch/arcadia/some/path'
        assert arcadia.branch_url(b, '/some/path', 0) == 'arcadia:/arc/branches/my/branch/arcadia/some/path'
        assert arcadia.branch_url(b, '/some/path', 12) == 'arcadia:/arc/branches/my/branch/arcadia/some/path@12'
        assert arcadia.branch_url(b, '/some/path', '12') == 'arcadia:/arc/branches/my/branch/arcadia/some/path@12'
        assert arcadia.branch_url(b, '/some/path@12') == 'arcadia:/arc/branches/my/branch/arcadia/some/path@12'
        assert arcadia.branch_url(b, '/some/path@12', 21) == 'arcadia:/arc/branches/my/branch/arcadia/some/path@21'

    def test__tag_url(self, arcadia):
        assert arcadia.tag_url('my/tag') == 'arcadia:/arc/tags/my/tag/arcadia'
        assert arcadia.tag_url('my/tag/') == 'arcadia:/arc/tags/my/tag/arcadia'
        assert arcadia.tag_url('/my/tag') == 'arcadia:/arc/tags/my/tag/arcadia'

        t = 'my/tag'
        assert arcadia.tag_url(t, 'some/path') == 'arcadia:/arc/tags/my/tag/arcadia/some/path'
        assert arcadia.tag_url(t, 'some/path/') == 'arcadia:/arc/tags/my/tag/arcadia/some/path'
        assert arcadia.tag_url(t, '/some/path') == 'arcadia:/arc/tags/my/tag/arcadia/some/path'
        assert arcadia.tag_url(t, '/some/path', '') == 'arcadia:/arc/tags/my/tag/arcadia/some/path'
        assert arcadia.tag_url(t, '/some/path', 0) == 'arcadia:/arc/tags/my/tag/arcadia/some/path'
        assert arcadia.tag_url(t, '/some/path', 12) == 'arcadia:/arc/tags/my/tag/arcadia/some/path@12'
        assert arcadia.tag_url(t, '/some/path', '12') == 'arcadia:/arc/tags/my/tag/arcadia/some/path@12'
        assert arcadia.tag_url(t, '/some/path@12') == 'arcadia:/arc/tags/my/tag/arcadia/some/path@12'
        assert arcadia.tag_url(t, '/some/path@12', 21) == 'arcadia:/arc/tags/my/tag/arcadia/some/path@21'

    def test__cat(self, arcadia):
        assert arcadia.cat(arcadia.trunk_url(_pytest_ini_path + "@3343622")) == _pytest_ini_r3343622
        assert arcadia.cat(arcadia.trunk_url(_pytest_ini_path), revision=3343622) == _pytest_ini_r3343622

    def test__get_revision(self, arcadia):
        assert arcadia.get_revision(arcadia.trunk_url('search/garden/sandbox/pytest.ini@1367503')) is None
        assert arcadia.get_revision(arcadia.trunk_url('search/garden/sandbox/pytest.ini@1367504')) == '1367504'
        assert arcadia.get_revision(arcadia.trunk_url('search/garden/sandbox/pytest.ini@1368180')) == '1368180'
        assert arcadia.get_revision(arcadia.trunk_url('non/existent/path')) is None

    def test__freeze_url_revision(self, arcadia):
        url = arcadia.trunk_url('sandbox/bin/client.py')
        freezed_url = arcadia.freeze_url_revision(url)
        u, s, r1 = freezed_url.partition('@')
        assert u == url
        assert s == '@'
        assert r1
        freezed_url = arcadia.freeze_url_revision(freezed_url)
        u, s, r2 = freezed_url.partition('@')
        assert u == url
        assert s == '@'
        assert r2 == r1

    def test__svn_url(self, arcadia):
        url = 'arcadia:/arc/trunk/data/antispam/fastban/totalban.txt'
        assert arcadia.svn_url(url) == 'svn+ssh://{}/arc/trunk/data/antispam/fastban/totalban.txt'.format(
            arcadia.ARCADIA_RW
        )

    def test__update_cache(self, arcadia, tmpdir):
        tmpdir = str(tmpdir)
        cache_dir = os.path.join(tmpdir, 'cache')
        os.mkdir(cache_dir)
        arcadia.base_cache_dir = cache_dir
        url = 'arcadia:/arc/trunk/arcadia/sandbox/bin'
        arcadia.get_arcadia_src_dir(url + '@3333333')

        removed_dir = os.path.join(cache_dir, 'arcadia_cache', 'tests')
        shutil.rmtree(removed_dir)

        removed_file = os.path.join(cache_dir, 'arcadia_cache', 'client.py')
        os.remove(removed_file)

        modified_file = os.path.join(cache_dir, 'arcadia_cache', 'ya.make')
        modified_file_len = os.stat(modified_file).st_size
        with open(modified_file, 'a') as f:
            f.write("Appending some text")

        new_file = os.path.join(cache_dir, 'arcadia_cache', 'foobar.txt')
        with open(new_file, 'w') as f:
            f.write("Creating new file")

        arcadia.get_arcadia_src_dir(url + '@3333333')

        cache_nodes = os.listdir(cache_dir)
        assert sorted([".metadata", ".metadata.lock", "arcadia_cache"]) == sorted(cache_nodes)

        assert os.path.isdir(removed_dir)
        assert os.path.isfile(removed_file)
        assert modified_file_len == os.stat(modified_file).st_size
        assert not os.path.isfile(new_file)


@pytest.mark.sdk_svn
class TestArcadiaTestdata:
    def test__testdata_usage_forbidden(self, arcadia_testdata, monkeypatch):
        monkeypatch.setattr(arcadia_testdata, "base_cache_dir", "/definitely/does/not/exist")
        with pytest.raises(common_errors.TaskFailure) as exc_info:
            arcadia_testdata.get_arcadia_test_data(None, None)  # arguments don't matter
        # message should say something like "not allowed on this host"
        assert "not allowed" in str(exc_info.value)
